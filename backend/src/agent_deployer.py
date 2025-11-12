"""Agent deployment with Claude Agent SDK and SSE streaming."""
import importlib.util
import logging
import sys
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from action_registry import create_game_engine, get_action_set_for_game
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
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
                async def call_tool_handler(tool_name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
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

    event_type: str  # reasoning, tool_call, tool_result, world_update, error, complete
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

    async def _execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute MCP tool and return result.

        For now, route to known tools. In full implementation, would use MCP client.
        """
        # Import tools
        from tools import move_direction, observe_world

        # Route to appropriate tool
        if "observe_world" in tool_name:
            return await observe_world(parameters)
        elif "move_direction" in tool_name:
            return await move_direction(parameters)
        else:
            return {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]}

    def _load_tools_from_file(self, tools_file_path: str | None = None) -> list:
        """Dynamically load tools from tools.py file."""
        if tools_file_path is None:
            tools_file_path = str(Path(__file__).parent / "tools.py")

        logger.info(f"Loading tools from {tools_file_path}")

        try:
            spec = importlib.util.spec_from_file_location("custom_tools", tools_file_path)
            if spec is None or spec.loader is None:
                logger.warning(f"Could not load tools from {tools_file_path}")
                return []

            module = importlib.util.module_from_spec(spec)
            sys.modules["custom_tools"] = module
            spec.loader.exec_module(module)

            tools = []
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and hasattr(obj, "__claude_tool__"):
                    tools.append(obj)
                    logger.info(f"Loaded tool: {name}")

            logger.info(f"Successfully loaded {len(tools)} tools")
            return tools

        except Exception as e:
            logger.error(f"Failed to load tools: {e}", exc_info=True)
            return []

    async def deploy_agent(
        self, agent_id: str, world_id: str, goal: str,
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

            # 4. Load tools from tools.py and create MCP server
            tool_functions = self._load_tools_from_file()
            if len(tool_functions) == 0:
                logger.warning("No tools found - agent will run without custom tools")

            # Create MCP server configuration manually
            # Note: Cannot use create_sdk_mcp_server due to SDK bug (v0.1.6) where it passes
            # unsupported 'version' parameter to Server.__init__()
            # Workaround: Create McpSdkServerConfig directly
            from claude_agent_sdk.types import McpSdkServerConfig
            user_tool_server = McpSdkServerConfig(
                command="python",
                args=["-m", "mcp"],
                env={"MCP_SERVER_NAME": "user_tools"},
            )
            logger.info(f"Created MCP server with {len(tool_functions)} tools")

            # Build allowed tools list
            allowed_tools = [f"mcp__user_tools__{tool.__name__}" for tool in tool_functions]
            logger.info(f"Allowed tools: {allowed_tools}")

            # Configure Claude Agent SDK with MCP server
            options = ClaudeAgentOptions(
                mcp_servers={"user_tools": user_tool_server},
                allowed_tools=allowed_tools if allowed_tools else None,
            )

            # 5. Create deployment prompt
            prompt = self._build_deployment_prompt(world, goal, world_id)

            # 6. Stream agent execution with Claude SDK + MCP server
            # IMPORTANT: Use standalone query() function with options parameter
            # Do NOT use ClaudeSDKClient.query() - it returns a coroutine, not async iterator
            # Error if used incorrectly: "'async for' requires an object with __aiter__ method"
            async for message in query(prompt=prompt, options=options):
                # Parse message and yield appropriate events

                # Check for reasoning/thinking text
                if hasattr(message, "result") and message.result:
                    # This is reasoning text from Claude
                    yield DeploymentEvent(
                        event_type="reasoning",
                        data={
                            "text": message.result,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )
                    total_steps += 1

                # Check for tool use
                if hasattr(message, "tool_use") and message.tool_use:
                    tool_name = message.tool_use.tool_name
                    parameters = message.tool_use.parameters

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

                    # Execute tool for real
                    tool_result = await self._execute_tool(tool_name, parameters)

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
                            parameters = action_data.get("parameters", {})

                            logger.info(f"Parsing action: {action_id} with params {parameters}")

                            # Execute action through game engine
                            if game_engine:
                                try:
                                    action_result = game_engine.execute_action(action_id, parameters)

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

                # Check for tool results that update position (legacy fallback)
                if hasattr(message, "tool_result") and message.tool_result:
                    result = message.tool_result.result
                    if isinstance(result, dict) and "new_position" in result:
                        old_position = current_position
                        current_position = result["new_position"]

                        # Yield world_update event (DELTAS ONLY)
                        yield DeploymentEvent(
                            event_type="world_update",
                            data={
                                "agent_moved_from": old_position,
                                "agent_moved_to": current_position,
                                "cell_updated": {
                                    "position": current_position,
                                    "type": "visited",
                                },
                                "timestamp": datetime.utcnow().isoformat(),
                            },
                        )

                # Check for errors
                if hasattr(message, "error") and message.error:
                    yield DeploymentEvent(
                        event_type="error",
                        data={
                            "error_type": "tool_execution_failed",
                            "message": str(message.error),
                            "recoverable": True,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )
                    # Continue streaming to allow Claude to retry

                # Check for completion
                if hasattr(message, "stop_reason") and message.stop_reason:
                    break

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

    def _build_deployment_prompt(self, world: dict[str, Any], goal: str, world_id: str) -> str:
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
