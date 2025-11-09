# Agent Evolution: 4 Stages of Development

An interactive web application demonstrating the 4-stage evolution of AI agents, from simple chat to sophisticated tool-using systems. Based on [Thorsten Ball's "How to Build an Agent"](https://ampcode.com/how-to-build-an-agent).

## Overview

This application showcases how agents evolve through distinct stages:

### Stage 1: Basic Chat
- Simple conversation loop with message history
- Agent maintains context across turns
- **Key Activity**: Plan a birthday party through conversation

### Stage 2: Tool Recognition
- Agent understands available tools
- Can identify when tools would be useful
- Explains tool usage but cannot execute
- **Key Activity**: Agent recognizes need for web_search tool

### Stage 3: Tool Execution
- Agent executes tools and processes results
- Single-tool operations with feedback loops
- **Key Activity**: Search and save party ideas to a file

### Stage 4: Multi-Tool Composition
- Agent chains multiple tools intelligently
- Complex multi-step reasoning
- Autonomous task decomposition
- **Key Activity**: Research, organize, and create comprehensive party plan

## Technical Stack

### Frontend
- React 18
- Vite 5
- Tailwind CSS 4.x with @tailwindcss/postcss
- Server-Sent Events for streaming
- Port: 5190

### Backend
- FastAPI
- Anthropic SDK (Claude 3.5 Sonnet)
- python-dotenv
- Server-Sent Events streaming
- Port: 8001

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.11+
- Anthropic API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd /Users/wz/Desktop/AICraft-agent-evolution/backend
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

5. Start the backend server:
```bash
python main.py
```

Backend will run on http://localhost:8001

### Frontend Setup

1. Open a new terminal and navigate to frontend directory:
```bash
cd /Users/wz/Desktop/AICraft-agent-evolution/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

Frontend will run on http://localhost:5190

### Access the Application

Open your browser and navigate to:
```
http://localhost:5190
```

## Features

### Visual Stage Progression
- Interactive stage indicator showing evolution path
- Visual feedback for unlocked capabilities
- Stage-specific color coding

### Real-time Streaming
- Live streaming of agent responses
- Tool execution visualization
- Thinking process transparency

### Tool System
The application implements 4 tools:
- `web_search`: Search the web for information (mock implementation)
- `file_write`: Create files with content
- `file_read`: Read file contents
- `file_edit`: Modify existing files

### User Journey

1. **Start at Stage 1**: Experience basic conversation
2. **Unlock Stage 2**: See tool recognition in action
3. **Unlock Stage 3**: Watch tools execute with real results
4. **Unlock Stage 4**: Experience intelligent tool chaining

Each stage has a "Try Key Activity" button that demonstrates the stage's capabilities with a pre-configured prompt.

## Architecture

### Backend Structure
```
backend/
├── main.py          # FastAPI server and routes
├── stages.py        # Stage-specific agent logic
├── tools.py         # Tool implementations
├── requirements.txt # Python dependencies
└── .env            # Environment variables
```

### Frontend Structure
```
frontend/
├── src/
│   ├── App.jsx                    # Main application
│   ├── components/
│   │   ├── StageIndicator.jsx    # Visual stage progression
│   │   ├── AgentChat.jsx         # Chat interface
│   │   └── ToolDisplay.jsx       # Tool event visualization
│   ├── hooks/
│   │   └── useAgentStream.js     # SSE streaming hook
│   ├── main.jsx                   # App entry point
│   └── index.css                  # Global styles
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Key Implementation Details

### Streaming Architecture
- Backend uses Server-Sent Events (SSE) for real-time streaming
- Frontend consumes events via `useAgentStream` hook
- Tool execution events are streamed as they occur

### Stage Differentiation
Each stage handler inherits from `AgentStage` base class:
- Stage 1: No tools passed to Claude
- Stage 2: Tools defined but not executed
- Stage 3: Single tool execution with result processing
- Stage 4: Multi-turn tool chaining with complex reasoning

### Tool Execution Flow
1. User sends message
2. Agent analyzes and decides on tool use
3. Backend executes tool and streams events
4. Results fed back to agent
5. Agent provides final response

## Development

### Running in Development Mode

Backend:
```bash
cd backend
source venv/bin/activate
python main.py
```

Frontend:
```bash
cd frontend
npm run dev
```

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

The build output will be in `frontend/dist/`

## API Endpoints

- `GET /` - Health check
- `GET /api/stages` - Get stage information
- `GET /api/tools` - Get tool definitions
- `POST /api/chat` - Stream chat responses (SSE)

## License

MIT

## Credits

Based on the article ["How to Build an Agent"](https://ampcode.com/how-to-build-an-agent) by Thorsten Ball.
