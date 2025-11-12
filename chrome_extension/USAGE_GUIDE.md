# Chrome Extension Usage Guide

## Quick Start: Fetch Agent from AICraft Server

### Prerequisites

1. **AICraft Backend Running**
   ```bash
   cd backend
   uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Chrome Extension Installed**
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `chrome_extension/pikachu-extension/` folder

### Step-by-Step: Fetch Agent

#### 1. Create Agent in AICraft

**Option A: Via Frontend**
- Open http://localhost:3000
- Click "Create Agent"
- Fill in agent details
- Copy the agent ID from the created agent

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Charmander",
    "backstory": "I am a Fire-type Pokemon. My tail flame represents my life force!",
    "personality_traits": ["brave", "energetic", "competitive"],
    "avatar_url": "http://localhost:8000/static/charmander.png"
  }'
```

Response:
```json
{
  "id": "29bb747e-186b-4c1c-a5b4-40b1d4277b0f",
  "name": "Charmander",
  ...
}
```

**Copy the ID**: `29bb747e-186b-4c1c-a5b4-40b1d4277b0f`

#### 2. Open Chrome Extension

1. Click the AICraft Companion extension icon in Chrome toolbar
2. Side panel opens with current agent

#### 3. Fetch New Agent

1. **Click the 🔗 button** in the extension header
   - This is the "Fetch agent by ID from server" button
   - Located next to the 📥 and 📂 buttons

2. **Enter Agent ID** when prompted
   - Paste the agent ID: `29bb747e-186b-4c1c-a5b4-40b1d4277b0f`
   - Click OK

3. **Agent Loads Automatically**
   - Extension fetches agent from server
   - Agent appears in dropdown
   - Extension switches to the new agent
   - Success message appears: "✓ Fetched agent: Charmander!"

#### 4. Start Chatting!

- Type a message in the input field
- Press Enter or click "Send"
- Agent responds based on their personality

## Three Ways to Load Agents

### Method 1: Fetch from Server (🔗 button) - RECOMMENDED

**Best for**: Quick loading of agents you created in AICraft

**Steps**:
1. Click 🔗 button
2. Enter agent ID
3. Done!

**Pros**:
- Fastest method
- No file management
- Always gets latest agent data

**Cons**:
- Requires server running
- Need to copy agent ID

### Method 2: Auto-Load (📥 button)

**Best for**: Loading multiple agents at once

**Steps**:
1. Click 📥 button
2. Extension checks for new agents
3. Loads all pending agents automatically

**Pros**:
- Loads multiple agents
- No manual ID entry

**Cons**:
- Requires separate backend_server.py running on port 8080
- More complex setup

### Method 3: Manual JSON Import (📂 button)

**Best for**: Offline testing, custom agents, sharing

**Steps**:
1. Export agent JSON file from AICraft
2. Click 📂 button in extension
3. Select JSON file
4. Agent loads

**Pros**:
- Works offline
- Can share agent files
- No server required

**Cons**:
- Manual file management
- Extra steps

## Troubleshooting

### "Error connecting to AICraft server"

**Problem**: Extension can't reach backend server

**Solutions**:
1. Check server is running:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. Check server port:
   - Main backend: http://localhost:8000
   - Extension backend: http://localhost:8080

3. Check extension permissions:
   - Open `chrome://extensions/`
   - Find AICraft Companion
   - Check "host_permissions" includes `http://localhost:8000/*`

### "Agent not found"

**Problem**: Agent ID doesn't exist in database

**Solutions**:
1. Verify agent ID is correct
2. Check agent exists:
   ```bash
   curl http://localhost:8000/api/agents/{agent_id}
   ```
3. Create agent first if needed

### "Invalid agent data"

**Problem**: Agent data missing required fields

**Required Fields**:
- `id` (string, non-empty)
- `name` (string, non-empty)
- `avatar_url` (string, non-empty)
- `backstory` (string, non-empty)
- `personality_traits` (array of strings, at least one)

**Solution**: Ensure agent was created with all required fields

### Agent Already Exists

**Problem**: Agent ID already in extension storage

**Solution**: Extension will ask if you want to overwrite
- Click "OK" to replace existing agent
- Click "Cancel" to keep current agent

## API Reference

### Export Endpoint

```
GET /api/agents/{agent_id}/export
```

**Response**:
```json
{
  "id": "uuid",
  "name": "string",
  "avatar_url": "string",
  "backstory": "string",
  "personality_traits": ["string", "string", ...]
}
```

**Status Codes**:
- `200` - Success
- `404` - Agent not found
- `500` - Server error

### Example Request

```bash
curl http://localhost:8000/api/agents/29bb747e-186b-4c1c-a5b4-40b1d4277b0f/export
```

## Tips & Best Practices

### Organizing Agents

1. **Create themed agents**: Water-type, Fire-type, Electric-type Pokemon
2. **Use descriptive names**: "Pikachu - Electric", "Squirtle - Water"
3. **Save agent IDs**: Keep a list of your favorite agent IDs

### Managing Chat History

- Each agent has separate chat history
- Clear history with 🗑️ button (per-agent)
- Switch agents with dropdown (preserves history)

### Testing Agents

1. Create agent in AICraft
2. Load in extension
3. Test conversation
4. Iterate on personality traits
5. Re-fetch updated agent

## Advanced Usage

### Bulk Import Multiple Agents

**Option 1: API Script**
```python
import requests

agents = [
    {"name": "Pikachu", "backstory": "...", ...},
    {"name": "Charmander", "backstory": "...", ...},
    {"name": "Squirtle", "backstory": "...", ...},
]

for agent_data in agents:
    response = requests.post("http://localhost:8000/api/agents", json=agent_data)
    agent = response.json()
    print(f"Created: {agent['name']} (ID: {agent['id']})")
```

**Option 2: JSON Files**
1. Create multiple JSON files
2. Import each via 📂 button
3. Or use auto-load via 📥 button

### Sharing Agents

**Export for Sharing**:
```bash
# Export agent to file
curl http://localhost:8000/api/agents/{agent_id}/export > charmander.json

# Share file with others
# They import via 📂 button
```

### Custom Avatars

1. Host image file in `/backend/static/`
2. Set `avatar_url`: `http://localhost:8000/static/my-avatar.png`
3. Or use data URI for inline images

## What's Next?

### Future Features

1. **List All Agents**: Browse all available agents
2. **Search Agents**: Find agents by name or traits
3. **Auto-Sync**: Real-time sync with backend
4. **Agent Updates**: Update existing agents from server
5. **Multi-Select**: Import multiple agents at once

### Feedback & Issues

Found a bug? Have suggestions?
- Check `/chrome_extension/TEST_CHECKLIST.md`
- File issues in project repository
- Contribute improvements!

---

**Happy chatting with your AICraft companions!** ⚡🔥💧
