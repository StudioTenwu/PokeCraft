"""Test script to verify environment setup for MCP server."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / 'src'))

def test_env_setup():
    """Verify all required environment variables are set."""
    print("=" * 60)
    print("AICraft Environment Setup Test")
    print("=" * 60)
    
    all_ok = True
    
    # Check for ANTHROPIC_API_KEY
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print("✅ ANTHROPIC_API_KEY is set")
        print(f"   Value: {api_key[:10]}..." if len(api_key) > 10 else f"   Value: {api_key}")
    else:
        print("❌ ANTHROPIC_API_KEY is NOT set")
        print("   This will cause MCP server initialization to fail!")
        print("   Solution: Create backend/.env file with ANTHROPIC_API_KEY=sk-ant-...")
        all_ok = False
    
    print()
    
    # Check for .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        print(f"✅ .env file exists at {env_file}")
    else:
        print(f"❌ .env file does NOT exist at {env_file}")
        print(f"   Solution: cp .env.example .env")
        all_ok = False
    
    print()
    
    # Test tool loading
    try:
        from agent_deployer import AgentDeployer
        deployer = AgentDeployer(None, None)
        tools = deployer._load_tools_from_file()
        print(f"✅ Tool loading works: {len(tools)} tools found")
    except Exception as e:
        print(f"❌ Tool loading failed: {e}")
        all_ok = False
    
    print()
    
    # Test MCP server creation
    try:
        import claude_agent_sdk
        from agent_deployer import AgentDeployer
        deployer = AgentDeployer(None, None)
        tools = deployer._load_tools_from_file()
        
        user_tool_server = claude_agent_sdk.create_sdk_mcp_server(
            name="user_tools",
            version="1.0.0",
            tools=tools if tools else None,
        )
        
        if user_tool_server.get("type") == "sdk" and "instance" in user_tool_server:
            print("✅ MCP server creation works")
        else:
            print("❌ MCP server creation returned invalid config")
            all_ok = False
    except Exception as e:
        print(f"❌ MCP server creation failed: {e}")
        all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("✅ All checks passed! Environment is properly configured.")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    success = test_env_setup()
    sys.exit(0 if success else 1)
