import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import AgentRunner from '../AgentRunner'

// Mock EventSource
class MockEventSource {
  constructor(url) {
    this.url = url
    this.listeners = {}
    this.readyState = 0
    MockEventSource.instances.push(this)
  }

  addEventListener(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  close() {
    this.readyState = 2
  }

  // Test helper to simulate events
  simulateEvent(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        callback({ data: JSON.stringify(data) })
      })
    }
  }

  static instances = []
  static reset() {
    MockEventSource.instances = []
  }
}

global.EventSource = MockEventSource

describe('AgentRunner', () => {
  const mockAgentId = 'test-agent-123'
  const mockWorldId = 'test-world-456'

  beforeEach(() => {
    vi.clearAllMocks()
    MockEventSource.reset()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  it('renders mission control interface', () => {
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)
    expect(screen.getByText('Mission Control 🚀')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Find the treasure/i)).toBeInTheDocument()
  })

  it('deploy button is disabled when goal is empty', () => {
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)
    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    expect(button).toBeDisabled()
  })

  it('deploy button is enabled when goal has text', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    expect(button).not.toBeDisabled()
  })

  it('connects to SSE stream on deploy', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
      const instance = MockEventSource.instances[0]
      expect(instance.url).toContain('/api/agents/deploy')
      expect(instance.url).toContain(`agent_id=${mockAgentId}`)
      expect(instance.url).toContain(`world_id=${mockWorldId}`)
      expect(instance.url).toContain('goal=Find%20the%20treasure')
    })
  })

  it('displays reasoning events', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const eventSource = MockEventSource.instances[0]
    eventSource.simulateEvent('reasoning', {
      text: 'Thinking about the best path',
      timestamp: new Date().toISOString()
    })

    await waitFor(() => {
      expect(screen.getByText(/Thinking about the best path/i)).toBeInTheDocument()
    })
  })

  it('displays tool_call events', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const eventSource = MockEventSource.instances[0]
    eventSource.simulateEvent('tool_call', {
      tool_name: 'move',
      parameters: { direction: 'north' },
      timestamp: new Date().toISOString()
    })

    await waitFor(() => {
      expect(screen.getByText(/Using move/i)).toBeInTheDocument()
    })
  })

  it('displays tool_result events with success indicator', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const eventSource = MockEventSource.instances[0]
    eventSource.simulateEvent('tool_result', {
      tool_name: 'move',
      success: true,
      result: 'Moved successfully',
      duration_ms: 50,
      timestamp: new Date().toISOString()
    })

    await waitFor(() => {
      expect(screen.getByText(/Moved successfully/i)).toBeInTheDocument()
    })
  })

  it('displays world_update events', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const eventSource = MockEventSource.instances[0]
    eventSource.simulateEvent('world_update', {
      agent_moved_from: [0, 0],
      agent_moved_to: [1, 0],
      cell_updated: { position: [1, 0] },
      timestamp: new Date().toISOString()
    })

    await waitFor(() => {
      expect(screen.getByText(/Moved to \[1, 0\]/i)).toBeInTheDocument()
    })
  })

  it('displays error events', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const eventSource = MockEventSource.instances[0]
    eventSource.simulateEvent('error', {
      error_type: 'tool_error',
      message: 'Tool execution failed',
      recoverable: true,
      timestamp: new Date().toISOString()
    })

    await waitFor(() => {
      expect(screen.getByText(/Tool execution failed/i)).toBeInTheDocument()
    })
  })

  it('displays complete events and closes connection', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const eventSource = MockEventSource.instances[0]
    eventSource.simulateEvent('complete', {
      status: 'success',
      goal_achieved: true,
      total_steps: 10,
      timestamp: new Date().toISOString()
    })

    await waitFor(() => {
      expect(screen.getByText(/Mission success!/i)).toBeInTheDocument()
      expect(eventSource.readyState).toBe(2) // closed
    })
  })

  it('shows stop button when deploying', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const button = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Stop Mission/i })).toBeInTheDocument()
    })
  })

  it('stops mission when stop button is clicked', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const deployButton = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(deployButton)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const stopButton = screen.getByRole('button', { name: /Stop Mission/i })
    await user.click(stopButton)

    await waitFor(() => {
      const eventSource = MockEventSource.instances[0]
      expect(eventSource.readyState).toBe(2) // closed
    })
  })

  it('clears event log when clear button is clicked', async () => {
    const user = userEvent.setup()
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    const input = screen.getByPlaceholderText(/Find the treasure/i)
    await user.type(input, 'Find the treasure')

    const deployButton = screen.getByRole('button', { name: /Deploy Agent/i })
    await user.click(deployButton)

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBe(1)
    })

    const eventSource = MockEventSource.instances[0]
    eventSource.simulateEvent('reasoning', {
      text: 'Test event',
      timestamp: new Date().toISOString()
    })

    await waitFor(() => {
      expect(screen.getByText(/Test event/i)).toBeInTheDocument()
    })

    // Stop mission first
    const stopButton = screen.getByRole('button', { name: /Stop Mission/i })
    await user.click(stopButton)

    // Then clear
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Clear Log/i })).toBeInTheDocument()
    })

    const clearButton = screen.getByRole('button', { name: /Clear Log/i })
    await user.click(clearButton)

    await waitFor(() => {
      expect(screen.queryByText(/Test event/i)).not.toBeInTheDocument()
    })
  })

  it('shows empty state when no events', () => {
    render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)
    expect(screen.getByText(/No events yet/i)).toBeInTheDocument()
  })

  it('cleans up EventSource on unmount', () => {
    const { unmount } = render(<AgentRunner agentId={mockAgentId} worldId={mockWorldId} />)

    unmount()

    // Should not throw or cause memory leaks
    expect(MockEventSource.instances.length).toBe(0)
  })
})
