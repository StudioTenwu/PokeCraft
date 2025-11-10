const API_BASE = 'http://localhost:8000'

export const api = {
  async createAgent(description) {
    const res = await fetch(`${API_BASE}/api/agents/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description })
    })
    if (!res.ok) {
      const error = await res.text()
      throw new Error(`Failed to create agent: ${error}`)
    }
    return res.json()
  },

  /**
   * Create agent with streaming progress updates.
   * @param {string} description - Agent description
   * @param {Object} callbacks - Event callbacks
   * @param {Function} callbacks.onLLMStart - Called when LLM generation starts
   * @param {Function} callbacks.onLLMComplete - Called when LLM generation completes
   * @param {Function} callbacks.onAvatarStart - Called when avatar generation starts
   * @param {Function} callbacks.onAvatarProgress - Called with avatar progress updates
   * @param {Function} callbacks.onAvatarComplete - Called when avatar is complete
   * @param {Function} callbacks.onComplete - Called when entire process completes
   * @param {Function} callbacks.onError - Called on error
   * @returns {Function} Cleanup function to close the stream
   */
  createAgentStream(description, callbacks = {}) {
    const controller = new AbortController()
    const signal = controller.signal

    // Use fetch API for POST with streaming response
    fetch(`${API_BASE}/api/agents/create/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
      signal
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            // Decode chunk and add to buffer
            buffer += decoder.decode(value, { stream: true })

            // Process complete SSE messages (separated by \n\n)
            const messages = buffer.split('\n\n')
            buffer = messages.pop() || '' // Keep incomplete message in buffer

            for (const message of messages) {
              if (!message.trim()) continue

              // Parse SSE message format: "event: name\ndata: json"
              const lines = message.split('\n')
              let eventName = 'message'
              let eventData = null

              for (const line of lines) {
                if (line.startsWith('event:')) {
                  eventName = line.substring(6).trim()
                } else if (line.startsWith('data:')) {
                  const dataStr = line.substring(5).trim()
                  try {
                    eventData = JSON.parse(dataStr)
                  } catch (e) {
                    console.error('Failed to parse SSE data:', dataStr, e)
                  }
                }
              }

              // Dispatch to appropriate callback
              if (eventData) {
                switch (eventName) {
                  case 'llm_start':
                    callbacks.onLLMStart?.(eventData)
                    break
                  case 'llm_complete':
                    callbacks.onLLMComplete?.(eventData)
                    break
                  case 'avatar_start':
                    callbacks.onAvatarStart?.(eventData)
                    break
                  case 'avatar_progress':
                    callbacks.onAvatarProgress?.(eventData)
                    break
                  case 'avatar_complete':
                    callbacks.onAvatarComplete?.(eventData)
                    break
                  case 'complete':
                    callbacks.onComplete?.(eventData)
                    break
                  case 'error':
                    callbacks.onError?.(new Error(eventData.message || 'Unknown error'))
                    break
                }
              }
            }
          }
        } catch (error) {
          if (error.name !== 'AbortError') {
            callbacks.onError?.(error)
          }
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          callbacks.onError?.(error)
        }
      })

    // Return cleanup function
    return () => controller.abort()
  },

  async getAgent(agentId) {
    const res = await fetch(`${API_BASE}/api/agents/${agentId}`)
    if (!res.ok) throw new Error('Failed to get agent')
    return res.json()
  },

  async createWorld(agentId, description) {
    const res = await fetch(`${API_BASE}/api/worlds/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, description })
    })
    if (!res.ok) {
      const error = await res.text()
      throw new Error(`Failed to create world: ${error}`)
    }
    return res.json()
  },

  async getWorld(worldId) {
    const res = await fetch(`${API_BASE}/api/worlds/${worldId}`)
    if (!res.ok) throw new Error('Failed to get world')
    return res.json()
  },

  async getWorldsByAgent(agentId) {
    const res = await fetch(`${API_BASE}/api/worlds/agent/${agentId}`)
    if (!res.ok) throw new Error('Failed to get worlds')
    return res.json()
  }
}

// Export individual functions for easier imports
export const createAgent = api.createAgent.bind(api)
export const createAgentStream = api.createAgentStream.bind(api)
export const getAgent = api.getAgent.bind(api)
export const createWorld = api.createWorld.bind(api)
export const getWorld = api.getWorld.bind(api)
export const getWorldsByAgent = api.getWorldsByAgent.bind(api)
