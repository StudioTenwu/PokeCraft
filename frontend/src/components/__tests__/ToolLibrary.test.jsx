import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import ToolLibrary from '../ToolLibrary'

// Mock fetch
global.fetch = vi.fn()

// Mock window.confirm
global.confirm = vi.fn()

describe('ToolLibrary', () => {
  const mockAgentId = 'test-agent-123'
  const mockOnToolDeleted = vi.fn()

  const mockTools = [
    {
      name: 'jump_tool',
      description: 'Lets agent jump over obstacles',
      category: 'Movement',
      code: 'def jump(): pass'
    },
    {
      name: 'scan_tool',
      description: 'Scans the environment',
      category: 'Perception',
      code: 'def scan(): pass'
    },
    {
      name: 'interact_tool',
      description: 'Interacts with objects',
      category: 'Interaction',
      code: 'def interact(): pass'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch.mockClear()
    global.confirm.mockClear()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  it('fetches and displays tools on mount', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText('jump_tool')).toBeInTheDocument()
      expect(screen.getByText('scan_tool')).toBeInTheDocument()
      expect(screen.getByText('interact_tool')).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    global.fetch.mockImplementationOnce(() =>
      new Promise(resolve =>
        setTimeout(() =>
          resolve({
            ok: true,
            json: async () => mockTools
          }), 100)
      )
    )

    render(<ToolLibrary agentId={mockAgentId} />)
    expect(screen.getByText(/Loading tools.../i)).toBeInTheDocument()
  })

  it('displays empty state when no tools exist', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => []
    })

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText(/No tools yet!/i)).toBeInTheDocument()
    })
  })

  it('applies correct category colors', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      const cards = screen.getAllByText(/tool$/i).map(el => el.closest('div'))
      expect(cards.length).toBeGreaterThan(0)
    })
  })

  it('toggles code view when view code button is clicked', async () => {
    const user = userEvent.setup()

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText('jump_tool')).toBeInTheDocument()
    })

    const viewCodeButtons = screen.getAllByText(/View Code/i)
    await user.click(viewCodeButtons[0])

    await waitFor(() => {
      expect(screen.getByText(/def jump/)).toBeInTheDocument()
      expect(screen.getByText(/Hide Code/i)).toBeInTheDocument()
    })

    // Click again to hide
    const hideCodeButton = screen.getByText(/Hide Code/i)
    await user.click(hideCodeButton)

    await waitFor(() => {
      expect(screen.queryByText(/def jump/)).not.toBeInTheDocument()
    })
  })

  it('shows confirmation dialog when delete is clicked', async () => {
    const user = userEvent.setup()

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    global.confirm.mockReturnValueOnce(false) // User cancels

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText('jump_tool')).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByText(/Delete/i)
    await user.click(deleteButtons[0])

    expect(global.confirm).toHaveBeenCalledWith(
      expect.stringContaining('Are you sure')
    )
  })

  it('deletes tool when confirmed', async () => {
    const user = userEvent.setup()

    // Mock initial fetch
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    // Mock delete request
    global.fetch.mockResolvedValueOnce({
      ok: true
    })

    global.confirm.mockReturnValueOnce(true) // User confirms

    render(<ToolLibrary agentId={mockAgentId} onToolDeleted={mockOnToolDeleted} />)

    await waitFor(() => {
      expect(screen.getByText('jump_tool')).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByText(/Delete/i)
    await user.click(deleteButtons[0])

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tools/jump_tool',
        { method: 'DELETE' }
      )
    })

    await waitFor(() => {
      expect(mockOnToolDeleted).toHaveBeenCalledWith('jump_tool')
    })
  })

  it('removes tool from list after successful deletion', async () => {
    const user = userEvent.setup()

    // Mock initial fetch
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    // Mock delete request
    global.fetch.mockResolvedValueOnce({
      ok: true
    })

    global.confirm.mockReturnValueOnce(true)

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText('jump_tool')).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByText(/Delete/i)
    await user.click(deleteButtons[0])

    await waitFor(() => {
      expect(screen.queryByText('jump_tool')).not.toBeInTheDocument()
    })
  })

  it('displays error message when fetch fails', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'))

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText(/Network error/i)).toBeInTheDocument()
    })
  })

  it('shows tool count when tools exist', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText(/3 skills learned/i)).toBeInTheDocument()
    })
  })

  it('displays category badges', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTools
    })

    render(<ToolLibrary agentId={mockAgentId} />)

    await waitFor(() => {
      expect(screen.getByText('Movement')).toBeInTheDocument()
      expect(screen.getByText('Perception')).toBeInTheDocument()
      expect(screen.getByText('Interaction')).toBeInTheDocument()
    })
  })
})
