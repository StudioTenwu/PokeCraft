import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import ActionDisplay from '../ActionDisplay'

global.fetch = vi.fn()

describe('ActionDisplay', () => {
  beforeEach(() => {
    fetch.mockClear()
  })

  it('should render a list of available actions', async () => {
    const mockActions = [
      { name: 'move_forward', description: 'Move one step forward' },
      { name: 'turn_left', description: 'Turn 90 degrees left' },
      { name: 'turn_right', description: 'Turn 90 degrees right' }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockActions
    })

    render(<ActionDisplay worldId="test-world-123" />)

    await waitFor(() => {
      expect(screen.getByText('move_forward')).toBeInTheDocument()
      expect(screen.getByText('turn_left')).toBeInTheDocument()
      expect(screen.getByText('turn_right')).toBeInTheDocument()
    })
  })

  it('should fetch actions from correct endpoint /api/actions/{worldId}', async () => {
    const mockActions = [
      { name: 'jump', description: 'Jump over obstacle' }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockActions
    })

    render(<ActionDisplay worldId="world-456" />)

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/actions/world-456')
    })
  })

  it('should display loading state while fetching', () => {
    fetch.mockImplementationOnce(() => new Promise(() => {}))

    render(<ActionDisplay worldId="test-world" />)

    expect(screen.getByText(/loading actions/i)).toBeInTheDocument()
  })

  it('should display error message when fetch fails', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))

    render(<ActionDisplay worldId="test-world" />)

    await waitFor(() => {
      expect(screen.getByText(/failed to load actions/i)).toBeInTheDocument()
    })
  })

  it('should display message when no actions available', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => []
    })

    render(<ActionDisplay worldId="test-world" />)

    await waitFor(() => {
      expect(screen.getByText(/no actions available/i)).toBeInTheDocument()
    })
  })

  it('should not fetch actions when worldId is not provided', () => {
    render(<ActionDisplay worldId={null} />)

    expect(fetch).not.toHaveBeenCalled()
    expect(screen.getByText(/select a world/i)).toBeInTheDocument()
  })
})
