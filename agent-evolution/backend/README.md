# Agent Evolution Backend

Backend API for the Agent Evolution prototype, demonstrating progressive agent capabilities using Claude Agent SDK.

## Overview

This backend implements a 4-stage curriculum for understanding agent capabilities:

1. **Stage 1: Basic Reasoning** - No tools, pure reasoning (3 turns)
2. **Stage 2: Tool Awareness** - Tools defined but explain only (3 turns)
3. **Stage 3: Single Tool Execution** - Execute individual tools (5 turns)
4. **Stage 4: Multi-Tool Orchestration** - Chain multiple tools (10 turns)

## Setup

### Prerequisites
- Python 3.11 (required for claude-agent-sdk)
- Anthropic API key from https://console.anthropic.com/

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API key:**
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your ANTHROPIC_API_KEY
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

3. **Start the server:**
```bash
./start.sh
```

Or manually:
```bash
/opt/homebrew/opt/python@3.11/bin/python3.11 -m uvicorn src.api.main:app --reload --port 8001
```

## API Endpoints

### GET /
Health check endpoint
```bash
curl http://localhost:8001/
```

### GET /health
Detailed health status including API key configuration
```bash
curl http://localhost:8001/health
```

### GET /api/stages
List all available stages
```bash
curl http://localhost:8001/api/stages
```

### GET /api/stages/{stage_id}
Get detailed configuration for a specific stage (1-4)
```bash
curl http://localhost:8001/api/stages/1
```

### POST /api/chat
Send a chat message to the agent
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me?",
    "stage": 1
  }'
```

### POST /api/chat/stream
Stream chat responses using Server-Sent Events (SSE)
```bash
curl -X POST http://localhost:8001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Search for Python tutorials and save to a file",
    "stage": 4
  }'
```

### GET /api/models
Get list of available Claude models
```bash
curl http://localhost:8001/api/models
```

## Architecture

### Core Files

- **tools.py** - Tool schemas and execution functions (web_search, file_write, file_read, file_edit)
- **stages.py** - Stage configurations with system prompts and teaching points
- **agent_handler.py** - Claude Agent SDK integration following gcallm pattern
- **src/api/main.py** - FastAPI application with all endpoints

### Key Patterns

1. **Claude Agent SDK Usage** - Following the pattern from `/Users/wz/Desktop/zPersonalProjects/gcallm/gcallm/agent.py`:
   - `ClaudeSDKClient` with `ClaudeAgentOptions`
   - Async streaming with `client.query()` and `client.receive_response()`
   - Proper message handling (AssistantMessage, TextBlock, ToolUseBlock)

2. **Stage Progression**:
   - Stage 1: No tools, max_turns=3
   - Stage 2: Tools visible but not executable, max_turns=3
   - Stage 3: Single tool execution, max_turns=5
   - Stage 4: Multi-tool chaining, max_turns=10

3. **Tool Execution**:
   - Stage 2: Special handler that explains tools without executing
   - Stages 3-4: Full tool execution with proper result handling

## Testing

### Test the API
```bash
# Test stages endpoint
curl http://localhost:8001/api/stages | python3 -m json.tool

# Test stage 1 (basic reasoning - no API key needed for metadata)
curl http://localhost:8001/api/stages/1 | python3 -m json.tool

# Test chat (requires ANTHROPIC_API_KEY)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?", "stage": 1}' | python3 -m json.tool
```

### Interactive API Docs
Visit http://localhost:8001/docs for Swagger UI

## Tools Available

### web_search
Search the web for information (mock implementation)
```json
{
  "query": "search term"
}
```

### file_write
Write content to a file
```json
{
  "path": "example.txt",
  "content": "Hello, world!"
}
```

### file_read
Read the contents of a file
```json
{
  "path": "example.txt"
}
```

### file_edit
Edit a file by applying changes
```json
{
  "path": "example.txt",
  "changes": "Replace line 1 with 'Updated content'"
}
```

## Development

### Running Tests
```bash
python3.11 -m pytest tests/
```

### Code Structure
```
backend/
├── tools.py              # Tool definitions and executors
├── stages.py             # Stage configurations
├── agent_handler.py      # Claude Agent SDK wrapper
├── src/
│   ├── api/
│   │   └── main.py       # FastAPI application
│   ├── agent/            # (unused in this prototype)
│   ├── environment/      # (unused in this prototype)
│   └── models/           # (unused in this prototype)
├── requirements.txt      # Python dependencies
├── .env                  # Configuration (add your API key)
├── start.sh              # Startup script
└── README.md             # This file
```

## Troubleshooting

### Python Version Issues
This project requires Python 3.11 because claude-agent-sdk has compatibility issues with Python 3.14+.

If you see `ModuleNotFoundError: No module named 'claude_agent_sdk'`:
```bash
# Use Python 3.11 explicitly
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip install -r requirements.txt
/opt/homebrew/opt/python@3.11/bin/python3.11 -m uvicorn src.api.main:app --reload --port 8001
```

### API Key Not Working
Make sure your `.env` file has the correct format:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Port Already in Use
If port 8001 is taken, change it in start.sh or run:
```bash
/opt/homebrew/opt/python@3.11/bin/python3.11 -m uvicorn src.api.main:app --reload --port 8002
```

## Next Steps

1. Add frontend integration (frontend expects these endpoints)
2. Implement more sophisticated tool execution
3. Add conversation history/memory
4. Add user authentication
5. Deploy to production

## References

- Claude Agent SDK: https://github.com/anthropics/claude-sdk-python
- FastAPI: https://fastapi.tiangolo.com/
- Anthropic API: https://docs.anthropic.com/

## License

MIT
