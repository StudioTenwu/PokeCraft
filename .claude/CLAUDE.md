# AICraft Project Standards

## Technology Stack

### Backend
- **Framework**: FastAPI with async/await
- **Database**: SQLite with SQLAlchemy ORM (async)
- **LLM Integration**: Claude Agent SDK (NOT direct Anthropic API)
- **Image Generation**: mflux (Flux Schnell 3-bit quantized model)
- **Type System**: Full Python type hints required (mypy strict mode)

### Frontend
- **Framework**: React 18 + Vite
- **Rendering**: PixiJS for 2D game worlds
- **Styling**: Tailwind CSS
- **Theme**: Pokémon Retro (Game Boy Color aesthetic)

## Coding Standards

### Python Backend

#### Type Hints (MANDATORY)
```python
# ✅ CORRECT - Full type annotations
async def generate_agent(self, description: str) -> AgentData:
    response_text: str = ""
    return agent_data

# ❌ INCORRECT - Missing types
async def generate_agent(self, description):
    response_text = ""
    return agent_data
```

**Rules:**
- ALL functions must have complete type hints
- Use `from typing import Any, Optional, Union, etc.`
- Use Pydantic models for data validation
- Configure mypy with `disallow_untyped_defs = true`

#### Pydantic Models
```python
from pydantic import BaseModel, Field

class AgentData(BaseModel):
    name: str
    backstory: str
    personality_traits: list[str]
    avatar_prompt: str
```

**Use Pydantic for:**
- API request/response validation
- LLM output validation
- Configuration models

#### Logging (NOT print statements)
```python
import logging

logger = logging.getLogger(__name__)

# ✅ CORRECT
logger.info(f"Agent created: {agent_id}")
logger.debug(f"Raw LLM response: {response[:100]}")
logger.error(f"Failed to generate: {error}", exc_info=True)

# ❌ INCORRECT
print("Agent created")
```

#### SQLAlchemy ORM Pattern
```python
# ✅ CORRECT - Use ORM models
async with self.session_factory() as session:
    agent = AgentDB(id=agent_id, name=name, ...)
    session.add(agent)
    await session.commit()
    await session.refresh(agent)

# ❌ INCORRECT - No raw SQL
cursor.execute("INSERT INTO agents VALUES ...")
```

### LLM Integration

#### Claude Agent SDK (REQUIRED)

**Why Agent SDK instead of Anthropic API?**
1. **Seamless Claude Code integration** - Works directly with Claude Code CLI
2. **No API key management** - Credentials handled by Claude Code
3. **Tool use integration** - Access to Claude Code's tool ecosystem
4. **Streaming support** - Built-in support for streaming responses
5. **Session management** - Automatic conversation state handling

**Standard Pattern:**
```python
from claude_agent_sdk import query

async def generate_with_llm(self, prompt: str) -> str:
    response_text = ""

    async for message in query(prompt=prompt):
        if hasattr(message, "result") and message.result:
            response_text = message.result
            # Continue to let generator finish naturally

    return response_text
```

**DO NOT use:**
```python
# ❌ INCORRECT - Don't use direct Anthropic API
from anthropic import AsyncAnthropic
client = AsyncAnthropic(api_key=...)
```

#### XML + JSON Output Format

LLM responses must use XML-wrapped JSON with CDATA:

```python
prompt = """Return your response in this exact format:
<output><![CDATA[
{
    "field1": "value",
    "field2": ["item1", "item2"]
}
]]></output>
"""

# Parse with XML then JSON
import xml.etree.ElementTree as ET
root = ET.fromstring(response_text)
json_str = root.text.strip()
data_dict = json.loads(json_str)
```

**Why this format?**
- Prevents markdown formatting interference
- Clear boundary markers for LLM
- Robust parsing with standard libraries

### Image Generation

#### mflux Configuration

**Standard Command:**
```bash
mflux-generate \
  --model schnell \
  --path ./models/schnell-3bit \
  --prompt "your prompt here" \
  --steps 2
```

**Parameters:**
- `--model schnell`: Flux Schnell (speed-optimized)
- `--path ./models/schnell-3bit`: 3-bit quantized model (faster, less memory)
- `--steps 2`: Minimum steps for fastest generation
- Output: Saves to current directory as `image_0.png`

**Avatar Prompt Template:**
```python
avatar_prompt = (
    f"{character_description}, "
    "pokemon-style character art, "
    "Game Boy Color aesthetic, "
    "retro pixel art style, "
    "colorful, cute, "
    "simple background"
)
```

## Testing Standards (TDD Required)

### Test Structure
```
backend/tests/
├── unit/           # Unit tests for services
│   ├── test_agent_service.py
│   ├── test_llm_client.py
│   └── test_world_service.py
├── integration/    # Integration tests
└── e2e/           # End-to-end tests
```

### Testing Pattern
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_agent_creation():
    # Arrange
    service = AgentService(db_path=":memory:")

    # Act
    result = await service.create_agent("test description")

    # Assert
    assert result["name"]
    assert len(result["personality_traits"]) > 0
```

**Rules:**
- Write tests BEFORE implementation (TDD)
- Use `pytest-asyncio` for async tests
- Mock external dependencies (LLM, database)
- Aim for >80% code coverage

## Frontend Standards

### Component Structure
```jsx
// ✅ CORRECT - TypeScript-style JSDoc + PropTypes
/**
 * @param {Object} props
 * @param {string} props.agentId
 * @param {Function} props.onComplete
 */
export function AgentCreation({ agentId, onComplete }) {
  const [loading, setLoading] = useState(false);
  // ...
}
```

### API Communication
```javascript
// Use EventSource for SSE streaming
const eventSource = new EventSource(
  `http://localhost:8000/api/agents/create?description=${encodeURIComponent(text)}`
);

eventSource.addEventListener('progress', (e) => {
  const data = JSON.parse(e.data);
  setProgress(data.progress);
});

eventSource.addEventListener('complete', (e) => {
  const data = JSON.parse(e.data);
  setAgent(data.agent);
  eventSource.close();
});
```

## Project Workflow

### Development Process
1. **Plan** - Document in `.orchestra/designer.md`
2. **Write tests** - TDD approach
3. **Implement** - Follow coding standards
4. **Review** - Check type hints, logging, test coverage
5. **Commit** - Use conventional commits

### Commit Messages
```bash
# Format: <type>(<scope>): <description>

feat(backend): add agent creation streaming endpoint
fix(frontend): resolve night mode toggle state issue
refactor(database): migrate to SQLAlchemy ORM
test(llm): add XML parsing validation tests
docs(readme): update installation instructions
```

### File Organization
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

## Dependencies Management

### Python (pyproject.toml)
```toml
[project]
dependencies = [
    "fastapi==0.115.6",
    "uvicorn[standard]==0.34.0",
    "claude-agent-sdk>=0.1.6",  # Agent SDK, not anthropic
    "sqlalchemy[asyncio]>=2.0",
    "greenlet>=3.1",
    "aiosqlite==0.20.0",
    "python-multipart==0.0.20",
]
```

**Use `uv` for package management:**
```bash
uv pip install -e ".[dev]"
uv pip install <package>
```

## Common Patterns

### Error Handling
```python
try:
    result = await risky_operation()
    logger.info("Operation succeeded")
    return result
except ValidationError as ve:
    logger.error(f"Validation failed: {ve}", exc_info=True)
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return fallback_value()
```

### Async Context Managers
```python
async with session_factory() as session:
    # Database operations
    await session.commit()
```

### Streaming Responses
```python
async def stream_progress():
    yield f"data: {json.dumps({'status': 'started'})}\n\n"

    # Do work...

    yield f"data: {json.dumps({'status': 'complete'})}\n\n"

return StreamingResponse(
    stream_progress(),
    media_type="text/event-stream"
)
```

---

## Development Setup

### Prerequisites
- **Python 3.11+** - Required for backend
- **Node.js 18+** - Required for frontend
- **uv** - Python package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **mflux** - Avatar generation (install: `brew install mflux`)
- **mflux model** - Download 3-bit Schnell model to `~/.AICraft/models/schnell-3bit/`

### Initial Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd AICraft
```

#### 2. Setup Backend
```bash
# Create virtual environment (Python 3.11)
uv venv
source .venv/bin/activate  # On macOS/Linux
# or .venv\Scripts\activate on Windows

# Install root package dependencies
uv pip install -e .

# Navigate to backend and install dependencies
cd backend
uv pip install -e ".[dev]"

# Initialize database
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

#### 3. Setup Frontend
```bash
cd frontend
npm install
```

### Running the Application

#### Terminal 1: Backend Server
```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be available at http://localhost:8000

#### Terminal 2: Frontend Dev Server
```bash
cd frontend
npm run dev
```
Frontend will be available at http://localhost:3000

### Running Tests

#### Backend Tests (111 tests)
```bash
cd backend

# Run all tests
uv run pytest tests/ -v

# Run specific test suite
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

#### Frontend Tests (138 tests)
```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### Project Structure
```
AICraft/
├── backend/                 # FastAPI backend
│   ├── src/                 # Source code
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # SQLAlchemy async setup
│   │   ├── agent_service.py # Agent CRUD operations
│   │   ├── world_service.py # World CRUD operations
│   │   ├── agent_deployer.py # Phase 3: Agent deployment
│   │   ├── llm_*.py         # Claude Agent SDK clients
│   │   ├── avatar_generator.py # mflux integration
│   │   └── models/          # Pydantic & SQLAlchemy models
│   ├── tests/               # Test suite (111 tests)
│   │   ├── unit/            # Unit tests
│   │   └── integration/     # Integration tests
│   ├── static/avatars/      # Generated avatar images
│   └── pyproject.toml       # Python dependencies
│
├── frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   ├── api.js           # Backend API client
│   │   ├── components/      # React components
│   │   │   ├── AgentCreation.jsx    # Phase 1: Agent creation
│   │   │   ├── WorldCreation.jsx    # Phase 2: World creation
│   │   │   ├── WorldCanvas.jsx      # PixiJS world renderer
│   │   │   ├── ToolCreator.jsx      # Phase 3: Tool creation
│   │   │   ├── ToolLibrary.jsx      # Phase 3: Tool management
│   │   │   └── AgentRunner.jsx      # Phase 3: Agent deployment UI
│   │   └── __tests__/       # Test suite (138 tests)
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
│
├── .orchestra/              # Designer agent workspace
│   ├── designer.md          # Task planning document
│   └── docs/                # Project documentation
├── pyproject.toml           # Root package config
└── README.md                # Project README
```

### Environment Configuration

#### Backend Environment Variables
Create `backend/.env`:
```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///agents.db

# Avatar Generation
AVATAR_MODEL_PATH=/Users/your-username/.AICraft/models/schnell-3bit

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aicraft.log

# CORS (for development)
ALLOWED_ORIGINS=http://localhost:3000
```

### Common Development Tasks

#### Add New Python Dependency
```bash
cd backend
uv pip install <package-name>
# Update pyproject.toml manually or:
uv pip freeze > requirements.txt  # if needed
```

#### Add New Frontend Dependency
```bash
cd frontend
npm install <package-name>
```

#### Database Migrations
```bash
cd backend
# The database auto-initializes on first run
# To reset database:
rm agents.db
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

#### View API Documentation
With backend running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Troubleshooting

#### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
cd backend
rm -rf .venv
uv venv
uv pip install -e ".[dev]"
```

#### Frontend won't start
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Tests failing
```bash
# Backend: Ensure database is initialized
cd backend
uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

# Frontend: Clear test cache
cd frontend
rm -rf coverage .vitest
npm test
```

#### Avatar generation errors
```bash
# Check mflux installation
which mflux-generate

# Verify model path
ls ~/.AICraft/models/schnell-3bit/

# Test mflux directly
mflux-generate --model schnell --path ~/.AICraft/models/schnell-3bit --prompt "test" --steps 2
```

### Development Workflow

1. **Create feature branch**: `git checkout -b feature-name`
2. **Write tests first** (TDD): Add tests in appropriate `tests/` directory
3. **Implement feature**: Follow coding standards above
4. **Run tests**: Ensure all tests pass (backend + frontend)
5. **Manual testing**: Test in browser at http://localhost:3000
6. **Commit**: Use conventional commit messages
7. **Create PR**: Submit for review

### Quick Start Commands

**Full stack in one go:**
```bash
# Terminal 1: Backend
cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Run tests
cd backend && uv run pytest tests/ -q && cd ../frontend && npm test
```

---

@orchestra.md
