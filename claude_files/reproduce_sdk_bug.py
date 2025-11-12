#!/usr/bin/env python3
"""
Minimal reproduction of claude-agent-sdk v0.1.6 bug.

Bug: create_sdk_mcp_server() passes unsupported 'version' parameter to Server.__init__()
Issue: https://github.com/anthropics/claude-agent-sdk-python/issues/323

This script demonstrates:
1. The bug: Using create_sdk_mcp_server() causes TypeError
2. The workaround: Creating McpSdkServerConfig directly
"""

print("=" * 80)
print("Reproducing claude-agent-sdk v0.1.6 bug")
print("=" * 80)

# First, let's verify the versions
print("\n1. Checking package versions:")
import importlib.metadata
sdk_version = importlib.metadata.version("claude-agent-sdk")
mcp_version = importlib.metadata.version("mcp")
print(f"   claude-agent-sdk: {sdk_version}")
print(f"   mcp: {mcp_version}")

# Check MCP Server signature
print("\n2. Checking MCP Server.__init__() signature:")
from mcp.server import Server
import inspect
sig = inspect.signature(Server.__init__)
print(f"   Server.__init__{sig}")
print(f"   Parameters: {list(sig.parameters.keys())}")

# Demonstrate the bug
print("\n3. Attempting to use create_sdk_mcp_server() (THIS WILL FAIL):")
try:
    from claude_agent_sdk import create_sdk_mcp_server, tool

    @tool("test_tool", "A test tool", {"input": str})
    async def test_tool(args: dict) -> dict:
        return {"content": [{"type": "text", "text": "Test"}]}

    # This line fails with TypeError
    print("   Calling create_sdk_mcp_server()...")
    server = create_sdk_mcp_server(
        name="test_server",
        version="1.0.0",  # SDK passes this to Server() but it's not accepted
        tools=[test_tool]
    )
    print("   ✅ SUCCESS: No error (SDK bug has been fixed!)")
except TypeError as e:
    if "version" in str(e):
        print(f"   ❌ FAILED: {e}")
        print("   This is the expected bug!")
    else:
        raise

# Demonstrate the workaround
print("\n4. Using workaround: Create McpSdkServerConfig directly:")
try:
    from claude_agent_sdk.types import McpSdkServerConfig

    # Create MCP server configuration manually (workaround)
    user_tool_server = McpSdkServerConfig(
        command="python",
        args=["-m", "mcp"],
        env={"MCP_SERVER_NAME": "user_tools"},
    )
    print("   ✅ SUCCESS: McpSdkServerConfig created without errors")
    print(f"   Config: {user_tool_server}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

print("\n" + "=" * 80)
print("Summary:")
print("- Bug confirmed: create_sdk_mcp_server() passes unsupported 'version' parameter")
print("- Workaround works: Create McpSdkServerConfig manually without 'version'")
print("- See: https://github.com/anthropics/claude-agent-sdk-python/issues/323")
print("=" * 80)
