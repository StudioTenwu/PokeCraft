"""Test MCP runtime server integration."""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.asyncio
async def test_mcp_server_loads_tools():
    """Test that MCP runtime server loads tools successfully."""
    from mcp_server_runtime import server, tool_handlers
    
    # Verify server is created
    assert server is not None
    assert server.name == "user_tools"
    
    # Verify tools are loaded
    assert len(tool_handlers) > 0
    
    # Verify expected tools exist
    assert "move_direction" in tool_handlers
    assert "observe_world" in tool_handlers
    
    print(f"✓ MCP server loaded {len(tool_handlers)} tools successfully")


@pytest.mark.asyncio
async def test_mcp_server_can_execute_tool():
    """Test that MCP server can execute a tool."""
    from mcp_server_runtime import tool_handlers
    
    # Test observe_world tool
    handler = tool_handlers["observe_world"]
    
    # Mock world state
    from state_manager import state_manager
    test_world = {
        "agent_position": [5, 5],
        "width": 10,
        "height": 10,
        "grid": [["." for _ in range(10)] for _ in range(10)]
    }
    state_manager.set_world("test-world", test_world)
    
    # Execute tool
    result = await handler({"world_id": "test-world"})
    
    # Verify result structure
    assert "content" in result
    assert len(result["content"]) > 0
    assert result["content"][0]["type"] == "text"
    assert "[5, 5]" in result["content"][0]["text"]
    
    print("✓ MCP tool execution successful")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_server_loads_tools())
    asyncio.run(test_mcp_server_can_execute_tool())
    print("\n✅ All MCP runtime tests passed!")
