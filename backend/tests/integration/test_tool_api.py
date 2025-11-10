"""Integration tests for tool API endpoints."""
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.tool_generator import ToolCode


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    # TestClient doesn't run lifespan, so we need to initialize services manually
    from src.tool_service import ToolService

    with TestClient(app) as test_client:
        # Initialize services
        tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:")

        # Manually initialize the DB (async operation)
        import asyncio

        asyncio.run(tool_service.init_db())

        # Add to app state
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
            json={"agent_id": "test-agent-123", "description": "move forward 3 steps"},
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
            json={"agent_id": "agent-retrieve-123", "description": "test tool"},
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
            json={"agent_id": "agent-delete-test", "description": "tool to delete"},
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


def test_create_tool_error_handling(client):
    """Test POST /api/tools/create error handling."""
    # Test with invalid request (missing description)
    response = client.post("/api/tools/create", json={"agent_id": "test-agent"})

    # Should return validation error
    assert response.status_code == 422  # Unprocessable Entity


def test_deploy_agent_endpoint_sse_streaming(client):
    """Test POST /api/agents/deploy - SSE streaming functionality."""
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
