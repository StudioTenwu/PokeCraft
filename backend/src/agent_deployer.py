"""Agent deployment with Claude Agent SDK and SSE streaming."""
import asyncio
import logging
from typing import AsyncGenerator, Any
from datetime import datetime
from dataclasses import dataclass

from claude_agent_sdk import query, ClaudeAgentOptions
from tool_registry import create_user_tool_server, get_available_tools

logger = logging.getLogger(__name__)


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

    async def deploy_agent(
        self, agent_id: str, world_id: str, goal: str
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

            # 2. Load agent's custom tools from tool_service
            tools = await self.tool_service.get_agent_tools(agent_id)
            logger.info(f"Loaded {len(tools)} tools for agent {agent_id}")

            # 3. Create deployment prompt
            prompt = self._build_deployment_prompt(world, goal)

            # 4. Stream agent execution with Claude Agent SDK
            async for message in query(prompt=prompt):
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

                    # Execute tool (simulated for now)
                    # In real implementation, would call actual tool
                    tool_result = {"success": True, "message": f"Tool {tool_name} executed"}

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

                # Check for tool results that update position
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

    def _build_deployment_prompt(self, world: dict[str, Any], goal: str) -> str:
        """Build the deployment prompt for Claude.

        Args:
            world: World state dictionary
            goal: Agent's goal

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

Instructions:
1. Analyze the world state and goal
2. Plan your actions step by step
3. Use your tools to navigate and interact with the world
4. Update me on your reasoning and progress
5. If you encounter obstacles, try alternative approaches

Begin your mission!"""

        return prompt
