# AICraft - Agent Evolution Platform

Interactive demonstration of how AI agents evolve from simple chat to sophisticated tool-using systems.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Anthropic API Key ([Get one here](https://console.anthropic.com/settings/keys))

### Setup

1. **Add your API key:**
   ```bash
   # Edit agent-evolution/backend/.env
   nano agent-evolution/backend/.env
   # Add: ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

2. **Start the backend:**
   ```bash
   cd agent-evolution/backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Start the frontend:**
   ```bash
   cd agent-evolution/frontend
   npm install
   npm run dev
   ```

4. **Open the app:**
   Visit [http://localhost:5190](http://localhost:5190)

## 📚 The 4 Stages of Agent Evolution

### Stage 1: Basic Chat
- Simple conversation loop with message history
- No tool access
- **Try it:** "Help me plan a birthday party"

### Stage 2: Tool Recognition
- Agent understands available tools
- Can identify when tools would be useful
- Cannot execute tools yet
- **Try it:** "Search the web for party ideas"

### Stage 3: Tool Execution
- Agent can execute tools and process results
- Single tool use per turn
- **Try it:** "Find party ideas and save them to a file"

### Stage 4: Multi-Tool Composition
- Agent chains multiple tools intelligently
- Complex multi-step reasoning
- **Try it:** "Research party ideas, create a comprehensive plan, and organize it"

## 🏗️ Architecture

```
agent-evolution/
├── frontend/          # React + Vite app (port 5190)
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentChat.jsx      # Main chat interface
│   │   │   ├── StageIndicator.jsx # Stage progression UI
│   │   │   └── ToolDisplay.jsx     # Tool execution visualization
│   │   ├── hooks/
│   │   │   └── useAgentStream.js  # SSE streaming hook
│   │   └── App.jsx
│   └── package.json
│
└── backend/           # FastAPI + Claude SDK (port 8001)
    ├── main.py        # API server with SSE endpoints
    ├── stages.py      # 4-stage agent implementations
    ├── tools.py       # Tool definitions and execution
    ├── requirements.txt
    └── .env           # API keys
```

## 🛠️ Technologies

**Frontend:**
- React 18
- Vite 5
- Tailwind CSS 4
- Server-Sent Events (SSE) for streaming

**Backend:**
- FastAPI
- Anthropic Python SDK (AsyncAnthropic)
- Claude 3.5 Sonnet
- Tool execution framework

## ⚙️ API Endpoints

- `GET /api/stages` - Get all stage information
- `GET /api/tools` - Get available tool definitions
- `POST /api/chat` - Stream chat responses (SSE)

## 🔧 How It Works

### Claude Agents SDK Integration

The backend uses the official Anthropic Python SDK with proper async streaming:

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=api_key)

async with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    system=system_message,
    messages=messages,
    tools=TOOL_DEFINITIONS  # Stage-dependent
) as stream:
    async for text in stream.text_stream:
        yield text
```

### Stage-Specific Behavior

Each stage modifies:
1. **System prompt** - Instructions about capabilities
2. **Tool availability** - Which tools are provided to Claude
3. **Tool execution** - Whether tools are actually executed
4. **Agentic loops** - How many tool-use turns are allowed

### Tool Execution

Tools are defined using Claude's tool schema and executed with proper error handling:

```python
{
    "name": "web_search",
    "description": "Search the web for information",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
}
```

## 📝 Adding New Tools

1. Define tool in `backend/tools.py`:
```python
TOOL_DEFINITIONS.append({
    "name": "your_tool",
    "description": "What it does",
    "input_schema": { ... }
})
```

2. Implement execution in `ToolExecutor`:
```python
async def execute(self, tool_name: str, tool_input: dict):
    if tool_name == "your_tool":
        return await self._your_tool(tool_input)
```

## 🎯 Educational Goals

This project demonstrates:
- How AI agents evolve from simple to complex
- Progressive capability unlocking
- Tool recognition vs. execution
- Multi-step agentic reasoning
- Real-time streaming UX

## 🐛 Troubleshooting

**Chat not working?**
- Check that `ANTHROPIC_API_KEY` is set in `backend/.env`
- Verify backend is running on port 8001
- Check browser console for errors

**Backend won't start?**
```bash
# Check if port 8001 is in use
lsof -i :8001

# Kill existing process
lsof -ti:8001 | xargs kill -9
```

**Frontend won't connect?**
- Ensure backend is running first
- Check CORS settings in `backend/main.py`
- Verify fetch URLs in frontend code

## 📜 License

MIT

## 🙏 Credits

Based on ["How to Build an Agent" by Thorsten Ball](https://thorstenball.com/)

Built with [Claude](https://claude.ai) and the [Anthropic API](https://docs.anthropic.com/)
