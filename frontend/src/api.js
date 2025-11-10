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
  async createAgentStream(description, callbacks = {}) {
    const controller = new AbortController()

    try {
      const response = await fetch(`${API_BASE}/api/agents/create/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
        signal: controller.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Process Server-Sent Events stream
      await this._consumeSSEStream(response.body, callbacks)
    } catch (error) {
      if (error.name !== 'AbortError') {
        callbacks.onError?.(error)
      }
    }

    // Return cleanup function
    return () => controller.abort()
  },

  /**
   * Helper to parse and consume SSE stream.
   * @private
   */
  async _consumeSSEStream(body, callbacks) {
    const reader = body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // Extract complete SSE messages (separated by \n\n)
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || '' // Keep incomplete message in buffer

      for (const rawMessage of parts) {
        if (!rawMessage.trim()) continue

        const event = this._parseSSEMessage(rawMessage)
        if (event) {
          this._dispatchSSEEvent(event, callbacks)
        }
      }
    }
  },

  /**
   * Parse a single SSE message.
   * @private
   * @returns {{event: string, data: any} | null}
   */
  _parseSSEMessage(rawMessage) {
    const lines = rawMessage.split('\n')
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
          return null
        }
      }
    }

    return eventData ? { event: eventName, data: eventData } : null
  },

  /**
   * Dispatch SSE event to appropriate callback.
   * @private
   */
  _dispatchSSEEvent({ event, data }, callbacks) {
    const eventMap = {
      'llm_start': 'onLLMStart',
      'llm_complete': 'onLLMComplete',
      'avatar_start': 'onAvatarStart',
      'avatar_progress': 'onAvatarProgress',
      'avatar_complete': 'onAvatarComplete',
      'complete': 'onComplete'
    }

    if (event === 'error') {
      callbacks.onError?.(new Error(data.message || 'Unknown error'))
    } else {
      const callbackName = eventMap[event]
      if (callbackName) {
        callbacks[callbackName]?.(data)
      }
    }
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
