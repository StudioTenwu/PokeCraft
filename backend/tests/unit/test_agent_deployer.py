"""Unit tests for AgentDeployer class."""
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

import pytest

from src.agent_deployer import AgentDeployer, DeploymentEvent


class MockWorldService:
    """Mock world service for testing."""

    async def get_world(self, world_id: str) -> dict[str, Any] | None:
        """Return mock world data."""
        if world_id == "world-1":
            return {
                "id": "world-1",
                "agent_id": "agent-1",
                "name": "Test World",
                "description": "A test world",
                "grid": [
                    [".", ".", ".", ".", "."],
                    [".", "#", "#", "#", "."],
                    [".", ".", "T", ".", "."],
                    [".", "#", "#", "#", "."],
                    [".", ".", ".", ".", "."],
                ],
                "width": 5,
                "height": 5,
                "agent_position": [0, 0],
            }
        return None


class MockToolService:
    """Mock tool service for testing."""

    async def get_agent_tools(self, agent_id: str) -> list[dict[str, Any]]:
        """Return mock tools."""
        if agent_id == "agent-1":
            return [
                {
                    "id": "tool-1",
                    "name": "move_forward",
                    "description": "Move forward one step",
                    "code": "async def move_forward(): pass",
                }
            ]
        return []


@pytest.mark.asyncio
async def test_deploy_agent_yields_reasoning_event():
    """Test that deployment yields reasoning events."""
    # Arrange
    mock_world_service = MockWorldService()
    mock_tool_service = MockToolService()
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock the Claude Agent SDK
    with patch("src.agent_deployer.query") as mock_query:
        # Simulate Claude streaming a thinking message
        async def mock_stream():
            mock_msg = MagicMock()
            mock_msg.result = "I need to move forward to explore the area"
            yield mock_msg

        mock_query.return_value = mock_stream()

        # Act
        events = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "find treasure"):
            events.append(event)
            if any(e.event_type == "reasoning" for e in events):
                break  # Found reasoning event, we can stop

        # Assert
        assert any(e.event_type == "reasoning" for e in events), "Should have reasoning event"
        reasoning_events = [e for e in events if e.event_type == "reasoning"]
        assert len(reasoning_events) > 0
        assert "text" in reasoning_events[0].data
        assert "timestamp" in reasoning_events[0].data


@pytest.mark.asyncio
async def test_deploy_agent_yields_tool_call_events():
    """Test that tool calls are streamed with proper structure."""
    # Arrange
    mock_world_service = MockWorldService()
    mock_tool_service = MockToolService()
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock the Claude Agent SDK with tool use
    with patch("src.agent_deployer.query") as mock_query:

        async def mock_stream():
            # Simulate tool use message
            mock_msg = MagicMock()
            mock_msg.tool_use = MagicMock()
            mock_msg.tool_use.tool_name = "move_forward"
            mock_msg.tool_use.parameters = {"steps": 1}
            yield mock_msg

        mock_query.return_value = mock_stream()

        # Act
        events = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "move forward"):
            events.append(event)
            if any(e.event_type == "tool_call" for e in events):
                break

        # Assert
        tool_call_events = [e for e in events if e.event_type == "tool_call"]
        assert len(tool_call_events) > 0, "Should have tool_call events"

        tool_call = tool_call_events[0]
        assert "tool_name" in tool_call.data
        assert "parameters" in tool_call.data
        assert "timestamp" in tool_call.data
        assert tool_call.data["tool_name"] == "move_forward"


@pytest.mark.asyncio
async def test_deploy_agent_handles_tool_errors_with_retry():
    """Test that tool errors trigger error events and allow retry."""
    # Arrange
    mock_world_service = MockWorldService()
    mock_tool_service = MockToolService()
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock tool execution that fails
    with patch("src.agent_deployer.query") as mock_query:

        async def mock_stream():
            # First: tool call
            msg1 = MagicMock()
            msg1.tool_use = MagicMock()
            msg1.tool_use.tool_name = "move_forward"
            msg1.tool_use.parameters = {}
            yield msg1

            # Second: simulated error
            msg2 = MagicMock()
            msg2.error = "Tool execution failed: wall detected"
            yield msg2

            # Third: retry with different approach
            msg3 = MagicMock()
            msg3.result = "I'll try a different direction"
            yield msg3

        mock_query.return_value = mock_stream()

        # Act
        events = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "move forward"):
            events.append(event)
            if any(e.event_type == "error" for e in events):
                # Check we also get reasoning after error (retry)
                if len([e for e in events if e.event_type == "reasoning"]) > 0:
                    break

        # Assert
        error_events = [e for e in events if e.event_type == "error"]
        assert len(error_events) > 0, "Should have error event"

        error_event = error_events[0]
        assert "error_type" in error_event.data
        assert "message" in error_event.data
        assert "recoverable" in error_event.data
        assert error_event.data["recoverable"] is True

        # Verify deployment continued after error (didn't stop)
        assert len(events) > 1, "Should have multiple events (not just error)"


@pytest.mark.asyncio
async def test_world_update_events_use_deltas():
    """Test that world updates only contain position deltas, not full state."""
    # Arrange
    mock_world_service = MockWorldService()
    mock_tool_service = MockToolService()
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock a tool that changes agent position
    with patch("src.agent_deployer.query") as mock_query:

        async def mock_stream():
            # Tool result that moves agent
            msg = MagicMock()
            msg.tool_result = MagicMock()
            msg.tool_result.result = {"new_position": [1, 0]}
            yield msg

        mock_query.return_value = mock_stream()

        # Act
        events = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "explore"):
            events.append(event)
            if any(e.event_type == "world_update" for e in events):
                break

        # Assert
        world_update_events = [e for e in events if e.event_type == "world_update"]
        assert len(world_update_events) > 0, "Should have world_update event"

        update = world_update_events[0]
        # Verify delta structure (from instructions)
        assert "agent_moved_from" in update.data
        assert "agent_moved_to" in update.data

        # Verify NO full grid is sent
        assert "grid" not in update.data, "Should not send full grid (deltas only!)"

        # Verify delta structure
        assert isinstance(update.data["agent_moved_from"], list)
        assert isinstance(update.data["agent_moved_to"], list)


@pytest.mark.asyncio
async def test_deploy_agent_yields_complete_event():
    """Test that deployment ends with complete event."""
    # Arrange
    mock_world_service = MockWorldService()
    mock_tool_service = MockToolService()
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock successful completion
    with patch("src.agent_deployer.query") as mock_query:

        async def mock_stream():
            # Final result
            msg = MagicMock()
            msg.result = "Task completed successfully!"
            msg.stop_reason = "end_turn"
            yield msg

        mock_query.return_value = mock_stream()

        # Act
        events = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "simple task"):
            events.append(event)

        # Assert
        # Last event should be complete
        assert len(events) > 0, "Should have at least one event"
        last_event = events[-1]
        assert last_event.event_type == "complete", "Last event should be complete"

        # Verify complete event structure
        assert "status" in last_event.data
        assert "timestamp" in last_event.data
        assert last_event.data["status"] in ["success", "partial", "failed"]


@pytest.mark.asyncio
async def test_deploy_agent_initializes_with_services():
    """Test AgentDeployer initializes correctly with services."""
    # Arrange & Act
    mock_world_service = MockWorldService()
    mock_tool_service = MockToolService()
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Assert
    assert deployer.tool_service is mock_tool_service
    assert deployer.world_service is mock_world_service


@pytest.mark.asyncio
async def test_deploy_agent_loads_world_state():
    """Test that deployer loads world state before execution."""
    # Arrange
    mock_world_service = MockWorldService()
    mock_tool_service = MockToolService()
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    with patch("src.agent_deployer.query") as mock_query:

        async def mock_stream():
            msg = MagicMock()
            msg.result = "Loaded world"
            yield msg

        mock_query.return_value = mock_stream()

        # Act - should not raise even if world doesn't exist
        events_list = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "test goal"):
            events_list.append(event)
            if len(events_list) >= 2:  # Get a few events
                break

        # Assert - no errors should occur
        assert len(events_list) > 0
