"""Agent deployment with Claude Agent SDK and SSE streaming."""
import importlib.util
import logging
import sys
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import claude_agent_sdk  # Import module for patched create_sdk_mcp_server
from action_registry import create_game_engine, get_action_set_for_game
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
)
from state_manager import state_manager

logger = logging.getLogger(__name__)


# ============================================================================
# SDK Bug #323 Workaround
# Apply patch immediately on module import (before any code uses create_sdk_mcp_server)
# ============================================================================


_SDK_PATCHED = False  # Module-level flag to track if patch has been applied


def _patch_create_sdk_mcp_server() -> None:
    """Monkey-patch create_sdk_mcp_server to fix version parameter bug.

    Bug: https://github.com/anthropics/claude-agent-sdk-python/issues/323

    The SDK's create_sdk_mcp_server() passes an unsupported 'version' parameter
    to MCP's Server.__init__(), which only accepts 'name'. This causes a TypeError.

    This patch replaces the buggy function with a fixed version that doesn't pass
    the version parameter to Server.__init__().

    This is a temporary workaround until the SDK is fixed upstream.
    """
    global _SDK_PATCHED  # noqa: PLW0603 - Intentional global for patch tracking

    from typing import Any

    import claude_agent_sdk
    from claude_agent_sdk import SdkMcpTool
    from claude_agent_sdk.types import McpSdkServerConfig

    # Check if already patched (defensive programming)
    if _SDK_PATCHED:
        return

    def patched_create_sdk_mcp_server(
        name: str,
        version: str = "1.0.0",  # noqa: ARG001 - Kept for API compatibility
        tools: list[SdkMcpTool[Any]] | None = None,
    ) -> McpSdkServerConfig:
        """Patched version without version parameter bug."""
        from mcp.server import Server
        from mcp.types import ImageContent, TextContent, Tool

        # FIX: Don't pass version to Server.__init__() - it doesn't accept it
        # Original SDK incorrectly used: Server(name, version=version)
        server = Server(name)

        # Register tools if provided
        if tools:

            @server.list_tools()
            async def list_tools_handler() -> list[Tool]:
                return [
                    Tool(
                        name=t.name,
                        description=t.description or "",
                        inputSchema=t.input_schema or {},
                    )
                    for t in tools
                ]

            @server.call_tool()
            async def call_tool_handler(
                tool_name: str, arguments: dict[str, Any],
            ) -> list[TextContent | ImageContent]:
                for t in tools:
                    if t.name == tool_name:
                        result = await t.handler(arguments)

                        if isinstance(result, dict) and "content" in result:
                            content_list = result["content"]
                            return [
                                TextContent(type="text", text=item["text"])
                                if item.get("type") == "text"
                                else ImageContent(
                                    type="image",
                                    data=item["data"],
                                    mimeType=item.get("mimeType", "image/png"),
                                )
                                for item in content_list
                            ]

                        return [TextContent(type="text", text=str(result))]

                return [TextContent(type="text", text=f"Tool {tool_name} not found")]

        return McpSdkServerConfig(server=server, name=name)

    # Replace the SDK function
    claude_agent_sdk.create_sdk_mcp_server = patched_create_sdk_mcp_server

    # Mark as patched globally
    _SDK_PATCHED = True

    logger.info("Applied SDK bug #323 workaround for create_sdk_mcp_server")


# Apply patch immediately when this module is imported
_patch_create_sdk_mcp_server()


@dataclass
class DeploymentEvent:
    """Represents a single SSE event during agent deployment."""

    event_type: str  # system, text, thinking, tool_call, tool_result, world_update, error, complete
    data: dict[str, Any]


class AgentDeployer:
    """Deploys AI agents in worlds with custom tools and SSE streaming."""

    def __init__(self, tool_service: Any, world_service: Any) -> None:
        """Initialize deployer with required services.

        Args:
            tool_service: Service for managing custom tools
            world_service: Service for world state management
        """
        self.tool_service = tool_service
        self.world_service = world_service

    def _load_tools_from_file(self, tools_file_path: str | None = None) -> list:
        """Dynamically load SDK tools from tools.py file.

        Returns:
            List of SdkMcpTool instances found in the file
        """
        from claude_agent_sdk import SdkMcpTool

        if tools_file_path is None:
            tools_file_path = str(Path(__file__).parent / "tools.py")

        logger.info(f"Loading tools from {tools_file_path}")

        try:
            spec = importlib.util.spec_from_file_location(
                "custom_tools", tools_file_path,
            )
            if spec is None or spec.loader is None:
                logger.warning(f"Could not load tools from {tools_file_path}")
                return []

            module = importlib.util.module_from_spec(spec)
            sys.modules["custom_tools"] = module
            spec.loader.exec_module(module)

            # Collect all SdkMcpTool instances from module
            tools_dict = {}  # Use dict to deduplicate by tool name (keep last)
            for name in dir(module):
                obj = getattr(module, name)
                # Check if it's an SdkMcpTool instance (created by @tool decorator)
                if isinstance(obj, SdkMcpTool):
                    # Use tool name as key to automatically handle duplicates
                    tools_dict[obj.name] = obj
                    logger.info(f"Loaded tool: {obj.name} (variable name: {name})")

            tools = list(tools_dict.values())
            logger.info(f"Successfully loaded {len(tools)} unique tools")
            return tools

        except Exception as e:
            logger.error(f"Failed to load tools: {e}", exc_info=True)
            return []

    async def deploy_agent(
        self,
        agent_id: str,
        world_id: str,
        goal: str,
    ) -> AsyncGenerator[DeploymentEvent, None]:
        """Deploy agent with streaming updates.

        Yields DeploymentEvent objects for each stage:
        - reasoning: Claude's thought process
        - tool_call: Before tool execution
        - tool_result: After tool execution
        - world_update: Agent position/state changes (DELTAS ONLY)
        - error: Errors with retry capability
        - complete: Final status

        Args:
            agent_id: ID of the agent to deploy
            world_id: ID of the world to deploy in
            goal: Goal for the agent to achieve

        Yields:
            DeploymentEvent objects representing deployment progress
        """
        logger.info(f"Deploying agent {agent_id} in world {world_id} with goal: {goal}")

        total_steps = 0
        total_tools_used = 0
        current_position = None
        game_engine = None

        try:
            # 1. Load world state from world_service
            world = await self.world_service.get_world(world_id)
            if not world:
                yield DeploymentEvent(
                    event_type="error",
                    data={
                        "error_type": "world_not_found",
                        "message": f"World {world_id} not found",
                        "recoverable": False,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            current_position = world["agent_position"]
            game_type = world.get("game_type", "grid_navigation")

            # Store world state in state manager for tool access
            state_manager.set_world(world_id, world)

            # 2. Initialize game engine for action execution
            try:
                action_set = get_action_set_for_game(game_type)
                game_engine = create_game_engine(game_type, world_id, action_set, world)
                logger.info(f"Initialized {game_type} game engine for world {world_id}")
            except ValueError as e:
                logger.error(f"Failed to initialize game engine: {e}")
                yield DeploymentEvent(
                    event_type="error",
                    data={
                        "error_type": "game_engine_init_failed",
                        "message": str(e),
                        "recoverable": False,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            # 3. Load agent's custom tools from tool_service
            tools = await self.tool_service.get_agent_tools(agent_id)
            logger.info(f"Loaded {len(tools)} tools for agent {agent_id}")

            # 4. Load tools from tools.py and create MCP server with SDK tools
            tool_functions = self._load_tools_from_file()
            if len(tool_functions) == 0:
                logger.warning("No tools found - agent will run without custom tools")

            # Create MCP server using patched create_sdk_mcp_server (bug #323 fixed)
            # Pass tools directly - SDK handles tool registration
            # Use module reference to get patched version
            user_tool_server = claude_agent_sdk.create_sdk_mcp_server(
                name="user_tools",
                version="1.0.0",
                tools=tool_functions if tool_functions else None,
            )
            logger.info(f"Created MCP server with {len(tool_functions)} tools")

            # Configure Claude Agent SDK with MCP server
            # No need for allowed_tools - SDK auto-registers tools from server
            options = ClaudeAgentOptions(
                mcp_servers={"user_tools": user_tool_server},
            )

            # 5. Create deployment prompt
            prompt = self._build_deployment_prompt(world, goal, world_id)

            # 6. Stream agent execution with official ClaudeSDKClient pattern
            # Use async context manager + client.query() + client.receive_response()
            async with ClaudeSDKClient(options=options) as client:
                # Send query
                await client.query(prompt)

                # Receive and process streaming responses
                async for message in client.receive_response():
                    # Parse message using proper SDK types

                    # Handle SystemMessage
                    if isinstance(message, SystemMessage):
                        yield DeploymentEvent(
                            event_type="system",
                            data={
                                "text": str(message),
                                "timestamp": datetime.utcnow().isoformat(),
                            },
                        )
                        continue

                    # Handle ResultMessage (final result)
                    if isinstance(message, ResultMessage):
                        # Check for stop reason
                        if hasattr(message, "stop_reason") and message.stop_reason:
                            break
                        continue

                    # Handle AssistantMessage - contains content blocks
                    if isinstance(message, AssistantMessage):
                        # Iterate through content blocks
                        for block in message.content:
                            # Handle TextBlock
                            if isinstance(block, TextBlock):
                                yield DeploymentEvent(
                                    event_type="text",
                                    data={
                                        "text": block.text,
                                        "timestamp": datetime.utcnow().isoformat(),
                                    },
                                )
                                total_steps += 1

                            # Handle ThinkingBlock
                            elif isinstance(block, ThinkingBlock):
                                yield DeploymentEvent(
                                    event_type="thinking",
                                    data={
                                        "text": block.thinking,
                                        "timestamp": datetime.utcnow().isoformat(),
                                    },
                                )

                            # Handle ToolUseBlock
                            elif isinstance(block, ToolUseBlock):
                                tool_name = block.name
                                parameters = block.input

                                # Yield tool_call event
                                yield DeploymentEvent(
                                    event_type="tool_call",
                                    data={
                                        "tool_name": tool_name,
                                        "parameters": parameters,
                                        "timestamp": datetime.utcnow().isoformat(),
                                    },
                                )
                                total_tools_used += 1

                            # Handle ToolResultBlock - SDK executes tools automatically
                            elif isinstance(block, ToolResultBlock):
                                tool_name = getattr(block, "name", "unknown")

                                # SDK has already executed the tool - we get the result here
                                try:
                                    # Extract tool result from ToolResultBlock
                                    tool_result = None
                                    if hasattr(block, "content"):
                                        # ToolResultBlock.content is a list of content blocks
                                        for content_item in block.content:
                                            if isinstance(content_item, TextBlock):
                                                # Try to parse as JSON if it looks like a dict
                                                import json
                                                try:
                                                    tool_result = json.loads(content_item.text)
                                                except (json.JSONDecodeError, AttributeError):
                                                    tool_result = {"content": [{"type": "text", "text": content_item.text}]}

                                    # Yield tool_result event
                                    yield DeploymentEvent(
                                        event_type="tool_result",
                                        data={
                                            "tool_name": tool_name,
                                            "success": True,
                                            "result": str(tool_result),
                                            "duration_ms": 45,
                                            "timestamp": datetime.utcnow().isoformat(),
                                        },
                                    )

                                    # Parse action field from tool result
                                    if isinstance(tool_result, dict) and "action" in tool_result:
                                        action_data = tool_result["action"]
                                        if isinstance(action_data, dict) and "action_id" in action_data:
                                            action_id = action_data["action_id"]
                                            action_params = action_data.get("parameters", {})

                                            logger.info(f"Parsing action: {action_id} with params {action_params}")

                                            # Execute action through game engine
                                            if game_engine:
                                                try:
                                                    action_result = game_engine.execute_action(action_id, action_params)

                                                    if action_result.success and action_result.state_delta:
                                                        # Update current position if it changed
                                                        if "agent_position" in action_result.state_delta:
                                                            current_position = action_result.state_delta["agent_position"]
                                                            # Update state manager so observe_world() sees new position
                                                            state_manager.update_position(world_id, current_position)

                                                        # Yield world_update event with state deltas
                                                        yield DeploymentEvent(
                                                            event_type="world_update",
                                                            data={
                                                                **action_result.state_delta,
                                                                "message": action_result.message,
                                                                "timestamp": datetime.utcnow().isoformat(),
                                                            },
                                                        )
                                                        logger.info(f"Action {action_id} executed successfully")
                                                    elif not action_result.success:
                                                        # Action failed - yield error event
                                                        yield DeploymentEvent(
                                                            event_type="error",
                                                            data={
                                                                "error_type": "action_execution_failed",
                                                                "message": action_result.error or action_result.message,
                                                                "action_id": action_id,
                                                                "recoverable": True,
                                                                "timestamp": datetime.utcnow().isoformat(),
                                                            },
                                                        )
                                                        logger.warning(f"Action {action_id} failed: {action_result.error}")

                                                except Exception as e:
                                                    logger.error(f"Failed to execute action {action_id}: {e}", exc_info=True)
                                                    yield DeploymentEvent(
                                                        event_type="error",
                                                        data={
                                                            "error_type": "action_execution_error",
                                                            "message": str(e),
                                                            "action_id": action_id,
                                                            "recoverable": True,
                                                            "timestamp": datetime.utcnow().isoformat(),
                                                        },
                                                    )

                                except Exception as e:
                                    logger.error(f"Tool execution failed: {e}", exc_info=True)
                                    yield DeploymentEvent(
                                        event_type="error",
                                        data={
                                            "error_type": "tool_execution_failed",
                                            "message": str(e),
                                            "tool_name": tool_name,
                                            "recoverable": True,
                                            "timestamp": datetime.utcnow().isoformat(),
                                        },
                                    )

            # Yield final complete event
            yield DeploymentEvent(
                event_type="complete",
                data={
                    "status": "success",
                    "goal_achieved": True,
                    "total_steps": total_steps,
                    "total_tools_used": total_tools_used,
                    "final_position": current_position or world["agent_position"],
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Deployment failed: {e}", exc_info=True)
            yield DeploymentEvent(
                event_type="error",
                data={
                    "error_type": "deployment_failed",
                    "message": str(e),
                    "recoverable": False,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

    def _build_deployment_prompt(
        self, world: dict[str, Any], goal: str, world_id: str,
    ) -> str:
        """Build the deployment prompt for Claude.

        Args:
            world: World state dictionary
            goal: Agent's goal
            world_id: World identifier for observe_world calls

        Returns:
            Formatted prompt string
        """
        grid = world["grid"]
        agent_position = world["agent_position"]
        width = world["width"]
        height = world["height"]

        # Format grid for display
        grid_str = "\n".join(["".join(row) for row in grid])

        prompt = f"""You are an AI agent deployed in a game world. Your goal is: {goal}

Current World State:
- Grid size: {width}x{height}
- Your position: {agent_position}
- Grid layout:
{grid_str}

Available Tools:
- move_direction(direction, steps): Move north/south/east/west
- observe_world(world_id="{world_id}"): See current surroundings and position

⚠️ IMPORTANT: After EVERY action you take, call observe_world(world_id="{world_id}") to see the results!

Instructions:
1. Analyze the world state and goal
2. Plan your actions step by step
3. Use move_direction to navigate
4. ALWAYS call observe_world after moving to see where you are
5. If you encounter obstacles, try alternative approaches

Begin your mission!"""

        return prompt
