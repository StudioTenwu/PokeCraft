# Agent Evolution - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                     http://localhost:5190                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP + SSE
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    React Frontend (Vite)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ App.jsx                                                  │  │
│  │  ├─ StageIndicator.jsx (visual progression)             │  │
│  │  ├─ AgentChat.jsx (chat interface)                      │  │
│  │  └─ ToolDisplay.jsx (tool event visualization)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ useAgentStream Hook                                      │  │
│  │  - SSE stream reader                                     │  │
│  │  - Event parsing                                         │  │
│  │  - State management                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ POST /api/chat
                             │ GET /api/stages
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend (Port 8001)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ main.py - FastAPI Application                           │  │
│  │  ├─ CORS middleware                                      │  │
│  │  ├─ GET / (health)                                       │  │
│  │  ├─ GET /api/stages                                      │  │
│  │  ├─ GET /api/tools                                       │  │
│  │  └─ POST /api/chat (SSE streaming)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│  ┌──────────────────────────▼────────────────────────────────┐ │
│  │ stages.py - Stage Handlers                               │ │
│  │  ├─ Stage1BasicChat (no tools)                           │ │
│  │  ├─ Stage2ToolRecognition (tools visible)                │ │
│  │  ├─ Stage3ToolExecution (single tools)                   │ │
│  │  └─ Stage4MultiTool (tool chaining)                      │ │
│  └──────────────────────────┬────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼────────────────────────────────┐ │
│  │ tools.py - Tool System                                    │ │
│  │  ├─ ToolExecutor class                                    │ │
│  │  ├─ TOOL_DEFINITIONS (schemas)                            │ │
│  │  └─ Tool implementations:                                 │ │
│  │     ├─ web_search (mock)                                  │ │
│  │     ├─ file_write                                         │ │
│  │     ├─ file_read                                          │ │
│  │     └─ file_edit                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Anthropic API calls
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   Anthropic API (Claude)                        │
│                 claude-3-5-sonnet-20241022                      │
│                                                                 │
│  - Streaming responses                                          │
│  - Tool use detection                                           │
│  - Multi-turn conversations                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Stage 1: Basic Chat Flow

```
User Input
    │
    ▼
Frontend (AgentChat)
    │
    ├─ Add to messages array
    │
    ▼
POST /api/chat {messages, stage: 1}
    │
    ▼
Backend (Stage1BasicChat)
    │
    ├─ Create system message (no tool context)
    │
    ▼
Anthropic API (stream mode, NO tools parameter)
    │
    ├─ Generate response
    │
    ▼
SSE Stream: data: {"type": "text", "content": "..."}
    │
    ▼
Frontend (useAgentStream)
    │
    ├─ Parse events
    ├─ Update currentMessage state
    │
    ▼
Display in chat UI (gray bubble)
```

### Stage 2: Tool Recognition Flow

```
User Input: "Search the web for party ideas"
    │
    ▼
Frontend (AgentChat)
    │
    ▼
POST /api/chat {messages, stage: 2}
    │
    ▼
Backend (Stage2ToolRecognition)
    │
    ├─ Create system message (tool awareness context)
    ├─ Pass TOOL_DEFINITIONS to Claude
    │
    ▼
Anthropic API (stream mode, WITH tools parameter)
    │
    ├─ Receive tool_use content block
    ├─ BUT: Don't execute, just recognize
    │
    ▼
SSE Stream:
    data: {"type": "tool_recognition", "tool_name": "web_search", "tool_input": {...}}
    data: {"type": "text", "content": "I would use web_search..."}
    │
    ▼
Frontend (useAgentStream)
    │
    ├─ toolEvents state updated
    │
    ▼
Display: Yellow "Tool Recognized" card + Agent explanation
```

### Stage 3: Tool Execution Flow

```
User Input: "Search for ideas and save to file"
    │
    ▼
Frontend (AgentChat)
    │
    ▼
POST /api/chat {messages, stage: 3}
    │
    ▼
Backend (Stage3ToolExecution)
    │
    ├─ Turn 1: Initial request
    │
    ▼
Anthropic API → tool_use block: web_search
    │
    ▼
SSE: {"type": "tool_use_start", "tool_name": "web_search"}
    │
    ▼
Backend: ToolExecutor.execute("web_search", {query: "..."})
    │
    ├─ Mock search returns results
    │
    ▼
SSE: {"type": "tool_executing", ...}
SSE: {"type": "tool_result", "result": {...}}
    │
    ▼
Backend: Add tool result to messages
    │
    ├─ Turn 2: Process results
    │
    ▼
Anthropic API → tool_use block: file_write
    │
    ▼
Backend: ToolExecutor.execute("file_write", {filename: "party_ideas.txt", ...})
    │
    ├─ Write to /tmp/agent_workspace/party_ideas.txt
    │
    ▼
SSE: {"type": "tool_result", "result": {"success": true, ...}}
    │
    ▼
Backend: Add to messages again
    │
    ├─ Turn 3: Final response
    │
    ▼
Anthropic API → text response (no tools)
    │
    ▼
SSE: {"type": "text", "content": "I've saved the ideas..."}
SSE: {"type": "done"}
    │
    ▼
Frontend: Display all tool events + final message
```

### Stage 4: Multi-Tool Chaining Flow

```
User Input: "Research, create, and organize party plan"
    │
    ▼
POST /api/chat {messages, stage: 4}
    │
    ▼
Backend (Stage4MultiTool) - up to 10 turns allowed
    │
    ├─ Turn 1: Planning
    ▼
Claude decides: "I'll search first"
→ tool_use: web_search
    │
    ▼
Execute → SSE events → Add result to messages
    │
    ├─ Turn 2: Initial creation
    ▼
Claude decides: "Now create file with results"
→ tool_use: file_write
    │
    ▼
Execute → SSE events → Add result to messages
    │
    ├─ Turn 3: Enhancement
    ▼
Claude decides: "Organize into sections"
→ tool_use: file_edit
    │
    ▼
Execute → SSE events → Add result to messages
    │
    ├─ Turn 4: Final response
    ▼
Claude: "I've created a comprehensive plan..."
→ text content (no tools)
    │
    ▼
SSE: {"type": "done"}
    │
    ▼
Frontend: Display complete chain of:
    - Blue "Tool Starting" cards (3x)
    - Purple "Executing" cards (3x)
    - Green "Result" cards (3x)
    - Final agent response
```

## Event Types (SSE)

### Text Event
```json
{
  "type": "text",
  "content": "Hello! I can help with that."
}
```

### Tool Recognition (Stage 2 only)
```json
{
  "type": "tool_recognition",
  "tool_name": "web_search",
  "tool_input": {"query": "party ideas"}
}
```

### Tool Use Start (Stages 3-4)
```json
{
  "type": "tool_use_start",
  "tool_name": "web_search",
  "tool_id": "toolu_abc123"
}
```

### Tool Executing (Stages 3-4)
```json
{
  "type": "tool_executing",
  "tool_name": "web_search",
  "tool_input": {"query": "birthday party ideas"}
}
```

### Tool Result (Stages 3-4)
```json
{
  "type": "tool_result",
  "tool_name": "web_search",
  "result": {
    "query": "birthday party ideas",
    "results": [...],
    "count": 3
  }
}
```

### Error Event
```json
{
  "type": "error",
  "error": "API key not configured"
}
```

### Done Event
```json
{
  "type": "done"
}
```

## State Management

### Frontend State

```javascript
// App.jsx
const [currentStage, setCurrentStage] = useState(1)  // 1-4
const [stages, setStages] = useState([])             // Stage info from API

// AgentChat.jsx
const [messages, setMessages] = useState([])         // Chat history
const [inputValue, setInputValue] = useState('')    // Current input

// useAgentStream hook
const [isStreaming, setIsStreaming] = useState(false)
const [currentMessage, setCurrentMessage] = useState('')  // Streaming text
const [toolEvents, setToolEvents] = useState([])          // Tool event array
```

### Backend State

```python
# Per request (no persistent state)
current_messages = messages.copy()  # Working copy of conversation

# Multi-turn loop (Stages 3-4)
for turn in range(max_turns):
    # Call Claude
    message = await stream.get_final_message()

    # If tool_use blocks present:
    current_messages.append(assistant_message)

    # Execute tools
    tool_results = await execute_tools()

    # Add results
    current_messages.append({"role": "user", "content": tool_results})

    # Continue loop → Claude processes results → decides next action
```

## Component Hierarchy

```
App
├── StageIndicator
│   ├── Stage circles (4x)
│   ├── Connection lines (3x)
│   ├── Capability badges (per stage)
│   └── Unlock button
│
├── AgentChat
│   ├── Header with key activity button
│   ├── Message list
│   │   ├── User messages (blue)
│   │   ├── Agent messages (gray)
│   │   │   └── ToolDisplay (nested)
│   │   └── Streaming message
│   │       └── ToolDisplay (nested)
│   └── Input area
│
└── Stage details panel
    ├── Description
    ├── Capabilities list
    └── Key activity card
```

## Key Design Decisions

### Why SSE over WebSockets?
- Simpler server implementation (no connection management)
- One-way communication sufficient (server → client)
- Built-in reconnection in browsers
- Better for streaming LLM responses

### Why Separate Stage Handlers?
- Clear separation of concerns
- Easy to understand differences between stages
- Prevents accidental tool execution in early stages
- Demonstrates progressive enhancement

### Why Mock web_search?
- No external API dependencies
- Faster response times
- Consistent demo experience
- Easy to extend with real API (Exa, Brave, etc.)

### Why Tool Events Array?
- Preserves chronological order
- Enables replay/debugging
- Visual feedback for each step
- Clear demonstration of tool chaining

## Extension Points

### Adding New Tools
1. Add to `tools.py`:
   - Method in `ToolExecutor` class
   - Definition in `TOOL_DEFINITIONS`
2. Tool automatically available to all stages 2-4

### Adding New Stages
1. Create handler class in `stages.py` (inherit `AgentStage`)
2. Add to `get_stage_handler()` mapping
3. Add stage info to `/api/stages` endpoint
4. Update frontend max stage logic

### Replacing Mock web_search
```python
# In tools.py
async def web_search(self, query: str) -> Dict[str, Any]:
    # Replace with real API:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.exa.ai/search",
            json={"query": query},
            headers={"Authorization": f"Bearer {EXA_API_KEY}"}
        )
        return response.json()
```

### Adding Authentication
```python
# In main.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/chat")
async def chat(request: ChatRequest, token: str = Depends(security)):
    # Verify token
    # ...
```

## Performance Considerations

### Current Limits
- Max tokens: 2048 per response
- Max turns Stage 3: 5
- Max turns Stage 4: 10
- Workspace: /tmp (cleaned on reboot)

### Optimization Opportunities
- Cache tool results (same query)
- Batch file operations
- Parallel tool execution where possible
- Stream compression for large tool results

## Security Notes

### Current Implementation
- API key in .env file (not in version control)
- CORS limited to localhost
- File operations restricted to /tmp/agent_workspace
- No user authentication (single-user demo)

### Production Considerations
- User authentication required
- API key per user or rate limiting
- Workspace per user with quotas
- Input validation on all tool parameters
- Sandboxed code execution if adding code tools
