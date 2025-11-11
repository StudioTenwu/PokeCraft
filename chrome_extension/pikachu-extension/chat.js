// Chat integration for AICraft Companion
// This module handles sending messages to Claude and streaming responses

/**
 * Send a message and get a response from the agent
 * @param {string} userMessage - The user's message
 * @param {Object} agentData - Agent data with backstory and personality
 * @returns {Promise<string>} - The agent's response
 */
export async function sendMessage(userMessage, agentData) {
  try {
    // Try calling the backend server (if running)
    const response = await fetch('http://localhost:8080/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: userMessage,
        agent_data: {
          id: agentData.id,  // Include agent ID for backend history tracking
          name: agentData.name,
          backstory: agentData.backstory,
          personality_traits: agentData.personality_traits
        }
      })
    });

    if (response.ok) {
      const data = await response.json();
      return data.response;
    }

    // Fallback to mock if backend not available
    console.log('Backend not available, using mock responses');
    return await getMockResponse(userMessage, agentData);

  } catch (error) {
    // Fallback to mock if backend not available
    console.log('Backend not available, using mock responses');
    return await getMockResponse(userMessage, agentData);
  }
}

/**
 * Build system prompt from agent data
 */
function buildSystemPrompt(agentData) {
  const personalityStr = agentData.personality_traits.join(', ');
  return `${agentData.backstory}\n\nPersonality: ${personalityStr}`;
}

/**
 * Mock response for MVP (placeholder for Claude integration)
 * TODO: Replace with actual Claude Agent SDK integration
 */
async function getMockResponse(userMessage, agentData) {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));

  const responses = [
    `As ${agentData.name}, I hear you! Let me help with that.`,
    `That's interesting! Here's what I think...`,
    `I understand. Based on my experience, I'd say...`,
    `Great question! Let me share my perspective...`
  ];

  const randomResponse = responses[Math.floor(Math.random() * responses.length)];
  return randomResponse;
}

/**
 * Load chat history from storage
 */
export async function loadChatHistory() {
  const data = await chrome.storage.local.get(['chatHistory']);
  return data.chatHistory || [];
}

/**
 * Save chat history to storage
 */
export async function saveChatHistory(history) {
  await chrome.storage.local.set({ chatHistory: history });
}
