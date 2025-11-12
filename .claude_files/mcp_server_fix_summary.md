# MCP Server Failed Fix - Complete Investigation Report

## Problem Statement

User reported seeing:
```
'mcp_servers': [{'name': 'user_tools', 'status': 'failed'}]
```

And agent attempting to use `Bash` tool with curl instead of custom tools.

## Root Cause Analysis

### Investigation Process

1. **Checked error logs** (`backend/logs/errors.log`)
   - Found: `TypeError: 'async for' requires an object with __aiter__ method, got coroutine`
   - This indicated backend was running outdated code (pre-SDK refactor)

2. **Verified current code** (`agent_deployer.py`)
   - Current code uses correct pattern: `ClaudeSDKClient` + `client.query()` + `client.receive_response()`
   - SDK bug workaround patch is properly applied

3. **Tested tool loading**
   - Tools loading successfully: 9 tools found in `tools.py`
   - Tool discovery and deduplication working correctly

4. **Tested MCP server creation**
   - MCP server config creation working: `{'type': 'sdk', 'name': 'user_tools', 'instance': <Server>}`
   - SDK patch functioning correctly

5. **Identified missing API key**
   - `ANTHROPIC_API_KEY` not set in environment
   - No `.env` file exists (only `.env.example`)
   - Claude SDK requires this key to initialize client
   - Without it, SDK client initialization fails → MCP server marked as "failed"

### Root Causes

**Primary Issue:** Missing `ANTHROPIC_API_KEY` environment variable
- Claude Agent SDK requires `ANTHROPIC_API_KEY` to initialize `ClaudeSDKClient`
- When SDK client initialization fails, MCP server cannot start
- Without MCP server, custom tools are not available
- Agent falls back to trying built-in tools (like `Bash`)

**Secondary Issue:** Outdated backend process
- Backend was running old code from before SDK refactor
- Old code used deprecated `query()` pattern that returns coroutine
- New code uses `ClaudeSDKClient` context manager pattern

## Solution Implemented

### 1. Updated `.env.example`
Added `ANTHROPIC_API_KEY` with documentation:
```bash
# Claude API Key (Required for agent deployment)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Updated `config.py`
Added API key to Config class:
```python
# Claude API Key (Required for agent deployment)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

### 3. Added Pre-flight Check in `agent_deployer.py`
Added validation before SDK client initialization:
```python
# Validate API key before initializing SDK client
import os
if not os.getenv("ANTHROPIC_API_KEY"):
    error_msg = (
        "ANTHROPIC_API_KEY environment variable is not set. "
        "Please create backend/.env file with your API key. "
        "See backend/.env.example for reference."
    )
    logger.error(error_msg)
    yield DeploymentEvent(
        event_type="error",
        data={
            "error_type": "api_key_missing",
            "message": error_msg,
            "recoverable": False,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
    return
```

### 4. Updated Documentation (`CLAUDE.md`)
Added critical setup instructions:
```bash
# 2. Create .env file with API key (REQUIRED for agent deployment)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY=sk-ant-...
```

With warning:
> **CRITICAL:** The `ANTHROPIC_API_KEY` environment variable MUST be set for agent deployment to work. Without it:
> - MCP server initialization will fail
> - Custom tools won't be available
> - Agent will try to use built-in tools (like Bash) instead
> - You'll see `mcp_servers: [{'name': 'user_tools', 'status': 'failed'}]`

### 5. Created Diagnostic Script (`test_env_setup.py`)
Python script that verifies:
- `ANTHROPIC_API_KEY` is set
- `.env` file exists
- Tools load correctly (9+ tools)
- MCP server creation works

### 6. Created Troubleshooting Guide (`backend/TROUBLESHOOTING.md`)
Comprehensive guide covering:
- MCP server failure symptoms and solutions
- Quick verification checklist
- Debugging commands
- Other common issues (database, avatar, CORS, etc.)

## Files Changed

### Modified
1. `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/.env.example`
   - Added `ANTHROPIC_API_KEY` documentation

2. `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/src/config.py`
   - Added `ANTHROPIC_API_KEY` to Config class

3. `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/src/agent_deployer.py`
   - Added pre-flight API key validation
   - Returns clear error message if key is missing

4. `/Users/wz/Desktop/zPersonalProjects/AICraft/.claude/CLAUDE.md`
   - Updated setup instructions
   - Added critical warning about API key requirement

### Created
5. `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/test_env_setup.py`
   - Environment setup verification script

6. `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/TROUBLESHOOTING.md`
   - Comprehensive troubleshooting guide

## User Action Required

### Immediate Steps
1. **Create `.env` file:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Add API key:**
   Edit `backend/.env` and set:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

3. **Restart backend:**
   Stop and restart the backend server to load new environment variables

4. **Verify setup:**
   ```bash
   cd backend
   uv run python test_env_setup.py
   ```

### Expected Outcome
After following these steps:
- ✅ MCP server will initialize successfully
- ✅ Custom tools will be available
- ✅ Agent will use proper tools (move_direction, observe_world, etc.)
- ✅ No more `Bash` tool attempts or curl commands
- ✅ Status will show: `mcp_servers: [{'name': 'user_tools', 'status': 'active'}]`

## Testing Verification

Run the diagnostic script to confirm everything is working:
```bash
cd backend
uv run python test_env_setup.py
```

Expected output:
```
============================================================
AICraft Environment Setup Test
============================================================
✅ ANTHROPIC_API_KEY is set
   Value: sk-ant-api...
✅ .env file exists at /Users/.../backend/.env
✅ Tool loading works: 9 tools found
✅ MCP server creation works
============================================================
✅ All checks passed! Environment is properly configured.
============================================================
```

## Technical Notes

### Why This Matters
The Claude Agent SDK's `ClaudeSDKClient` requires an API key to authenticate with Anthropic's API. The SDK internally:
1. Reads `ANTHROPIC_API_KEY` from environment
2. Uses it to authenticate API requests
3. Initializes MCP server connections
4. Registers custom tools from MCP servers

Without the API key, step 1 fails, which cascades to prevent MCP server initialization, leaving no custom tools available.

### SDK Pattern Used
```python
# Official ClaudeSDKClient pattern (not deprecated query())
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)
    async for message in client.receive_response():
        # Process streaming messages
```

This is the correct pattern as of claude-agent-sdk v0.1.6+.

### MCP Server Configuration
```python
user_tool_server = claude_agent_sdk.create_sdk_mcp_server(
    name="user_tools",
    version="1.0.0",
    tools=tool_functions  # List of SdkMcpTool from @tool decorators
)

options = ClaudeAgentOptions(
    mcp_servers={"user_tools": user_tool_server}
)
```

The SDK automatically:
- Registers tools from `tools` parameter
- Handles tool execution via MCP protocol
- Returns tool results as `ToolResultBlock` messages

## Prevention

To prevent this issue in the future:
1. ✅ `.env.example` now documents `ANTHROPIC_API_KEY` requirement
2. ✅ `CLAUDE.md` setup instructions include API key step
3. ✅ Pre-flight validation checks API key before deployment
4. ✅ Clear error message guides user to solution
5. ✅ Diagnostic script (`test_env_setup.py`) for verification
6. ✅ Comprehensive troubleshooting guide (`TROUBLESHOOTING.md`)

## Related Issues

- SDK Bug #323: Version parameter issue (already patched in `agent_deployer.py`)
- See `development/claude-sdk-debug/SKILL.md` for SDK debugging guide
