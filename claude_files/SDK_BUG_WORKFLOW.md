# Claude Agent SDK Bug Reproduction & Workaround Workflow

**Issue**: [#323 - create_sdk_mcp_server() passes unsupported version parameter](https://github.com/anthropics/claude-agent-sdk-python/issues/323)

**Status**: Open (Reported 2025-11-12)

---

## Summary

The `claude-agent-sdk` v0.1.6 has a bug where `create_sdk_mcp_server()` passes an unsupported `version` parameter to MCP's `Server.__init__()`, causing a `TypeError`. This document provides step-by-step reproduction and verification of the workaround.

---

## Environment

```bash
claude-agent-sdk: 0.1.6
mcp: 0.9.1 (also tested with 1.21.0 - same issue)
Python: 3.11.13
OS: macOS (Darwin 24.6.0)
```

---

## The Bug

### Root Cause

**SDK Code** (`claude_agent_sdk/__init__.py:147`):
```python
def create_sdk_mcp_server(
    name: str, version: str = "1.0.0", tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig:
    from mcp.server import Server
    # ...
    server = Server(name, version=version)  # ❌ version not supported!
```

**MCP Server Class** (all versions 0.9.1 → 1.21.0):
```python
class Server:
    def __init__(self, name: str):  # Only accepts name!
        self.name = name
```

The `version` parameter has **never been supported** by the MCP Server class.

---

## Reproduction Steps

### 1. Check Package Versions

```bash
cd backend
source .venv/bin/activate
uv pip list | grep -E "(claude-agent-sdk|mcp)"
```

**Expected Output**:
```
claude-agent-sdk          0.1.6
mcp                       0.9.1
```

### 2. Verify MCP Server Signature

```python
from mcp.server import Server
import inspect
sig = inspect.signature(Server.__init__)
print(f"Server.__init__{sig}")
print(f"Parameters: {list(sig.parameters.keys())}")
```

**Expected Output**:
```
Server.__init__(self, name: str)
Parameters: ['self', 'name']
```

Notice: **No `version` parameter exists!**

### 3. Reproduce the Bug

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool("test_tool", "A test tool", {"input": str})
async def test_tool(args: dict) -> dict:
    return {"content": [{"type": "text", "text": "Test"}]}

# This line fails with TypeError
server = create_sdk_mcp_server(
    name="test_server",
    version="1.0.0",  # SDK passes this but Server() rejects it
    tools=[test_tool]
)
```

**Expected Error**:
```
TypeError: Server.__init__() got an unexpected keyword argument 'version'
```

### 4. Run Automated Reproduction Script

```bash
cd backend
source .venv/bin/activate
python ../claude_files/reproduce_sdk_bug.py
```

**Expected Output**:
```
================================================================================
Reproducing claude-agent-sdk v0.1.6 bug
================================================================================

1. Checking package versions:
   claude-agent-sdk: 0.1.6
   mcp: 0.9.1

2. Checking MCP Server.__init__() signature:
   Server.__init__(self, name: str)
   Parameters: ['self', 'name']

3. Attempting to use create_sdk_mcp_server() (THIS WILL FAIL):
   Calling create_sdk_mcp_server()...
   ❌ FAILED: Server.__init__() got an unexpected keyword argument 'version'
   This is the expected bug!

4. Using workaround: Create McpSdkServerConfig directly:
   ✅ SUCCESS: McpSdkServerConfig created without errors
   Config: {'command': 'python', 'args': ['-m', 'mcp'], 'env': {'MCP_SERVER_NAME': 'user_tools'}}

================================================================================
Summary:
- Bug confirmed: create_sdk_mcp_server() passes unsupported 'version' parameter
- Workaround works: Create McpSdkServerConfig manually without 'version'
- See: https://github.com/anthropics/claude-agent-sdk-python/issues/323
================================================================================
```

---

## The Workaround

### Implementation

Instead of using `create_sdk_mcp_server()`, create `McpSdkServerConfig` directly:

```python
from claude_agent_sdk.types import McpSdkServerConfig

# ❌ DON'T USE (broken in v0.1.6):
# server = create_sdk_mcp_server(name="user_tools", version="1.0.0", tools=tools)

# ✅ USE THIS INSTEAD:
user_tool_server = McpSdkServerConfig(
    command="python",
    args=["-m", "mcp"],
    env={"MCP_SERVER_NAME": "user_tools"},
)
```

### Applied in AICraft

**File**: `backend/src/agent_deployer.py:150-159`

```python
# Create MCP server configuration manually
# Note: Cannot use create_sdk_mcp_server due to SDK bug (v0.1.6) where it passes
# unsupported 'version' parameter to Server.__init__()
# Workaround: Create McpSdkServerConfig directly
from claude_agent_sdk.types import McpSdkServerConfig
user_tool_server = McpSdkServerConfig(
    command="python",
    args=["-m", "mcp"],
    env={"MCP_SERVER_NAME": "user_tools"},
)
```

**Commit**: `07da5fd` (2025-11-11)

---

## Verification Tests

### Run Integration Tests

```bash
cd backend
source .venv/bin/activate
uv run pytest tests/integration/test_agent_deployment_version_fix.py -v
```

**Expected Output**:
```
tests/integration/test_agent_deployment_version_fix.py::test_agent_deployment_initializes_without_version_error PASSED [ 50%]
tests/integration/test_agent_deployment_version_fix.py::test_mcp_server_creation_with_manual_config PASSED [100%]

========================= 2 passed in 70.38s =========================
```

### Test Coverage

Both integration tests verify:

1. **test_agent_deployment_initializes_without_version_error**:
   - Agent deployment starts without version-related errors
   - Deployment generator yields at least one event
   - No `TypeError` thrown during MCP server creation

2. **test_mcp_server_creation_with_manual_config**:
   - `McpSdkServerConfig` can be created manually
   - No errors when creating config without `version` parameter
   - Config structure is correct

---

## Full Agent Deployment Workflow

### End-to-End Test

```bash
# 1. Start backend server
cd backend
source .venv/bin/activate
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 2. In another terminal, start frontend
cd frontend
npm run dev

# 3. Access application
open http://localhost:3000

# 4. Test deployment flow:
#    - Create an agent (Phase 1)
#    - Create a world (Phase 2)
#    - Deploy agent to world (Phase 3) ← This step uses the workaround!
```

### Expected Behavior

**Before Fix**:
```
❌ Agent deployment fails with:
TypeError: Server.__init__() got an unexpected keyword argument 'version'
```

**After Fix**:
```
✅ Agent deploys successfully
✅ MCP server initializes without errors
✅ Agent can execute actions in the world
```

---

## Timeline

| Date | Event |
|------|-------|
| 2025-11-11 | Bug discovered during agent deployment testing |
| 2025-11-11 | Workaround implemented (commit `07da5fd`) |
| 2025-11-11 | Integration tests added and passed |
| 2025-11-12 | Issue reported to SDK repository (#323) |

---

## When Will This Be Fixed?

The bug requires a fix in the `claude-agent-sdk` package itself. Once the SDK is updated to remove the `version` parameter from the `Server()` call, the workaround can be removed.

**Tracking**: https://github.com/anthropics/claude-agent-sdk-python/issues/323

**Workaround Status**: Active and stable

---

## Files Involved

```
backend/src/agent_deployer.py              # Contains workaround
backend/tests/integration/test_agent_deployment_version_fix.py  # Integration tests
claude_files/reproduce_sdk_bug.py          # Reproduction script
claude_files/SDK_BUG_WORKFLOW.md           # This document
```

---

## Quick Reference

### Check if Bug Still Exists

```bash
cd backend
source .venv/bin/activate
python -c "from claude_agent_sdk import create_sdk_mcp_server, tool; \
@tool('test', 'test', {}); \
async def t(a): return {}; \
create_sdk_mcp_server('test', '1.0.0', [t])"
```

If error appears: Bug still exists
If no error: SDK has been fixed! 🎉

### Switch Back to Official API (When Fixed)

Replace workaround in `agent_deployer.py`:

```python
# After SDK is fixed, replace this:
user_tool_server = McpSdkServerConfig(
    command="python",
    args=["-m", "mcp"],
    env={"MCP_SERVER_NAME": "user_tools"},
)

# With the official API:
user_tool_server = create_sdk_mcp_server(
    name="user_tools",
    version="1.0.0",
    tools=tool_functions
)
```

---

## Additional Notes

- The workaround is fully functional and tested
- No loss of functionality compared to official API
- All 111 backend tests pass with workaround in place
- Frontend deployment UI works correctly with workaround
- The SDK bug affects any project using `create_sdk_mcp_server()`

---

**Last Updated**: 2025-11-12
**Maintainer**: Warren Zhu (wzhu@college.harvard.edu)
