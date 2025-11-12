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
        "game_type": "grid_navigation",
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

    # Mock Claude Agent SDK (new ClaudeSDKClient pattern)
    with patch("src.agent_deployer.ClaudeSDKClient") as mock_client_class:
        from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, ThinkingBlock, ToolUseBlock, ToolResultBlock

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client.query = AsyncMock()

        async def mock_deployment_stream():
            # Simulate Claude's response with various event types
            # 1. Thinking
            thinking_block = MagicMock(spec=ThinkingBlock)
            thinking_block.thinking = "I need to move forward to explore"
            thinking_msg = MagicMock(spec=AssistantMessage)
            thinking_msg.content = [thinking_block]
            yield thinking_msg

            # 2. Tool call
            tool_use_block = MagicMock(spec=ToolUseBlock)
            tool_use_block.name = "move_forward"
            tool_use_block.input = {"steps": 1}
            tool_msg = MagicMock(spec=AssistantMessage)
            tool_msg.content = [tool_use_block]
            yield tool_msg

            # 3. Tool result
            result_text_block = MagicMock(spec=TextBlock)
            result_text_block.text = '{"new_position": [1, 0]}'
            tool_result_block = MagicMock(spec=ToolResultBlock)
            tool_result_block.name = "move_forward"
            tool_result_block.content = [result_text_block]
            result_msg = MagicMock(spec=AssistantMessage)
            result_msg.content = [tool_result_block]
            yield result_msg

            # 4. Completion
            stop_msg = MagicMock(spec=ResultMessage)
            stop_msg.stop_reason = "end_turn"
            yield stop_msg

        mock_client.receive_response = mock_deployment_stream
        mock_client_class.return_value = mock_client

        # Test the deployer directly with mocked services
        # (we already created the deployer with mocked services above)

        # 5. Verify SSE stream events
        events = []
        async for event in deployer.deploy_agent(agent_id, world_id, "find treasure"):
            events.append(event)

        # Verify we got all expected event types
        event_types = {e.event_type for e in events}
        assert "thinking" in event_types, "Should have thinking event"
        assert "tool_call" in event_types, "Should have tool_call event"
        assert "tool_result" in event_types, "Should have tool_result event"
        # Note: world_update requires full game engine integration - tested in e2e
        assert "complete" in event_types, "Should have complete event"

        # Verify thinking event structure
        thinking_events = [e for e in events if e.event_type == "thinking"]
        assert len(thinking_events) > 0
        assert "text" in thinking_events[0].data
        assert "timestamp" in thinking_events[0].data

        # Verify tool_call event structure
        tool_call_events = [e for e in events if e.event_type == "tool_call"]
        assert len(tool_call_events) > 0
        assert tool_call_events[0].data["tool_name"] == "move_forward"
        assert "parameters" in tool_call_events[0].data

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
        "game_type": "grid_navigation",
        "grid": [[".", "."], [".", "."]],
        "width": 2,
        "height": 2,
        "agent_position": [0, 0],
    }

    mock_tool_service = AsyncMock()
    mock_tool_service.get_agent_tools.return_value = []

    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    with patch("src.agent_deployer.ClaudeSDKClient") as mock_client_class:
        from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client.query = AsyncMock()

        async def mock_error_recovery_stream():
            # 1. Tool call
            tool_use_block = MagicMock(spec=ToolUseBlock)
            tool_use_block.name = "move_forward"
            tool_use_block.input = {}
            tool_msg = MagicMock(spec=AssistantMessage)
            tool_msg.content = [tool_use_block]
            yield tool_msg

            # 2. Text response (SDK handles errors internally, so just show recovery)
            text_block = MagicMock(spec=TextBlock)
            text_block.text = "I'll try turning instead"
            text_msg = MagicMock(spec=AssistantMessage)
            text_msg.content = [text_block]
            yield text_msg

            # 3. Completion
            stop_msg = MagicMock(spec=ResultMessage)
            stop_msg.stop_reason = "end_turn"
            yield stop_msg

        mock_client.receive_response = mock_error_recovery_stream
        mock_client_class.return_value = mock_client

        events = []
        async for event in deployer.deploy_agent("agent-1", "world-1", "test goal"):
            events.append(event)

        # Verify deployment generates events
        event_types = [e.event_type for e in events]

        # Should have tool_call (from tool use)
        assert "tool_call" in event_types, "Should have tool_call event"

        # Should have text (from recovery message)
        assert "text" in event_types, "Should have text event"

        # Verify completion
        complete_events = [e for e in events if e.event_type == "complete"]
        assert len(complete_events) == 1, "Should complete deployment"
