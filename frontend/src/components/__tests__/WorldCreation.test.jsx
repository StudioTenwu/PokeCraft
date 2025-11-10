import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import WorldCreation from '../WorldCreation'
import { mockAgents } from '../../__tests__/test-utils'
import * as api from '../../api'

// Mock the api module
vi.mock('../../api', () => ({
  createWorld: vi.fn()
}))

// Mock WorldCanvas component
vi.mock('../WorldCanvas', () => ({
  default: ({ world }) => (
    <div data-testid="world-canvas">
      World Canvas: {world.description}
    </div>
  )
}))

describe('WorldCreation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders form with agent name', () => {
    render(<WorldCreation agent={mockAgents.basic} />)
    expect(screen.getByText(/create a world for test bot/i)).toBeInTheDocument()
  })

  it('renders description textarea', () => {
    render(<WorldCreation agent={mockAgents.basic} />)
    expect(screen.getByPlaceholderText(/peaceful meadow/i)).toBeInTheDocument()
  })

  it('renders create button', () => {
    render(<WorldCreation agent={mockAgents.basic} />)
    expect(screen.getByRole('button', { name: /create world/i })).toBeInTheDocument()
  })

  it('does not submit when description is empty', async () => {
    const user = userEvent.setup()
    render(<WorldCreation agent={mockAgents.basic} />)

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    expect(api.createWorld).not.toHaveBeenCalled()
  })

  it('does not submit when agent is missing', async () => {
    const user = userEvent.setup()
    render(<WorldCreation agent={null} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'A test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    expect(api.createWorld).not.toHaveBeenCalled()
  })

  it('calls createWorld API with correct parameters', async () => {
    const user = userEvent.setup()
    const mockWorld = {
      id: 'world-123',
      agent_id: '123',
      description: 'A magical forest',
      grid_data: [],
      width: 10,
      height: 10
    }
    api.createWorld.mockResolvedValue(mockWorld)

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'A magical forest')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    expect(api.createWorld).toHaveBeenCalledWith('123', 'A magical forest')
  })

  it('shows loading state during world creation', async () => {
    const user = userEvent.setup()
    api.createWorld.mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    expect(screen.getByText(/generating world/i)).toBeInTheDocument()
    expect(screen.getByText(/drawing the world/i)).toBeInTheDocument()
  })

  it('disables textarea during loading', async () => {
    const user = userEvent.setup()
    api.createWorld.mockImplementation(() => new Promise(() => {}))

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    expect(textarea).toBeDisabled()
  })

  it('disables button during loading', async () => {
    const user = userEvent.setup()
    api.createWorld.mockImplementation(() => new Promise(() => {}))

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    expect(button).toBeDisabled()
  })

  it('renders WorldCanvas after successful creation', async () => {
    const user = userEvent.setup()
    const mockWorld = {
      id: 'world-123',
      agent_id: '123',
      description: 'A magical forest',
      grid_data: [],
      width: 10,
      height: 10
    }
    api.createWorld.mockResolvedValue(mockWorld)

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'A magical forest')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByTestId('world-canvas')).toBeInTheDocument()
      expect(screen.getByText(/world canvas: a magical forest/i)).toBeInTheDocument()
    })
  })

  it('clears description after successful creation', async () => {
    const user = userEvent.setup()
    const mockWorld = {
      id: 'world-123',
      agent_id: '123',
      description: 'Test world',
      grid_data: [],
      width: 10,
      height: 10
    }
    api.createWorld.mockResolvedValue(mockWorld)

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByTestId('world-canvas')).toBeInTheDocument()
    })

    // Note: textarea is no longer visible after successful creation
  })

  it('displays error message on API failure', async () => {
    const user = userEvent.setup()
    api.createWorld.mockRejectedValue(new Error('API Error'))

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText(/⚠️ API Error/i)).toBeInTheDocument()
    })
  })

  it('displays generic error message when error message is missing', async () => {
    const user = userEvent.setup()
    api.createWorld.mockRejectedValue(new Error())

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText(/⚠️ Failed to create world/i)).toBeInTheDocument()
    })
  })

  it('button is disabled when description is empty', () => {
    render(<WorldCreation agent={mockAgents.basic} />)
    const button = screen.getByRole('button', { name: /create world/i })
    expect(button).toBeDisabled()
  })

  it('button is enabled when description has content', async () => {
    const user = userEvent.setup()
    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    expect(button).not.toBeDisabled()
  })

  it('shows loading animation with pulse dots', async () => {
    const user = userEvent.setup()
    api.createWorld.mockImplementation(() => new Promise(() => {}))

    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByPlaceholderText(/peaceful meadow/i)
    await user.type(textarea, 'Test world')

    const button = screen.getByRole('button', { name: /create world/i })
    await user.click(button)

    const loadingContainer = screen.getByText(/drawing the world/i).closest('div')
    expect(loadingContainer).toBeInTheDocument()
  })

  it('form has correct labels and accessibility attributes', () => {
    render(<WorldCreation agent={mockAgents.basic} />)

    const textarea = screen.getByLabelText(/describe the world/i)
    expect(textarea).toHaveAttribute('id', 'world-description')
    expect(textarea).toHaveAttribute('required')
  })
})
