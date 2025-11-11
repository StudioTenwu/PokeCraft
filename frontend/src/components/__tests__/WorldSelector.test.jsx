import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WorldSelector from '../WorldSelector'

global.fetch = vi.fn()

describe('WorldSelector', () => {
  beforeEach(() => {
    fetch.mockClear()
  })

  it('should render a dropdown for world selection', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => []
    })

    render(<WorldSelector onWorldSelect={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument()
      expect(screen.getByText(/select a world/i)).toBeInTheDocument()
    })
  })

  it('should fetch and display available worlds on mount', async () => {
    const mockWorlds = [
      { id: 'world-1', name: 'Test World 1', game_type: 'grid_navigation' },
      { id: 'world-2', name: 'Test World 2', game_type: 'grid_navigation' }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWorlds
    })

    render(<WorldSelector onWorldSelect={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Test World 1')).toBeInTheDocument()
      expect(screen.getByText('Test World 2')).toBeInTheDocument()
    })

    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/worlds')
  })

  it('should call onWorldSelect when a world is selected', async () => {
    const mockWorlds = [
      { id: 'world-1', name: 'Test World 1', game_type: 'grid_navigation' }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWorlds
    })

    const onWorldSelect = vi.fn()
    const user = userEvent.setup()

    render(<WorldSelector onWorldSelect={onWorldSelect} />)

    await waitFor(() => {
      expect(screen.getByText('Test World 1')).toBeInTheDocument()
    })

    const select = screen.getByRole('combobox')
    await user.selectOptions(select, 'world-1')

    expect(onWorldSelect).toHaveBeenCalledWith('world-1')
  })

  it('should display error message when fetch fails', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))

    render(<WorldSelector onWorldSelect={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText(/failed to load worlds/i)).toBeInTheDocument()
    })
  })

  it('should display loading state while fetching', () => {
    fetch.mockImplementationOnce(() => new Promise(() => {})) // Never resolves

    render(<WorldSelector onWorldSelect={vi.fn()} />)

    expect(screen.getByText(/loading worlds/i)).toBeInTheDocument()
  })
})
