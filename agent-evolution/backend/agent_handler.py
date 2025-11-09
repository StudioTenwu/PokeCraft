"""Agent handler using Claude Agent SDK for the agent evolution curriculum."""

import asyncio
import os
from typing import Optional, AsyncGenerator, Dict, Any

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
)

from stages import get_stage_config
from tools import execute_tool


class AgentHandler:
    """Handles agent interactions using Claude Agent SDK across different stages."""

    def __init__(self, stage: int, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize the agent handler.

        Args:
            stage: Stage number (1-4)
            model: Claude model to use
        """
        self.stage = stage
        self.model = model
        self.config = get_stage_config(stage)

        # Claude Agent SDK handles authentication automatically via system credentials
        # No need to validate ANTHROPIC_API_KEY manually

    async def process_message(
        self, user_message: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a user message and stream the response.

        Args:
            user_message: The user's message

        Yields:
            Dictionaries containing response chunks with type and content
        """
        # Get stage configuration
        system_prompt = self.config["system_prompt"]
        max_turns = self.config["max_turns"]
        tools_executable = self.config["tools_executable"]

        # For Stage 2, we need special handling - tools are visible but not executable
        # We'll provide tools to the agent options but intercept execution
        tools = self.config.get("tools", [])

        # Configure agent options
        options = ClaudeAgentOptions(
            model=self.model,
            system_prompt=system_prompt,
            permission_mode="bypassPermissions",
            max_turns=max_turns,
            # For stages 1 and 2, we don't provide tools or we handle them specially
            # For stages 3 and 4, we provide tools normally
        )

        # Stage 2 special case: Agent can see tools but shouldn't execute them
        # We'll handle this by not passing tools to the SDK
        # and having the system prompt explain the tools

        async with ClaudeSDKClient(options=options) as client:
            # Send the user's message
            await client.query(user_message)

            # Stream the response
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            # Yield text content
                            yield {
                                "type": "text",
                                "content": block.text
                            }

                        elif isinstance(block, ToolUseBlock):
                            # Handle tool execution based on stage
                            tool_name = block.name
                            tool_input = block.input

                            # Yield tool usage notification
                            yield {
                                "type": "tool_use",
                                "tool_name": tool_name,
                                "tool_input": tool_input
                            }

                            # For Stage 2, explain that we can't execute
                            if not tools_executable:
                                yield {
                                    "type": "tool_result",
                                    "tool_name": tool_name,
                                    "success": False,
                                    "message": "Tool execution is not enabled in this stage. "
                                              "The agent can only explain what it would do."
                                }
                            else:
                                # For Stages 3 and 4, execute the tool
                                result = execute_tool(tool_name, tool_input)
                                yield {
                                    "type": "tool_result",
                                    "tool_name": tool_name,
                                    **result
                                }

    async def chat(self, user_message: str) -> Dict[str, Any]:
        """Process a chat message and return the complete response.

        This is a simplified synchronous wrapper for testing.

        Args:
            user_message: The user's message

        Returns:
            Dictionary with response text and metadata
        """
        response_parts = []
        tool_calls = []

        async for chunk in self.process_message(user_message):
            if chunk["type"] == "text":
                response_parts.append(chunk["content"])
            elif chunk["type"] == "tool_use":
                tool_calls.append({
                    "tool": chunk["tool_name"],
                    "input": chunk["tool_input"]
                })
            elif chunk["type"] == "tool_result":
                # Store tool result
                if tool_calls:
                    tool_calls[-1]["result"] = chunk

        return {
            "response": "".join(response_parts),
            "tool_calls": tool_calls,
            "stage": self.stage,
            "max_turns": self.config["max_turns"]
        }


# Simplified version without SDK for Stage 2 where tools are only explained
class Stage2AgentHandler:
    """Special handler for Stage 2 that doesn't use actual tool execution.

    In Stage 2, the agent should explain what tools it would use
    without actually calling them.
    """

    def __init__(self, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize Stage 2 agent handler.

        Args:
            model: Claude model to use
        """
        self.stage = 2
        self.model = model
        self.config = get_stage_config(2)

    async def process_message(
        self, user_message: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process message for Stage 2 (explain tools only).

        Args:
            user_message: The user's message

        Yields:
            Response chunks
        """
        system_prompt = self.config["system_prompt"]
        max_turns = self.config["max_turns"]

        # For Stage 2, we don't pass tools to SDK
        # The system prompt explains what tools exist
        options = ClaudeAgentOptions(
            model=self.model,
            system_prompt=system_prompt,
            permission_mode="bypassPermissions",
            max_turns=max_turns,
        )

        async with ClaudeSDKClient(options=options) as client:
            await client.query(user_message)

            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            yield {
                                "type": "text",
                                "content": block.text
                            }

    async def chat(self, user_message: str) -> Dict[str, Any]:
        """Process a chat message for Stage 2.

        Args:
            user_message: The user's message

        Returns:
            Dictionary with response
        """
        response_parts = []

        async for chunk in self.process_message(user_message):
            if chunk["type"] == "text":
                response_parts.append(chunk["content"])

        return {
            "response": "".join(response_parts),
            "tool_calls": [],
            "stage": self.stage,
            "max_turns": self.config["max_turns"]
        }


def create_agent_handler(stage: int, model: str = "claude-sonnet-4-5-20250929"):
    """Factory function to create the appropriate agent handler for a stage.

    Args:
        stage: Stage number (1-4)
        model: Claude model to use

    Returns:
        AgentHandler instance (or Stage2AgentHandler for stage 2)
    """
    if stage == 2:
        return Stage2AgentHandler(model=model)
    else:
        return AgentHandler(stage=stage, model=model)


# Synchronous wrapper for convenience
def run_agent(stage: int, user_message: str, model: str = "claude-sonnet-4-5-20250929") -> Dict[str, Any]:
    """Synchronous wrapper to run an agent.

    Args:
        stage: Stage number (1-4)
        user_message: User's message
        model: Claude model to use

    Returns:
        Dictionary with response and metadata
    """
    handler = create_agent_handler(stage, model)
    return asyncio.run(handler.chat(user_message))
