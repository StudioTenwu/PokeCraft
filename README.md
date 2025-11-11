# AICraft - Pokemon Edition 🎮

Interactive platform where you create AI agents, design worlds, teach them custom tools, and watch them explore autonomously.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- **uv** - Fast Python package manager ([Install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **mflux** - For avatar generation ([GitHub](https://github.com/filipstrand/mflux))
- Flux Schnell 3-bit model at `~/.AICraft/models/schnell-3bit`

### Setup

> **Full installation guide**: See [INSTALLATION.md](./INSTALLATION.md) for complete instructions

**Quick start:**

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up mflux model** (for avatar generation):
   ```bash
   mkdir -p ~/.AICraft/models
   # Download Flux Schnell 3-bit model to ~/.AICraft/models/schnell-3bit
   # See: https://github.com/filipstrand/mflux
   ```

3. **Backend setup:**
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"

   # Start server
   uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Frontend setup** (new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Open the app:**
   Visit [http://localhost:5173](http://localhost:5173)

## 🎯 The 3 Phases

### Phase 1: Agent Birth 🥚
Create AI pokemons with unique personalities:
- **LLM-powered generation** - Claude creates backstories and traits
- **AI avatar generation** - mflux generates Pokemon-style avatar images
- **Persistent storage** - SQLite database with SQLAlchemy ORM
- **SSE streaming** - Real-time progress updates during creation

**Try it:** Create an agent with "A brave explorer who loves discovering new places"

### Phase 2: World Creation 🌍
Design 2D game worlds for your agents:
- **Visual world editor** - PixiJS-powered canvas
- **Terrain types** - Grass, water, mountains, forests
- **Item placement** - Resources, obstacles, treasures
- **Multi-world support** - Each agent can have multiple worlds

**Try it:** Create a world with forests, rivers, and hidden treasures

### Phase 3: Teaching Tools 🛠️
Teach agents custom abilities through natural language:
- **Tool generation** - Claude generates Python `@tool` functions from descriptions
- **Dynamic loading** - Tools loaded at runtime via MCP
- **Agent deployment** - Watch agents use tools to accomplish goals
- **SSE streaming** - Real-time reasoning, tool calls, and world updates

**Try it:**
1. Create tool: "Move the agent forward 3 steps"
2. Deploy agent with goal: "Explore the world and collect items"
3. Watch SSE stream: reasoning → tool_call → tool_result → world_update

## 🏗️ Architecture

```
AICraft/
├── frontend/          # React + Vite (port 5173)
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentCreation.jsx      # Phase 1: Agent birth
│   │   │   ├── WorldCreation.jsx      # Phase 2: World editor
│   │   │   ├── ToolCreator.jsx        # Phase 3: Tool teaching
│   │   │   ├── AgentRunner.jsx        # Phase 3: Agent deployment
│   │   │   ├── AgentCard.jsx          # Display agent info
│   │   │   └── WorldCanvas.jsx        # PixiJS world renderer
│   │   └── App.jsx
│   └── package.json
│
└── backend/           # FastAPI + Claude SDK (port 8000)
    ├── src/
    │   ├── main.py              # API server with SSE endpoints
    │   ├── agent_service.py     # Phase 1: Agent CRUD
    │   ├── world_service.py     # Phase 2: World CRUD
    │   ├── tool_service.py      # Phase 3: Tool CRUD
    │   ├── tool_generator.py    # Phase 3: LLM tool generation
    │   ├── agent_deployer.py    # Phase 3: Agent execution
    │   ├── llm_client.py        # Claude Agent SDK wrapper
    │   ├── avatar_generator.py  # mflux integration
    │   ├── config.py            # Environment-based configuration
    │   └── models/
    │       ├── agent.py         # Pydantic models
    │       ├── tool.py          # Tool models
    │       └── db_models.py     # SQLAlchemy ORM models
    ├── tests/
    │   ├── unit/                # 28 unit tests
    │   └── integration/         # 8 integration tests
    └── pyproject.toml
```

## 🛠️ Technologies

**Frontend:**
- React 18 with hooks
- Vite 5
- Tailwind CSS
- PixiJS 7 (2D rendering)
- EventSource API (SSE streaming)

**Backend:**
- FastAPI (async/await)
- Claude Agent SDK (NOT direct Anthropic API)
- SQLAlchemy 2.0 (async ORM)
- SQLite with aiosqlite
- mflux (Flux Schnell avatar generation)
- Pydantic (data validation)

**Testing:**
- pytest + pytest-asyncio
- vitest + @testing-library/react
- 36 backend tests (28 unit + 8 integration)
- 62 frontend tests

## ⚙️ API Endpoints

### Phase 1: Agent Management
- `POST /api/agents/create` - Create agent (blocking)
- `GET /api/agents/create/stream` - Create agent with SSE streaming
- `GET /api/agents/{agent_id}` - Get agent details

### Phase 2: World Management
- `POST /api/worlds/create` - Create world for agent
- `GET /api/worlds/{world_id}` - Get world details
- `GET /api/worlds/agent/{agent_id}` - List agent's worlds

### Phase 3: Tool Management & Deployment
- `POST /api/tools/create` - Generate custom tool from description
- `GET /api/tools/agent/{agent_id}` - List agent's tools
- `DELETE /api/tools/{tool_name}` - Delete tool
- `POST /api/agents/deploy` - Deploy agent with SSE streaming

### Utility
- `GET /health` - Health check
- `GET /static/avatars/{id}.png` - Serve avatar images

## 🔧 How It Works

### Avatar Generation

AICraft uses mflux to generate Pokemon-style avatars:

```python
# Configured in config.py
AVATAR_MODEL_PATH = ~/.AICraft/models/schnell-3bit

# Generation command
mflux-generate \
  --model schnell \
  --path ~/.AICraft/models/schnell-3bit \
  --prompt "{description}, Game Boy Color style, retro pixel art" \
  --steps 2 \
  --output backend/static/avatars/{agent_id}.png
```

**Fallback:** If mflux fails, returns SVG emoji avatar

### Claude Agent SDK Integration

Uses Claude Code's Agent SDK (NOT direct Anthropic API):

```python
from claude_agent_sdk import query

async for message in query(prompt=prompt):
    if hasattr(message, "result") and message.result:
        response_text = message.result
```

**Why Agent SDK?**
- No API key management (handled by Claude Code)
- Seamless tool integration
- Built-in streaming support
- Session management

### Tool Generation

Phase 3 generates Python tools from natural language:

```python
# Input: "Move the agent forward 3 steps"
# Output:
@tool
async def move_forward(steps: int) -> str:
    """Move the agent forward by the specified number of steps."""
    # Implementation generated by Claude
    return f"Moved forward {steps} steps"
```

**Process:**
1. User describes desired tool
2. Claude generates `@tool` decorated Python function
3. Tool saved to `tools.py` and database
4. Loaded dynamically via MCP at runtime
5. Available for agent deployment

### SSE Streaming Events

Phase 3 deployment streams 6 event types:

```javascript
// Frontend EventSource
const eventSource = new EventSource('/api/agents/deploy');

eventSource.addEventListener('reasoning', (e) => {
  console.log('Agent thinking:', JSON.parse(e.data));
});

eventSource.addEventListener('tool_call', (e) => {
  const { tool, args } = JSON.parse(e.data);
  console.log(`Calling ${tool} with`, args);
});

eventSource.addEventListener('tool_result', (e) => {
  console.log('Result:', JSON.parse(e.data));
});

eventSource.addEventListener('world_update', (e) => {
  const { position } = JSON.parse(e.data);
  updateAgentPosition(position); // Delta updates
});

eventSource.addEventListener('error', (e) => {
  console.error('Error:', JSON.parse(e.data));
});

eventSource.addEventListener('complete', (e) => {
  console.log('Goal accomplished!', JSON.parse(e.data));
  eventSource.close();
});
```

## 📝 Configuration

Environment variables (optional, has defaults):

```bash
# Avatar Generation
AVATAR_MODEL_PATH=~/.AICraft/models/schnell-3bit  # mflux model path

# Server
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database
DB_PATH=backend/agents.db

# Logging
LOG_LEVEL=INFO
LOG_DIR=backend/logs
LOG_FORMAT=json  # or 'text'
```

## 🎯 Project Standards

See [.claude/CLAUDE.md](./.claude/CLAUDE.md) for:
- Full type hints (mypy strict mode)
- Pydantic for validation
- Logging (no print statements)
- SQLAlchemy ORM (no raw SQL)
- Claude Agent SDK (not Anthropic API)
- TDD with 80%+ coverage

## 🧪 Testing

**Run backend tests:**
```bash
cd backend
uv run pytest                           # All tests
uv run pytest tests/unit               # Unit tests only
uv run pytest tests/integration        # Integration tests
uv run pytest --cov=src --cov-report=html  # Coverage report
```

**Run frontend tests:**
```bash
cd frontend
npm test                  # Run tests
npm run test:ui          # Test UI
npm run test:coverage    # Coverage report
```

## 🐛 Troubleshooting

**Avatar generation fails?**
- Verify mflux is installed: `which mflux-generate`
- Check model exists: `ls -la ~/.AICraft/models/schnell-3bit`
- Test manually: `mflux-generate --model schnell --path ~/.AICraft/models/schnell-3bit --prompt "test" --steps 2`
- Check logs: `tail -f backend/logs/aicraft.log`

**Database schema errors?**
```bash
# Delete database to force recreation
rm backend/agents.db
# Restart server - schema will be created automatically
```

**Backend won't start?**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
lsof -ti:8000 | xargs kill -9
```

**Frontend won't connect?**
- Ensure backend is running first: `curl http://localhost:8000/health`
- Check CORS settings in `backend/src/config.py`
- Verify API_BASE_URL points to correct backend

**Tests failing?**
```bash
# Backend: Verify virtual environment
cd backend
source .venv/bin/activate
uv pip install -e ".[dev]"

# Frontend: Clear cache
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📊 Current Status

**✅ Phase 1 Complete:** Agent creation with avatars
**✅ Phase 2 Complete:** World creation and visualization
**✅ Phase 3 Backend Complete:** Tool generation, management, deployment (36 tests passing)
**⏳ Phase 3 Frontend:** In progress (ToolCreator, ToolLibrary, AgentRunner components)

## 📜 License

MIT

## 🙏 Credits

Built with:
- [Claude Code](https://claude.ai/code) - Development environment
- [Claude](https://claude.ai) - LLM for agent generation and tool creation
- [mflux](https://github.com/filipstrand/mflux) - Fast Flux inference on Mac
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [PixiJS](https://pixijs.com/) - 2D rendering engine
