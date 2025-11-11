"""Unit tests for validating generated tools use valid world actions."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tool_service import ToolService
from tool_generator import ToolCode
from action_registry import get_action_set_for_game


@pytest.mark.asyncio
async def test_generated_tool_uses_world_action():
    """Test that generated tool's action_id is validated against world's action set."""
    # Arrange
    tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:")
    await tool_service.init_db()

    # Mock world service to return test world
    test_world = {
        "id": "test-world-123",
        "name": "Test Arena",
        "width": 10,
        "height": 10,
        "game_type": "grid_navigation"
    }

    mock_world_service = MagicMock()
    mock_world_service.get_world = AsyncMock(return_value=test_world)
    tool_service.world_service = mock_world_service

    # Get the actual action set for grid_navigation
    action_set = get_action_set_for_game("grid_navigation")
    valid_action_ids = [action.action_id for action in action_set.actions]

    # Mock the tool generator to return a tool with INVALID action_id
    async def mock_generate_tool(description, agent_id, action_set, world_context=None):
        return ToolCode(
            tool_name="invalid_action_tool",
            code="@tool(...)\nasync def invalid_action_tool(args): pass",
            explanation="Test tool",
            action_id="INVALID_ACTION_ID"  # This should fail validation
        )

    tool_service.tool_generator.generate_tool = mock_generate_tool

    # Mock file operations
    with patch("tool_service.append_tool_to_file"):
        # Act & Assert - Should raise ValueError for invalid action_id
        with pytest.raises(ValueError, match="Invalid action_id"):
            await tool_service.create_tool(
                agent_id="test-agent",
                world_id="test-world-123",
                description="move forward"
            )


@pytest.mark.asyncio
async def test_generated_tool_with_valid_action_succeeds():
    """Test that generated tool with valid action_id succeeds."""
    # Arrange
    tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:")
    await tool_service.init_db()

    # Mock world service
    test_world = {
        "id": "test-world-123",
        "name": "Test Arena",
        "width": 10,
        "height": 10,
        "game_type": "grid_navigation"
    }

    mock_world_service = MagicMock()
    mock_world_service.get_world = AsyncMock(return_value=test_world)
    tool_service.world_service = mock_world_service

    # Mock the tool generator to return a tool with VALID action_id
    async def mock_generate_tool(description, agent_id, action_set, world_context=None):
        return ToolCode(
            tool_name="move_forward_tool",
            code="@tool(...)\nasync def move_forward_tool(args): pass",
            explanation="Test tool",
            action_id="move"  # This is a valid action_id for grid_navigation
        )

    tool_service.tool_generator.generate_tool = mock_generate_tool

    # Mock file operations
    with patch("tool_service.append_tool_to_file"):
        # Act - Should succeed with valid action_id
        result = await tool_service.create_tool(
            agent_id="test-agent",
            world_id="test-world-123",
            description="move forward"
        )

        # Assert
        assert result["action_id"] == "move"
        assert result["category"] == "Movement"  # move action is in Movement category
