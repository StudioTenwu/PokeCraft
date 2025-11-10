# Backend Installation

> **Note**: For complete installation instructions including frontend setup, see [../INSTALLATION.md](../INSTALLATION.md)

## Quick Start (Backend Only)

### Using uv (Recommended - 10-100x faster)

```bash
cd backend

# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate         # macOS/Linux
# .venv\Scripts\activate          # Windows

# Production
uv pip install -e .

# Development (with testing & linting tools)
uv pip install -e ".[dev]"
```

### Using pip (Legacy)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate

# Production
pip install -e .

# Development
pip install -e ".[dev]"
```

## Configuration

```bash
# Create environment file
cp .env.example .env

# Add your Anthropic API key
nano .env
```

## Running

```bash
# Activate environment
source .venv/bin/activate

# Start server
python src/main.py

# API runs on http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_agent_service.py
```

## Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Formatting
black src/
isort src/

# Run all checks
pre-commit run --all-files
```

## Dependencies

All dependencies are managed in `pyproject.toml`:

- **Production** (`[project]` section): FastAPI, SQLAlchemy, Anthropic SDK, etc.
- **Development** (`[project.optional-dependencies]` section): pytest, mypy, ruff, black, etc.

See the root [INSTALLATION.md](../INSTALLATION.md) for complete dependency management guide.
