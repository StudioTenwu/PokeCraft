import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import ToolCreator from '../ToolCreator'

// Mock fetch
global.fetch = vi.fn()

describe('ToolCreator', () => {
  const mockAgentId = 'test-agent-123'
  const mockOnToolCreated = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch.mockClear()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  it('renders tool creator form', () => {
    render(<ToolCreator agentId={mockAgentId} />)
    expect(screen.getByPlaceholderText(/Describe what you want/i)).toBeInTheDocument()
    expect(screen.getByText('Teach Your Agent a New Skill!')).toBeInTheDocument()
  })

  it('renders create button', () => {
    render(<ToolCreator agentId={mockAgentId} />)
    expect(screen.getByRole('button', { name: /Create Tool/i })).toBeInTheDocument()
  })

  it('button is disabled when description is empty', () => {
    render(<ToolCreator agentId={mockAgentId} />)
    const button = screen.getByRole('button', { name: /Create Tool/i })
    expect(button).toBeDisabled()
  })

  it('button is enabled when description has text', async () => {
    const user = userEvent.setup()
    render(<ToolCreator agentId={mockAgentId} />)

    const textarea = screen.getByPlaceholderText(/Describe what you want/i)
    await user.type(textarea, 'make a tool that jumps')

    const button = screen.getByRole('button', { name: /Create Tool/i })
    expect(button).not.toBeDisabled()
  })

  it('submits tool description on button click', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      tool_name: 'jump_tool',
      code: 'def jump(): pass',
      explanation: 'This tool lets your agent jump'
    }

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })

    render(<ToolCreator agentId={mockAgentId} onToolCreated={mockOnToolCreated} />)

    const textarea = screen.getByPlaceholderText(/Describe what you want/i)
    await user.type(textarea, 'make a tool that jumps')

    const button = screen.getByRole('button', { name: /Create Tool/i })
    await user.click(button)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tools/create',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: mockAgentId,
            description: 'make a tool that jumps'
          })
        })
      )
    })
  })

  it('displays generated code after successful creation', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      tool_name: 'jump_tool',
      code: 'def jump():\n    return "jumping"',
      explanation: 'This tool lets your agent jump'
    }

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })

    render(<ToolCreator agentId={mockAgentId} />)

    const textarea = screen.getByPlaceholderText(/Describe what you want/i)
    await user.type(textarea, 'make a tool that jumps')

    const button = screen.getByRole('button', { name: /Create Tool/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText(/Tool created: jump_tool/i)).toBeInTheDocument()
      expect(screen.getByText(/def jump/)).toBeInTheDocument()
    })
  })

  it('shows explanation when explain button is clicked', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      tool_name: 'jump_tool',
      code: 'def jump(): pass',
      explanation: 'This tool lets your agent jump'
    }

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })

    render(<ToolCreator agentId={mockAgentId} />)

    const textarea = screen.getByPlaceholderText(/Describe what you want/i)
    await user.type(textarea, 'make a tool that jumps')

    const button = screen.getByRole('button', { name: /Create Tool/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText(/Explain Tool/i)).toBeInTheDocument()
    })

    const explainButton = screen.getByText(/Explain Tool/i)
    await user.click(explainButton)

    await waitFor(() => {
      expect(screen.getByText(/This tool lets your agent jump/i)).toBeInTheDocument()
    })
  })

  it('displays error message on API failure', async () => {
    const user = userEvent.setup()

    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Failed to generate tool' })
    })

    render(<ToolCreator agentId={mockAgentId} />)

    const textarea = screen.getByPlaceholderText(/Describe what you want/i)
    await user.type(textarea, 'make a tool that jumps')

    const button = screen.getByRole('button', { name: /Create Tool/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText(/Failed to generate tool/i)).toBeInTheDocument()
    })
  })

  it('calls onToolCreated callback after successful creation', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      tool_name: 'jump_tool',
      code: 'def jump(): pass',
      explanation: 'This tool lets your agent jump'
    }

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })

    render(<ToolCreator agentId={mockAgentId} onToolCreated={mockOnToolCreated} />)

    const textarea = screen.getByPlaceholderText(/Describe what you want/i)
    await user.type(textarea, 'make a tool that jumps')

    const button = screen.getByRole('button', { name: /Create Tool/i })
    await user.click(button)

    await waitFor(() => {
      expect(mockOnToolCreated).toHaveBeenCalledWith(mockResponse)
    })
  })

  it('shows loading state during generation', async () => {
    const user = userEvent.setup()

    global.fetch.mockImplementationOnce(() =>
      new Promise(resolve =>
        setTimeout(() =>
          resolve({
            ok: true,
            json: async () => ({
              tool_name: 'jump_tool',
              code: 'def jump(): pass',
              explanation: 'This tool lets your agent jump'
            })
          }), 100)
      )
    )

    render(<ToolCreator agentId={mockAgentId} />)

    const textarea = screen.getByPlaceholderText(/Describe what you want/i)
    await user.type(textarea, 'make a tool that jumps')

    const button = screen.getByRole('button', { name: /Create Tool/i })
    await user.click(button)

    expect(screen.getByText(/Generating your tool.../i)).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.queryByText(/Generating your tool.../i)).not.toBeInTheDocument()
    })
  })
})
