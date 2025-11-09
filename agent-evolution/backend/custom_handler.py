"""Custom agent handler that uses user-provided configuration."""

import json
from typing import AsyncGenerator, Dict, Any, List
from stages import get_stage_config


class CustomAgentHandler:
    """Handles agent interactions with custom user configuration."""

    def __init__(self, api_key: str, stage: int, config: Dict[str, Any] | None = None):
        """Initialize the custom agent handler.

        Args:
            api_key: Anthropic API key
            stage: Stage number (1-4)
            config: User configuration overrides
        """
        self.api_key = api_key
        self.stage = stage
        self.base_config = get_stage_config(stage)
        self.user_config = config or {}

    def get_system_prompt(self) -> str:
        """Get the system prompt, using user config if provided."""
        if self.user_config.get('systemPrompt'):
            return self.user_config['systemPrompt']
        return self.base_config.get('system_prompt', '')

    def get_max_turns(self) -> int:
        """Get max turns, using user config if provided."""
        if self.user_config.get('maxTurns'):
            return self.user_config['maxTurns']
        return self.base_config.get('max_turns', 5)

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools based on stage and user config."""
        # Stage 1: No tools
        if self.stage == 1:
            return []

        # User configured tools
        if self.user_config.get('tools'):
            configured_tools = self.user_config.get('tools', [])
            # For stage 2, tools are visible but not executable
            # For stage 3+, check executableTools
            return [self._get_tool_schema(tool) for tool in configured_tools]

        # Default stage tools
        return self.base_config.get('tools', [])

    def _get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get the schema for a specific tool."""
        from tools import TOOL_DEFINITIONS
        for tool in TOOL_DEFINITIONS:
            if tool['name'] == tool_name:
                return tool
        return {}

    def is_tool_executable(self, tool_name: str) -> bool:
        """Check if a tool is executable based on stage and config."""
        # Stage 1 and 2: No execution
        if self.stage < 3:
            return False

        # User configured executable tools
        if self.user_config.get('executableTools'):
            return tool_name in self.user_config.get('executableTools', [])

        # Default: all tools executable in stage 3+
        return self.base_config.get('tools_executable', False)

    async def process_message(
        self, messages: List[Dict[str, Any]], stage: int
    ) -> AsyncGenerator[str, None]:
        """Process messages and stream the response.

        Args:
            messages: List of conversation messages
            stage: Current stage number

        Yields:
            JSON-encoded event strings
        """
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        system_prompt = self.get_system_prompt()
        max_turns = self.get_max_turns()
        tools = self.get_tools()

        # Build the request parameters
        request_params = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 4096,
            "messages": messages,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        # For Stage 2: Include tools but they won't be executed
        # For Stage 3+: Include tools and they can be executed
        if stage >= 2 and tools:
            request_params["tools"] = tools

        # Stream the response
        try:
            with client.messages.stream(**request_params) as stream:
                current_text = ""

                for event in stream:
                    # Handle text content
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_delta':
                            if hasattr(event, 'delta'):
                                if hasattr(event.delta, 'text'):
                                    current_text += event.delta.text
                                    yield json.dumps({
                                        "type": "text",
                                        "content": event.delta.text
                                    })

                        elif event.type == 'content_block_start':
                            if hasattr(event, 'content_block'):
                                block = event.content_block
                                if hasattr(block, 'type') and block.type == 'tool_use':
                                    # Tool use started
                                    yield json.dumps({
                                        "type": "tool_start",
                                        "toolName": block.name,
                                        "toolId": block.id
                                    })

                                    # For Stage 2, emit recognition event
                                    if stage == 2:
                                        yield json.dumps({
                                            "type": "tool_recognition",
                                            "toolName": block.name,
                                            "message": f"Agent recognizes the need for {block.name} tool"
                                        })

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "error": str(e)
            })


def get_stage_handler(api_key: str, stage: int, config: Dict[str, Any] | None = None):
    """Factory function to create a custom agent handler.

    Args:
        api_key: Anthropic API key
        stage: Stage number (1-4)
        config: User configuration overrides

    Returns:
        CustomAgentHandler instance
    """
    return CustomAgentHandler(api_key, stage, config)
