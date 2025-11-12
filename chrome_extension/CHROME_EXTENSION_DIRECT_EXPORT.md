# Chrome Extension Direct Agent Export

## Overview

This feature allows the AICraft Companion chrome extension to fetch agents directly from the main AICraft backend server (http://localhost:8000) without needing to manually export/import JSON files.

## Implementation

### Backend Changes

**New Endpoint**: `GET /api/agents/{agent_id}/export`

Location: `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/src/main.py`

```python
@app.get("/api/agents/{agent_id}/export")
async def export_agent_for_extension(agent_id: str, req: Request):
    """Export agent in chrome extension format.

    Returns agent data compatible with AICraft Companion chrome extension.
    Includes all required fields: id, name, avatar_url, backstory, personality_traits.
    """
    agent = await req.app.state.agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Return in extension-compatible format
    return {
        "id": agent["id"],
        "name": agent["name"],
        "avatar_url": agent["avatar_url"],
        "backstory": agent["backstory"],
        "personality_traits": agent["personality_traits"],
    }
```

**Response Format**:
```json
{
  "id": "uuid",
  "name": "Agent Name",
  "avatar_url": "http://...",
  "backstory": "Agent backstory text",
  "personality_traits": ["trait1", "trait2", "trait3"]
}
```

**Error Handling**:
- Returns 404 if agent not found
- Returns only required fields for chrome extension (filters out internal fields)

### Chrome Extension Changes

**UI Update**: Added new button in extension header

Location: `/Users/wz/Desktop/zPersonalProjects/AICraft/chrome_extension/pikachu-extension/panel.html`

```html
<button id="fetch-agent-button" class="upload-button" title="Fetch agent by ID from server">
  🔗
</button>
```

**Handler Function**: `handleFetchAgentById()`

Location: `/Users/wz/Desktop/zPersonalProjects/AICraft/chrome_extension/pikachu-extension/panel.js`

```javascript
async function handleFetchAgentById() {
  // Prompt user for agent ID
  const agentId = prompt('Enter agent ID to fetch from AICraft server:');
  if (!agentId || agentId.trim() === '') {
    return;
  }

  try {
    addSystemMessage(`Fetching agent ${agentId}...`);

    // Fetch agent from main backend (port 8000)
    const response = await fetch(`http://localhost:8000/api/agents/${agentId}/export`);

    if (!response.ok) {
      if (response.status === 404) {
        addSystemMessage(`❌ Agent not found: ${agentId}`);
      } else {
        addSystemMessage(`❌ Error fetching agent: ${response.status} ${response.statusText}`);
      }
      return;
    }

    const agentData = await response.json();

    // Validate agent data schema
    const validationError = validateAgentSchema(agentData);
    if (validationError) {
      addSystemMessage(`❌ Invalid agent data: ${validationError}`);
      console.error('Validation error:', validationError);
      return;
    }

    // Check for duplicate agent ID
    if (allAgents[agentData.id]) {
      const overwrite = confirm(`Agent "${agentData.name}" (ID: ${agentData.id}) already exists. Overwrite?`);
      if (!overwrite) {
        addSystemMessage('Fetch cancelled.');
        return;
      }
    }

    // Add to agents
    allAgents[agentData.id] = agentData;
    allChatHistories[agentData.id] = allChatHistories[agentData.id] || [];

    // Save to storage
    await chrome.storage.local.set({
      agents: allAgents,
      chatHistories: allChatHistories
    });

    // Switch to new agent
    await handleAgentSwitch(agentData.id);

    // Rebuild dropdown
    buildAgentDropdown();

    addSystemMessage(`✓ Fetched agent: ${agentData.name}!`);
  } catch (error) {
    console.error('Error fetching agent by ID:', error);
    addSystemMessage('❌ Error connecting to AICraft server. Make sure the server is running on http://localhost:8000');
  }
}
```

**Event Listener**: Added in `initPanel()`

```javascript
const fetchAgentButton = document.getElementById('fetch-agent-button');
fetchAgentButton.addEventListener('click', handleFetchAgentById);
```

## Usage

### Step 1: Start AICraft Backend

```bash
cd backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Create an Agent

Via frontend or API:

```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Squirtle",
    "backstory": "I am a Water-type Pokemon!",
    "personality_traits": ["playful", "loyal", "brave"],
    "avatar_url": "http://localhost:8000/static/squirtle.png"
  }'
```

Response:
```json
{
  "id": "29bb747e-186b-4c1c-a5b4-40b1d4277b0f",
  "name": "Squirtle",
  ...
}
```

### Step 3: Open Chrome Extension

1. Open Chrome extension (side panel)
2. Click the 🔗 button
3. Enter agent ID: `29bb747e-186b-4c1c-a5b4-40b1d4277b0f`
4. Agent loads automatically!

## Security Considerations

### CORS

The chrome extension has host permissions for `http://localhost:8000/*`:

```json
{
  "host_permissions": [
    "http://localhost:8000/*",
    "http://localhost:8080/*"
  ]
}
```

This allows the extension to make HTTP requests to localhost without CORS restrictions.

### Production Considerations

For production deployment:

1. **Authentication**: Add API key or OAuth authentication
2. **HTTPS**: Use HTTPS for all requests
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Input Validation**: Already implemented (validates agent ID format)

## Testing

### Unit Tests

Location: `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/tests/unit/test_agent_export.py`

```bash
cd backend
uv run pytest tests/unit/test_agent_export.py -v
```

Tests:
- ✅ `test_export_agent_success` - Successful export
- ✅ `test_export_agent_not_found` - 404 handling
- ✅ `test_export_agent_only_includes_required_fields` - Field filtering

### Integration Test

```bash
python3 /tmp/test_chrome_extension_flow.py
```

Tests:
- ✅ Create agent via API
- ✅ Export agent via `/export` endpoint
- ✅ Verify export format matches extension schema
- ✅ Test 404 handling

## Documentation Updates

### README.md

Added section documenting three agent loading methods:

1. **Fetch from AICraft Server (🔗 button)** - NEW!
2. **Auto-Load from Backend Server (📥 button)** - Existing
3. **Manual JSON Import (📂 button)** - Existing

Location: `/Users/wz/Desktop/zPersonalProjects/AICraft/chrome_extension/README.md`

## API Endpoints Summary

### Main Backend (Port 8000)

```
GET  /api/agents/{agent_id}         - Get full agent details
GET  /api/agents/{agent_id}/export  - Export agent for extension (NEW)
POST /api/agents                     - Create agent from data
POST /api/agents/create              - Create agent from description (LLM)
```

### Extension Backend (Port 8080)

```
GET  /agents/pending                 - Get pending agents for auto-load
POST /chat                           - Chat with agent
```

## Benefits

### Before

1. Create agent in AICraft
2. Copy agent JSON manually
3. Save to file
4. Upload file to extension

### After

1. Create agent in AICraft
2. Copy agent ID
3. Click 🔗 button in extension
4. Done!

## Future Enhancements

1. **List Agents**: Add endpoint to list all available agents
2. **Search**: Add search functionality for agents by name
3. **Auto-Sync**: Automatically sync new agents to extension
4. **Multi-Select**: Allow importing multiple agents at once
5. **Agent Updates**: Support updating existing agents from server

## Files Changed

1. `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/src/main.py` - Added export endpoint
2. `/Users/wz/Desktop/zPersonalProjects/AICraft/chrome_extension/pikachu-extension/panel.html` - Added 🔗 button
3. `/Users/wz/Desktop/zPersonalProjects/AICraft/chrome_extension/pikachu-extension/panel.js` - Added handler function
4. `/Users/wz/Desktop/zPersonalProjects/AICraft/chrome_extension/README.md` - Updated documentation
5. `/Users/wz/Desktop/zPersonalProjects/AICraft/backend/tests/unit/test_agent_export.py` - Added unit tests

## Commit Message

```
feat(extension): Add direct agent export from main backend

- Add GET /api/agents/{id}/export endpoint in main.py
- Export returns extension-compatible JSON format
- Add 🔗 button to chrome extension UI
- Implement handleFetchAgentById() to fetch from port 8000
- Add comprehensive error handling (404, network errors)
- Add unit tests for export endpoint (3 tests)
- Update chrome_extension/README.md with usage docs
- All tests passing (unit, integration)
```
