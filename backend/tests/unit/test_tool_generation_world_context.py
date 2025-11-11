"""Unit tests for tool generation with world context."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tool_service import ToolService
from tool_generator import ToolCode


@pytest.mark.asyncio
async def test_tool_generation_uses_world_context():
    """Test that tool generation includes world context in the prompt."""
    # Arrange
    tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:")
    await tool_service.init_db()  # Initialize database tables

    # Mock world service to return test world with specific dimensions
    test_world = {
        "id": "test-world-123",
        "name": "Test Arena",
        "width": 15,
        "height": 20,
        "game_type": "grid_navigation"
    }

    mock_world_service = MagicMock()
    mock_world_service.get_world = AsyncMock(return_value=test_world)
    tool_service.world_service = mock_world_service

    # Mock the tool generator's generate_tool method to capture the prompt
    captured_world_context = {}

    async def mock_generate_tool(description, agent_id, action_set, world_context=None):
        # Capture the world_context parameter
        if world_context:
            captured_world_context.update(world_context)
        return ToolCode(
            tool_name="test_tool",
            code="@tool(...)\nasync def test_tool(args): pass",
            explanation="Test tool",
            action_id="move"
        )

    tool_service.tool_generator.generate_tool = mock_generate_tool

    # Mock file operations
    with patch("tool_service.append_tool_to_file"):
        # Act
        await tool_service.create_tool(
            agent_id="test-agent",
            world_id="test-world-123",
            description="move forward"
        )

    # Assert - Verify world context was passed to generator
    assert "width" in captured_world_context, "World width should be passed to generator"
    assert "height" in captured_world_context, "World height should be passed to generator"
    assert "game_type" in captured_world_context, "Game type should be passed to generator"
    assert captured_world_context["width"] == 15
    assert captured_world_context["height"] == 20
    assert captured_world_context["game_type"] == "grid_navigation"
