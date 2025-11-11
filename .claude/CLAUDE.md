# AICraft Project Standards

## Technology Stack

**Backend:** FastAPI (async) | SQLite + SQLAlchemy ORM | Claude Agent SDK | mflux (Schnell 3-bit) | Python 3.11+ with full type hints

**Frontend:** React 18 + Vite | PixiJS | Tailwind CSS | Pokemon Game Boy Color theme

---

## Coding Standards

### Python: Type Hints (MANDATORY)
```python
# ALL functions need complete type annotations
async def generate_agent(self, description: str) -> AgentData:
    response_text: str = ""
    return agent_data
```

### Python: Core Patterns
```python
# Pydantic models for validation
class AgentData(BaseModel):
    name: str
    backstory: str
    personality_traits: list[str]

# Logging (NOT print)
logger.info(f"Agent created: {agent_id}")
logger.error(f"Error: {e}", exc_info=True)

# SQLAlchemy ORM (NOT raw SQL)
async with session_factory() as session:
    agent = AgentDB(id=id, name=name, ...)
    session.add(agent)
    await session.commit()
```

### LLM: Claude Agent SDK (NOT Anthropic API)
```python
from claude_agent_sdk import query

async def generate_with_llm(self, prompt: str) -> str:
    response_text = ""
    async for message in query(prompt=prompt):
        if hasattr(message, "result") and message.result:
            response_text = message.result
    return response_text
```

**Why Agent SDK:** Seamless Claude Code integration, no API keys, tool use support, streaming, session management

### LLM: XML + JSON Output Format
```python
# Request format
prompt = """Return response as:
<output><![CDATA[
{"field1": "value", "field2": ["item1", "item2"]}
]]></output>
"""

# Parse
import xml.etree.ElementTree as ET
root = ET.fromstring(response_text)
data_dict = json.loads(root.text.strip())
```

**Why:** Prevents markdown interference, clear boundaries, robust parsing

### Image Generation: mflux
```bash
mflux-generate --model schnell --path ~/.AICraft/models/schnell-3bit --prompt "character, pokemon-style art, Game Boy Color aesthetic" --steps 2
```

### Frontend: Component Standards
```jsx
// JSDoc + PropTypes
export function AgentCreation({ agentId, onComplete }) {
  const [loading, setLoading] = useState(false);
  // Use EventSource for SSE streaming
  const eventSource = new EventSource(`http://localhost:8000/api/...`);
}
```

### Testing: TDD Required
```python
@pytest.mark.asyncio
async def test_agent_creation():
    service = AgentService(db_path=":memory:")
    result = await service.create_agent("test")
    assert result["name"]
```

**Rules:** Write tests BEFORE implementation | pytest-asyncio | Mock externals | >80% coverage

### Commits: Conventional Format
```bash
feat(backend): add streaming endpoint
fix(frontend): resolve toggle state
refactor(database): migrate to ORM
```

---

## Development Setup

### Prerequisites
- Python 3.11+ | Node.js 18+ | uv | mflux | mflux model at `~/.AICraft/models/schnell-3bit/`

### Quick Setup
```bash
# Root
git clone <url> && cd AICraft
uv venv && source .venv/bin/activate
uv pip install -e .

# Backend
cd backend
uv pip install -e ".[dev]"
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

# Frontend
cd frontend && npm install
```

### Run Application
```bash
# Terminal 1: Backend (http://localhost:8000)
cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (http://localhost:3000)
cd frontend && npm run dev
```

### Run Tests
```bash
cd backend && uv run pytest tests/ -v              # 111 tests
cd frontend && npm test                             # 138 tests
cd backend && uv run pytest tests/ --cov=src        # With coverage
```

### Project Structure
```
AICraft/
├── backend/src/
│   ├── main.py              # FastAPI app
│   ├── database.py          # SQLAlchemy async
│   ├── agent_service.py     # Agent CRUD
│   ├── world_service.py     # World CRUD
│   ├── agent_deployer.py    # Phase 3: Deployment
│   ├── llm_*.py             # Claude Agent SDK
│   ├── avatar_generator.py  # mflux
│   └── models/              # Pydantic + SQLAlchemy
├── backend/tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── frontend/src/
│   ├── App.jsx              # Main app
│   ├── api.js               # API client
│   └── components/
│       ├── AgentCreation.jsx    # Phase 1
│       ├── WorldCreation.jsx    # Phase 2
│       ├── WorldCanvas.jsx      # PixiJS renderer
│       ├── ToolCreator.jsx      # Phase 3
│       ├── ToolLibrary.jsx      # Phase 3
│       └── AgentRunner.jsx      # Phase 3
└── .orchestra/
    ├── designer.md          # Task planning
    └── docs/                # Documentation
```

### Environment Configuration
Create `backend/.env`:
```bash
DATABASE_URL=sqlite+aiosqlite:///agents.db
AVATAR_MODEL_PATH=/Users/username/.AICraft/models/schnell-3bit
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000
```

### Common Commands
```bash
# Dependencies
uv pip install <package>             # Python
npm install <package>                # Node

# Database
rm agents.db && uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

# API Docs
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

### Troubleshooting
```bash
# Backend won't start
python --version                     # Check 3.11+
cd backend && rm -rf .venv && uv venv && uv pip install -e ".[dev]"

# Frontend won't start
cd frontend && rm -rf node_modules package-lock.json && npm install

# Tests failing
cd backend && uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
cd frontend && rm -rf coverage .vitest && npm test

# Avatar errors
which mflux-generate
ls ~/.AICraft/models/schnell-3bit/
mflux-generate --model schnell --path ~/.AICraft/models/schnell-3bit --prompt "test" --steps 2
```

### Development Workflow
1. Create branch: `git checkout -b feature-name`
2. Write tests (TDD)
3. Implement following standards
4. Run all tests (backend + frontend)
5. Manual test at http://localhost:3000
6. Commit with conventional format
7. Create PR

---

## File Organization

```
backend/src/
├── main.py              # FastAPI app
├── config.py            # Configuration
├── database.py          # SQLAlchemy setup
├── models/              # Pydantic + SQLAlchemy models
│   ├── agent.py
│   ├── world.py
│   └── db_models.py
├── agent_service.py     # Agent CRUD
├── world_service.py     # World CRUD
├── llm_client.py        # Claude Agent SDK wrapper
└── avatar_generator.py  # mflux integration
```

---

## Common Patterns

```python
# Error handling
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

# Async context managers
async with session_factory() as session:
    await session.commit()

# Streaming responses
async def stream_progress():
    yield f"data: {json.dumps({'status': 'started'})}\n\n"
    # Do work...
    yield f"data: {json.dumps({'status': 'complete'})}\n\n"

return StreamingResponse(stream_progress(), media_type="text/event-stream")
```

---

@orchestra.md
