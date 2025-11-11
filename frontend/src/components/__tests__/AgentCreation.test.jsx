import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import AgentCreation from '../AgentCreation'
import * as api from '../../api'

// Mock the api module
vi.mock('../../api', () => ({
  api: {
    createAgentStream: vi.fn()
  }
}))

describe('AgentCreation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  it('renders the form with description textarea', () => {
    render(<AgentCreation />)
    expect(screen.getByPlaceholderText(/brave explorer/i)).toBeInTheDocument()
    expect(screen.getByText('Hatch Your Pokemon')).toBeInTheDocument()
  })

  it('shows error when submitting empty description', async () => {
    const user = userEvent.setup()
    render(<AgentCreation />)

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    expect(screen.getByText(/please describe your pokemon/i)).toBeInTheDocument()
  })

  it('does not call API when description is empty', async () => {
    const user = userEvent.setup()
    render(<AgentCreation />)

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    expect(api.api.createAgentStream).not.toHaveBeenCalled()
  })

  it('calls API with correct description on submit', async () => {
    const user = userEvent.setup()
    const mockCleanup = vi.fn()
    api.api.createAgentStream.mockReturnValue(mockCleanup)

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'A helpful robot')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    expect(api.api.createAgentStream).toHaveBeenCalledWith(
      'A helpful robot',
      expect.objectContaining({
        onLLMStart: expect.any(Function),
        onLLMComplete: expect.any(Function),
        onAvatarStart: expect.any(Function),
        onAvatarProgress: expect.any(Function),
        onAvatarComplete: expect.any(Function),
        onComplete: expect.any(Function),
        onError: expect.any(Function)
      })
    )
  })

  it('shows loading state with egg emoji during creation', async () => {
    const user = userEvent.setup()
    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onLLMStart?.({ message: 'Dreaming up your pokemon...' })
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'A test bot')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    expect(screen.getByText('🥚')).toBeInTheDocument()
    expect(screen.getByText(/dreaming up your pokemon/i)).toBeInTheDocument()
  })

  it('updates progress indicators from LLM to Avatar phase', async () => {
    const user = userEvent.setup()
    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onLLMStart?.({ message: 'Dreaming...' })
      setTimeout(() => {
        callbacks.onAvatarStart?.({ message: 'Hatching...' })
      }, 50)
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    // LLM phase
    expect(screen.getByText(/dreaming/i)).toBeInTheDocument()

    // Avatar phase
    await waitFor(() => {
      expect(screen.getByText(/hatching/i)).toBeInTheDocument()
    }, { timeout: 100 })
  })

  it('shows progress bar during avatar generation', async () => {
    const user = userEvent.setup()
    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onAvatarStart?.({ message: 'Hatching...' })
      callbacks.onAvatarProgress?.({ step: 1, total: 2, percent: 50, message: 'Step 1/2' })
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Step 1/2 - 50%')).toBeInTheDocument()
    })
  })

  it('displays AgentCard after successful creation', async () => {
    const user = userEvent.setup()
    const mockAgent = {
      id: '123',
      name: 'Test Bot',
      backstory: 'A test bot',
      personality_traits: ['Helpful'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onComplete?.({ agent: mockAgent })
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Pokemon Hatched! ✨')).toBeInTheDocument()
      expect(screen.getByText('Test Bot')).toBeInTheDocument()
    })
  })

  it('calls onAgentCreated callback after completion', async () => {
    const user = userEvent.setup()
    const onAgentCreated = vi.fn()
    const mockAgent = {
      id: '123',
      name: 'Test Bot',
      backstory: 'A test bot',
      personality_traits: ['Helpful'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onComplete?.({ agent: mockAgent })
      return vi.fn()
    })

    render(<AgentCreation onAgentCreated={onAgentCreated} />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    await waitFor(() => {
      expect(onAgentCreated).toHaveBeenCalledWith(mockAgent)
    })
  })

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup()
    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onError?.(new Error('API Error'))
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText(/failed to hatch your pokemon/i)).toBeInTheDocument()
    })
  })

  it('example button clicks populate description', async () => {
    const user = userEvent.setup()
    render(<AgentCreation />)

    const exampleButton = screen.getByText(/cheerful robot who loves exploring/i)
    await user.click(exampleButton)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    expect(textarea).toHaveValue('A cheerful robot who loves exploring and collecting shiny gems')
  })

  it('shows "Hatch Another" button after successful creation', async () => {
    const user = userEvent.setup()
    const mockAgent = {
      id: '123',
      name: 'Test Bot',
      backstory: 'A test bot',
      personality_traits: ['Helpful'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onComplete?.({ agent: mockAgent })
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /hatch another/i })).toBeInTheDocument()
    })
  })

  it('resets form when "Hatch Another" is clicked', async () => {
    const user = userEvent.setup()
    const mockAgent = {
      id: '123',
      name: 'Test Bot',
      backstory: 'A test bot',
      personality_traits: ['Helpful'],
      avatar_url: null
    }

    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onComplete?.({ agent: mockAgent })
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const createButton = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(createButton)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /hatch another/i })).toBeInTheDocument()
    })

    const hatchAnotherButton = screen.getByRole('button', { name: /hatch another/i })
    await user.click(hatchAnotherButton)

    // Form should be back
    expect(screen.getByPlaceholderText(/brave explorer/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /hatch pokemon/i })).toBeInTheDocument()
  })

  it('disables textarea during loading', async () => {
    const user = userEvent.setup()
    api.api.createAgentStream.mockImplementation(() => vi.fn())

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    expect(textarea).toBeDisabled()
  })

  it('shows hatching egg emoji (🐣) when avatar progress >= 50%', async () => {
    const user = userEvent.setup()
    api.api.createAgentStream.mockImplementation((desc, callbacks) => {
      callbacks.onAvatarStart?.({ message: 'Hatching...' })
      callbacks.onAvatarProgress?.({ step: 2, total: 2, percent: 100, message: 'Step 2/2' })
      return vi.fn()
    })

    render(<AgentCreation />)

    const textarea = screen.getByPlaceholderText(/brave explorer/i)
    await user.type(textarea, 'Test')

    const button = screen.getByRole('button', { name: /hatch pokemon/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('🐣')).toBeInTheDocument()
    })
  })
})
