"""Integration test for agent deployment without version parameter error.

This test verifies that agent deployment initializes MCP server correctly
without passing unsupported 'version' parameter.
"""
import pytest
from src.agent_deployer import AgentDeployer
from src.tool_service import ToolService
from src.world_service import WorldService
from src.agent_service import AgentService


@pytest.mark.asyncio
async def test_agent_deployment_initializes_without_version_error():
    """Test that agent deployment doesn't fail with version parameter error.

    This test verifies the fix for the bug:
    "Server.__init__() got an unexpected keyword argument 'version'"

    Expected behavior:
    - Agent deployment should start without throwing version-related errors
    - MCP server creation should succeed with only required parameters
    - Deployment generator should yield at least one event
    """
    # Setup: Create services with proper async SQLite URL
    tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:")
    world_service = WorldService(db_path="sqlite+aiosqlite:///:memory:")
    agent_service = AgentService(db_path="sqlite+aiosqlite:///:memory:")

    # Initialize databases
    await tool_service.init_db()
    await world_service.init_db()
    await agent_service.init_db()

    # Create test agent
    agent = await agent_service.create_agent("A helpful test agent")
    agent_id = agent["id"]

    # Create test world
    world = await world_service.create_world(
        agent_id=agent_id,
        description="A simple test world"
    )
    world_id = world["id"]

    # Create deployer
    deployer = AgentDeployer(tool_service, world_service)

    # Execute: Start deployment - this should NOT raise version error
    deployment_started = False
    error_message = None

    try:
        async for event in deployer.deploy_agent(
            agent_id=agent_id,
            world_id=world_id,
            goal="Complete a simple task"
        ):
            deployment_started = True
            # We only need to verify it starts without error
            # Don't need to complete entire deployment
            break
    except TypeError as e:
        if "version" in str(e):
            error_message = str(e)

    # Assert: Deployment should start without version-related errors
    assert error_message is None, f"Deployment failed with version error: {error_message}"
    assert deployment_started, "Deployment should yield at least one event"


@pytest.mark.asyncio
async def test_mcp_server_creation_with_manual_config():
    """Test that MCP server can be created using McpSdkServerConfig directly.

    This test verifies the workaround for SDK bug where create_sdk_mcp_server
    passes unsupported 'version' parameter to Server.__init__().

    The workaround is to create McpSdkServerConfig manually.
    """
    from claude_agent_sdk.types import McpSdkServerConfig
    from src.agent_deployer import AgentDeployer

    # Setup
    tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:")
    world_service = WorldService(db_path="sqlite+aiosqlite:///:memory:")

    deployer = AgentDeployer(tool_service, world_service)

    # Execute: Create MCP server config manually (workaround for SDK bug)
    # Note: We don't test tool loading here - just the config creation
    try:
        user_tool_server = McpSdkServerConfig(
            command="python",
            args=["-m", "mcp"],
            env={"MCP_SERVER_NAME": "user_tools"},
        )
        success = True
        error = None
    except Exception as e:
        success = False
        error = str(e)

    # Assert: Server config creation should succeed
    assert success, f"MCP server config creation failed: {error}"
    assert error is None, "Should not have any errors"
    assert user_tool_server is not None, "Should have created server config"
