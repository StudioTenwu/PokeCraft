"""Agent deployer service for executing agents with custom tools.

This service:
1. Loads custom tools for an agent
2. Deploys agent with Claude Agent SDK
3. Streams reasoning and tool execution via SSE
4. Updates world state in real-time
"""
import logging
from dataclasses import dataclass
from typing import Any, AsyncGenerator

from claude_agent_sdk import query

from src.tool_registry import get_available_tools, write_tools_to_temp_file

logger = logging.getLogger(__name__)


@dataclass
class DeploymentEvent:
    """Represents a deployment event for SSE streaming."""

    event_type: str  # progress, reasoning, tool_call, complete, error
    data: dict[str, Any]


class AgentDeployer:
    """Service for deploying agents with custom tools in worlds."""

    def __init__(self, tool_service: Any, world_service: Any) -> None:
        """Initialize agent deployer.

        Args:
            tool_service: Service for managing tools
            world_service: Service for managing worlds
        """
        self.tool_service = tool_service
        self.world_service = world_service

    async def deploy_agent(
        self, agent_id: str, world_id: str, goal: str
    ) -> AsyncGenerator[DeploymentEvent, None]:
        """Deploy an agent in a world with a goal.

        This method:
        1. Loads the world
        2. Retrieves custom tools for the agent
        3. Creates temporary tools file
        4. Streams agent execution via Claude Agent SDK
        5. Yields SSE events for frontend consumption

        Args:
            agent_id: ID of the agent to deploy
            world_id: ID of the world to deploy in
            goal: Natural language goal for the agent

        Yields:
            DeploymentEvent: Events for SSE streaming
        """
        try:
            # Event 1: Starting
            yield DeploymentEvent(
                event_type="progress",
                data={"status": "starting", "message": "Initializing agent..."},
            )

            # Load world
            world = await self.world_service.get_world(world_id)
            if not world:
                yield DeploymentEvent(
                    event_type="error", data={"message": f"World {world_id} not found"}
                )
                return

            logger.info(f"Loaded world {world_id} for agent {agent_id}")

            # Event 2: Loading tools
            yield DeploymentEvent(
                event_type="progress",
                data={"status": "loading_tools", "message": "Loading custom tools..."},
            )

            # Get agent's custom tools from database
            tools_data = await self.tool_service.get_agent_tools(agent_id)
            logger.info(f"Found {len(tools_data)} custom tools for agent {agent_id}")

            # Write tools to temporary file and load them
            if tools_data:
                temp_tools_file = write_tools_to_temp_file(tools_data)
                tools = get_available_tools(agent_id, temp_tools_file)
                logger.info(f"Loaded {len(tools)} callable tools")
            else:
                tools = []

            # Event 3: Starting execution
            yield DeploymentEvent(
                event_type="progress",
                data={"status": "executing", "message": "Agent is thinking..."},
            )

            # Build prompt with world context and goal
            world_context = self._build_world_context(world)
            prompt = f"""You are an AI agent deployed in a 2D grid world. Your goal: {goal}

World Context:
{world_context}

Available Custom Tools:
{self._format_tools_for_prompt(tools_data)}

Think step by step to accomplish your goal. Use your custom tools when appropriate.
"""

            logger.debug(f"Deployment prompt: {prompt[:200]}...")

            # Stream agent execution via Claude Agent SDK
            async for message in query(prompt=prompt):
                # Handle reasoning text
                if hasattr(message, "result") and message.result:
                    yield DeploymentEvent(
                        event_type="reasoning",
                        data={"message": message.result},
                    )
                    logger.debug(f"Agent reasoning: {message.result[:100]}")

                # Handle tool calls
                if hasattr(message, "content"):
                    for content_block in message.content:
                        if hasattr(content_block, "tool_name"):
                            tool_name = content_block.tool_name
                            tool_input = getattr(content_block, "tool_input", {})

                            logger.info(
                                f"Agent called tool: {tool_name} with args {tool_input}"
                            )

                            # Yield tool call event
                            yield DeploymentEvent(
                                event_type="tool_call",
                                data={
                                    "tool": tool_name,
                                    "args": tool_input,
                                    "result": f"Tool {tool_name} executed",
                                },
                            )

            # Event 4: Completion
            yield DeploymentEvent(
                event_type="complete",
                data={
                    "status": "complete",
                    "message": "Goal accomplished!",
                    "agent_id": agent_id,
                    "world_id": world_id,
                },
            )

            logger.info(f"Agent {agent_id} completed deployment in world {world_id}")

        except Exception as e:
            logger.error(f"Error during agent deployment: {e}", exc_info=True)
            yield DeploymentEvent(
                event_type="error", data={"message": f"Deployment error: {str(e)}"}
            )

    def _build_world_context(self, world: dict[str, Any]) -> str:
        """Build a text description of the world for the agent.

        Args:
            world: World data from database

        Returns:
            str: Human-readable world context
        """
        description = world.get("description", "A grid world")
        grid_size = world.get("grid_size", 10)
        return f"{description}\nGrid size: {grid_size}x{grid_size}"

    def _format_tools_for_prompt(self, tools_data: list[dict[str, Any]]) -> str:
        """Format tools list for inclusion in prompt.

        Args:
            tools_data: List of tool dictionaries from database

        Returns:
            str: Formatted tools list
        """
        if not tools_data:
            return "No custom tools available."

        lines = []
        for tool in tools_data:
            name = tool.get("name", "unknown")
            description = tool.get("description", "No description")
            lines.append(f"- {name}: {description}")

        return "\n".join(lines)
