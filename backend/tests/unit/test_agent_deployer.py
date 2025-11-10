"""Unit tests for agent deployer service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agent_deployer import AgentDeployer, DeploymentEvent


@pytest.fixture
def mock_tool_service():
    """Create a mock tool service."""
    service = MagicMock()
    service.get_agent_tools = AsyncMock(return_value=[
        {
            "id": "tool-123",
            "agent_id": "agent-123",
            "name": "move_forward",
            "code": "@tool('move_forward', 'Move forward', {'steps': 'int'})\nasync def move_forward(args): pass",
            "description": "Move forward",
            "category": "Movement",
        }
    ])
    return service


@pytest.fixture
def mock_world_service():
    """Create a mock world service."""
    service = MagicMock()
    service.get_world = AsyncMock(return_value={
        "id": "world-123",
        "agent_id": "agent-123",
        "grid_size": 10,
        "description": "A simple 2D world",
    })
    return service


@pytest.mark.asyncio
async def test_deployer_initialization(mock_tool_service, mock_world_service):
    """Test AgentDeployer initialization."""
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    assert deployer.tool_service is mock_tool_service
    assert deployer.world_service is mock_world_service


@pytest.mark.asyncio
async def test_deploy_agent_yields_progress_events(mock_tool_service, mock_world_service):
    """Test that deploy_agent yields progress events."""
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock the Claude Agent SDK query function
    mock_messages = [
        MagicMock(result="Agent is thinking..."),
        MagicMock(result="Using tool: move_forward"),
        MagicMock(result="Goal accomplished!"),
    ]

    with patch("src.agent_deployer.query") as mock_query:
        mock_query.return_value = async_generator(mock_messages)

        events = []
        async for event in deployer.deploy_agent("agent-123", "world-123", "Find treasure"):
            events.append(event)

        # Should have at least: starting, loading_tools, reasoning, complete
        assert len(events) >= 4

        # Check event structure
        assert all(isinstance(e, DeploymentEvent) for e in events)
        assert events[0].event_type == "progress"
        assert events[0].data["status"] == "starting"


@pytest.mark.asyncio
async def test_deploy_agent_loads_custom_tools(mock_tool_service, mock_world_service):
    """Test that deploy_agent loads custom tools for the agent."""
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    with patch("src.agent_deployer.query") as mock_query:
        mock_query.return_value = async_generator([MagicMock(result="Done")])

        with patch("src.agent_deployer.get_available_tools") as mock_get_tools:
            mock_get_tools.return_value = [MagicMock(__name__="move_forward")]

            events = []
            async for event in deployer.deploy_agent("agent-123", "world-123", "Test goal"):
                events.append(event)

            # Verify tools were loaded
            mock_tool_service.get_agent_tools.assert_called_once_with("agent-123")
            mock_get_tools.assert_called_once()


@pytest.mark.asyncio
async def test_deploy_agent_with_tool_execution(mock_tool_service, mock_world_service):
    """Test agent deployment with tool execution streaming."""
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock Claude response with tool use
    mock_tool_use = MagicMock()
    mock_tool_use.tool_name = "move_forward"
    mock_tool_use.tool_input = {"steps": 3}

    mock_message = MagicMock()
    mock_message.content = [mock_tool_use]
    mock_message.result = None

    with patch("src.agent_deployer.query") as mock_query:
        mock_query.return_value = async_generator([mock_message])

        with patch("src.agent_deployer.get_available_tools"):
            events = []
            async for event in deployer.deploy_agent("agent-123", "world-123", "Move forward"):
                events.append(event)

            # Should have tool_call event
            tool_events = [e for e in events if e.event_type == "tool_call"]
            assert len(tool_events) > 0
            assert tool_events[0].data["tool"] == "move_forward"


@pytest.mark.asyncio
async def test_deploy_agent_error_handling(mock_tool_service, mock_world_service):
    """Test error handling during agent deployment."""
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    # Mock query to raise exception
    with patch("src.agent_deployer.query") as mock_query:
        mock_query.side_effect = Exception("LLM error")

        events = []
        async for event in deployer.deploy_agent("agent-123", "world-123", "Test"):
            events.append(event)

        # Should yield error event
        error_events = [e for e in events if e.event_type == "error"]
        assert len(error_events) > 0
        assert "error" in error_events[0].data["message"].lower()


@pytest.mark.asyncio
async def test_deploy_agent_world_not_found(mock_tool_service, mock_world_service):
    """Test deployment fails gracefully if world not found."""
    mock_world_service.get_world = AsyncMock(return_value=None)
    deployer = AgentDeployer(mock_tool_service, mock_world_service)

    events = []
    async for event in deployer.deploy_agent("agent-123", "invalid-world", "Test"):
        events.append(event)

    # Should have error event
    error_events = [e for e in events if e.event_type == "error"]
    assert len(error_events) > 0


def async_generator(items):
    """Helper to create async generator from list."""
    async def gen():
        for item in items:
            yield item
    return gen()
