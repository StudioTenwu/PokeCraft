import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import App from '../../App'
import * as api from '../../api'

// Mock API
vi.mock('../../api', () => ({
  api: {
    createAgentStream: vi.fn()
  }
}))

// Mock WorldCanvas to avoid PixiJS issues
vi.mock('../../components/WorldCanvas', () => ({
  default: ({ world }) => (
    <div data-testid="world-canvas">World Canvas: {world?.description}</div>
  )
}))

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('renders header with AICraft title', () => {
    render(<App />)
    expect(screen.getByText('AICraft')).toBeInTheDocument()
  })

  it('renders Pokémon Edition subtitle', () => {
    render(<App />)
    expect(screen.getByText('Pokémon Edition')).toBeInTheDocument()
  })

  it('renders theme toggle button', () => {
    render(<App />)
    // Theme toggle should have moon or sun emoji
    const themeButton = screen.getByRole('button', { name: /toggle theme/i })
    expect(themeButton).toBeInTheDocument()
  })

  it('renders mock agent card for testing', () => {
    render(<App />)
    expect(screen.getByText('Pixel Pal')).toBeInTheDocument()
    expect(screen.getByText(/brave companion born from retro gaming magic/i)).toBeInTheDocument()
  })

  it('renders AgentCreation component', () => {
    render(<App />)
    expect(screen.getByText('Hatch Your Companion')).toBeInTheDocument()
  })

  it('shows backend connection info in footer', () => {
    render(<App />)
    expect(screen.getByText(/backend: http:\/\/localhost:8000/i)).toBeInTheDocument()
  })

  it('displays agent count in footer after creating agents', async () => {
    const user = userEvent.setup()
    const mockAgent = {
      id: '123',
      name: 'New Bot',
      backstory: 'A new bot',
      personality_traits: ['Helpful'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onComplete?.({ agent: mockAgent })
      return vi.fn()
    })

    render(<App />)

    // Find and fill textarea
    const textareas = screen.getAllByPlaceholderText(/brave explorer/i)
    const textarea = textareas[0]
    await user.type(textarea, 'Test bot')

    // Click create button
    const createButtons = screen.getAllByRole('button', { name: /hatch companion/i })
    await user.click(createButtons[0])

    // Wait for agent to be created and displayed in footer
    await waitFor(() => {
      expect(screen.getByText(/1 companion hatched/i)).toBeInTheDocument()
    })
  })

  it('displays created agents in "Created Agents" section', async () => {
    const user = userEvent.setup()
    const mockAgent = {
      id: '456',
      name: 'Created Bot',
      backstory: 'A bot that was just created',
      personality_traits: ['Friendly'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      // Simulate async callback to allow state updates
      setTimeout(() => {
        callbacks.onComplete?.({ agent: mockAgent })
      }, 50)
      return vi.fn()
    })

    render(<App />)

    // Create agent
    const textareas = screen.getAllByPlaceholderText(/brave explorer/i)
    await user.type(textareas[0], 'Test')

    const createButtons = screen.getAllByRole('button', { name: /hatch companion/i })
    await user.click(createButtons[0])

    // Wait for agent to appear - it shows in a success screen first
    await waitFor(() => {
      expect(screen.getByText('Companion Hatched! ✨')).toBeInTheDocument()
    })

    // Now click "Hatch Another" to return to main view and see created agents
    const hatchAnotherButton = screen.getByRole('button', { name: /hatch another/i })
    await user.click(hatchAnotherButton)

    // Now created agents section should be visible
    await waitFor(() => {
      expect(screen.getByText('Created Agents')).toBeInTheDocument()
      expect(screen.getByText('Created Bot')).toBeInTheDocument()
    })
  })

  it('auto-selects newly created agent', async () => {
    const user = userEvent.setup()
    const mockAgent = {
      id: '789',
      name: 'Auto Selected Bot',
      backstory: 'Should be auto-selected',
      personality_traits: ['Smart'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onComplete?.({ agent: mockAgent })
      return vi.fn()
    })

    render(<App />)

    // Create agent
    const textareas = screen.getAllByPlaceholderText(/brave explorer/i)
    await user.type(textareas[0], 'Test')

    const createButtons = screen.getAllByRole('button', { name: /hatch companion/i })
    await user.click(createButtons[0])

    // World creation should appear for the new agent
    await waitFor(() => {
      expect(screen.getByText(/create a world for auto selected bot/i)).toBeInTheDocument()
    })
  })

  it('shows world creation form when agent is selected', async () => {
    const user = userEvent.setup()
    const mockAgent = {
      id: '999',
      name: 'World Ready Bot',
      backstory: 'Ready for a world',
      personality_traits: ['Adventurous'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onComplete?.({ agent: mockAgent })
      return vi.fn()
    })

    render(<App />)

    // Create agent
    const textareas = screen.getAllByPlaceholderText(/brave explorer/i)
    await user.type(textareas[0], 'Test')

    const createButtons = screen.getAllByRole('button', { name: /hatch companion/i })
    await user.click(createButtons[0])

    // Check world creation appears
    await waitFor(() => {
      expect(screen.getByText(/create a world for world ready bot/i)).toBeInTheDocument()
    })
  })

  it('applies gradient background styling', () => {
    const { container } = render(<App />)
    const mainDiv = container.firstChild
    expect(mainDiv).toHaveClass('min-h-screen')
  })

  it('renders with responsive padding', () => {
    const { container } = render(<App />)
    const mainDiv = container.firstChild
    expect(mainDiv).toHaveClass('p-4', 'sm:p-8')
  })

  it('shows testing colors header', () => {
    render(<App />)
    expect(screen.getByText(/testing personality colors/i)).toBeInTheDocument()
  })

  it.skip('handles multiple agents in state', async () => {
    const user = userEvent.setup()
    const mockAgent1 = {
      id: '1',
      name: 'First Bot',
      backstory: 'First companion',
      personality_traits: ['A'],
      avatar_url: null
    }
    const mockAgent2 = {
      id: '2',
      name: 'Second Bot',
      backstory: 'Second companion',
      personality_traits: ['B'],
      avatar_url: null
    }

    // First agent creation
    api.api.createAgentStream.mockImplementationOnce((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onComplete?.({ agent: mockAgent1 })
      }, 50)
      return vi.fn()
    })

    render(<App />)

    // Create first agent
    const textareas = screen.getAllByPlaceholderText(/brave explorer/i)
    await user.type(textareas[0], 'First agent')
    let createButtons = screen.getAllByRole('button', { name: /hatch companion/i })
    await user.click(createButtons[0])

    // Wait for first agent to complete
    await waitFor(() => {
      expect(screen.getByText('Companion Hatched! ✨')).toBeInTheDocument()
      expect(screen.getByText('First Bot')).toBeInTheDocument()
    }, { timeout: 2000 })

    // Click "Hatch Another"
    const hatchAnotherButton = screen.getByRole('button', { name: /hatch another/i })
    await user.click(hatchAnotherButton)

    // Second agent creation
    api.api.createAgentStream.mockImplementationOnce((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onComplete?.({ agent: mockAgent2 })
      }, 50)
      return vi.fn()
    })

    // Create second agent
    const textareas2 = screen.getAllByPlaceholderText(/brave explorer/i)
    await user.type(textareas2[0], 'Second agent')
    createButtons = screen.getAllByRole('button', { name: /hatch companion/i })
    await user.click(createButtons[0])

    // Wait for second agent
    await waitFor(() => {
      expect(screen.getByText('Companion Hatched! ✨')).toBeInTheDocument()
      expect(screen.getByText('Second Bot')).toBeInTheDocument()
    }, { timeout: 2000 })

    // Click "Hatch Another" again to see the full list
    const hatchAnotherButton2 = screen.getByRole('button', { name: /hatch another/i })
    await user.click(hatchAnotherButton2)

    // Now check the footer shows both agents
    await waitFor(() => {
      expect(screen.getByText(/2 companions hatched/i)).toBeInTheDocument()
    })
  })

  it('centers content with max-width constraint', () => {
    const { container } = render(<App />)
    const contentDiv = container.querySelector('.max-w-4xl.mx-auto')
    expect(contentDiv).toBeInTheDocument()
  })
})
