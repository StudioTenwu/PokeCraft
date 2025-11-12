"""Test script to verify FastMCP server works via stdio."""
import subprocess
import json
import sys

def test_mcp_server():
    """Test the FastMCP server by sending MCP protocol messages."""

    # Start the server
    proc = subprocess.Popen(
        ["uv", "run", "fastmcp", "run", "game_tools_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()

        # Read response
        response_line = proc.stdout.readline()
        print(f"📥 Initialize response: {response_line}")

        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        proc.stdin.write(json.dumps(tools_request) + "\n")
        proc.stdin.flush()

        # Read response
        response_line = proc.stdout.readline()
        print(f"📥 Tools list response: {response_line}")

        if response_line:
            response = json.loads(response_line)
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"\n✅ Server responded with {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool.get('description', 'No description')}")
                return True

        print("❌ Failed to get tools list")
        return False

    finally:
        proc.terminate()
        proc.wait(timeout=2)

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
