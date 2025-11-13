import { EVENT_CALLBACK_MAP, validateEvent } from './types/streaming.js'

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
   * Create agent with streaming progress updates using EventSource.
   * @param {string} description - Agent description
   * @param {import('./types/streaming.js').AgentCreationCallbacks} callbacks - Event callbacks
   * @returns {Function} Cleanup function to close the stream
   */
  createAgentStream(description, callbacks = {}) {
    // Build URL with query parameter
    const url = `${API_BASE}/api/agents/create/stream?description=${encodeURIComponent(description)}`

    // Create EventSource (built-in SSE support!)
    const eventSource = new EventSource(url)

    // Register event listeners for each event type
    Object.entries(EVENT_CALLBACK_MAP).forEach(([eventName, callbackName]) => {
      eventSource.addEventListener(eventName, (event) => {
        try {
          const data = JSON.parse(event.data)

          // Validate against contract
          if (!validateEvent(eventName, data)) {
            console.error(`Invalid event received: ${eventName}`, data)
            return
          }

          // Call the appropriate callback
          callbacks[callbackName]?.(data)
        } catch (e) {
          console.error(`Failed to parse event data for ${eventName}:`, e)
        }
      })
    })

    // Handle error events
    eventSource.addEventListener('error', (event) => {
      try {
        const data = JSON.parse(event.data)
        callbacks.onError?.(new Error(data.message || 'Unknown error'))
      } catch {
        // If parsing fails, it's likely a connection error
        callbacks.onError?.(new Error('Connection error'))
      }
    })

    // Handle connection errors
    eventSource.onerror = (err) => {
      console.error('EventSource error:', err)
      callbacks.onError?.(new Error('Stream connection failed'))
      eventSource.close()
    }

    // Return cleanup function
    return () => eventSource.close()
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
  },

  /**
   * Deploy agent with streaming updates using EventSource.
   * @param {string} agentId - Agent ID to deploy
   * @param {string} worldId - World ID to deploy in
   * @param {string} goal - Mission goal for the agent
   * @param {Object} callbacks - Event callbacks for deployment events
   * @returns {Function} Cleanup function to close the stream
   */
  deployAgent(agentId, worldId, goal, callbacks = {}) {
    // Build URL with query parameters
    const url = `${API_BASE}/api/agents/deploy?agent_id=${encodeURIComponent(agentId)}&world_id=${encodeURIComponent(worldId)}&goal=${encodeURIComponent(goal)}`

    console.log('SSE connecting to:', url)

    // Create EventSource for SSE
    const eventSource = new EventSource(url)

    // Register listeners for deployment event types
    const deploymentEvents = ['system', 'thinking', 'text', 'tool_call', 'tool_result', 'world_update', 'error', 'complete']

    deploymentEvents.forEach(eventName => {
      eventSource.addEventListener(eventName, (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log(`SSE event: ${eventName}`, data)

          // Call the appropriate callback
          const callbackName = `on${eventName.charAt(0).toUpperCase() + eventName.slice(1).replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())}`
          callbacks[callbackName]?.(data)
        } catch (e) {
          console.error(`Failed to parse event data for ${eventName}:`, e)
        }
      })
    })

    // Handle connection errors
    eventSource.onerror = (err) => {
      console.error('EventSource error:', err)
      callbacks.onError?.(new Error('Stream connection failed'))
      eventSource.close()
    }

    // Return cleanup function
    return () => eventSource.close()
  }
}

// Export individual functions for easier imports
export const createAgent = api.createAgent.bind(api)
export const createAgentStream = api.createAgentStream.bind(api)
export const getAgent = api.getAgent.bind(api)
export const createWorld = api.createWorld.bind(api)
export const getWorld = api.getWorld.bind(api)
export const getWorldsByAgent = api.getWorldsByAgent.bind(api)
export const deployAgent = api.deployAgent.bind(api)
