import { vi } from 'vitest'

// Mock implementation of createAgentStream
export const createAgentStreamMock = vi.fn((description, callbacks = {}) => {
  // Simulate async streaming behavior
  setTimeout(() => {
    callbacks.onLLMStart?.({ message: 'Dreaming up your companion...' })
  }, 10)

  setTimeout(() => {
    callbacks.onLLMComplete?.({ agent: { id: '123', name: 'Test Bot' } })
  }, 20)

  setTimeout(() => {
    callbacks.onAvatarStart?.({ message: 'Hatching your companion...' })
  }, 30)

  setTimeout(() => {
    callbacks.onAvatarProgress?.({ step: 1, total: 2, percent: 50, message: 'Step 1/2' })
  }, 40)

  setTimeout(() => {
    callbacks.onAvatarProgress?.({ step: 2, total: 2, percent: 100, message: 'Step 2/2' })
  }, 50)

  setTimeout(() => {
    callbacks.onAvatarComplete?.({ avatar_url: 'http://example.com/avatar.png' })
  }, 60)

  setTimeout(() => {
    callbacks.onComplete?.({
      agent: {
        id: '123',
        name: 'Test Bot',
        backstory: 'A test bot',
        personality_traits: ['Helpful', 'Brave'],
        avatar_url: 'http://example.com/avatar.png'
      }
    })
  }, 70)

  // Return cleanup function
  return vi.fn()
})

// Mock API object
export const api = {
  createAgent: vi.fn(async (description) => {
    return {
      id: '123',
      name: 'Test Bot',
      backstory: 'A test bot',
      personality_traits: ['Helpful', 'Brave'],
      avatar_url: null
    }
  }),

  createAgentStream: createAgentStreamMock,

  getAgent: vi.fn(async (agentId) => {
    return {
      id: agentId,
      name: 'Test Bot',
      backstory: 'A test bot',
      personality_traits: ['Helpful'],
      avatar_url: null
    }
  }),

  createWorld: vi.fn(async (agentId, description) => {
    return {
      id: 'world-123',
      agent_id: agentId,
      description,
      grid_data: Array(10).fill(null).map(() => Array(10).fill(0)),
      width: 10,
      height: 10
    }
  }),

  getWorld: vi.fn(async (worldId) => {
    return {
      id: worldId,
      agent_id: '123',
      description: 'Test world',
      grid_data: Array(10).fill(null).map(() => Array(10).fill(0)),
      width: 10,
      height: 10
    }
  }),

  getWorldsByAgent: vi.fn(async (agentId) => {
    return []
  })
}

// Export individual functions
export const createAgent = api.createAgent
export const createAgentStream = api.createAgentStream
export const getAgent = api.getAgent
export const createWorld = api.createWorld
export const getWorld = api.getWorld
export const getWorldsByAgent = api.getWorldsByAgent
