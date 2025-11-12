# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Stack

**Backend:** FastAPI (async) | SQLite + SQLAlchemy ORM | Claude Agent SDK | mflux (Schnell 3-bit) | Python 3.11+ with full type hints

**Frontend:** React 18 + Vite | PixiJS | Tailwind CSS | Pokemon Game Boy Color theme

---

## Architecture Overview

### Three-Phase System

**Phase 1: Agent Creation**
- LLM generates Pokemon-themed agent (name, backstory, personality)
- Avatar generated with mflux (local Schnell 3-bit model)
- Stored in SQLite via AgentService

**Phase 2: World Creation**
- LLM generates game worlds (grid_navigation, dungeon_crawler, etc.)
- Default starter worlds available (Pallet Town, etc.)
- WorldService manages grid-based environments

**Phase 3: Agent Deployment** (Current Focus)
- Agent explores world using custom tools
- Tools loaded dynamically from `tools.py` via `@tool` decorator
- Real-time SSE streaming to frontend showing agent's thinking/actions
- Game engine executes actions and updates world state

### Critical SDK Integration

**Claude Agent SDK with MCP Servers:**

The deployment system uses Claude Agent SDK's `ClaudeSDKClient` pattern with in-process MCP servers for custom tools. This replaced the deprecated `query()` pattern.

```python
# Official pattern (agent_deployer.py)
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
import claude_agent_sdk  # Module ref for patched create_sdk_mcp_server

# Create MCP server with @tool decorated functions
user_tool_server = claude_agent_sdk.create_sdk_mcp_server(
    name="user_tools",
    version="1.0.0",
    tools=tool_functions  # List of SdkMcpTool from tools.py
)

# Configure options
options = ClaudeAgentOptions(
    mcp_servers={"user_tools": user_tool_server}
)

# Use async context manager
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)
    async for message in client.receive_response():
        # Process AssistantMessage, ToolUseBlock, ToolResultBlock, etc.
        ...
```

**CRITICAL SDK Bug Workaround:**

`agent_deployer.py` applies a monkey-patch on module import to fix SDK bug #323 (https://github.com/anthropics/claude-agent-sdk-python/issues/323). The patch:
1. Fixes version parameter bug in `create_sdk_mcp_server()`
2. Returns correct McpSdkServerConfig structure with keys: `type="sdk"`, `name`, `instance`

**Why this matters:** SDK strips the `instance` field before JSON serialization (subprocess_cli.py:154-159). Wrong keys cause "Object of type Server is not JSON serializable" error. See `development/claude-sdk-debug/SKILL.md` snippet for comprehensive debugging guide.

### Dynamic Tool Loading

Tools are loaded from `backend/src/tools.py` using the `@tool` decorator:

```python
from claude_agent_sdk import tool

@tool("move_direction", "Move in a direction", {"direction": str})
async def move_direction(args: dict[str, Any]) -> dict[str, Any]:
    # Tool implementation
    return {"content": [{"type": "text", "text": "Moved north"}]}
```

The deployer automatically discovers all `@tool` decorated functions via `_load_tools_from_file()` which uses `isinstance(obj, SdkMcpTool)` checks. Tools are deduplicated by name.

### SSE Event Stream

Deployment streams events to frontend via Server-Sent Events:

- `thinking` - Agent's reasoning (from ThinkingBlock)
- `text` - Agent's text responses (from TextBlock)
- `tool_call` - Tool invocations (from ToolUseBlock)
- `tool_result` - Tool execution results (from ToolResultBlock)
- `world_update` - Grid state changes (from game engine)
- `complete` - Deployment finished
- `error` - Failures (recoverable vs fatal)

SDK handles tool execution automatically via MCP server. Results come back as `ToolResultBlock` messages.

---

## Development Commands

### Setup

```bash
# Backend
cd backend
uv pip install -e ".[dev]"
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

# Frontend
cd frontend && npm install
```

### Running

```bash
# Terminal 1: Backend (http://localhost:8000)
cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (http://localhost:3000)
cd frontend && npm run dev
```

### Testing

```bash
# All tests
cd backend && uv run pytest tests/ -v

# Single test file
uv run pytest tests/unit/test_agent_deployer.py -v

# Single test
uv run pytest tests/unit/test_agent_deployer.py::test_deploy_agent_yields_tool_call_events -xvs

# With coverage
uv run pytest tests/ --cov=src --cov-report=html

# Frontend tests
cd frontend && npm test
```

### Database Reset

```bash
# Clean start (required for E2E tests)
rm -f backend/agents.db
cd backend && uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Debugging

```bash
# Check backend logs for SDK errors (CRITICAL for debugging)
tail -50 backend/logs/errors.log

# Grep for specific errors
grep "JSON serializable" backend/logs/errors.log | tail -5

# Watch logs in real-time
tail -f backend/logs/aicraft.log
```

---

## Coding Standards

### Python Type Hints (MANDATORY)

ALL functions require complete type annotations:

```python
async def generate_agent(self, description: str) -> AgentData:
    response_text: str = ""
    return agent_data
```

### Claude Agent SDK Patterns

**Use ClaudeSDKClient, NOT query():**

```python
# Correct (new pattern)
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ThinkingBlock):
                    # Handle thinking
                elif isinstance(block, ToolUseBlock):
                    # Handle tool call
                elif isinstance(block, ToolResultBlock):
                    # Handle tool result

# Deprecated (old pattern)
async for message in query(prompt=prompt, options=options):
    # Don't use this
```

**TypedDict Contracts:**

When working with SDK types, match exact TypedDict keys expected by SDK internal processing:

```python
# McpSdkServerConfig requires these exact keys
McpSdkServerConfig(
    type="sdk",        # SDK checks: config.get("type") == "sdk"
    name="server_name",
    instance=server    # SDK strips before JSON: k != "instance"
)
```

### LLM XML + JSON Output

```python
prompt = """Return response as:
<output><![CDATA[
{"field1": "value", "field2": ["item1", "item2"]}
]]></output>
"""

import xml.etree.ElementTree as ET
root = ET.fromstring(response_text)
data_dict = json.loads(root.text.strip())
```

### Logging (NOT print)

```python
logger.info(f"Agent created: {agent_id}")
logger.error(f"Error: {e}", exc_info=True)
```

### SQLAlchemy ORM (NOT raw SQL)

```python
async with session_factory() as session:
    agent = AgentDB(id=id, name=name, ...)
    session.add(agent)
    await session.commit()
```

---

## Testing Guidelines

### TDD Required

Write tests BEFORE implementation | pytest-asyncio | Mock externals | >80% coverage

### E2E Test Database Reset

**CRITICAL:** Before running E2E tests, reset database to prevent flaky tests:

```bash
rm -f backend/agents.db
cd backend && uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

**Why:** Prevents UNIQUE constraint violations and UUID conflicts.

### Playwright Selector Specificity

Use attribute-based selectors, NOT positional:

```python
# Good
page.locator('textarea[placeholder="World description"]')
page.locator('button:has-text("Create World")')

# Bad
page.locator('textarea').first
page.locator('button').nth(2)
```

### Form Button Pattern

Fill inputs BEFORE clicking submit buttons:

```python
# 1. Fill fields
input_field.fill("value")

# 2. Wait for button enabled
button = page.locator('button:has-text("Submit")')
expect(button).to_be_enabled(timeout=5000)

# 3. Then click
button.click()
```

---

## Debugging SDK Errors

### Check Full Tracebacks

SDK errors surface deep in internal code. User-facing errors hide root causes.

**Always check logs:**

```bash
tail -50 backend/logs/errors.log
grep "TypeError" backend/logs/errors.log
```

### Read SDK Source

When SDK errors occur:

1. Find traceback in `logs/errors.log` with file:line (e.g., `subprocess_cli.py:169`)
2. Locate SDK source: `find .venv/lib -name "subprocess_cli.py"`
3. Read SDK code at failure point to understand expectations
4. Compare your implementation vs SDK's internal processing logic

**Example:** "Object of type Server is not JSON serializable" → Check traceback → Find `subprocess_cli.py:169` → Read SDK's stripping logic at lines 154-159 → Discover TypedDict key mismatch.

See `development/claude-sdk-debug/SKILL.md` snippet for comprehensive guide.

---

## Project-Specific Patterns

### Frontend UUID Generation

When POSTing entities, OMIT id field - let backend generate UUIDs:

```javascript
// Good
const { id, ...pokemonData } = pokemon
fetch('/api/agents', { body: JSON.stringify(pokemonData) })

// Bad - causes UNIQUE constraint violations
fetch('/api/agents', { body: JSON.stringify(pokemon) })  // includes id
```

### SSE Streaming Format

```python
async def stream_progress():
    yield f"data: {json.dumps({'status': 'started'})}\n\n"
    # Work...
    yield f"data: {json.dumps({'status': 'complete'})}\n\n"

return StreamingResponse(stream_progress(), media_type="text/event-stream")
```

### Error Handling

```python
try:
    result = await risky_operation()
    logger.info("Success")
    return result
except ValidationError as ve:
    logger.error(f"Validation failed: {ve}", exc_info=True)
    raise
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return fallback_value()
```

---

## File Structure

```
backend/src/
├── main.py              # FastAPI app + API endpoints
├── agent_deployer.py    # SDK integration + MCP servers + SSE streaming
├── agent_service.py     # Agent CRUD
├── world_service.py     # World CRUD
├── tool_service.py      # Tool CRUD
├── tools.py             # @tool decorated functions for MCP
├── game_engine.py       # Grid state + action execution
├── action_registry.py   # Game-specific action sets
├── state_manager.py     # World state tracking
├── llm_client.py        # Agent SDK wrapper
├── database.py          # SQLAlchemy setup
└── models/              # Pydantic + SQLAlchemy models

backend/tests/
├── unit/                # Unit tests (mocked dependencies)
├── integration/         # Integration tests (real SDK, mocked services)
└── e2e/                 # End-to-end with Playwright

frontend/src/
├── App.jsx              # Main app
├── api.js               # API client
└── components/
    ├── AgentCreation.jsx
    ├── WorldCreation.jsx
    ├── AgentRunner.jsx      # Deployment UI + SSE handling
    └── WorldCanvas.jsx      # PixiJS renderer
```

---

## Quality Checks

See `.quibbler/rules.md` for comprehensive project-specific rules including:
- E2E test database reset
- Playwright selector specificity
- Form button patterns
- Frontend UUID generation
- Type hint completeness
- API contract verification
- **SDK error traceback checking**

---

## Commit Format

```bash
feat(backend): add streaming endpoint
fix(frontend): resolve toggle state
refactor(database): migrate to ORM
test(e2e): add deployment flow test
docs(quibbler): add SDK debugging rule
```

---

@orchestra.md
