import { vi } from 'vitest';

// Mock agent response
const mockAgentResponse = {
  id: 'mock-agent-123',
  name: 'Mock Buddy',
  backstory: 'A test pokemon for testing purposes',
  personality_traits: ['Brave', 'Curious', 'Helpful'],
  avatar_url: 'data:image/png;base64,mock-base64-data'
};

// Mock world response
const mockWorldResponse = {
  id: 'mock-world-123',
  agent_id: 'mock-agent-123',
  description: 'A test world',
  grid: [
    [1, 1, 1],
    [1, 0, 1],
    [1, 1, 1]
  ],
  agent_position: { x: 1, y: 1 }
};

// Create mock API object
export const api = {
  createAgent: vi.fn(async (description) => {
    return {
      ...mockAgentResponse,
      backstory: description
    };
  }),

  createAgentStream: vi.fn((description, callbacks = {}) => {
    // Simulate streaming with timeouts
    const simulate = async () => {
      // LLM start
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onLLMStart?.({ message: 'Dreaming up your pokemon...' });

      // LLM complete
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onLLMComplete?.({
        name: mockAgentResponse.name,
        backstory: mockAgentResponse.backstory,
        personality_traits: mockAgentResponse.personality_traits
      });

      // Avatar start
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onAvatarStart?.({ message: 'Hatching your pokemon...' });

      // Avatar progress - step 1
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onAvatarProgress?.({
        message: 'Hatching... Step 1/2',
        step: 1,
        total: 2,
        percent: 50
      });

      // Avatar progress - step 2
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onAvatarProgress?.({
        message: 'Hatching... Step 2/2',
        step: 2,
        total: 2,
        percent: 100
      });

      // Avatar complete
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onAvatarComplete?.({
        avatar_url: mockAgentResponse.avatar_url
      });

      // Complete
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onComplete?.({
        agent: {
          ...mockAgentResponse,
          backstory: description
        }
      });
    };

    simulate().catch(err => {
      callbacks.onError?.(err);
    });

    // Return cleanup function
    return vi.fn();
  }),

  getAgent: vi.fn(async (agentId) => {
    return { ...mockAgentResponse, id: agentId };
  }),

  createWorld: vi.fn(async (agentId, description) => {
    return {
      ...mockWorldResponse,
      agent_id: agentId,
      description
    };
  }),

  getWorld: vi.fn(async (worldId) => {
    return { ...mockWorldResponse, id: worldId };
  }),

  getWorldsByAgent: vi.fn(async (agentId) => {
    return [{ ...mockWorldResponse, agent_id: agentId }];
  })
};

// Export individual functions
export const createAgent = api.createAgent;
export const createAgentStream = api.createAgentStream;
export const getAgent = api.getAgent;
export const createWorld = api.createWorld;
export const getWorld = api.getWorld;
export const getWorldsByAgent = api.getWorldsByAgent;
