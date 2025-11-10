import { describe, it, expect, vi } from 'vitest';
import { render, screen } from './test-utils';
import App from './App';

// Mock child components
vi.mock('./components/AgentCreation', () => ({
  default: ({ onAgentCreated }) => (
    <div data-testid="agent-creation">
      <button onClick={() => onAgentCreated({ id: 'test-1', name: 'Test Agent' })}>
        Create Agent
      </button>
    </div>
  )
}));

vi.mock('./components/AgentCard', () => ({
  default: ({ agent }) => (
    <div data-testid="agent-card">{agent.name}</div>
  )
}));

vi.mock('./components/ThemeToggle', () => ({
  default: () => <button data-testid="theme-toggle">Toggle Theme</button>
}));

vi.mock('./components/WorldCreation', () => ({
  default: ({ agent }) => (
    <div data-testid="world-creation">Create world for {agent.name}</div>
  )
}));

describe('App', () => {
  it('renders header with title', () => {
    render(<App />);
    expect(screen.getByText('AICraft')).toBeInTheDocument();
    expect(screen.getByText('Pokémon Edition')).toBeInTheDocument();
  });

  it('renders theme toggle', () => {
    render(<App />);
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
  });

  it('renders agent creation component', () => {
    render(<App />);
    expect(screen.getByTestId('agent-creation')).toBeInTheDocument();
  });

  it('renders tagline', () => {
    render(<App />);
    expect(screen.getByText(/Hatch your AI companion/i)).toBeInTheDocument();
  });

  it('shows backend info in footer', () => {
    render(<App />);
    expect(screen.getByText(/Backend: http:\/\/localhost:8000/i)).toBeInTheDocument();
  });

  // Removed outdated test for mock data that no longer exists in App.jsx
});
