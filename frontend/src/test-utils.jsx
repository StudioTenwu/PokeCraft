import { render } from '@testing-library/react';
import { vi } from 'vitest';

// Mock fixtures
export const mockAgent = {
  id: 'test-agent-1',
  name: 'Test Buddy',
  backstory: 'A brave pokemon ready to explore the digital world!',
  personality_traits: ['Brave', 'Curious', 'Helpful', 'Creative', 'Friendly'],
  avatar_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
};

export const mockAgentNoAvatar = {
  id: 'test-agent-2',
  name: 'Pixel Pal',
  backstory: 'An energetic friend with endless curiosity',
  personality_traits: ['Energetic', 'Loyal', 'Playful'],
  avatar_url: null
};

export const mockWorld = {
  id: 'test-world-1',
  agent_id: 'test-agent-1',
  description: 'A mystical forest filled with ancient trees',
  grid: [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 2, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1]
  ],
  agent_position: { x: 2, y: 2 }
};

// Custom render function (can be extended with providers if needed)
export function renderWithProviders(ui, options = {}) {
  return render(ui, { ...options });
}

// Helper to wait for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0));

// Helper to mock SSE streaming
export function createMockStreamResponse(events) {
  const encoder = new TextEncoder();

  return {
    ok: true,
    status: 200,
    body: {
      getReader: () => {
        let eventIndex = 0;

        return {
          read: async () => {
            if (eventIndex >= events.length) {
              return { done: true };
            }

            const event = events[eventIndex++];
            const message = `event: ${event.type}\ndata: ${JSON.stringify(event.data)}\n\n`;
            const chunk = encoder.encode(message);

            return { done: false, value: chunk };
          }
        };
      }
    }
  };
}

// Helper to create fetch mock for streaming
export function mockFetchStream(events, delayMs = 10) {
  return vi.fn(() => {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(createMockStreamResponse(events));
      }, delayMs);
    });
  });
}

// Export all testing library utilities
export * from '@testing-library/react';
