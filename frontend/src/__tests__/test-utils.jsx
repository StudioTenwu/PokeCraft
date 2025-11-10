import { render } from '@testing-library/react'

// Custom render function with any providers if needed
export function customRender(ui, options = {}) {
  return render(ui, { ...options })
}

// Mock agents for testing
export const mockAgents = {
  basic: {
    id: '123',
    name: 'Test Bot',
    backstory: 'A test bot created for unit testing purposes',
    personality_traits: ['Helpful', 'Curious', 'Brave'],
    avatar_url: null
  },
  withHttpAvatar: {
    id: '456',
    name: 'Avatar Bot',
    backstory: 'A bot with an HTTP avatar URL',
    personality_traits: ['Creative', 'Friendly'],
    avatar_url: 'http://example.com/avatar.png'
  },
  withDataUriAvatar: {
    id: '789',
    name: 'Data URI Bot',
    backstory: 'A bot with a data URI avatar',
    personality_traits: ['Loyal'],
    avatar_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
  },
  manyTraits: {
    id: '999',
    name: 'Trait Test Bot',
    backstory: 'Testing personality badge colors',
    personality_traits: [
      'Brave', 'Curious', 'Helpful', 'Creative', 'Friendly',
      'Energetic', 'Loyal', 'Playful', 'Clever', 'Kind',
      'Adventurous', 'Patient'
    ],
    avatar_url: null
  }
}

// Mock worlds for testing
export const mockWorlds = {
  basic: {
    id: 'world-123',
    agent_id: '123',
    description: 'A magical forest world',
    grid_data: Array(10).fill(null).map(() => Array(10).fill(0)),
    width: 10,
    height: 10
  }
}

// Mock SSE events for agent creation streaming
export const mockSSEEvents = {
  llmStart: {
    event: 'llm_start',
    data: { message: 'Dreaming up your companion...' }
  },
  llmComplete: {
    event: 'llm_complete',
    data: { agent: { id: '123', name: 'Test Bot' } }
  },
  avatarStart: {
    event: 'avatar_start',
    data: { message: 'Hatching your companion...' }
  },
  avatarProgress: {
    event: 'avatar_progress',
    data: { step: 1, total: 2, percent: 50, message: 'Hatching... Step 1/2' }
  },
  avatarComplete: {
    event: 'avatar_complete',
    data: { avatar_url: 'http://example.com/avatar.png' }
  },
  complete: {
    event: 'complete',
    data: { agent: mockAgents.basic }
  },
  error: {
    event: 'error',
    data: { message: 'Something went wrong' }
  }
}

// Re-export everything from React Testing Library
export * from '@testing-library/react'
export { customRender as render }
