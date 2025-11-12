# AICraft Backend Troubleshooting Guide

## MCP Server Failed - Tools Not Available

### Symptoms
- Agent deployment fails with MCP server errors
- You see: `mcp_servers: [{'name': 'user_tools', 'status': 'failed'}]`
- Agent tries to use built-in tools (like `Bash`) instead of custom tools
- Agent uses curl to call API endpoints instead of using tools directly

### Root Cause
The Claude Agent SDK requires `ANTHROPIC_API_KEY` environment variable to initialize. Without it:
1. SDK client initialization fails
2. MCP server cannot start
3. Custom tools are not loaded
4. Agent falls back to trying built-in tools

### Solution

#### Step 1: Create .env file
```bash
cd backend
cp .env.example .env
```

#### Step 2: Add your API key
Edit `backend/.env` and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Get your API key from: https://console.anthropic.com/settings/keys

#### Step 3: Restart the backend
If the backend is running, restart it to load the new environment variables:
```bash
# Stop the running backend (Ctrl+C)
# Then restart:
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 4: Verify setup
Run the environment setup test:
```bash
cd backend
uv run python test_env_setup.py
```

You should see:
```
✅ All checks passed! Environment is properly configured.
```

### Quick Verification Checklist

- [ ] `backend/.env` file exists
- [ ] `ANTHROPIC_API_KEY=sk-ant-...` is set in `.env`
- [ ] Backend has been restarted after creating `.env`
- [ ] `test_env_setup.py` passes all checks

### Still Having Issues?

#### Check error logs
```bash
tail -50 backend/logs/errors.log
```

Look for errors related to:
- `ANTHROPIC_API_KEY`
- `ClaudeSDKClient`
- `user_tools`
- MCP server initialization

#### Verify tools are loading
```bash
cd backend
uv run python -c "
from src.agent_deployer import AgentDeployer
deployer = AgentDeployer(None, None)
tools = deployer._load_tools_from_file()
print(f'Loaded {len(tools)} tools')
for tool in tools:
    print(f'  - {tool.name}')
"
```

Should show 9+ tools including:
- `move_direction`
- `observe_world`
- `jump`
- `move`
- etc.

#### Check API key format
Valid API keys start with `sk-ant-` and are 108 characters long. Example:
```
sk-ant-api03-abcd1234...xyz
```

### Related Documentation
- Setup instructions: `CLAUDE.md` (Development Commands section)
- SDK bug workarounds: `development/claude-sdk-debug/SKILL.md`
- Tool system: `CLAUDE.md` (Phase 3: Tool System section)

---

## Other Common Issues

### Backend won't start
**Symptom:** `uvicorn` command fails or crashes immediately

**Solution:**
1. Check Python version: `python --version` (requires 3.11+)
2. Reinstall dependencies: `uv pip install -e ".[dev]"`
3. Check logs: `cat backend/logs/errors.log`

### Database errors
**Symptom:** SQLite or SQLAlchemy errors

**Solution:**
```bash
# Reset database
rm backend/agents.db
cd backend
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Avatar generation fails
**Symptom:** `mflux-generate` errors during agent creation

**Solution:**
Avatar generation is optional. Check:
1. mflux is installed: `which mflux-generate`
2. Model path exists: `ls ~/.AICraft/models/schnell-3bit/`
3. If missing, agent creation will still work (just without avatar)

### Tool loading fails
**Symptom:** `Loaded 0 tools` or tool import errors

**Solution:**
1. Check `backend/src/tools.py` exists and has `@tool` decorated functions
2. Verify imports: `from claude_agent_sdk import tool`
3. Check for syntax errors in tools.py
4. Run tool test script (see "Verify tools are loading" above)

### CORS errors in frontend
**Symptom:** Frontend can't connect to backend, CORS errors in browser console

**Solution:**
1. Backend must be running on `http://localhost:8000`
2. Frontend must be running on `http://localhost:3000` or `http://localhost:5173`
3. Check `backend/src/config.py` CORS_ORIGINS setting
