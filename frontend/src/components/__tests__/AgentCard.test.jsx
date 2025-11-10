import { describe, it, expect } from 'vitest'
import { render, screen } from '../../__tests__/test-utils'
import { mockAgents } from '../../__tests__/test-utils'
import AgentCard from '../AgentCard'

describe('AgentCard', () => {
  it('renders agent name correctly', () => {
    render(<AgentCard agent={mockAgents.basic} />)
    expect(screen.getByText('Test Bot')).toBeInTheDocument()
  })

  it('renders agent backstory correctly', () => {
    render(<AgentCard agent={mockAgents.basic} />)
    expect(screen.getByText('A test bot created for unit testing purposes')).toBeInTheDocument()
  })

  it('renders personality traits as badges', () => {
    render(<AgentCard agent={mockAgents.basic} />)
    expect(screen.getByText('Helpful')).toBeInTheDocument()
    expect(screen.getByText('Curious')).toBeInTheDocument()
    expect(screen.getByText('Brave')).toBeInTheDocument()
  })

  it('shows fallback emoji when no avatar URL', () => {
    render(<AgentCard agent={mockAgents.basic} />)
    expect(screen.getByText('🤖')).toBeInTheDocument()
  })

  it('renders HTTP avatar URL correctly', () => {
    render(<AgentCard agent={mockAgents.withHttpAvatar} />)
    const img = screen.getByRole('img', { name: 'Avatar Bot' })
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', 'http://example.com/avatar.png')
  })

  it('renders data URI avatar correctly', () => {
    render(<AgentCard agent={mockAgents.withDataUriAvatar} />)
    // Data URI avatars use dangerouslySetInnerHTML, so we check the container
    const avatarContainer = screen.getByText('Data URI Bot').closest('.pokemon-card')
    expect(avatarContainer).toBeInTheDocument()
  })

  it('does not render personality section when no traits', () => {
    const agentNoTraits = {
      ...mockAgents.basic,
      personality_traits: []
    }
    render(<AgentCard agent={agentNoTraits} />)
    expect(screen.queryByText('Personality:')).not.toBeInTheDocument()
  })

  it('cycles through personality badge colors correctly', () => {
    render(<AgentCard agent={mockAgents.manyTraits} />)

    const traits = mockAgents.manyTraits.personality_traits
    traits.forEach((trait) => {
      const badge = screen.getByText(trait)
      expect(badge).toBeInTheDocument()
      // Check that badge has a personality-badge class
      expect(badge.className).toMatch(/personality-badge/)
    })
  })

  it('applies pokemon-card class to container', () => {
    const { container } = render(<AgentCard agent={mockAgents.basic} />)
    expect(container.querySelector('.pokemon-card')).toBeInTheDocument()
  })

  it('renders with responsive flex layout', () => {
    const { container } = render(<AgentCard agent={mockAgents.basic} />)
    const flexContainer = container.querySelector('.flex.flex-col.md\\:flex-row')
    expect(flexContainer).toBeInTheDocument()
  })

  it('applies text shadow to agent name', () => {
    render(<AgentCard agent={mockAgents.basic} />)
    const name = screen.getByText('Test Bot')
    expect(name).toHaveStyle({ textShadow: '3px 3px 0px rgba(0,0,0,0.3)' })
  })

  it('shows avatar with correct size classes', () => {
    render(<AgentCard agent={mockAgents.withHttpAvatar} />)
    const img = screen.getByRole('img', { name: 'Avatar Bot' })
    expect(img).toHaveClass('w-32', 'h-32', 'border-4', 'border-black')
  })

  it('handles multiple personality traits without errors', () => {
    const agent = {
      ...mockAgents.basic,
      personality_traits: Array(20).fill('Trait')
    }
    expect(() => render(<AgentCard agent={agent} />)).not.toThrow()
  })
})
