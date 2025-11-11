# 🤖 AICraft Extension Backend with Claude Agent SDK

This backend server provides **real Claude AI responses** for the AICraft Chrome extension using the Claude Agent SDK.

## ✨ Features

- ⚡ Real-time AI chat using Claude Agent SDK
- 🎭 In-character responses based on agent personality
- 🔌 Simple REST API (single `/chat` endpoint)
- 🌐 CORS enabled for Chrome extension
- 💾 No database required
- 🚀 Lightweight and fast

## 📋 Requirements

- Python 3.11+
- Claude Code CLI installed and configured
- `claude-agent-sdk` package
- `fastapi` and `uvicorn`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install claude-agent-sdk fastapi uvicorn
```

### 2. Start the Backend Server

```bash
python backend_server.py
```

You should see:
```
🎮 Starting AICraft Extension Backend Server...
📡 Extension can connect to: http://localhost:8080/chat
💡 Press Ctrl+C to stop

INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 3. Load the Chrome Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `pikachu-extension` folder
5. Click the extension icon and start chatting!

## 🧪 Testing the Backend

Test with curl:

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Who are you?",
    "agent_data": {
      "name": "Pikachu",
      "backstory": "I am Pikachu, an Electric-type Pokémon!",
      "personality_traits": ["energetic", "loyal", "friendly"]
    }
  }'
```

Expected response:
```json
{
  "response": "Pika pika! ⚡ I'm Pikachu, an Electric-type Pokémon..."
}
```

## 📡 API Documentation

### POST `/chat`

Send a chat message and get an AI response.

**Request Body:**
```json
{
  "message": "Hello!",
  "agent_data": {
    "name": "Pikachu",
    "backstory": "I am Pikachu, an Electric-type Pokémon...",
    "personality_traits": ["energetic", "loyal", "brave"]
  }
}
```

**Response:**
```json
{
  "response": "Pika pika! I'm Pikachu..."
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "AICraft Extension Backend"
}
```

## 🎮 How It Works

1. **Chrome extension** sends user message to `http://localhost:8080/chat`
2. **Backend** builds a system prompt from agent backstory + personality
3. **Claude Agent SDK** generates an in-character response
4. **Response** is sent back to the extension and displayed

## 🔧 Configuration

The backend runs on **port 8080** by default. To change:

```python
# In backend_server.py
uvicorn.run(app, host="0.0.0.0", port=8080)  # Change port here
```

Then update the extension's `chat.js`:

```javascript
// In chat.js
const response = await fetch('http://localhost:8080/chat', {  // Update port
```

## 🐛 Troubleshooting

### "Claude Agent SDK not installed"

```bash
pip install claude-agent-sdk
```

### "Connection refused"

Make sure the backend server is running:
```bash
python backend_server.py
```

### "Control request timeout"

The Claude Code CLI might not be configured properly. Check:
```bash
which claude
claude --version
```

### Extension shows mock responses

The extension **automatically falls back to mock responses** if the backend is not available. This is by design! Check:

1. Backend server is running on port 8080
2. No firewall blocking localhost:8080
3. Check browser console (F12) for connection errors

## 💡 Tips

- **Keep the server running** while using the extension
- Extension works **offline with mock responses** if server is down
- Server logs show each chat request in real-time
- Use Ctrl+C to stop the server

## 🎨 Customization

### Change AI Model

Edit `backend_server.py`:

```python
options = ClaudeAgentOptions(
    system_prompt=system_prompt,
    model="claude-3-5-sonnet-20241022",  # Add this line
    permission_mode='bypassPermissions',
    max_turns=1,
)
```

### Adjust Response Length

Edit the system prompt in `backend_server.py`:

```python
system_prompt = f"""...
You are {request.agent_data.name}. Respond in character,
keeping your responses concise and friendly (1 sentence max)."""  # Changed from 2-3
```

## 📦 Project Structure

```
chrome_extension/
├── backend_server.py          # ← Backend server (this file)
├── pikachu-extension/         # Chrome extension
│   ├── chat.js                # Calls backend (port 8080)
│   ├── panel.html
│   ├── styles.css             # Yellow Pikachu theme
│   └── ...
└── BACKEND_README.md          # This file
```

## 🚀 Production Deployment

For production, consider:

1. **Use environment variables** for configuration
2. **Add authentication** (API keys, OAuth)
3. **Rate limiting** to prevent abuse
4. **Deploy to cloud** (Railway, Render, Fly.io)
5. **Use HTTPS** for security
6. **Add logging** and monitoring

## 📝 License

Part of the AICraft project.
