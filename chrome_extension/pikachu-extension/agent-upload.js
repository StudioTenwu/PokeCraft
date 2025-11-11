// Custom agent upload and validation for AICraft Companion
// Handles file upload, JSON validation, and storage

/**
 * Validate agent JSON schema
 * @param {Object} agentData - Agent data to validate
 * @throws {Error} If validation fails
 * @returns {boolean} True if valid
 */
function validateAgentSchema(agentData) {
  // Check required fields
  const required = ['id', 'name', 'avatar_url', 'backstory', 'personality_traits'];

  for (const field of required) {
    if (!agentData[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
    if (typeof agentData[field] === 'string' && agentData[field].trim() === '') {
      throw new Error(`Field "${field}" cannot be empty`);
    }
  }

  // Validate types
  if (!Array.isArray(agentData.personality_traits)) {
    throw new Error('personality_traits must be an array');
  }

  if (agentData.personality_traits.length === 0) {
    throw new Error('personality_traits must contain at least one trait');
  }

  // Validate personality traits are strings
  for (const trait of agentData.personality_traits) {
    if (typeof trait !== 'string' || trait.trim() === '') {
      throw new Error('Each personality trait must be a non-empty string');
    }
  }

  // Validate string lengths
  if (agentData.name.length > 50) {
    throw new Error('Agent name too long (max 50 characters)');
  }

  if (agentData.backstory.length > 1000) {
    throw new Error('Backstory too long (max 1000 characters)');
  }

  // Validate each trait length
  for (const trait of agentData.personality_traits) {
    if (trait.length > 30) {
      throw new Error(`Personality trait too long (max 30 characters): "${trait}"`);
    }
  }

  // Validate avatar URL
  if (!isValidURL(agentData.avatar_url)) {
    throw new Error('Invalid avatar_url. Must be a valid https:// URL or data:// URI');
  }

  return true;
}

/**
 * Validate URL format
 * @param {string} string - URL to validate
 * @returns {boolean} True if valid
 */
function isValidURL(string) {
  try {
    const url = new URL(string);
    // Allow https, http, and data URLs
    return ['https:', 'http:', 'data:'].includes(url.protocol);
  } catch (_) {
    return false;
  }
}

/**
 * Sanitize string to prevent XSS
 * @param {string} str - String to sanitize
 * @returns {string} Sanitized string
 */
function sanitizeString(str) {
  if (typeof str !== 'string') return str;

  // Remove any HTML tags
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Handle agent file upload
 * @param {File} file - Uploaded JSON file
 * @returns {Promise<Object>} Validated agent data
 */
async function handleAgentUpload(file) {
  // Validate file size (max 100KB)
  if (file.size > 100 * 1024) {
    throw new Error('File too large (max 100KB)');
  }

  // Validate file type
  if (!file.name.endsWith('.json')) {
    throw new Error('Please upload a .json file');
  }

  // Read file content
  const fileContent = await file.text();

  // Parse JSON
  let agentData;
  try {
    agentData = JSON.parse(fileContent);
  } catch (e) {
    throw new Error(`Invalid JSON: ${e.message}`);
  }

  // Validate schema
  validateAgentSchema(agentData);

  // Sanitize string fields to prevent XSS
  agentData.name = sanitizeString(agentData.name);
  agentData.backstory = sanitizeString(agentData.backstory);
  agentData.personality_traits = agentData.personality_traits.map(trait => sanitizeString(trait));

  // Build system prompt from backstory and personality
  const personalityStr = agentData.personality_traits.join(', ');
  agentData.system_prompt = `${agentData.backstory}\n\nPersonality: ${personalityStr}`;

  // Mark as custom agent
  agentData.isCustom = true;

  // Load current multi-agent data
  const currentData = await chrome.storage.local.get(['agents', 'activeAgentId', 'chatHistories']);
  const agents = currentData.agents || {};
  const chatHistories = currentData.chatHistories || {};

  // Add new agent to agents object (don't replace existing ones)
  agents[agentData.id] = agentData;

  // Initialize empty chat history for new agent
  chatHistories[agentData.id] = [];

  // Set new agent as active
  const activeAgentId = agentData.id;

  // Store updated multi-agent data
  await chrome.storage.local.set({
    agents: agents,
    activeAgentId: activeAgentId,
    chatHistories: chatHistories
  });

  return agentData;
}

/**
 * Reset to default agent
 * @returns {Promise<Object>} Default agent data
 */
async function resetToDefaultAgent() {
  const { defaultAgentBackup } = await chrome.storage.local.get(['defaultAgentBackup']);

  if (defaultAgentBackup) {
    await chrome.storage.local.set({
      agentData: defaultAgentBackup,
      chatHistory: []
    });
    return defaultAgentBackup;
  }

  throw new Error('No default agent backup found');
}

/**
 * Check if current agent is custom
 * @returns {Promise<boolean>} True if current agent is custom
 */
async function isCurrentAgentCustom() {
  const { agentData } = await chrome.storage.local.get(['agentData']);
  return agentData && agentData.isCustom === true;
}
