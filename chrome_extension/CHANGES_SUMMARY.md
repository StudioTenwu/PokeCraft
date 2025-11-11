# Chrome Extension Multi-Agent Feature Implementation

## Overview

This document summarizes the implementation of three major features for the AICraft Chrome Extension:
1. **Multi-Pokemon Selector** - Allow users to switch between multiple Pokemon agents
2. **Agent Export/Load System** - Export agents from AICraft and load them directly into the extension
3. **JSON File Import** - Import agents from JSON files with schema validation

## Changes Made

### 1. Multi-Pokemon Selector Feature

#### Backend Template Files

**File: `backend/extension_templates/panel.html`**
- Added agent selector dropdown component in header
- Added load agents button for importing new agents
- Structure:
  ```html
  <!-- Agent Selector Dropdown -->
  <div class="agent-selector-container">
    <div id="agent-selector" class="agent-selector">
      <span id="current-agent-name" class="current-agent-name">{{AGENT_NAME}}</span>
      <span class="dropdown-arrow">▼</span>
    </div>
    <div id="agent-dropdown" class="agent-dropdown hidden">
      <!-- Populated dynamically by panel.js -->
    </div>
  </div>

  <button id="load-agents-button" class="upload-button" title="Load new agents from AICraft">
    📥
  </button>
  ```

**File: `backend/extension_templates/panel.js`**
- Converted from single-agent to multi-agent architecture
- Key changes:
  - Storage structure: `{agents: {}, activeAgentId: string, chatHistories: {}}`
  - Added `buildAgentDropdown()` - Populates dropdown with all available agents
  - Added `toggleAgentDropdown()` - Shows/hides agent selector
  - Added `handleAgentSwitch(newAgentId)` - Switches between agents, preserves separate chat histories
  - Added `updateAgentUI()` - Updates avatar, name, and Pokemon colors
  - Modified `handleSendMessage()` - Saves history per-agent
  - Modified `handleClearHistory()` - Clears only current agent's history
  - Added `checkForNewAgents()` - Polls backend for new agents to load

Storage Migration:
```javascript
// OLD (single agent)
const data = await chrome.storage.local.get(['agentData', 'chatHistory']);

// NEW (multi-agent)
const data = await chrome.storage.local.get(['agents', 'activeAgentId', 'chatHistories']);
allAgents = data.agents || {};
activeAgentId = data.activeAgentId;
allChatHistories = data.chatHistories || {};
```

Agent Switching Logic:
```javascript
async function handleAgentSwitch(newAgentId) {
  // Save current agent's chat history
  allChatHistories[activeAgentId] = chatHistory;
  await chrome.storage.local.set({ chatHistories: allChatHistories });

  // Switch to new agent
  activeAgentId = newAgentId;
  agentData = allAgents[newAgentId];
  chatHistory = allChatHistories[newAgentId] || [];

  // Update storage and UI
  await chrome.storage.local.set({ activeAgentId });
  updateAgentUI();
  buildAgentDropdown();
  displayChatHistory();
  toggleAgentDropdown();

  addSystemMessage(`Switched to ${agentData.name}!`);
}
```

#### Runtime Extension Files

**Files Synced:**
- `chrome_extension/pikachu-extension/panel.html` - Synced from template
- `chrome_extension/pikachu-extension/panel.js` - Synced from template

### 2. Agent Export/Load System

#### Backend Server API

**File: `chrome_extension/backend_server.py`**

Added in-memory agent queue:
```python
# In-memory pending agents queue (for agent export/import)
pending_agents: list[dict] = []
```

Added POST endpoint for AICraft to queue agents:
```python
@app.post("/agents/queue")
async def queue_agent(agent_data: dict):
    """Queue an agent for loading into the extension.

    Called by AICraft frontend to send agent data to extension.
    Extension will poll /agents/pending to fetch queued agents.
    """
    required_fields = ['id', 'name', 'avatar_url', 'backstory', 'personality_traits']
    for field in required_fields:
        if field not in agent_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    pending_agents.append(agent_data)
    logger.info(f"Queued agent for export: {agent_data['name']} (id: {agent_data['id']})")

    return {
        "status": "queued",
        "agent_id": agent_data['id'],
        "agent_name": agent_data['name']
    }
```

Added GET endpoint for extension to poll:
```python
@app.get("/agents/pending")
async def get_pending_agents():
    """Get list of pending agents waiting to be loaded into extension.

    Extension polls this endpoint to fetch new agents.
    Returns and clears the pending queue.
    """
    global pending_agents

    agents = pending_agents.copy()
    pending_agents.clear()  # Clear after fetching

    if agents:
        logger.info(f"Returning {len(agents)} pending agent(s) to extension")

    return {"agents": agents, "count": len(agents)}
```

#### Extension Load Logic

**File: `backend/extension_templates/panel.js`** (and runtime)

Added auto-check for new agents:
```javascript
// Auto-check for new agents on panel open
checkForNewAgents();

// Also check when user clicks load button
loadAgentsButton.addEventListener('click', checkForNewAgents);
```

Load agents function:
```javascript
async function checkForNewAgents() {
  try {
    const response = await fetch('http://localhost:8080/agents/pending');
    if (!response.ok) {
      console.log('Backend server not reachable for agent loading');
      return;
    }

    const { agents, count } = await response.json();
    if (count === 0) {
      console.log('No new agents to load');
      return;
    }

    console.log(`Loading ${count} new agent(s)...`);

    // Merge new agents into storage
    for (const newAgent of agents) {
      allAgents[newAgent.id] = newAgent;
      allChatHistories[newAgent.id] = [];
    }

    // Save to storage
    await chrome.storage.local.set({
      agents: allAgents,
      chatHistories: allChatHistories
    });

    // Switch to first new agent
    if (agents.length > 0) {
      await handleAgentSwitch(agents[0].id);
    }

    // Rebuild dropdown
    buildAgentDropdown();

    addSystemMessage(`✓ Loaded ${count} new agent(s)!`);
  } catch (error) {
    console.error('Error checking for new agents:', error);
    // Silently fail - don't show error to user unless they explicitly clicked the button
  }
}
```

### 3. JSON File Import Feature

#### UI Changes

**File: `backend/extension_templates/panel.html`**
- Added import button and hidden file input
```html
<button id="import-json-button" class="upload-button" title="Import agent from JSON file">
  📂
</button>
<input type="file" id="json-file-input" accept=".json" style="display: none;">
```

#### Import Logic

**File: `backend/extension_templates/panel.js`**

Added event listeners:
```javascript
const importJsonButton = document.getElementById('import-json-button');
const jsonFileInput = document.getElementById('json-file-input');

importJsonButton.addEventListener('click', () => jsonFileInput.click());
jsonFileInput.addEventListener('change', handleJsonImport);
```

Added `handleJsonImport()` function:
```javascript
async function handleJsonImport(event) {
  const file = event.target.files[0];
  if (!file) return;

  try {
    // Read and parse JSON
    const text = await file.text();
    const agentData = JSON.parse(text);

    // Validate schema
    const validationError = validateAgentSchema(agentData);
    if (validationError) {
      addSystemMessage(`❌ Invalid JSON: ${validationError}`);
      return;
    }

    // Check for duplicates
    if (allAgents[agentData.id]) {
      const overwrite = confirm(`Agent "${agentData.name}" already exists. Overwrite?`);
      if (!overwrite) return;
    }

    // Import agent
    allAgents[agentData.id] = agentData;
    allChatHistories[agentData.id] = allChatHistories[agentData.id] || [];

    // Save and switch
    await chrome.storage.local.set({ agents: allAgents, chatHistories: allChatHistories });
    await handleAgentSwitch(agentData.id);
    buildAgentDropdown();

    addSystemMessage(`✓ Imported agent: ${agentData.name}!`);
  } catch (error) {
    console.error('Error importing JSON:', error);
    addSystemMessage('❌ Error importing agent. Please try again.');
  }
}
```

Added `validateAgentSchema()` function:
```javascript
function validateAgentSchema(agent) {
  const requiredFields = ['id', 'name', 'avatar_url', 'backstory', 'personality_traits'];

  // Check required fields exist
  for (const field of requiredFields) {
    if (!(field in agent)) {
      return `Missing required field: "${field}"`;
    }
  }

  // Validate types
  if (typeof agent.id !== 'string' || agent.id.trim() === '') {
    return '"id" must be a non-empty string';
  }
  // ... (additional type checks for all fields)

  if (!Array.isArray(agent.personality_traits)) {
    return '"personality_traits" must be an array';
  }

  if (agent.personality_traits.length === 0) {
    return '"personality_traits" must contain at least one trait';
  }

  return null; // Valid
}
```

#### JSON Schema

Required agent schema:
```json
{
  "id": "unique_agent_id",
  "name": "Agent Name",
  "avatar_url": "https://example.com/avatar.png",
  "backstory": "Agent backstory and personality",
  "personality_traits": ["trait1", "trait2", "trait3"]
}
```

#### Example File

**File: `chrome_extension/example-agent.json`**
```json
{
  "id": "charizard_001",
  "name": "Charizard",
  "avatar_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png",
  "backstory": "I am Charizard, a powerful Fire/Flying-type Pokémon!...",
  "personality_traits": ["brave", "competitive", "protective", "confident", "passionate"]
}
```

#### Documentation

**File: `chrome_extension/JSON_IMPORT_README.md`**
- Complete JSON schema documentation
- Validation rules and requirements
- Import instructions and workflow
- Example agents
- Avatar URL handling (HTTP, data URIs, relative paths)
- Error handling documentation
- Troubleshooting guide

## Architecture Overview

### Storage Structure

```javascript
{
  "agents": {
    "pikachu_001": {
      "id": "pikachu_001",
      "name": "Pikachu",
      "avatar_url": "assets/icon128.png",
      "backstory": "...",
      "personality_traits": ["energetic", "friendly"]
    },
    "charizard_002": {
      "id": "charizard_002",
      "name": "Charizard",
      // ...
    }
  },
  "activeAgentId": "pikachu_001",
  "chatHistories": {
    "pikachu_001": [
      {"role": "user", "content": "Hello!", "timestamp": "..."},
      {"role": "agent", "content": "Pika pika!", "timestamp": "..."}
    ],
    "charizard_002": [
      // Separate history for Charizard
    ]
  }
}
```

### Agent Export/Load Flow

```
1. AICraft Frontend (TODO)
   ↓ (User clicks "Export to Extension")
   POST http://localhost:8080/agents/queue
   Body: {id, name, avatar_url, backstory, personality_traits}

2. Backend Server
   ↓ (Stores in pending_agents queue)
   Queue: [agent1, agent2, ...]

3. Chrome Extension
   ↓ (Auto-polls on panel open + manual button)
   GET http://localhost:8080/agents/pending

4. Backend Server
   ↓ (Returns agents and clears queue)
   Response: {agents: [...], count: 2}

5. Chrome Extension
   ↓ (Merges into storage, switches to new agent)
   Storage: agents, chatHistories updated
   UI: Shows success message, updates dropdown
```

## Key Design Decisions

1. **Per-Agent Chat History**
   - Each agent maintains separate conversation history
   - Clear history only affects current agent
   - Enables personalized conversations per Pokemon

2. **In-Memory Queue**
   - Pending agents stored in memory (cleared after fetch)
   - Simple, no database needed
   - Extension polls on open (auto-check)

3. **Graceful Degradation**
   - Silent failure if backend not running
   - Extension still works with existing agents
   - Load button available for manual check

4. **Agent Switching**
   - Saves current history before switch
   - Loads new agent's data and history
   - Updates UI with new Pokemon colors
   - Shows confirmation message

5. **Template Variables**
   - Templates keep `{{PLACEHOLDERS}}` for exporter
   - Runtime extension can also use placeholders
   - JavaScript populates dynamically from storage

## Testing Checklist

### Multi-Pokemon Selector
- [ ] Open extension panel
- [ ] Verify dropdown shows all 4 default Pokemon
- [ ] Click on different Pokemon to switch
- [ ] Verify chat history switches correctly
- [ ] Verify colors change per Pokemon
- [ ] Send messages to each Pokemon
- [ ] Switch back and forth - verify histories preserved

### Clear History
- [ ] Chat with Pokemon A
- [ ] Click clear history
- [ ] Verify only Pokemon A's history cleared
- [ ] Switch to Pokemon B
- [ ] Verify Pokemon B's history still intact

### Agent Loading (Backend API)
- [ ] Start backend server: `python backend_server.py`
- [ ] Queue test agent via API:
  ```bash
  curl -X POST http://localhost:8080/agents/queue \
    -H "Content-Type: application/json" \
    -d '{
      "id": "test_001",
      "name": "Test Pokemon",
      "avatar_url": "https://example.com/avatar.png",
      "backstory": "Test backstory",
      "personality_traits": ["test"]
    }'
  ```
- [ ] Click load agents button (📥)
- [ ] Verify new agent appears in dropdown
- [ ] Verify auto-switch to new agent
- [ ] Verify success message shown

### JSON File Import
- [ ] Click import button (📂)
- [ ] Select `chrome_extension/example-agent.json`
- [ ] Verify validation success message
- [ ] Verify Charizard appears in dropdown
- [ ] Verify auto-switch to Charizard
- [ ] Chat with Charizard to test personality
- [ ] Test invalid JSON file (missing fields)
- [ ] Verify error message shows validation issue
- [ ] Test duplicate import (same agent ID)
- [ ] Verify overwrite confirmation prompt
- [ ] Test JSON with malformed syntax
- [ ] Verify appropriate error message

## Pending Work

### AICraft Frontend Integration
**Not yet implemented** - Need to add "Export to Extension" button to AICraft UI

**Suggested Location:** `frontend/src/components/AgentPanel.jsx` or `AgentCreation.jsx`

**Implementation:**
```javascript
async function exportToExtension(agent) {
  try {
    const response = await fetch('http://localhost:8080/agents/queue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: agent.id,
        name: agent.name,
        avatar_url: agent.avatar_url, // May need conversion if file:// URL
        backstory: agent.backstory,
        personality_traits: agent.personality_traits
      })
    });

    if (response.ok) {
      const result = await response.json();
      alert(`Agent ${result.agent_name} queued for extension!`);
    }
  } catch (error) {
    console.error('Export failed:', error);
    alert('Failed to export agent. Is the backend server running?');
  }
}
```

**Button:**
```jsx
<button
  onClick={() => exportToExtension(agent)}
  className="export-button"
>
  📤 Export to Chrome Extension
</button>
```

### Avatar URL Handling
- If AICraft uses `file://` URLs, need to convert to data URLs or base64
- Extension can't access local file:// paths
- Consider converting at export time

## Files Modified

### Backend Templates
- `backend/extension_templates/panel.html` - Added dropdown, load button, and JSON import button
- `backend/extension_templates/panel.js` - Multi-agent logic + JSON import/validation functions

### Runtime Extension
- `chrome_extension/pikachu-extension/panel.html` - Synced from template
- `chrome_extension/pikachu-extension/panel.js` - Synced from template

### Backend Server
- `chrome_extension/backend_server.py` - Added /agents/queue and /agents/pending endpoints

### Documentation & Examples
- `chrome_extension/CHANGES_SUMMARY.md` - This file (updated with JSON import feature)
- `chrome_extension/JSON_IMPORT_README.md` - Complete JSON import documentation
- `chrome_extension/example-agent.json` - Example Charizard agent for testing

## Rollout Instructions

1. **Backend Server**
   ```bash
   cd chrome_extension
   python backend_server.py
   # Server runs on http://localhost:8080
   ```

2. **Chrome Extension**
   - Navigate to `chrome://extensions`
   - Enable "Developer mode"
   - Click "Reload" on AICraft Companion extension
   - Open extension side panel

3. **Testing**
   - Test multi-Pokemon selector (4 default Pokemon)
   - Test clear history per-agent
   - Test agent loading via API

4. **AICraft Integration (Future)**
   - Add export button to AICraft frontend
   - Handle avatar URL conversion
   - Test full export → load flow
