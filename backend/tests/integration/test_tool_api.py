"""Integration tests for tool API endpoints."""
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.tool_generator import ToolCode


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    # TestClient doesn't run lifespan, so we need to initialize services manually
    from src.tool_service import ToolService
    from src.world_service import WorldService

    with TestClient(app) as test_client:
        # Initialize services
        world_service = WorldService(db_path=":memory:")
        tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:", world_service=world_service)

        # Manually initialize the DB (async operation)
        import asyncio

        asyncio.run(world_service.init_db())
        asyncio.run(tool_service.init_db())

        # Mock world_service.get_world to return a test world
        async def mock_get_world(world_id):
            return {
                "id": world_id,
                "name": "Test World",
                "game_type": "grid_navigation",
                "agent_position": [0, 0],
                "grid": [["." for _ in range(10)] for _ in range(10)],
                "width": 10,
                "height": 10,
            }

        world_service.get_world = mock_get_world

        # Add to app state
        app.state.world_service = world_service
        app.state.tool_service = tool_service

        yield test_client


@pytest.fixture
def temp_tools_file():
    """Create a temporary tools.py file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('"""Auto-generated tool storage."""\n')
        f.write("from typing import Any\n\n")
        tools_file = Path(f.name)
    yield str(tools_file)
    # Cleanup
    tools_file.unlink(missing_ok=True)


def test_create_tool_endpoint(client, temp_tools_file):
    """Test POST /api/tools/create - full request/response cycle."""
    # Mock the tool_generator on the service instance (already initialized)
    mock_tool_code = ToolCode(
        tool_name="test_move_forward",
        code='@tool("test_move_forward", "Move forward", {"steps": "int"})\n'
        + "async def test_move_forward(args: dict[str, Any]) -> dict[str, Any]:\n"
        + '    return {"content": [{"type": "text", "text": "Moved forward"}]}',
        explanation="This tool moves the agent forward",
    )

    # Patch the generate_tool method on the service's tool_generator instance
    app.state.tool_service.tool_generator.generate_tool = AsyncMock(return_value=mock_tool_code)

    # Mock file appending
    with patch("src.tool_service.append_tool_to_file") as mock_append:
        response = client.post(
            "/api/tools/create",
            json={
                "agent_id": "test-agent-123",
                "world_id": "test-world-123",
                "description": "move forward 3 steps"
            },
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["tool_name"] == "test_move_forward"
        assert "code" in data
        assert "@tool" in data["code"]
        assert "explanation" in data
        assert "tool_id" in data

        # Verify tool was appended to file
        mock_append.assert_called_once()


def test_get_agent_tools_endpoint(client):
    """Test GET /api/tools/agent/{agent_id} - verify DB retrieval."""
    # First create a tool so we have something to retrieve
    mock_tool_code = ToolCode(
        tool_name="retrieval_test_tool",
        code="@tool(...)\nasync def retrieval_test_tool(args): pass",
        explanation="Tool for testing retrieval",
    )
    app.state.tool_service.tool_generator.generate_tool = AsyncMock(return_value=mock_tool_code)

    with patch("src.tool_service.append_tool_to_file"):
        # Create the tool
        create_response = client.post(
            "/api/tools/create",
            json={
                "agent_id": "agent-retrieve-123",
                "world_id": "test-world-retrieve",
                "description": "test tool"
            },
        )
        assert create_response.status_code == 200

    # Now retrieve tools for this agent
    response = client.get("/api/tools/agent/agent-retrieve-123")

    # Verify response
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) > 0

    # Verify tool structure
    tool = tools[0]
    assert "id" in tool
    assert tool["agent_id"] == "agent-retrieve-123"
    assert tool["name"] == "retrieval_test_tool"
    assert "code" in tool
    assert "description" in tool
    assert "created_at" in tool


def test_get_agent_tools_empty_result(client):
    """Test GET /api/tools/agent/{agent_id} for agent with no tools."""
    response = client.get("/api/tools/agent/nonexistent-agent")

    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) == 0


def test_delete_tool_endpoint(client):
    """Test DELETE /api/tools/{tool_name} - verify DB deletion."""
    # First create a tool
    mock_tool_code = ToolCode(
        tool_name="delete_me_tool",
        code="@tool(...)\nasync def delete_me_tool(args): pass",
        explanation="Tool to be deleted",
    )
    app.state.tool_service.tool_generator.generate_tool = AsyncMock(return_value=mock_tool_code)

    with patch("src.tool_service.append_tool_to_file"):
        create_response = client.post(
            "/api/tools/create",
            json={
                "agent_id": "agent-delete-test",
                "world_id": "test-world-delete",
                "description": "tool to delete"
            },
        )
        assert create_response.status_code == 200

    # Delete the tool
    delete_response = client.delete("/api/tools/delete_me_tool")

    # Verify deletion succeeded
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert "message" in data
    assert "deleted successfully" in data["message"]

    # Verify tool is gone from database
    get_response = client.get("/api/tools/agent/agent-delete-test")
    tools = get_response.json()
    assert len(tools) == 0


def test_delete_nonexistent_tool_returns_404(client):
    """Test DELETE /api/tools/{tool_name} for nonexistent tool."""
    response = client.delete("/api/tools/this_tool_does_not_exist")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_create_tool_returns_action_id(client, temp_tools_file):
    """Test POST /api/tools/create - verify action_id is returned."""
    # Mock the tool_generator to return a tool with action_id
    mock_tool_code = ToolCode(
        tool_name="move_north_tool",
        code='@tool("move_north_tool", "Move north", {})\n'
        + "async def move_north_tool(args: dict[str, Any]) -> dict[str, Any]:\n"
        + '    return {"action": {"action_id": "move", "parameters": {"direction": "north"}}}',
        explanation="This tool moves the agent north",
        action_id="move"  # This should be parsed from the generated code
    )

    # Patch the generate_tool method to return mock with action_id
    app.state.tool_service.tool_generator.generate_tool = AsyncMock(return_value=mock_tool_code)

    # Mock file appending
    with patch("src.tool_service.append_tool_to_file") as mock_append:
        response = client.post(
            "/api/tools/create",
            json={
                "agent_id": "test-agent-123",
                "world_id": "test-world-123",
                "description": "move north"
            },
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "action_id" in data
        assert data["action_id"] == "move"

def test_create_tool_error_handling(client):
    """Test POST /api/tools/create error handling."""
    # Test with invalid request (missing description)
    response = client.post("/api/tools/create", json={"agent_id": "test-agent"})

    # Should return validation error
    assert response.status_code == 422  # Unprocessable Entity


def test_deploy_agent_endpoint_sse_streaming(client):
    """Test POST /api/agents/deploy - SSE streaming functionality."""
    from src.agent_deployer import DeploymentEvent

    # Mock the AgentDeployer to return test events
    async def mock_deploy_agent(agent_id, world_id, goal):
        # Yield mock deployment events
        yield DeploymentEvent(event_type="progress", data={"status": "starting", "message": "Initializing agent..."})
        yield DeploymentEvent(event_type="progress", data={"status": "loading_tools", "message": "Loading custom tools..."})
        yield DeploymentEvent(event_type="reasoning", data={"message": "Analyzing the world..."})
        tool_call_data = {"tool": "move_forward", "args": {"steps": 3}, "result": "Moved 3 steps"}
        yield DeploymentEvent(event_type="tool_call", data=tool_call_data)
        yield DeploymentEvent(event_type="complete", data={"status": "complete", "message": "Goal accomplished!", "agent_id": agent_id, "world_id": world_id})

    # Patch the AgentDeployer where it's imported in main.py's event_generator (local import)
    with patch("agent_deployer.AgentDeployer") as mock_deployer_class:
        mock_deployer = MagicMock()
        mock_deployer.deploy_agent = mock_deploy_agent
        mock_deployer_class.return_value = mock_deployer

        response = client.post(
            "/api/agents/deploy",
            json={"agent_id": "test-agent", "world_id": "test-world", "goal": "Find treasure"},
        )

        # Verify SSE response
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Parse SSE events from response
        content = response.text
        assert "event: progress" in content
        assert "event: reasoning" in content
        assert "event: tool_call" in content
        assert "event: complete" in content

        # Verify event data contains expected information
        assert "Initializing agent" in content
        assert "Loading custom tools" in content
        assert "test-agent" in content
        assert "test-world" in content


def test_deploy_agent_missing_fields_returns_422(client):
    """Test POST /api/agents/deploy with missing fields."""
    response = client.post(
        "/api/agents/deploy",
        json={"agent_id": "test-agent"},  # Missing world_id and goal
    )

    assert response.status_code == 422
