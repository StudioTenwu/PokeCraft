import { useRef, useEffect, useState } from 'react'
import PropTypes from 'prop-types'

/**
 * ThinkingItem - Renders a single thinking event with expandable JSON
 */
function ThinkingItem({ event }) {
  const [expanded, setExpanded] = useState(false)

  const eventConfig = {
    system: { icon: '🔧', color: 'text-gray-400', label: 'System' },
    text: { icon: '💬', color: 'text-blue-400', label: 'Response' },
    thinking: { icon: '🧠', color: 'text-yellow-400', label: 'Thinking' },
    tool_call: { icon: '🔨', color: 'text-green-400', label: 'Tool Call' },
    tool_result: { icon: '✅', color: 'text-cyan-400', label: 'Tool Result' },
    world_update: { icon: '🗺️', color: 'text-purple-400', label: 'World Update' },
    error: { icon: '❌', color: 'text-red-400', label: 'Error' },
    complete: { icon: '🎯', color: 'text-yellow-500', label: 'Complete' }
  }

  const config = eventConfig[event.type] || { icon: '•', color: 'text-gray-300', label: event.type }

  // Helper to safely format data for display
  const formatData = (data) => {
    if (typeof data === 'string') return data
    try {
      return JSON.stringify(data, null, 2)
    } catch {
      return String(data)
    }
  }

  // Helper to check if data is JSON-like (object/array)
  const isStructured = (data) => {
    return typeof data === 'object' && data !== null
  }

  return (
    <div className="p-3 border-b border-gray-700 hover:bg-gray-800 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-1">
          <span className="text-lg">{config.icon}</span>
          <span className={`font-pixel text-xs ${config.color}`}>
            {config.label}
          </span>
        </div>
        <div className="text-xs text-gray-600">
          {new Date(event.timestamp || Date.now()).toLocaleTimeString()}
        </div>
      </div>

      {/* Content */}
      <div className="mt-2 ml-7">
        {/* Text-based events */}
        {(event.type === 'system' || event.type === 'text' || event.type === 'thinking') && (
          <div className={`text-sm ${config.color}`}>
            {event.text}
          </div>
        )}

        {/* Tool Call */}
        {event.type === 'tool_call' && (
          <div className="text-sm">
            <div className="text-green-400 font-semibold mb-1">
              {event.tool_name}
            </div>
            {event.parameters && isStructured(event.parameters) && (
              <div>
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="text-xs text-gray-400 hover:text-gray-200 mb-1"
                >
                  {expanded ? '▼' : '▶'} Parameters
                </button>
                {expanded && (
                  <pre className="text-xs bg-gray-900 p-2 rounded overflow-x-auto text-gray-300">
                    {formatData(event.parameters)}
                  </pre>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tool Result */}
        {event.type === 'tool_result' && (
          <div className="text-sm">
            <div className={`mb-1 ${event.success ? 'text-green-400' : 'text-red-400'}`}>
              {event.success ? 'Success' : 'Failed'} • {event.tool_name}
              {event.duration_ms && (
                <span className="text-gray-400 text-xs ml-2">({event.duration_ms}ms)</span>
              )}
            </div>
            {event.result && (
              <div>
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="text-xs text-gray-400 hover:text-gray-200 mb-1"
                >
                  {expanded ? '▼' : '▶'} Result
                </button>
                {expanded && (
                  <pre className="text-xs bg-gray-900 p-2 rounded overflow-x-auto text-gray-300">
                    {formatData(event.result)}
                  </pre>
                )}
              </div>
            )}
          </div>
        )}

        {/* World Update */}
        {event.type === 'world_update' && (
          <div className="text-sm">
            {event.message && (
              <div className="text-purple-400 mb-1">{event.message}</div>
            )}
            {event.agent_position && (
              <div className="text-purple-300 text-xs">
                Position: [{event.agent_position.join(', ')}]
              </div>
            )}
            {event.agent_moved_to && (
              <div className="text-purple-300 text-xs">
                Moved to: [{event.agent_moved_to.join(', ')}]
              </div>
            )}
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-gray-400 hover:text-gray-200 mt-1"
            >
              {expanded ? '▼' : '▶'} Details
            </button>
            {expanded && (
              <pre className="text-xs bg-gray-900 p-2 rounded overflow-x-auto text-gray-300 mt-1">
                {formatData(event)}
              </pre>
            )}
          </div>
        )}

        {/* Error */}
        {event.type === 'error' && (
          <div className="text-sm">
            <div className="text-red-400 mb-1">{event.message}</div>
            {event.error_type && (
              <div className="text-red-300 text-xs">Type: {event.error_type}</div>
            )}
            {event.recoverable !== undefined && (
              <div className={`text-xs ${event.recoverable ? 'text-yellow-400' : 'text-red-300'}`}>
                {event.recoverable ? 'Recoverable' : 'Fatal'}
              </div>
            )}
          </div>
        )}

        {/* Complete */}
        {event.type === 'complete' && (
          <div className="text-sm">
            <div className="text-yellow-500 font-semibold mb-2">
              Status: {event.status}
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {event.total_steps !== undefined && (
                <div className="text-gray-300">Steps: {event.total_steps}</div>
              )}
              {event.total_tools_used !== undefined && (
                <div className="text-gray-300">Tools: {event.total_tools_used}</div>
              )}
              {event.goal_achieved !== undefined && (
                <div className={event.goal_achieved ? 'text-green-400' : 'text-red-400'}>
                  Goal: {event.goal_achieved ? 'Achieved' : 'Not Achieved'}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

ThinkingItem.propTypes = {
  event: PropTypes.shape({
    type: PropTypes.string.isRequired,
    timestamp: PropTypes.string,
    text: PropTypes.string,
    tool_name: PropTypes.string,
    parameters: PropTypes.any,
    result: PropTypes.any,
    success: PropTypes.bool,
    duration_ms: PropTypes.number,
    message: PropTypes.string,
    agent_position: PropTypes.array,
    agent_moved_to: PropTypes.array,
    error_type: PropTypes.string,
    recoverable: PropTypes.bool,
    status: PropTypes.string,
    total_steps: PropTypes.number,
    total_tools_used: PropTypes.number,
    goal_achieved: PropTypes.bool
  }).isRequired
}

/**
 * ThinkingPanel - Comprehensive agent cognition display
 * Shows ALL Claude Agent SDK message types in real-time
 *
 * @param {Object} props
 * @param {Array} props.events - Array of thinking events to display
 * @param {boolean} props.isActive - Whether agent is currently thinking
 */
export default function ThinkingPanel({ events, isActive }) {
  const panelRef = useRef(null)
  const [autoScroll, setAutoScroll] = useState(true)

  // Auto-scroll to latest event
  useEffect(() => {
    if (autoScroll && panelRef.current) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight
    }
  }, [events, autoScroll])

  // Calculate stats
  const stats = {
    total: events.length,
    thinking: events.filter(e => e.type === 'thinking').length,
    text: events.filter(e => e.type === 'text').length,
    tools: events.filter(e => e.type === 'tool_call').length,
    updates: events.filter(e => e.type === 'world_update').length,
    errors: events.filter(e => e.type === 'error').length
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-pixel text-sm" style={{ color: 'var(--text-primary)' }}>
          Agent Thinking
        </h3>
        {isActive && (
          <div className="flex items-center gap-2">
            <div className="pokeball-animation text-sm">🧠</div>
            <span className="font-pixel text-xs text-yellow-400">
              Active
            </span>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex gap-2 mb-3 items-center">
        <label className="flex items-center gap-2 text-xs font-pixel cursor-pointer" style={{ color: 'var(--text-primary)' }}>
          <input
            type="checkbox"
            checked={autoScroll}
            onChange={(e) => setAutoScroll(e.target.checked)}
            className="form-checkbox h-4 w-4"
          />
          Auto-scroll
        </label>
      </div>

      {/* Thinking Stream */}
      <div
        ref={panelRef}
        className="flex-1 bg-black rounded border-4 border-black overflow-y-auto"
        style={{ minHeight: '400px', maxHeight: '600px' }}
      >
        {events.length === 0 ? (
          <div className="text-gray-500 text-center py-8 px-4">
            <p className="text-4xl mb-4">🧠</p>
            <p>No thinking events yet.</p>
            <p className="mt-2">Deploy an agent to see their thought process!</p>
          </div>
        ) : (
          <div>
            {events.map((event, i) => (
              <ThinkingItem key={i} event={event} />
            ))}
          </div>
        )}
      </div>

      {/* Stats */}
      {events.length > 0 && (
        <div className="mt-3 p-2 bg-gray-900 rounded border border-gray-700">
          <div className="font-pixel text-xs grid grid-cols-3 gap-2" style={{ color: 'var(--text-primary)' }}>
            <div>📊 Total: {stats.total}</div>
            <div>🧠 Thinking: {stats.thinking}</div>
            <div>💬 Text: {stats.text}</div>
            <div>🔨 Tools: {stats.tools}</div>
            <div>🗺️ Updates: {stats.updates}</div>
            <div>❌ Errors: {stats.errors}</div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-2 text-xs opacity-70" style={{ color: 'var(--text-primary)' }}>
        <p className="font-pixel">
          Legend: 🔧 System • 💬 Text • 🧠 Thinking • 🔨 Tool • ✅ Result • 🗺️ Update
        </p>
      </div>
    </div>
  )
}

ThinkingPanel.propTypes = {
  events: PropTypes.array,
  isActive: PropTypes.bool
}

ThinkingPanel.defaultProps = {
  events: [],
  isActive: false
}
