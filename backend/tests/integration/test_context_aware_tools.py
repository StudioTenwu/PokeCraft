"""
Integration tests for context-aware tool generation workflow.

Tests the complete end-to-end flow:
1. Create a world with specific game type and actions
2. Fetch available actions for that world
3. Generate a context-aware tool based on world context
4. Verify the tool is properly persisted and includes world actions
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


def test_full_context_aware_tool_workflow(client):
    """Test complete workflow: create world -> get actions -> create tool."""

    # Step 1: Create a world with specific game type
    world_data = {
        "name": "Grid Navigation World",
        "game_type": "grid_navigation",
        "description": "A world where agents navigate on a 2D grid"
    }

    response = client.post("/api/worlds/create", json=world_data)
    assert response.status_code == 200
    world = response.json()
    world_id = world["id"]
    assert world["name"] == "Grid Navigation World"
    assert world["game_type"] == "grid_navigation"

    # Step 2: Fetch available actions for the world
    response = client.get(f"/api/worlds/{world_id}/actions")
    assert response.status_code == 200
    actions = response.json()

    # Verify grid_navigation actions are returned
    assert len(actions) > 0
    action_names = [action["name"] for action in actions]
    assert "move_forward" in action_names
    assert "turn_left" in action_names
    assert "turn_right" in action_names

    # Step 3: Create a context-aware tool with the world_id
    # Mock the LLM client since we don't want to hit actual Claude API
    mock_tool_code = '''
@tool
def navigate_to_target(x: int, y: int) -> str:
    """Navigate agent to target coordinates using move_forward, turn_left, turn_right."""
    # Implementation would use available world actions
    return f"Navigating to ({x}, {y})"
'''

    mock_explanation = "This tool navigates the agent to target coordinates using the available grid navigation actions: move_forward, turn_left, and turn_right."

    with patch('src.tool_generator.ToolGenerator.generate_tool') as mock_generate:
        mock_generate.return_value = {
            "tool_name": "navigate_to_target",
            "code": mock_tool_code,
            "explanation": mock_explanation,
            "available_actions": ["move_forward", "turn_left", "turn_right"]
        }

        tool_request = {
            "agent_id": "test-agent-123",
            "world_id": world_id,
            "description": "Create a tool that navigates the agent to target coordinates"
        }

        response = client.post("/api/tools/create", json=tool_request)
        assert response.status_code == 200
        tool = response.json()

        # Verify tool was created with world context
        assert tool["tool_name"] == "navigate_to_target"
        assert "move_forward" in tool["code"]
        assert tool["explanation"] == mock_explanation

        # Verify the tool generator was called with world_id
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args[1]
        assert call_kwargs["world_id"] == world_id
        assert call_kwargs["agent_id"] == "test-agent-123"



def test_get_actions_for_nonexistent_world(client):
    """Test fetching actions for a world that doesn't exist."""
    response = client.get("/api/worlds/nonexistent-world-id/actions")
    assert response.status_code == 404



def test_create_tool_without_world_id(client):
    """Test that tools can still be created without world_id (backward compatible)."""
    mock_tool_code = '''
@tool
def generic_tool() -> str:
    """A generic tool without world context."""
    return "Generic action"
'''

    with patch('src.tool_generator.ToolGenerator.generate_tool') as mock_generate:
        mock_generate.return_value = {
            "tool_name": "generic_tool",
            "code": mock_tool_code,
            "explanation": "A generic tool",
            "available_actions": []
        }

        tool_request = {
            "agent_id": "test-agent-456",
            "description": "Create a generic tool"
            # No world_id provided
        }

        response = client.post("/api/tools/create", json=tool_request)
        assert response.status_code == 200
        tool = response.json()
        assert tool["tool_name"] == "generic_tool"



def test_different_game_types_have_different_actions(client):
    """Test that different game types return different sets of actions."""

    # Create a grid_navigation world
    grid_world = {
        "name": "Grid World",
        "game_type": "grid_navigation",
        "description": "Grid-based navigation"
    }
    response = client.post("/api/worlds/create", json=grid_world)
    assert response.status_code == 200
    grid_world_id = response.json()["id"]

    # Create a resource_collection world
    resource_world = {
        "name": "Resource World",
        "game_type": "resource_collection",
        "description": "Resource gathering and management"
    }
    response = client.post("/api/worlds/create", json=resource_world)
    assert response.status_code == 200
    resource_world_id = response.json()["id"]

    # Get actions for grid_navigation world
    response = client.get(f"/api/worlds/{grid_world_id}/actions")
    assert response.status_code == 200
    grid_actions = response.json()
    grid_action_names = {action["name"] for action in grid_actions}

    # Get actions for resource_collection world
    response = client.get(f"/api/worlds/{resource_world_id}/actions")
    assert response.status_code == 200
    resource_actions = response.json()
    resource_action_names = {action["name"] for action in resource_actions}

    # Verify grid_navigation has movement actions
    assert "move_forward" in grid_action_names
    assert "turn_left" in grid_action_names

    # Verify resource_collection has resource actions
    assert "collect_resource" in resource_action_names
    assert "drop_resource" in resource_action_names

    # Verify they have different action sets
    assert grid_action_names != resource_action_names
