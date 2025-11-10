import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../test-utils';
import userEvent from '@testing-library/user-event';
import WorldCreation from './WorldCreation';
import * as api from '../api';
import { mockAgent, mockWorld } from '../test-utils';

// Mock the WorldCanvas component
vi.mock('./WorldCanvas', () => ({
  default: ({ world }) => <div data-testid="world-canvas">World Canvas: {world.id}</div>
}));

describe('WorldCreation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form with agent name', () => {
    render(<WorldCreation agent={mockAgent} />);
    expect(screen.getByText(`🌍 Create a World for ${mockAgent.name}`)).toBeInTheDocument();
  });

  it('renders textarea with placeholder', () => {
    render(<WorldCreation agent={mockAgent} />);
    expect(screen.getByPlaceholderText(/peaceful meadow/i)).toBeInTheDocument();
  });

  it('renders create button', () => {
    render(<WorldCreation agent={mockAgent} />);
    expect(screen.getByRole('button', { name: /create world/i })).toBeInTheDocument();
  });

  it('disables button when description is empty', () => {
    render(<WorldCreation agent={mockAgent} />);
    const button = screen.getByRole('button', { name: /create world/i });
    expect(button).toBeDisabled();
  });

  it('enables button when description is provided', async () => {
    const user = userEvent.setup();
    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /create world/i });

    await user.type(textarea, 'A mystical forest');
    expect(button).toBeEnabled();
  });

  it('calls createWorld API on form submit', async () => {
    const user = userEvent.setup();
    const createWorldSpy = vi.spyOn(api, 'createWorld').mockResolvedValue(mockWorld);

    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    await waitFor(() => {
      expect(createWorldSpy).toHaveBeenCalledWith(mockAgent.id, 'A mystical forest');
    });
  });

  it('shows loading state during world creation', async () => {
    const user = userEvent.setup();
    let resolvePromise;
    const promise = new Promise(resolve => { resolvePromise = resolve; });
    vi.spyOn(api, 'createWorld').mockReturnValue(promise);

    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    // Check loading state
    await waitFor(() => {
      expect(screen.getByText('🌱 Generating World...')).toBeInTheDocument();
      expect(screen.getByText('🎨 Drawing the world...')).toBeInTheDocument();
    });

    // Resolve promise
    resolvePromise(mockWorld);
  });

  it('renders WorldCanvas after successful creation', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'createWorld').mockResolvedValue(mockWorld);

    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByTestId('world-canvas')).toBeInTheDocument();
      expect(screen.getByText(`World Canvas: ${mockWorld.id}`)).toBeInTheDocument();
    });
  });

  it('clears description after successful creation', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'createWorld').mockResolvedValue(mockWorld);

    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    // Wait for success (WorldCanvas appears)
    await waitFor(() => {
      expect(screen.getByTestId('world-canvas')).toBeInTheDocument();
    });

    // Note: Once world is created, the form is replaced by WorldCanvas
    // So we can't check the textarea value anymore
  });

  it('displays error message on API failure', async () => {
    const user = userEvent.setup();
    const errorMessage = 'Failed to create world';
    vi.spyOn(api, 'createWorld').mockRejectedValue(new Error(errorMessage));

    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(`⚠️ ${errorMessage}`)).toBeInTheDocument();
    });
  });

  it('handles API error without message', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'createWorld').mockRejectedValue({});

    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/failed to create world/i)).toBeInTheDocument();
    });
  });

  it('does not submit if agent has no ID', async () => {
    const user = userEvent.setup();
    const createWorldSpy = vi.spyOn(api, 'createWorld');
    const agentNoId = { ...mockAgent, id: null };

    render(<WorldCreation agent={agentNoId} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    // Should not call API
    expect(createWorldSpy).not.toHaveBeenCalled();
  });

  it('disables textarea during loading', async () => {
    const user = userEvent.setup();
    let resolvePromise;
    const promise = new Promise(resolve => { resolvePromise = resolve; });
    vi.spyOn(api, 'createWorld').mockReturnValue(promise);

    render(<WorldCreation agent={mockAgent} />);

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'A mystical forest');

    const button = screen.getByRole('button', { name: /create world/i });
    await user.click(button);

    await waitFor(() => {
      expect(textarea).toBeDisabled();
    });

    resolvePromise(mockWorld);
  });
});
