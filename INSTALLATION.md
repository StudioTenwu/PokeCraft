# AICraft Installation Guide

Complete installation instructions for the AICraft platform using modern tooling.

## Prerequisites

- **Python**: 3.11+ (managed via `uv`)
- **Node.js**: 16+ with npm
- **uv**: Fast Python package manager ([Install here](https://docs.astral.sh/uv/getting-started/installation/))
- **Anthropic API Key**: [Get one here](https://console.anthropic.com/settings/keys)

## Quick Start (Full Stack)

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. Clone and Setup

```bash
# Clone the repository
cd /path/to/AICraft

# Backend setup with uv
cd backend
uv venv                           # Create virtual environment
source .venv/bin/activate         # Activate (macOS/Linux)
# .venv\Scripts\activate          # Activate (Windows)
uv pip install -e ".[dev]"        # Install with dev dependencies

# Configure environment
cp .env.example .env
nano .env                         # Add your ANTHROPIC_API_KEY

# Frontend setup
cd ../frontend
npm install                       # Install dependencies
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
python src/main.py
# Server runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# App runs on http://localhost:5173
```

### 4. Access the Application

Open your browser to **http://localhost:5173**

---

## Backend Installation (Python)

### Production Mode

Install only production dependencies:

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
```

**Installed packages:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Anthropic SDK (LLM integration)
- SQLAlchemy + aiosqlite (async database)
- python-multipart (file uploads)

### Development Mode

Install with testing, linting, and formatting tools:

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Additional dev tools:**
- pytest + plugins (testing framework)
- httpx (API testing)
- black (code formatting)
- isort (import sorting)
- ruff (fast linting)
- mypy (type checking)
- pre-commit (git hooks)

### Running Tests

```bash
cd backend
pytest                          # Run all tests
pytest --cov=src                # With coverage report
pytest -v                       # Verbose output
pytest tests/unit/              # Specific directory
```

### Code Quality Checks

```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Formatting
black src/
isort src/

# Run all checks (pre-commit)
pre-commit run --all-files
```

---

## Frontend Installation (Node.js)

### Production Build

```bash
cd frontend
npm install
npm run build
npm run preview              # Preview production build
```

### Development Mode

```bash
cd frontend
npm install
npm run dev                  # Hot-reload dev server
```

### Running Tests

```bash
cd frontend
npm test                     # Run tests in watch mode
npm run test:ui              # Interactive test UI
npm run test:coverage        # Generate coverage report
```

---

## Environment Configuration

### Backend (.env)

Create `backend/.env` from the example:

```bash
cd backend
cp .env.example .env
```

Required variables:
```env
# Required: Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Database configuration
DATABASE_PATH=./aicraft.db

# Optional: Server configuration
HOST=0.0.0.0
PORT=8000
```

### Frontend

No environment configuration needed. API endpoints are configured in `vite.config.js`.

---

## Dependency Management

### Why uv instead of pip?

**uv** is a modern, Rust-based Python package manager that is:
- **10-100x faster** than pip for installs
- **Compatible** with pip/PyPI (drop-in replacement)
- **Reliable** with better dependency resolution
- **Efficient** with built-in caching

### Common uv Commands

```bash
# Create virtual environment
uv venv                      # Python 3.11+ auto-detected
uv venv --python 3.12        # Specific Python version

# Install packages
uv pip install package-name
uv pip install -e .          # Install project (production)
uv pip install -e ".[dev]"   # Install project (with dev deps)

# Update dependencies
uv pip install --upgrade package-name
uv pip list --outdated       # Show outdated packages

# Sync from pyproject.toml
uv pip sync                  # Install exact dependencies

# Freeze dependencies
uv pip freeze > requirements-lock.txt
```

### Updating Dependencies

**Backend:**
```bash
cd backend
source .venv/bin/activate

# Update specific package
uv pip install --upgrade fastapi

# Update all packages
uv pip install --upgrade $(uv pip list --format=freeze | cut -d= -f1)

# Update pyproject.toml versions after testing
# Then reinstall
uv pip install -e ".[dev]"
```

**Frontend:**
```bash
cd frontend

# Update specific package
npm update react

# Update all packages
npm update

# Check for outdated packages
npm outdated
```

---

## Project Structure

```
AICraft/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── main.py         # API server
│   │   ├── models/         # Pydantic + SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── config.py       # Configuration
│   ├── tests/              # Pytest tests
│   ├── pyproject.toml      # Python dependencies & config
│   ├── .env.example        # Environment template
│   └── INSTALLATION.md     # Backend-specific docs
│
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   └── App.jsx         # Main app
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
│
└── INSTALLATION.md         # This file (root installation)
```

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
lsof -ti:8000 | xargs kill -9
```

**Database locked error:**
```bash
# Stop all backend processes
# Delete database and restart
rm backend/aicraft.db
python backend/src/main.py
```

**Missing API key:**
```bash
# Verify .env file exists
cat backend/.env | grep ANTHROPIC_API_KEY

# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

**Type checking errors:**
```bash
# Install type stubs
uv pip install types-python-dateutil
mypy src/
```

### Frontend Issues

**Module not found errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Vite port conflict (5173):**
```bash
# Edit vite.config.js to use different port
# Or kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**CORS errors:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/src/main.py`
- Verify fetch URLs in frontend match backend

### General Issues

**Virtual environment not activating:**
```bash
# Recreate virtual environment
cd backend
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Python version mismatch:**
```bash
# Check current Python
python --version

# Use specific version with uv
uv venv --python 3.11
```

---

## Docker Deployment (Future)

Coming soon: Docker Compose setup for containerized deployment.

---

## Legacy pip Installation

If you prefer traditional pip (not recommended):

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Why uv is better:**
- 10-100x faster installs
- Better dependency resolution
- Built-in caching
- Drop-in pip replacement

---

## Next Steps

After installation:

1. **Read the documentation**: See `README.md` for project overview
2. **Run tests**: Verify everything works with `pytest` and `npm test`
3. **Explore the code**: Check out `backend/src/` and `frontend/src/`
4. **Try the app**: Create your first AI agent!

For development guidelines, see `backend/.claude/CLAUDE.md` and project standards.

---

## Support

- **Documentation**: `/docs`
- **Issues**: GitHub Issues
- **API Docs**: http://localhost:8000/docs (when backend is running)
