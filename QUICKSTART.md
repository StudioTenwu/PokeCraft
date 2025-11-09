# Quick Start Guide

Get the Agent Engineering Playground running locally in 5 minutes.

## Current Implementation Status

✅ **Fully Implemented**:
- Backend API with Grid World engine, 8 tools, Levels 1-2
- ReAct agent executor with Google Gemini integration
- Frontend with Canvas grid renderer, agent config UI, reasoning trace
- Real-time WebSocket execution
- Complete data flow from UI → API → LLM → Grid → UI

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- **Google Gemini API key** (MVP currently supports Gemini only)
  - Get your key at [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Place it at `~/.gemini/apikey.txt`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/WarrenZhu050413/AICraft.git
cd AICraft
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add at least one API key:
# ANTHROPIC_API_KEY=your_anthropic_key_here
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_API_KEY=your_google_gemini_key_here
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

## Running the Application

Open two terminal windows:

### Terminal 1: Start Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Important: Set PYTHONPATH so imports work correctly
PYTHONPATH=./src uvicorn src.api.main:app --reload --port 8000
```

Backend will run at `http://localhost:8000`

**Note**: The backend is currently running and serving at http://localhost:8000!

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will run at `http://localhost:5173`

## Verify Installation

1. Open `http://localhost:5173` in your browser
2. You should see the Agent Engineering Playground homepage
3. Backend health check: `http://localhost:8000/health`

## Next Steps

- Read the [full README](README.md) for project overview
- Check out [PROJECT_PHILOSOPHY.md](docs/PROJECT_PHILOSOPHY.md) to understand our approach
- See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute

## Troubleshooting

### Backend won't start
- Verify Python version: `python --version` (should be 3.10+)
- Check if port 8000 is available
- Ensure API key is correctly set in `.env`

### Frontend won't start
- Verify Node version: `node --version` (should be 18+)
- Try deleting `node_modules` and run `npm install` again
- Check if port 5173 is available

### API Connection Issues
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify `.env` file exists and has valid API keys

## Development Mode Features

- **Hot Reload**: Both frontend and backend auto-reload on code changes
- **API Docs**: Visit `http://localhost:8000/docs` for interactive API documentation
- **Error Messages**: Detailed error traces in terminal

---

**Ready to learn agent engineering?** Visit http://localhost:5173 and start with Level 1!
