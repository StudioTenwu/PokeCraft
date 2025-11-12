# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Stack

**Backend:** FastAPI (async) | SQLite + SQLAlchemy ORM | Claude Agent SDK | mflux (Schnell 3-bit) | Python 3.11+ with full type hints

**Frontend:** React 18 + Vite | Canvas 2D | Tailwind CSS | Pokemon Game Boy Color theme

---

## Architecture Overview

### Three-Phase System (ALL COMPLETE)

**Phase 1: Agent Creation** ✅
- LLM generates Pokemon-themed agent (name, backstory, personality)
- Avatar generated with mflux (local Schnell 3-bit model, 2 steps)
- SSE streaming for real-time progress (fake progress + mflux parsing)
- Stored in SQLite via AgentService
- Frontend: AgentCreation.jsx, AgentCard.jsx, AgentPanel.jsx, ThemeToggle.jsx

**Phase 2: World Creation** ✅
- LLM generates game worlds from descriptions OR instant creation from pre-defined data
- Default starter worlds available (Pallet Town, etc.)
- WorldService manages grid-based environments
- Frontend: WorldCreation.jsx, WorldCanvas.jsx, WorldSelector.jsx, GameWorldView.jsx

**Phase 3: Tool System** ✅
- Child describes tool → LLM generates Python code with `@tool` decorator
- Tools validated (AST parsing, forbidden imports check)
- Dynamic tool discovery via `_load_tools_from_file()`
- Tools appended to `tools.py` and saved to database
- Tool-action binding mechanism (tools specify game action IDs)
- Frontend: ToolWorkshop.jsx, ToolCreator.jsx, ToolLibrary.jsx

**Phase 4: Agent Deployment** ✅
- Agent explores world using custom tools via Claude Agent SDK
- Real-time SSE streaming (thinking, tool_call, tool_result, world_update, error, complete)
- Game engine executes actions and returns state deltas (only changed values)
- Three-column deployment UI: ThinkingPanel (left) | GameWorldView (center) | EventLogSidebar (right)
- Frontend: AgentRunner.jsx, ThinkingPanel.jsx, EventLogSidebar.jsx, ActionDisplay.jsx

---

### Game System Architecture

**Action System:**
```python
# models/game_actions.py - Defines action schemas
class GameAction(BaseModel):
    action_id: str
    name: str
    description: str
    parameters: list[ActionParameter]
    category: str | None  # Movement, Perception, Interaction

class GameActionSet(BaseModel):
    game_type: str
    actions: list[GameAction]

# Predefined action set for grid_navigation
GRID_NAVIGATION_ACTIONS = [
    move (direction: north/south/east/west),
    pickup (no params),
    wait (turns: int)
]
```

**Game Engine Pattern:**
```python
# game_engine.py - Abstract base + concrete implementations
class GameEngine(ABC):
    def execute_action(self, action_id: str, parameters: dict) -> ActionResult
    @abstractmethod
    def _execute_action_impl(...) -> ActionResult

class GridNavigationEngine(GameEngine):
    def _execute_action_impl(...):
        if action_id == "move":
            return self._execute_move(parameters)
        # ...
```

**State Delta Pattern:**
Only changed state is returned to frontend for efficient updates:
```python
ActionResult(
    success=True,
    state_delta={  # Only changed values
        "agent_position": [3, 5],
        "agent_moved_from": [2, 5],
        "agent_moved_to": [3, 5]
    },
    message="Moved east to position [3, 5]"
)
```

**Action Registry:**
- `action_registry.py` - Maps game types to action sets
- Factory pattern for game engine creation
- GET `/api/actions/{world_id}` - Fetch available actions for world

---

### Tool-Action Binding Mechanism

**Critical pattern:** Tools specify which game action they invoke via `action` field in return value:

```python
@tool("move_direction", "Move in a direction", {"direction": str, "steps": int})
async def move_direction(args: dict[str, Any]) -> dict[str, Any]:
    # Tool validates and formats parameters
    return {
        "content": [{"type": "text", "text": f"Moving {steps} steps {direction}!"}],
        "action": {
            "action_id": "move",  # References GRID_NAVIGATION_ACTIONS
            "parameters": {"direction": direction, "steps": steps}
        }
    }
```

**Execution flow:**
1. Agent uses tool via Claude Agent SDK
2. Tool returns result with `action` field
3. Deployer extracts `action_id` and `parameters`
4. Game engine executes action via `execute_action()`
5. State delta yielded as `world_update` SSE event
6. Frontend updates GameWorldView with delta

**Tool categories:** Movement, Perception, Interaction (stored in ToolDB)

---

### Critical SDK Integration

**Two SDK Patterns in Codebase:**

1. **Old pattern** (`query()`) - Used in tool_generator.py, llm_client.py, llm_world_generator.py
2. **New pattern** (`ClaudeSDKClient`) - Used in agent_deployer.py

**Why both?** Migration in progress. Use `ClaudeSDKClient` for new code with MCP servers.

**Deployment pattern (agent_deployer.py):**
```python
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
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ThinkingBlock):
                    yield SSE event: thinking
                elif isinstance(block, TextBlock):
                    yield SSE event: text
                elif isinstance(block, ToolUseBlock):
                    yield SSE event: tool_call
                elif isinstance(block, ToolResultBlock):
                    yield SSE event: tool_result
                    # Extract action from tool result
                    if "action" in result:
                        action_result = game_engine.execute_action(...)
                        yield SSE event: world_update
```

**CRITICAL SDK Bug Workaround:**

`agent_deployer.py` applies a monkey-patch on module import to fix SDK bug #323 (https://github.com/anthropics/claude-agent-sdk-python/issues/323). The patch:
1. Fixes version parameter bug in `create_sdk_mcp_server()`
2. Returns correct McpSdkServerConfig structure with keys: `type="sdk"`, `name`, `instance`

**Why this matters:** SDK strips the `instance` field before JSON serialization (subprocess_cli.py:154-159). Wrong keys cause "Object of type Server is not JSON serializable" error. See `development/claude-sdk-debug/SKILL.md` snippet for comprehensive debugging guide.

---

### SSE Event Streaming

**Complete event types:**

**Agent creation streaming:**
- `llm_start`, `llm_progress`, `llm_complete` - LLM generation
- `avatar_start`, `avatar_progress`, `avatar_complete` - mflux avatar generation

**Agent deployment streaming:**
- `system` - SystemMessage from SDK
- `thinking` - Agent's reasoning (from ThinkingBlock)
- `text` - Agent's text responses (from TextBlock)
- `tool_call` - Tool invocations (from ToolUseBlock)
- `tool_result` - Tool execution results (from ToolResultBlock)
- `world_update` - Grid state changes (state deltas only)
- `error` - Action failures, tool errors, deployment errors
- `complete` - Final status with metrics

SDK handles tool execution automatically via MCP server. Results come back as `ToolResultBlock` messages.

---

## Complete API Reference

### Agent Endpoints
```
POST /api/agents/create
  Input: { description }
  Output: AgentData (blocking)

GET /api/agents/create/stream
  Input: ?description=...
  Output: SSE stream (llm_start, llm_progress, avatar_start, etc.)

POST /api/agents
  Input: AgentData (pre-defined, no id)
  Output: AgentData
  Note: For instant agent creation (default Pokemon templates)

GET /api/agents/{agent_id}
  Output: AgentData

GET /api/agents/deploy
  Input: ?agent_id=...&world_id=...&goal=...
  Output: SSE stream (thinking, tool_call, world_update, complete)
  Note: Changed from POST to GET for SSE compatibility
```

### World Endpoints
```
POST /api/worlds/create
  Input: { agent_id, description }
  Output: WorldData (LLM-generated)

POST /api/worlds/create-from-data
  Input: WorldData (pre-defined, no id)
  Output: WorldData
  Note: For instant world creation (starter worlds)

GET /api/worlds/{world_id}
  Output: WorldData

GET /api/worlds/agent/{agent_id}
  Output: [WorldData] (all worlds for agent)

GET /api/actions/{world_id}
  Output: GameActionSet (available actions for world's game_type)
```

### Tool Endpoints
```
POST /api/tools/create
  Input: { agent_id, description }
  Output: { tool_name, code, explanation, category }

GET /api/tools/agent/{agent_id}
  Output: [ToolData] (all tools for agent)

DELETE /api/tools/{tool_name}
  Output: { message }
```

---

## Frontend Architecture

### Component Hierarchy

**Main App Layout (App.jsx):**
- Fixed-width left sidebar (320px): AgentPanel
- Flexible right section: WorldSelector + ToolWorkshop

**Agent Creation Phase:**
- AgentCreation.jsx - Agent creation UI with SSE streaming
- AgentCard.jsx - Display agent info
- AgentPanel.jsx - Agent details with equipped tools
- ThemeToggle.jsx - Day/Night mode toggle

**World Creation Phase:**
- WorldCreation.jsx - World creation UI
- WorldCanvas.jsx - Canvas-based world renderer
- WorldSelector.jsx - Select from multiple worlds
- GameWorldView.jsx - Deployment world visualization

**Tool System:**
- ToolWorkshop.jsx - Collapsible workshop panel
- ToolCreator.jsx - Tool creation UI
- ToolLibrary.jsx - Tool management

**Deployment UI:**
- AgentRunner.jsx - Full deployment UI with SSE
- Three-column layout:
  - Left (30%): ThinkingPanel - Agent reasoning
  - Center (45%): GameWorldView - Real-time world visualization
  - Right (25%): EventLogSidebar - Event stream
- ActionDisplay.jsx - Action visualization

**Shared Components:**
- PokemonButton.jsx - Themed button component

### SSE Event Handling Pattern

```javascript
const eventSource = new EventSource(`/api/agents/create/stream?description=${desc}`)

eventSource.addEventListener('llm_progress', (e) => {
  const data = JSON.parse(e.data)
  setProgress(data.progress)
})

eventSource.addEventListener('complete', (e) => {
  const data = JSON.parse(e.data)
  setAgent(data.agent)
  eventSource.close()
})

eventSource.addEventListener('error', (e) => {
  console.error('SSE error:', e)
  eventSource.close()
})
```

---

## Database Schema

### Tables

**agents:**
```python
id: String (UUID)
name: String
backstory: Text
personality_traits: JSON (list[str])
avatar_url: String
created_at: DateTime
```

**worlds:**
```python
id: String (UUID)
agent_id: String (FK to agents.id)
name: String
description: Text
grid_data: Text (JSON serialized)
agent_position_x: Integer
agent_position_y: Integer
width: Integer
height: Integer
game_type: String (default: "grid_navigation")
created_at: DateTime
```

**tools:**
```python
id: String (UUID)
agent_id: String (FK to agents.id)
name: String (unique)
description: Text
code: Text (full Python function with @tool decorator)
category: String (Movement, Perception, Interaction)
expected_action_id: String | None
created_at: DateTime
```

---

## Development Commands

### Setup

```bash
# Backend
cd backend

# 1. Install dependencies
uv pip install -e ".[dev]"

# 2. Create .env file with API key (REQUIRED for agent deployment)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY=sk-ant-...

# 3. Initialize database
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

# Frontend
cd frontend && npm install
```

**CRITICAL:** The `ANTHROPIC_API_KEY` environment variable MUST be set for agent deployment to work. Without it:
- MCP server initialization will fail
- Custom tools won't be available
- Agent will try to use built-in tools (like Bash) instead
- You'll see `mcp_servers: [{'name': 'user_tools', 'status': 'failed'}]`

### Running

```bash
# Terminal 1: Backend (http://localhost:8000)
cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (http://localhost:3000)
cd frontend && npm run dev
```

### Testing

```bash
# Backend - All tests (98 total: 36 unit, 28 integration, 34 e2e)
cd backend && uv run pytest tests/ -v

# Single test file
uv run pytest tests/unit/test_agent_deployer.py -v

# Single test
uv run pytest tests/unit/test_agent_deployer.py::test_deploy_agent_yields_tool_call_events -xvs

# With coverage
uv run pytest tests/ --cov=src --cov-report=html

# E2E tests (requires database reset first!)
rm -f backend/agents.db
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
uv run pytest tests/e2e/ -v

# Frontend tests (62 total with Vitest)
cd frontend && npm test
```

### Database Reset

```bash
# Clean start (REQUIRED before E2E tests)
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

**Use ClaudeSDKClient for new code with MCP servers:**

```python
# Correct (new pattern - use for MCP server integration)
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

# Old pattern (still used in tool_generator.py, llm_client.py)
async for message in query(prompt=prompt):
    if hasattr(message, "result") and message.result:
        response_text = message.result
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
├── tool_generator.py    # LLM-based tool code generation
├── tool_registry.py     # Dynamic tool discovery + append to tools.py
├── tools.py             # @tool decorated functions for MCP
├── game_engine.py       # Grid state + action execution
├── action_registry.py   # Game-specific action sets
├── state_manager.py     # World state tracking
├── llm_client.py        # Agent SDK wrapper
├── llm_world_generator.py  # World generation via LLM
├── avatar_generator.py  # mflux integration
├── database.py          # SQLAlchemy setup
├── config.py            # Environment configuration
└── models/              # Pydantic + SQLAlchemy models
    ├── agent.py
    ├── world.py
    ├── tool.py
    ├── game_actions.py
    └── db_models.py

backend/tests/
├── unit/                # Unit tests (36 tests)
├── integration/         # Integration tests (28 tests)
└── e2e/                 # End-to-end with Playwright (34 tests)
    ├── helpers.py
    ├── test_pokemon_creation.py
    ├── test_world_creation.py
    ├── test_tool_creation.py
    └── test_agent_deployment.py

frontend/src/
├── App.jsx              # Main app
├── api.js               # API client
└── components/
    ├── AgentCreation.jsx
    ├── AgentCard.jsx
    ├── AgentPanel.jsx
    ├── WorldCreation.jsx
    ├── WorldCanvas.jsx
    ├── WorldSelector.jsx
    ├── GameWorldView.jsx
    ├── ToolWorkshop.jsx
    ├── ToolCreator.jsx
    ├── ToolLibrary.jsx
    ├── AgentRunner.jsx
    ├── ThinkingPanel.jsx
    ├── EventLogSidebar.jsx
    ├── ActionDisplay.jsx
    ├── ThemeToggle.jsx
    └── PokemonButton.jsx
```

---

## Configuration

### Environment Variables

```bash
# Avatar Generation
AVATAR_MODEL_PATH="~/.AICraft/models/schnell-3bit"

# Server
API_HOST="0.0.0.0"
API_PORT=8000
API_BASE_URL="http://localhost:8000"

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"

# Database
DB_PATH="backend/agents.db"

# Logging
LOG_LEVEL="INFO"
LOG_DIR="backend/logs"
LOG_FORMAT="json"  # or 'text'
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
- SDK error traceback checking
- Tool-action binding validation

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
