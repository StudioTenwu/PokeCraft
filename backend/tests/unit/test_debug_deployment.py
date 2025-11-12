"""Test debug deployment endpoint for testing and debugging.

Following TDD - these tests define the desired behavior before implementation.
"""
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture()
async def async_client():
    """Create async HTTP client for testing."""
    from agent_service import AgentService
    from main import app
    from tool_service import ToolService
    from world_service import WorldService

    # Initialize services in app state
    app.state.tool_service = ToolService(world_service=WorldService())
    app.state.world_service = WorldService()
    app.state.agent_service = AgentService()

    # Initialize service databases
    await app.state.agent_service.init_db()
    await app.state.world_service.init_db()
    await app.state.tool_service.init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio()
async def test_debug_deploy_returns_structured_events(async_client: AsyncClient):
    """Test that debug deployment endpoint returns structured event log.

    RED: This test will fail because endpoint doesn't exist yet.
    """
    # Arrange
    agent_id = "test-agent-id"
    world_id = "test-world-id"
    goal = "Find the treasure at position [9, 9]"

    # Act
    response = await async_client.post(
        "/api/debug/deploy",
        json={"agent_id": agent_id, "world_id": world_id, "goal": goal},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should have structured response with events and traces
    assert "events" in data
    assert "thinking_traces" in data
    assert "final_status" in data

    # Events should be a list
    assert isinstance(data["events"], list)

    # Thinking traces should be extractable
    assert isinstance(data["thinking_traces"], list)


@pytest.mark.asyncio()
async def test_debug_deploy_validates_required_fields(async_client: AsyncClient):
    """Test that debug deployment endpoint validates required fields.

    RED: This test will fail because endpoint doesn't exist yet.
    """
    # Act - Missing required fields
    response = await async_client.post("/api/debug/deploy", json={})

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio()
async def test_debug_deploy_handles_nonexistent_world(async_client: AsyncClient):
    """Test that debug deployment handles nonexistent world gracefully.

    RED: This test will fail because endpoint doesn't exist yet.
    """
    # Act
    response = await async_client.post(
        "/api/debug/deploy",
        json={
            "agent_id": "fake-agent",
            "world_id": "nonexistent-world",
            "goal": "Test goal",
        },
    )

    # Assert - Should return error in final_status
    assert response.status_code == 200  # Endpoint exists
    data = response.json()
    assert data["final_status"] == "error"
    assert any("not found" in str(event).lower() for event in data["events"])


@pytest.mark.asyncio()
async def test_debug_deploy_exposes_tool_calls(async_client: AsyncClient):
    """Test that debug deployment exposes tool call details.

    RED: This test will fail because endpoint doesn't exist yet.
    """
    # Arrange
    agent_id = "test-agent"
    world_id = "test-world"
    goal = "Move one step"

    # Act
    response = await async_client.post(
        "/api/debug/deploy",
        json={"agent_id": agent_id, "world_id": world_id, "goal": goal},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should have tool_call events
    tool_events = [e for e in data["events"] if e.get("event_type") == "tool_call"]

    # Each tool call should have tool_name and parameters
    for event in tool_events:
        assert "tool_name" in event["data"]
        assert "parameters" in event["data"]
