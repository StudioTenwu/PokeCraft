// Panel UI controller for AICraft Companion extension
import { sendMessage, loadChatHistory, saveChatHistory } from './chat.js';
import { applyAgentColors } from './pokemon-colors.js';

let agentData = null;
let chatHistory = [];
let activeAgentId = null;
let allAgents = {};
let allChatHistories = {};

// Initialize panel
async function initPanel() {
  // Load multi-agent data from storage
  const data = await chrome.storage.local.get(['agents', 'activeAgentId', 'chatHistories']);

  allAgents = data.agents || {};
  activeAgentId = data.activeAgentId;
  allChatHistories = data.chatHistories || {};

  // Get active agent
  if (activeAgentId && allAgents[activeAgentId]) {
    agentData = allAgents[activeAgentId];
    chatHistory = allChatHistories[activeAgentId] || [];
  } else {
    // Fallback: use first available agent
    const agentIds = Object.keys(allAgents);
    if (agentIds.length > 0) {
      activeAgentId = agentIds[0];
      agentData = allAgents[activeAgentId];
      chatHistory = allChatHistories[activeAgentId] || [];
      await chrome.storage.local.set({ activeAgentId });
    } else {
      // No agents available
      addSystemMessage('No agents available. Please load agents first.');
      return;
    }
  }

  // Populate UI with agent info
  updateAgentUI();

  // Build agent selector dropdown
  buildAgentDropdown();

  // Load chat history
  displayChatHistory();

  // Set up event listeners
  const sendButton = document.getElementById('send-button');
  const messageInput = document.getElementById('message-input');
  const clearHistoryButton = document.getElementById('clear-history-button');
  const loadAgentsButton = document.getElementById('load-agents-button');
  const importJsonButton = document.getElementById('import-json-button');
  const jsonFileInput = document.getElementById('json-file-input');
  const agentSelector = document.getElementById('agent-selector');

  sendButton.addEventListener('click', handleSendMessage);
  messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  });
  clearHistoryButton.addEventListener('click', handleClearHistory);
  loadAgentsButton.addEventListener('click', checkForNewAgents);
  importJsonButton.addEventListener('click', () => jsonFileInput.click());
  jsonFileInput.addEventListener('change', handleJsonImport);
  agentSelector.addEventListener('click', toggleAgentDropdown);

  // Auto-check for new agents on panel open
  checkForNewAgents();

  // Focus input
  messageInput.focus();
}

// Update UI with current agent data
function updateAgentUI() {
  document.getElementById('current-agent-name').textContent = agentData.name;
  document.getElementById('agent-avatar').src = agentData.avatar_url;

  // Apply Pokemon color theme
  if (agentData.id) {
    applyAgentColors(agentData.id);
  }
}

// Build agent selector dropdown
function buildAgentDropdown() {
  const dropdown = document.getElementById('agent-dropdown');
  dropdown.innerHTML = '';

  for (const [id, agent] of Object.entries(allAgents)) {
    const option = document.createElement('div');
    option.className = `agent-option ${id === activeAgentId ? 'active' : ''}`;
    option.dataset.agentId = id;

    const avatar = document.createElement('img');
    avatar.src = agent.avatar_url;
    avatar.className = 'agent-option-avatar';
    avatar.alt = agent.name;

    const name = document.createElement('span');
    name.className = 'agent-option-name';
    name.textContent = agent.name;

    option.appendChild(avatar);
    option.appendChild(name);
    option.addEventListener('click', () => handleAgentSwitch(id));

    dropdown.appendChild(option);
  }
}

// Toggle agent dropdown visibility
function toggleAgentDropdown() {
  const dropdown = document.getElementById('agent-dropdown');
  const selector = document.getElementById('agent-selector');

  dropdown.classList.toggle('hidden');
  selector.classList.toggle('open');
}

// Handle agent switching
async function handleAgentSwitch(newAgentId) {
  if (newAgentId === activeAgentId) {
    toggleAgentDropdown();
    return;
  }

  // Save current agent's chat history
  allChatHistories[activeAgentId] = chatHistory;
  await chrome.storage.local.set({ chatHistories: allChatHistories });

  // Switch to new agent
  activeAgentId = newAgentId;
  agentData = allAgents[newAgentId];
  chatHistory = allChatHistories[newAgentId] || [];

  // Update storage
  await chrome.storage.local.set({ activeAgentId });

  // Update UI
  updateAgentUI();
  buildAgentDropdown(); // Rebuild to update active state
  displayChatHistory();
  toggleAgentDropdown();

  addSystemMessage(`Switched to ${agentData.name}!`);
}

// Display chat history
function displayChatHistory() {
  const chatArea = document.getElementById('chat-area');
  chatArea.innerHTML = '';

  if (chatHistory.length === 0) {
    addSystemMessage('Start chatting with your AICraft companion!');
  } else {
    chatHistory.forEach(msg => {
      addMessageToUI(msg.role, msg.content);
    });
  }

  scrollToBottom();
}

// Handle send message
async function handleSendMessage() {
  const input = document.getElementById('message-input');
  const sendButton = document.getElementById('send-button');
  const message = input.value.trim();

  if (!message) return;

  // Disable input while processing
  input.disabled = true;
  sendButton.disabled = true;

  // Add user message to UI
  addMessageToUI('user', message);
  input.value = '';

  // Add to history
  chatHistory.push({
    role: 'user',
    content: message,
    timestamp: new Date().toISOString()
  });

  // Add loading indicator
  const loadingId = addLoadingIndicator();

  try {
    // Send to chat handler and get response
    const response = await sendMessage(message, agentData);

    // Remove loading indicator
    removeLoadingIndicator(loadingId);

    // Add agent response to UI
    addMessageToUI('agent', response);

    // Add to history
    chatHistory.push({
      role: 'agent',
      content: response,
      timestamp: new Date().toISOString()
    });

    // Save history for current agent
    allChatHistories[activeAgentId] = chatHistory;
    await chrome.storage.local.set({ chatHistories: allChatHistories });

  } catch (error) {
    console.error('Error sending message:', error);
    removeLoadingIndicator(loadingId);
    addSystemMessage('Error: Could not get response. Please try again.');
  } finally {
    // Re-enable input
    input.disabled = false;
    sendButton.disabled = false;
    input.focus();
  }
}

// Add message to UI
function addMessageToUI(role, content) {
  const chatArea = document.getElementById('chat-area');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;
  messageDiv.textContent = content;
  chatArea.appendChild(messageDiv);
  scrollToBottom();
}

// Add system message
function addSystemMessage(content) {
  const chatArea = document.getElementById('chat-area');
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message system';
  messageDiv.textContent = content;
  chatArea.appendChild(messageDiv);
  scrollToBottom();
}

// Scroll to bottom of chat
function scrollToBottom() {
  const chatArea = document.getElementById('chat-area');
  chatArea.scrollTop = chatArea.scrollHeight;
}

// Add loading indicator with spinning sprite
function addLoadingIndicator() {
  const chatArea = document.getElementById('chat-area');
  const loadingDiv = document.createElement('div');
  const loadingId = `loading-${Date.now()}`;
  loadingDiv.id = loadingId;
  loadingDiv.className = 'message agent loading';

  // Create spinning sprite image
  const sprite = document.createElement('img');
  sprite.src = agentData.avatar_url;
  sprite.className = 'loading-sprite';
  sprite.alt = 'Loading...';

  // Create dots animation
  const dots = document.createElement('span');
  dots.className = 'loading-dots';
  dots.textContent = '...';

  loadingDiv.appendChild(sprite);
  loadingDiv.appendChild(dots);
  chatArea.appendChild(loadingDiv);
  scrollToBottom();

  return loadingId;
}

// Remove loading indicator
function removeLoadingIndicator(loadingId) {
  const loadingDiv = document.getElementById(loadingId);
  if (loadingDiv) {
    loadingDiv.remove();
  }
}

// Handle clear history
async function handleClearHistory() {
  // Confirm with user - mention which agent
  const confirmed = confirm(`Clear conversation history for ${agentData.name}? This will delete all messages for this agent only.`);

  if (!confirmed) return;

  try {
    // Clear current agent's history
    chatHistory = [];
    allChatHistories[activeAgentId] = [];
    await chrome.storage.local.set({ chatHistories: allChatHistories });

    // Clear backend history by sending a special clear_history flag
    const response = await fetch('http://localhost:8080/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: '',
        agent_data: {
          id: agentData.id,
          name: agentData.name,
          backstory: agentData.backstory,
          personality_traits: agentData.personality_traits
        },
        clear_history: true
      })
    });

    // Check if backend succeeded
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    // Refresh UI
    displayChatHistory();
    addSystemMessage(`Conversation history cleared for ${agentData.name}!`);
  } catch (error) {
    console.error('Error clearing history:', error);
    addSystemMessage('Error: Could not clear history. Please try again.');
  }
}

// Check for new agents from backend server
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

// Handle JSON file import
async function handleJsonImport(event) {
  const file = event.target.files[0];
  if (!file) return;

  try {
    // Read file content
    const text = await file.text();
    const agentData = JSON.parse(text);

    // Validate agent data schema
    const validationError = validateAgentSchema(agentData);
    if (validationError) {
      addSystemMessage(`❌ Invalid JSON: ${validationError}`);
      console.error('Validation error:', validationError);
      return;
    }

    // Check for duplicate agent ID
    if (allAgents[agentData.id]) {
      const overwrite = confirm(`Agent "${agentData.name}" (ID: ${agentData.id}) already exists. Overwrite?`);
      if (!overwrite) {
        addSystemMessage('Import cancelled.');
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

    addSystemMessage(`✓ Imported agent: ${agentData.name}!`);
  } catch (error) {
    console.error('Error importing JSON:', error);
    if (error instanceof SyntaxError) {
      addSystemMessage('❌ Invalid JSON file. Please check the file format.');
    } else {
      addSystemMessage('❌ Error importing agent. Please try again.');
    }
  } finally {
    // Reset file input
    event.target.value = '';
  }
}

// Validate agent JSON schema
function validateAgentSchema(agent) {
  // Required fields
  const requiredFields = ['id', 'name', 'avatar_url', 'backstory', 'personality_traits'];

  for (const field of requiredFields) {
    if (!(field in agent)) {
      return `Missing required field: "${field}"`;
    }
  }

  // Type validation
  if (typeof agent.id !== 'string' || agent.id.trim() === '') {
    return '"id" must be a non-empty string';
  }

  if (typeof agent.name !== 'string' || agent.name.trim() === '') {
    return '"name" must be a non-empty string';
  }

  if (typeof agent.avatar_url !== 'string' || agent.avatar_url.trim() === '') {
    return '"avatar_url" must be a non-empty string';
  }

  if (typeof agent.backstory !== 'string' || agent.backstory.trim() === '') {
    return '"backstory" must be a non-empty string';
  }

  if (!Array.isArray(agent.personality_traits)) {
    return '"personality_traits" must be an array';
  }

  if (agent.personality_traits.length === 0) {
    return '"personality_traits" must contain at least one trait';
  }

  if (!agent.personality_traits.every(trait => typeof trait === 'string')) {
    return 'All items in "personality_traits" must be strings';
  }

  return null; // Valid
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initPanel);
