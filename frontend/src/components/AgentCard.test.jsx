import { describe, it, expect } from 'vitest';
import { render, screen } from '../test-utils';
import { mockAgent, mockAgentNoAvatar } from '../test-utils';
import AgentCard from './AgentCard';

describe('AgentCard', () => {
  it('renders agent name', () => {
    render(<AgentCard agent={mockAgent} />);
    expect(screen.getByText(mockAgent.name)).toBeInTheDocument();
  });

  it('renders agent backstory', () => {
    render(<AgentCard agent={mockAgent} />);
    expect(screen.getByText(mockAgent.backstory)).toBeInTheDocument();
  });

  it('renders personality traits', () => {
    render(<AgentCard agent={mockAgent} />);

    mockAgent.personality_traits.forEach(trait => {
      expect(screen.getByText(trait)).toBeInTheDocument();
    });
  });

  it('applies correct badge classes cycling through colors', () => {
    const agentWithManyTraits = {
      ...mockAgent,
      personality_traits: [
        'Trait1', 'Trait2', 'Trait3', 'Trait4', 'Trait5',
        'Trait6', 'Trait7', 'Trait8', 'Trait9', 'Trait10',
        'Trait11', 'Trait12', 'Trait13' // More than 11 colors to test cycling
      ]
    };

    render(<AgentCard agent={agentWithManyTraits} />);

    // First trait should have first color
    const firstBadge = screen.getByText('Trait1');
    expect(firstBadge).toHaveClass('personality-badge-brave');

    // 12th trait should cycle back to first color (index 11 % 11 = 0)
    const twelfthBadge = screen.getByText('Trait12');
    expect(twelfthBadge).toHaveClass('personality-badge-brave');
  });

  it('renders HTTP avatar URL', () => {
    const agentWithHttpAvatar = {
      ...mockAgent,
      avatar_url: 'http://example.com/avatar.png'
    };

    render(<AgentCard agent={agentWithHttpAvatar} />);

    const img = screen.getByRole('img', { name: agentWithHttpAvatar.name });
    expect(img).toHaveAttribute('src', 'http://example.com/avatar.png');
  });

  it('renders data URI avatar', () => {
    render(<AgentCard agent={mockAgent} />);

    // The data URI is rendered using dangerouslySetInnerHTML
    // Check that it exists in the DOM
    const container = screen.getByRole('img', { name: mockAgent.name }).closest('div');
    expect(container).toBeInTheDocument();
  });

  it('shows fallback emoji when no avatar', () => {
    render(<AgentCard agent={mockAgentNoAvatar} />);

    // The fallback emoji is in a div, not an img tag
    expect(screen.getByText('🤖')).toBeInTheDocument();
  });

  it('does not render personality section if no traits', () => {
    const agentNoTraits = {
      ...mockAgent,
      personality_traits: []
    };

    render(<AgentCard agent={agentNoTraits} />);

    expect(screen.queryByText('Personality:')).not.toBeInTheDocument();
  });

  it('does not render personality section if traits is null', () => {
    const agentNullTraits = {
      ...mockAgent,
      personality_traits: null
    };

    render(<AgentCard agent={agentNullTraits} />);

    expect(screen.queryByText('Personality:')).not.toBeInTheDocument();
  });

  it('renders with correct CSS classes', () => {
    const { container } = render(<AgentCard agent={mockAgent} />);

    const card = container.querySelector('.pokemon-card');
    expect(card).toBeInTheDocument();
  });
});
