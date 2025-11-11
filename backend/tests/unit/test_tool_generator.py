"""Unit tests for ToolGenerator class."""
import ast
from unittest.mock import AsyncMock, patch

import pytest

from src.tool_generator import ToolCode, ToolGenerator


class TestToolGenerator:
    """Test suite for ToolGenerator."""

    @pytest.fixture
    def generator(self) -> ToolGenerator:
        """Create a ToolGenerator instance for testing."""
        return ToolGenerator()

    @pytest.mark.asyncio
    async def test_generate_simple_movement_tool(self, generator: ToolGenerator) -> None:
        """Test generating a simple movement tool."""
        description = "Move the agent forward 3 steps"
        agent_id = "test-agent-123"

        # Mock the Claude Agent SDK response
        # Note: The code field uses \\n for newlines to make valid JSON
        mock_response = """<output><![CDATA[
{
    "tool_name": "move_forward",
    "code": "@tool(\\"move_forward\\", \\"Move agent forward\\", {\\"steps\\": \\"int\\"})\\nasync def move_forward(args: dict[str, Any]) -> dict[str, Any]:\\n    steps = args.get('steps', 1)\\n    return {'content': [{'type': 'text', 'text': f'Moved forward {steps} steps'}]}",
    "explanation": "This tool makes your agent move forward by a number of steps!"
}
]]></output>"""

        with patch("src.tool_generator.query") as mock_query:
            # Mock the async generator
            async def mock_query_gen(*args, **kwargs):
                class MockMessage:
                    def __init__(self, result):
                        self.result = result

                yield MockMessage(mock_response)

            mock_query.return_value = mock_query_gen()

            result = await generator.generate_tool(description, agent_id)

            # Verify result structure
            assert isinstance(result, ToolCode)
            assert result.tool_name == "move_forward"
            assert "async def move_forward" in result.code
            assert "@tool" in result.code
            assert len(result.explanation) > 0

    @pytest.mark.asyncio
    async def test_generate_tool_with_parameters(self, generator: ToolGenerator) -> None:
        """Test generating a tool with multiple parameters."""
        description = "Turn the agent left or right by a certain angle"
        agent_id = "test-agent-123"

        mock_response = """<output><![CDATA[
{
    "tool_name": "turn_agent",
    "code": "@tool(\\"turn_agent\\", \\"Turn agent\\", {\\"direction\\": \\"str\\", \\"angle\\": \\"int\\"})\\nasync def turn_agent(args: dict[str, Any]) -> dict[str, Any]:\\n    direction = args.get('direction', 'left')\\n    angle = args.get('angle', 90)\\n    return {'content': [{'type': 'text', 'text': f'Turned {direction} by {angle} degrees'}]}",
    "explanation": "This tool turns your agent left or right!"
}
]]></output>"""

        with patch("src.tool_generator.query") as mock_query:
            async def mock_query_gen(*args, **kwargs):
                class MockMessage:
                    def __init__(self, result):
                        self.result = result

                yield MockMessage(mock_response)

            mock_query.return_value = mock_query_gen()

            result = await generator.generate_tool(description, agent_id)

            assert result.tool_name == "turn_agent"
            assert "direction" in result.code
            assert "angle" in result.code

    @pytest.mark.asyncio
    async def test_validate_safe_code(self, generator: ToolGenerator) -> None:
        """Test that code validation accepts safe code."""
        safe_code = """@tool("safe_tool", "Safe tool", {})
async def safe_tool(args: dict[str, Any]) -> dict[str, Any]:
    x = 1 + 1
    return {'content': [{'type': 'text', 'text': 'Safe!'}]}"""

        # Should not raise any exception
        generator._validate_code_safety(safe_code, "safe_tool")

    @pytest.mark.asyncio
    async def test_reject_dangerous_imports(self, generator: ToolGenerator) -> None:
        """Test that dangerous imports are rejected."""
        dangerous_codes = [
            "import os\n@tool('bad', 'bad', {})\nasync def bad(args): pass",
            "import subprocess\n@tool('bad', 'bad', {})\nasync def bad(args): pass",
            "import sys\n@tool('bad', 'bad', {})\nasync def bad(args): pass",
            "from os import system\n@tool('bad', 'bad', {})\nasync def bad(args): pass",
        ]

        for dangerous_code in dangerous_codes:
            with pytest.raises(ValueError, match="Forbidden import"):
                generator._validate_code_safety(dangerous_code, "bad")

    @pytest.mark.asyncio
    async def test_syntax_validation(self, generator: ToolGenerator) -> None:
        """Test that invalid Python syntax is rejected."""
        invalid_code = """@tool("bad", "bad", {})
async def bad(args: dict[str, Any]) -> dict[str, Any]
    # Missing colon above
    return {'content': []}"""

        with pytest.raises(ValueError, match="Invalid Python syntax"):
            generator._validate_code_safety(invalid_code, "bad")

    @pytest.mark.asyncio
    async def test_missing_tool_decorator(self, generator: ToolGenerator) -> None:
        """Test that code without @tool decorator is rejected."""
        code_without_decorator = """async def missing_decorator(args: dict[str, Any]) -> dict[str, Any]:
    return {'content': [{'type': 'text', 'text': 'No decorator'}]}"""

        with pytest.raises(ValueError, match="must have @tool decorator"):
            generator._validate_code_safety(code_without_decorator, "missing_decorator")

    @pytest.mark.asyncio
    async def test_function_name_mismatch(self, generator: ToolGenerator) -> None:
        """Test that function name must match tool name."""
        code_with_mismatch = """@tool("expected_name", "desc", {})
async def different_name(args: dict[str, Any]) -> dict[str, Any]:
    return {'content': []}"""

        with pytest.raises(ValueError, match="Function name.*does not match"):
            generator._validate_code_safety(code_with_mismatch, "expected_name")

    @pytest.mark.asyncio
    async def test_generate_tool_with_action_set(self, generator: ToolGenerator) -> None:
        """Test generating tool with GameActionSet parameter."""
        from src.models.game_actions import GRID_NAVIGATION_ACTIONS

        description = "Move the agent north"
        agent_id = "test-agent-123"

        mock_response = """<output><![CDATA[
{
    "tool_name": "move_north",
    "code": "@tool(\\"move_north\\", \\"Move north\\", {})\\nasync def move_north(args: dict[str, Any]) -> dict[str, Any]:\\n    return {\\n        'content': [{'type': 'text', 'text': 'Moving north'}],\\n        'action': {'action_id': 'move', 'parameters': {'direction': 'north'}}\\n    }",
    "explanation": "Moves the agent north using the game action system"
}
]]></output>"""

        with patch("src.tool_generator.query") as mock_query:
            async def mock_query_gen(*args, **kwargs):
                class MockMessage:
                    def __init__(self, result):
                        self.result = result
                yield MockMessage(mock_response)

            mock_query.return_value = mock_query_gen()

            result = await generator.generate_tool(
                description, agent_id, game_action_set=GRID_NAVIGATION_ACTIONS
            )

            assert result.tool_name == "move_north"
            assert "action" in result.code
            assert "action_id" in result.code

    def test_format_actions_for_prompt(self, generator: ToolGenerator) -> None:
        """Test formatting actions for LLM prompt."""
        from src.models.game_actions import GRID_NAVIGATION_ACTIONS

        formatted = generator._format_actions_for_prompt(GRID_NAVIGATION_ACTIONS)

        assert isinstance(formatted, str)
        assert len(formatted) > 0
        # Should contain action information
        assert "move" in formatted.lower()
        assert "direction" in formatted.lower()

    @pytest.mark.asyncio
    async def test_prompt_includes_actions(self, generator: ToolGenerator) -> None:
        """Test that the prompt includes available actions."""
        from src.models.game_actions import GRID_NAVIGATION_ACTIONS

        description = "Create a movement tool"
        agent_id = "test-agent-123"

        captured_prompt = None

        mock_response = """<output><![CDATA[
{
    "tool_name": "test_tool",
    "code": "@tool(\\"test_tool\\", \\"Test\\", {})\\nasync def test_tool(args): return {'content': [], 'action': {}}",
    "explanation": "Test"
}
]]></output>"""

        with patch("src.tool_generator.query") as mock_query:
            async def mock_query_gen(*args, **kwargs):
                nonlocal captured_prompt
                captured_prompt = kwargs.get('prompt')
                class MockMessage:
                    def __init__(self, result):
                        self.result = result
                yield MockMessage(mock_response)

            mock_query.side_effect = mock_query_gen

            await generator.generate_tool(
                description, agent_id, game_action_set=GRID_NAVIGATION_ACTIONS
            )

            # Verify prompt includes action information
            assert captured_prompt is not None
            assert "action" in captured_prompt.lower()
            # Should mention available actions or include formatted actions
            assert ("available actions" in captured_prompt.lower() or
                    "move" in captured_prompt.lower())
