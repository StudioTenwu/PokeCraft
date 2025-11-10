import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '../test-utils';
import userEvent from '@testing-library/user-event';
import AgentCreation from './AgentCreation';
import { mockAgent } from '../test-utils';

// Mock the API module
vi.mock('../api', () => ({
  api: {
    createAgentStream: vi.fn()
  }
}));

// Mock AgentCard component
vi.mock('./AgentCard', () => ({
  default: ({ agent }) => <div data-testid="agent-card">Agent: {agent.name}</div>
}));

// Import the mocked api after setting up the mock
import { api } from '../api';

describe('AgentCreation', () => {
  const mockOnAgentCreated = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form with title', () => {
    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);
    expect(screen.getByText('Hatch Your Companion')).toBeInTheDocument();
  });

  it('renders textarea with placeholder', () => {
    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);
    expect(screen.getByPlaceholderText(/brave explorer/i)).toBeInTheDocument();
  });

  it('renders hatch button', () => {
    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);
    expect(screen.getByRole('button', { name: 'Hatch Companion' })).toBeInTheDocument();
  });

  it('shows error when submitting empty description', async () => {
    const user = userEvent.setup();
    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/please describe your companion/i)).toBeInTheDocument();
    });
  });

  it('shows error when submitting whitespace-only description', async () => {
    const user = userEvent.setup();
    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, '   ');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/please describe your companion/i)).toBeInTheDocument();
    });
  });

  it('calls createAgentStream API on valid submission', async () => {
    const user = userEvent.setup();
    api.createAgentStream.mockReturnValue(vi.fn());

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(api.createAgentStream).toHaveBeenCalledWith(
        'A brave explorer',
        expect.objectContaining({
          onLLMStart: expect.any(Function),
          onLLMComplete: expect.any(Function),
          onAvatarStart: expect.any(Function),
          onAvatarProgress: expect.any(Function),
          onAvatarComplete: expect.any(Function),
          onComplete: expect.any(Function),
          onError: expect.any(Function)
        })
      );
    });
  });

  it('shows egg emoji during LLM phase', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onLLMStart({ message: 'Dreaming up your companion...' });
      }, 0);
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('🥚')).toBeInTheDocument();
      expect(screen.getByText('Dreaming up your companion...')).toBeInTheDocument();
    });
  });

  it('shows progress messages during avatar generation', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation((desc, callbacks) => {
      // Call avatar progress callbacks using setTimeout to properly update state
      setTimeout(() => {
        act(() => {
          callbacks.onAvatarStart({ message: 'Hatching your companion...' });
        });
        setTimeout(() => {
          act(() => {
            callbacks.onAvatarProgress({
              message: 'Hatching... Step 1/2',
              step: 1,
              total: 2,
              percent: 50
            });
          });
        }, 10);
      }, 10);
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    // Check that avatar phase UI shows up
    await waitFor(() => {
      expect(screen.getByText('Hatching your companion...')).toBeInTheDocument();
    }, { timeout: 500 });
  });

  it('shows hatching emoji when avatar progress >= 50%', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onAvatarStart({ message: 'Hatching...' });
      }, 10);
      setTimeout(() => {
        callbacks.onAvatarProgress({
          message: 'Hatching...',
          step: 2,
          total: 2,
          percent: 100
        });
      }, 20);
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    // First check for egg
    await waitFor(() => {
      expect(screen.getByText('🥚')).toBeInTheDocument();
    });

    // Then check for hatching emoji
    await waitFor(() => {
      expect(screen.getByText('🐣')).toBeInTheDocument();
    });
  });

  it('renders success screen with AgentCard after completion', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onComplete({ agent: mockAgent });
      }, 0);
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Companion Hatched! ✨')).toBeInTheDocument();
      expect(screen.getByTestId('agent-card')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Hatch Another' })).toBeInTheDocument();
    });
  });

  it('calls onAgentCreated callback on completion', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onComplete({ agent: mockAgent });
      }, 0);
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(mockOnAgentCreated).toHaveBeenCalledWith(mockAgent);
    });
  });

  it('resets form on "Hatch Another" click', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onComplete({ agent: mockAgent });
      }, 0);
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Hatch Another' })).toBeInTheDocument();
    });

    const hatchAnotherButton = screen.getByRole('button', { name: 'Hatch Another' });
    await user.click(hatchAnotherButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Hatch Companion' })).toBeInTheDocument();
      expect(screen.getByRole('textbox')).toHaveValue('');
    });
  });

  it('shows error message on API error', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation((desc, callbacks) => {
      setTimeout(() => {
        callbacks.onError(new Error('Connection failed'));
      }, 0);
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/failed to hatch your companion/i)).toBeInTheDocument();
      expect(screen.getByText(/make sure the backend is running/i)).toBeInTheDocument();
    });
  });

  it('renders example buttons', () => {
    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);
    expect(screen.getByText(/cheerful robot/i)).toBeInTheDocument();
    expect(screen.getByText(/wise owl/i)).toBeInTheDocument();
    expect(screen.getByText(/playful cat/i)).toBeInTheDocument();
  });

  it('populates description when example button clicked', async () => {
    const user = userEvent.setup();
    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const exampleButton = screen.getByText(/cheerful robot/i);
    await user.click(exampleButton);

    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveValue('A cheerful robot who loves exploring and collecting shiny gems');
  });

  it('disables textarea and examples during loading', async () => {
    const user = userEvent.setup();

    api.createAgentStream.mockImplementation(() => {
      return vi.fn();
    });

    render(<AgentCreation onAgentCreated={mockOnAgentCreated} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A brave explorer');

    const button = screen.getByRole('button', { name: 'Hatch Companion' });
    await user.click(button);

    await waitFor(() => {
      expect(textarea).toBeDisabled();
    });

    const exampleButton = screen.getByText(/cheerful robot/i);
    expect(exampleButton).toBeDisabled();
  });
});
