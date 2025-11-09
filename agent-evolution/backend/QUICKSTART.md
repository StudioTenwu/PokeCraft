# Quick Start Guide

## 1-Minute Setup

### Step 1: Add API Key
```bash
cd /Users/wz/Desktop/zPersonalProjects/AICraft-agent-evolution/backend
```

Edit `.env` and replace `sk-ant-YOUR-KEY-HERE` with your actual Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Get your key from: https://console.anthropic.com/

### Step 2: Start the Server
```bash
./start.sh
```

That's it! The server is now running on http://localhost:8001

### Step 3: Test It
```bash
# In another terminal
./test_api.sh
```

Or visit http://localhost:8001/docs for interactive API documentation.

## Quick Test with curl

### Test Stage 1 (Basic Reasoning)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?", "stage": 1}'
```

### Test Stage 4 (Multi-Tool)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search for Python tutorials and save the results to a file named tutorials.txt", "stage": 4}'
```

## The 4 Stages

1. **Stage 1** - Pure reasoning, no tools (3 turns)
2. **Stage 2** - Explain tools without executing (3 turns)
3. **Stage 3** - Execute single tools (5 turns)
4. **Stage 4** - Chain multiple tools together (10 turns)

## Troubleshooting

**Python version error?**
- This requires Python 3.11 (not 3.14+)
- The start.sh script handles this automatically

**Port already in use?**
- Change port in start.sh: `--port 8002`

**API key not working?**
- Check .env file format
- No quotes around the key
- No spaces

## What's Working

All endpoints are functional:
- `/api/stages` - List stages ✓
- `/api/stages/{id}` - Stage details ✓
- `/api/chat` - Chat with agent ✓
- `/api/chat/stream` - Streaming chat ✓
- `/health` - Health check ✓
- `/api/models` - List models ✓

Backend is ready for frontend integration!
