"""Integration tests for agent deployment flow."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app
from src.agent_deployer import DeploymentEvent


@pytest.fixture
def sync_client():
    """Create a sync test client."""
    # Use synchronous TestClient since async is more complex for this test
    # The important part is testing the deployer logic, not the HTTP layer
    from src.agent_service import AgentService
    from src.world_service import WorldService
    from src.tool_service import ToolService
    import asyncio
    import tempfile
    import os

    # Create a unique temporary database for this test
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        # Initialize services with unique DB
        agent_service = AgentService(db_path=db_path)
        world_service = WorldService(db_path=db_path)
        tool_service = ToolService(db_path=f"sqlite+aiosqlite:///{db_path}")

        # Initialize tool service DB
        asyncio.run(tool_service.init_db())

        # Add to app state
        app.state.agent_service = agent_service
        app.state.world_service = world_service
        app.state.tool_service = tool_service

        with TestClient(app) as client:
            yield client
    finally:
        # Cleanup temp database
        try:
            os.unlink(db_path)
        except OSError:
            pass


@pytest.mark.asyncio
async def test_deploy_agent_full_flow(sync_client):
    """Test complete agent deployment through deployer (simplified).

    This test verifies:
    1. Deployer correctly loads world and tools from services
    2. Deploy agent streams all event types correctly
    3. Verify SSE stream events structure matches specifications
    """
    # Use simple mock data instead of creating via API
    # This focuses the test on the deployer logic, not the API endpoints
    agent_id = "test-agent-123"
    world_id = "test-world-456"

    # Mock the services directly
    mock_world_service = AsyncMock()
    mock_world_service.get_world.return_value = {
        "id": world_id,
        "agent_id": agent_id,
        "name": "Test World",
        "grid": [
            [".", ".", ".", ".", "."],
            [".", "#", "#", "#", "."],
            [".", ".", "T", ".", "."],
            [".", "#", "#", "#", "."],
            [".", ".", ".", ".", "."]
        ],
        "width": 5,
        "height": 5,
        "agent_position": [0, 0],
    }

    mock_tool_service = AsyncMock()
    mock_tool_service.get_agent_tools.return_value = [
        {
            "id": "tool-1",
            "name": "move_forward",
            "description": "Move forward",
            "code": "async def move_forward(): pass",
        }
    ]

    # Create deployer with mocked services
    from src.agent_deployer import AgentDeployer
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock Claude Agent SDK streaming
    with patch("src.agent_deployer.query") as mock_query:

        async def mock_deployment_stream():
            # Simulate Claude's response with various event types
            # 1. Reasoning
            msg1 = MagicMock()
            msg1.result = "I need to move forward to explore"
            msg1.tool_use = None
            msg1.tool_result = None
            msg1.error = None
            msg1.stop_reason = None
            yield msg1

            # 2. Tool call
            msg2 = MagicMock()
            msg2.result = None
            msg2.tool_use = MagicMock()
            msg2.tool_use.tool_name = "move_forward"
            msg2.tool_use.parameters = {"steps": 1}
            msg2.tool_result = None
            msg2.error = None
            msg2.stop_reason = None
            yield msg2

            # 3. Tool result with position update
            msg3 = MagicMock()
            msg3.result = None
            msg3.tool_use = None
            msg3.tool_result = MagicMock()
            msg3.tool_result.result = {"new_position": [1, 0]}
            msg3.error = None
            msg3.stop_reason = None
            yield msg3

            # 4. Completion
            msg4 = MagicMock()
            msg4.result = "Task complete"
            msg4.tool_use = None
            msg4.tool_result = None
            msg4.error = None
            msg4.stop_reason = "end_turn"
            yield msg4

        mock_query.return_value = mock_deployment_stream()

        # Test the deployer directly with mocked services
        # (we already created the deployer with mocked services above)

        # 5. Verify SSE stream events
        events = []
        async for event in deployer.deploy_agent(agent_id, world_id, "find treasure"):
            events.append(event)

        # Verify we got all expected event types
        event_types = {e.event_type for e in events}
        assert "reasoning" in event_types, "Should have reasoning event"
        assert "tool_call" in event_types, "Should have tool_call event"
        assert "tool_result" in event_types, "Should have tool_result event"
        assert "world_update" in event_types, "Should have world_update event"
        assert "complete" in event_types, "Should have complete event"

        # Verify reasoning event structure
        reasoning_events = [e for e in events if e.event_type == "reasoning"]
        assert len(reasoning_events) > 0
        assert "text" in reasoning_events[0].data
        assert "timestamp" in reasoning_events[0].data

        # Verify tool_call event structure
        tool_call_events = [e for e in events if e.event_type == "tool_call"]
        assert len(tool_call_events) > 0
        assert tool_call_events[0].data["tool_name"] == "move_forward"
        assert "parameters" in tool_call_events[0].data

        # Verify world_update event uses deltas only
        world_update_events = [e for e in events if e.event_type == "world_update"]
        assert len(world_update_events) > 0
        assert "agent_moved_from" in world_update_events[0].data
        assert "agent_moved_to" in world_update_events[0].data
        assert "grid" not in world_update_events[0].data, "Should not send full grid!"

        # Verify complete event
        complete_events = [e for e in events if e.event_type == "complete"]
        assert len(complete_events) == 1
        assert complete_events[0].data["status"] in ["success", "partial", "failed"]
        assert "total_steps" in complete_events[0].data
        assert "total_tools_used" in complete_events[0].data

        # 6. Verify world state could be updated (we don't actually persist in this test)
        # In a real scenario, the world service would be called to update the grid
        # For this integration test, we've verified the events are correct


@pytest.mark.asyncio
async def test_deploy_agent_handles_missing_world():
    """Test deployment fails gracefully when world doesn't exist."""
    from src.agent_deployer import AgentDeployer
    from src.tool_service import ToolService
    from src.world_service import WorldService

    tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:")
    world_service = WorldService()

    deployer = AgentDeployer(tool_service, world_service)

    events = []
    async for event in deployer.deploy_agent("agent-1", "nonexistent-world", "test"):
        events.append(event)

    # Should get error event
    assert len(events) == 1
    assert events[0].event_type == "error"
    assert "world_not_found" in events[0].data["error_type"]
    assert events[0].data["recoverable"] is False


@pytest.mark.asyncio
async def test_deploy_agent_error_recovery():
    """Test that deployment continues after recoverable errors."""
    from src.agent_deployer import AgentDeployer
    from src.tool_service import ToolService
    from src.world_service import WorldService

    # Mock services
    mock_world_service = AsyncMock()
    mock_world_service.get_world.return_value = {
        "id": "world-1",
        "agent_id": "agent-1",
        "name": "Test World",
        "grid": [[".", "."], [".", "."]],
        "width": 2,
        "height": 2,
        "agent_position": [0, 0],
    }

    mock_tool_service = AsyncMock()
    mock_tool_service.get_agent_tools.return_value = []

    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    with patch("src.agent_deployer.query") as mock_query:

        async def mock_error_recovery_stream():
            # 1. Tool call
            msg1 = MagicMock()
            msg1.result = None
            msg1.tool_use = MagicMock()
            msg1.tool_use.tool_name = "move_forward"
            msg1.tool_use.parameters = {}
            msg1.tool_result = None
            msg1.error = None
            msg1.stop_reason = None
            yield msg1

            # 2. Error
            msg2 = MagicMock()
            msg2.result = None
            msg2.tool_use = None
            msg2.tool_result = None
            msg2.error = "Wall detected"
            msg2.stop_reason = None
            yield msg2

            # 3. Retry with different approach
            msg3 = MagicMock()
            msg3.result = "I'll try turning instead"
            msg3.tool_use = None
            msg3.tool_result = None
            msg3.error = None
            msg3.stop_reason = None
            yield msg3

            # 4. Completion
            msg4 = MagicMock()
            msg4.result = None
            msg4.tool_use = None
            msg4.tool_result = None
            msg4.error = None
            msg4.stop_reason = "end_turn"
            yield msg4

        mock_query.return_value = mock_error_recovery_stream()

        events = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "test goal"):
            events.append(event)

        # Verify error was encountered
        error_events = [e for e in events if e.event_type == "error"]
        assert len(error_events) > 0
        assert error_events[0].data["recoverable"] is True

        # Verify deployment continued after error
        reasoning_after_error = [
            e
            for e in events
            if e.event_type == "reasoning" and "try turning" in e.data.get("text", "")
        ]
        assert len(reasoning_after_error) > 0, "Should continue after recoverable error"

        # Verify completion
        complete_events = [e for e in events if e.event_type == "complete"]
        assert len(complete_events) == 1
