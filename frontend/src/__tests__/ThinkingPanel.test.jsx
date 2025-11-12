import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ThinkingPanel from '../components/ThinkingPanel'

describe('ThinkingPanel', () => {
  test('renders markdown in thinking events', () => {
    const events = [
      {
        type: 'thinking',
        text: '**Bold text** and *italic text*',
        timestamp: new Date().toISOString()
      }
    ]

    render(<ThinkingPanel events={events} isActive={false} />)

    // ReactMarkdown should render the markdown
    expect(screen.getByText(/Bold text/)).toBeInTheDocument()
  })

  test('renders tool calls with simplified view', () => {
    const events = [
      {
        type: 'tool_call',
        tool_name: 'move_direction',
        parameters: { direction: 'north' },
        timestamp: new Date().toISOString()
      }
    ]

    render(<ThinkingPanel events={events} isActive={false} />)

    // Should show action label and tool name
    expect(screen.getByText('Action')).toBeInTheDocument()
    expect(screen.getByText(/move_direction/)).toBeInTheDocument()
    expect(screen.getByText(/Going north/)).toBeInTheDocument()

    // Details should be collapsed by default
    expect(screen.getByText(/Show Details/)).toBeInTheDocument()
  })

  test('renders tool results with simplified view', () => {
    const events = [
      {
        type: 'tool_result',
        tool_name: 'move_direction',
        success: true,
        duration_ms: 123,
        result: { status: 'moved' },
        timestamp: new Date().toISOString()
      }
    ]

    render(<ThinkingPanel events={events} isActive={false} />)

    // Should show simplified success message
    expect(screen.getByText(/✓ Success/)).toBeInTheDocument()
    expect(screen.getByText(/123ms/)).toBeInTheDocument()

    // Details should be collapsed by default
    expect(screen.getByText(/Show Details/)).toBeInTheDocument()
  })

  test('renders complete events with child-friendly language', () => {
    const events = [
      {
        type: 'complete',
        status: 'completed',
        goal_achieved: true,
        total_steps: 5,
        total_tools_used: 3,
        timestamp: new Date().toISOString()
      }
    ]

    render(<ThinkingPanel events={events} isActive={false} />)

    // Should show child-friendly completion message
    expect(screen.getByText(/Finished/)).toBeInTheDocument()
    expect(screen.getByText(/Goal achieved/)).toBeInTheDocument()
    expect(screen.getByText(/5 steps taken/)).toBeInTheDocument()
    expect(screen.getByText(/3 actions used/)).toBeInTheDocument()
  })

  test('hides system events by default', () => {
    const events = [
      {
        type: 'system',
        text: 'Technical system message',
        timestamp: new Date().toISOString()
      }
    ]

    render(<ThinkingPanel events={events} isActive={false} />)

    // System text should not be visible by default
    expect(screen.queryByText('Technical system message')).not.toBeInTheDocument()

    // Should have show details button
    expect(screen.getByText(/Show Details/)).toBeInTheDocument()
  })

  test('shows child-friendly stats', () => {
    const events = [
      { type: 'thinking', text: 'thinking', timestamp: new Date().toISOString() },
      { type: 'tool_call', tool_name: 'test', timestamp: new Date().toISOString() },
      { type: 'world_update', message: 'moved', timestamp: new Date().toISOString() }
    ]

    render(<ThinkingPanel events={events} isActive={false} />)

    // Should show child-friendly stat labels
    expect(screen.getByText(/3 events/)).toBeInTheDocument()
    expect(screen.getByText(/1 thoughts/)).toBeInTheDocument()
    expect(screen.getByText(/1 actions/)).toBeInTheDocument()
    expect(screen.getByText(/1 moves/)).toBeInTheDocument()
  })
})
