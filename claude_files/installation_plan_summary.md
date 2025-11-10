# AICraft Installation Plan Summary

## Overview

This document summarizes the modernized installation approach for the AICraft platform, using **uv** as the primary Python package manager instead of pip.

## Why uv Instead of pip?

### Performance Benefits
- **10-100x faster** installation times
- Built-in caching reduces redundant downloads
- Parallel dependency resolution

### Reliability
- Better dependency conflict resolution
- More reliable cross-platform behavior
- Rust-based (modern, memory-safe)

### Compatibility
- Drop-in replacement for pip
- Works with existing PyPI ecosystem
- Compatible with pyproject.toml standard

### Developer Experience
- Single tool for venv creation and package management
- Cleaner command interface
- Better error messages

## Project Structure

```
AICraft/
├── INSTALLATION.md              # Root installation guide (NEW)
├── README.md                    # Quick start (UPDATED to use uv)
│
├── backend/
│   ├── pyproject.toml          # All dependencies consolidated here
│   ├── INSTALLATION.md         # Backend-specific guide (UPDATED)
│   ├── .env.example            # Environment template
│   └── src/                    # Source code
│
└── frontend/
    ├── package.json            # Node dependencies
    └── src/                    # React components
```

## Installation Workflow

### For New Developers

**Step 1: Install uv**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2: Backend Setup**
```bash
cd backend
uv venv                      # Create virtual environment
source .venv/bin/activate    # Activate it
uv pip install -e ".[dev]"   # Install all dependencies

cp .env.example .env         # Configure environment
nano .env                    # Add ANTHROPIC_API_KEY
```

**Step 3: Frontend Setup**
```bash
cd frontend
npm install                  # Install Node dependencies
```

**Step 4: Run**
```bash
# Terminal 1 - Backend
cd backend
source .venv/bin/activate
python src/main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Step 5: Access**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Dependency Management

### Backend (Python)

**File**: `backend/pyproject.toml`

**Production dependencies** (`[project]` section):
- fastapi==0.115.6
- uvicorn[standard]==0.34.0
- anthropic==0.42.0
- python-multipart==0.0.20
- aiosqlite==0.20.0
- sqlalchemy[asyncio]==2.0.36
- greenlet==3.1.1

**Development dependencies** (`[project.optional-dependencies]` section):
- pytest==7.4.3
- pytest-asyncio==0.21.1
- pytest-cov==4.1.0
- pytest-mock==3.12.0
- httpx==0.25.2
- black==23.11.0
- isort==5.12.0
- ruff==0.1.6
- mypy==1.7.1
- pre-commit==3.5.0

**Common commands**:
```bash
# Install production only
uv pip install -e .

# Install with dev tools
uv pip install -e ".[dev]"

# Update specific package
uv pip install --upgrade fastapi

# Update all packages
uv pip install --upgrade $(uv pip list --format=freeze | cut -d= -f1)
```

### Frontend (Node.js)

**File**: `frontend/package.json`

**Production dependencies**:
- react: ^18.3.1
- react-dom: ^18.3.1

**Development dependencies**:
- @vitejs/plugin-react: ^4.7.0
- vite: ^6.0.5
- vitest: ^4.0.8
- tailwindcss: ^3.4.17
- And testing libraries (@testing-library/*)

**Common commands**:
```bash
# Install all dependencies
npm install

# Update specific package
npm update react

# Update all packages
npm update

# Check for outdated
npm outdated
```

## Testing Workflows

### Backend Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_agent_service.py

# Verbose mode
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests in watch mode
npm test

# Run with UI
npm run test:ui

# Generate coverage
npm run test:coverage
```

### Code Quality (Backend)

```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Auto-format code
black src/
isort src/

# Run all pre-commit checks
pre-commit run --all-files
```

## Environment Configuration

### Backend (.env)

Located at: `backend/.env`

Required variables:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
DATABASE_PATH=./aicraft.db
HOST=0.0.0.0
PORT=8000
```

### Frontend

No special environment configuration needed. Vite handles it automatically.

## Common Troubleshooting

### Port Conflicts

**Backend (port 8000)**:
```bash
lsof -i :8000
lsof -ti:8000 | xargs kill -9
```

**Frontend (port 5173)**:
```bash
lsof -i :5173
lsof -ti:5173 | xargs kill -9
```

### Database Issues

```bash
# Delete and recreate
rm backend/aicraft.db
python backend/src/main.py
```

### Virtual Environment Issues

```bash
# Recreate from scratch
cd backend
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Frontend Module Issues

```bash
# Clean reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Migration from pip to uv

If you were using pip before:

**Old way**:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**New way (uv)**:
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**What changed**:
- Removed `requirements.txt` and `requirements-dev.txt`
- All dependencies now in `pyproject.toml`
- Use `uv` commands instead of `pip`
- Much faster installation

**Compatibility**:
- Can still use `pip` if needed (but slower)
- All packages come from PyPI (same source)
- Virtual environments work the same

## Documentation Files

### Root Level
- **INSTALLATION.md** - Complete installation guide for full stack
- **README.md** - Project overview with quick start using uv

### Backend
- **backend/INSTALLATION.md** - Backend-specific instructions
- **backend/pyproject.toml** - Dependency definitions + tool configs
- **backend/.env.example** - Environment template

### Frontend
- **frontend/package.json** - Node dependencies
- **frontend/vite.config.js** - Build configuration

## Quick Reference

### Daily Development Commands

**Start development servers**:
```bash
# Terminal 1 - Backend
cd backend && source .venv/bin/activate && python src/main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**Run tests before commit**:
```bash
# Backend
cd backend && pytest && mypy src/

# Frontend
cd frontend && npm test
```

**Update dependencies**:
```bash
# Backend
cd backend && uv pip install --upgrade <package>

# Frontend
cd frontend && npm update <package>
```

**Code formatting**:
```bash
cd backend
black src/
isort src/
ruff check src/
```

## Key Improvements Made

1. **Consolidated dependencies**: All Python deps now in `pyproject.toml`
2. **Modernized tooling**: Using `uv` instead of `pip`
3. **Comprehensive documentation**: Root INSTALLATION.md covers everything
4. **Clear separation**: Backend vs frontend instructions
5. **Troubleshooting guide**: Common issues and solutions
6. **Standards alignment**: Follows project CLAUDE.md standards

## Next Steps

1. ✅ Dependencies consolidated to pyproject.toml
2. ✅ Installation documentation updated
3. ✅ README.md modernized with uv
4. Future: Consider adding Docker/Docker Compose support
5. Future: Add CI/CD pipeline documentation
