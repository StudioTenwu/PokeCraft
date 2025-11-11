import { useRef, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import PokemonButton from './PokemonButton'

/**
 * EventItem - Compact rendering of a single event (Phase 5)
 */
function EventItem({ event }) {
  const icons = {
    reasoning: '🤔',
    tool_call: '⚙️',
    tool_result: event.success ? '✓' : '✗',
    world_update: '📍',
    error: '❌',
    complete: '🎉'
  }

  const icon = icons[event.type] || '•'

  return (
    <div className="p-2 text-sm border-b border-gray-700">
      <span className="mr-2">{icon}</span>

      {event.type === 'reasoning' && (
        <span className="text-yellow-400">
          {event.text?.slice(0, 60)}{event.text?.length > 60 ? '...' : ''}
        </span>
      )}

      {event.type === 'tool_call' && (
        <span className="text-blue-400">
          Using {event.tool_name}({JSON.stringify(event.parameters)})
        </span>
      )}

      {event.type === 'tool_result' && (
        <>
          <span className={event.success ? 'text-green-400' : 'text-red-400'}>
            {event.success ? 'Success' : 'Failed'}
          </span>
          {event.duration_ms && (
            <span className="text-gray-400 text-xs ml-1"> • {event.duration_ms}ms</span>
          )}
          {event.result && (
            <div className="text-xs text-gray-300 ml-6 mt-1">
              {String(event.result).slice(0, 50)}{String(event.result).length > 50 ? '...' : ''}
            </div>
          )}
        </>
      )}

      {event.type === 'world_update' && (
        <span className="text-cyan-400">
          Moved to [{event.agent_moved_to?.join(', ') || 'unknown'}]
        </span>
      )}

      {event.type === 'error' && (
        <>
          <span className="text-red-400">{event.message}</span>
          {event.recoverable && (
            <span className="text-yellow-400 text-xs ml-1">(recoverable)</span>
          )}
        </>
      )}

      {event.type === 'complete' && (
        <>
          <span className="text-green-400">Mission {event.status}!</span>
          {event.total_steps && (
            <span className="text-gray-400 text-xs ml-1"> • Steps: {event.total_steps}</span>
          )}
        </>
      )}

      <div className="text-xs text-gray-600 mt-1">
        {new Date(event.timestamp || Date.now()).toLocaleTimeString()}
      </div>
    </div>
  )
}

EventItem.propTypes = {
  event: PropTypes.object.isRequired
}

/**
 * EventGroup - Collapsible group of related events (Phase 5)
 */
function EventGroup({ title, events, defaultExpanded = false }) {
  const [expanded, setExpanded] = useState(defaultExpanded)

  return (
    <div className="border-l-4 border-blue-500 mb-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left p-2 hover:bg-gray-800 transition-colors"
      >
        <span className="mr-2">{expanded ? '▼' : '▶'}</span>
        <span className="font-pixel text-xs text-gray-300">
          {title} ({events.length} event{events.length !== 1 ? 's' : ''})
        </span>
      </button>
      {expanded && (
        <div className="ml-2">
          {events.map((e, i) => (
            <EventItem key={i} event={e} />
          ))}
        </div>
      )}
    </div>
  )
}

EventGroup.propTypes = {
  title: PropTypes.string.isRequired,
  events: PropTypes.array.isRequired,
  defaultExpanded: PropTypes.bool
}

/**
 * EventLogSidebar - Compact event stream sidebar (Phase 5: With grouping and stats)
 * @param {Object} props
 * @param {Array} props.events - Array of events to display
 * @param {boolean} props.deploying - Whether agent is currently deploying
 * @param {Function} props.onClear - Callback to clear event log
 */
export default function EventLogSidebar({ events, deploying, onClear }) {
  const logRef = useRef(null)
  const [groupingEnabled, setGroupingEnabled] = useState(false)

  // Auto-scroll to bottom
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [events])

  // Group events by tool execution cycles (tool_call -> tool_result)
  const groupEvents = (events) => {
    const groups = []
    let currentGroup = []
    let groupIndex = 0

    events.forEach((event) => {
      if (event.type === 'tool_call') {
        if (currentGroup.length > 0) {
          groups.push({
            title: `Tool Execution #${groupIndex + 1}`,
            events: currentGroup
          })
          groupIndex++
        }
        currentGroup = [event]
      } else if (event.type === 'tool_result' && currentGroup.length > 0) {
        currentGroup.push(event)
        groups.push({
          title: `Tool Execution #${groupIndex + 1}`,
          events: currentGroup
        })
        groupIndex++
        currentGroup = []
      } else {
        if (currentGroup.length > 0) {
          currentGroup.push(event)
        } else {
          // Standalone events (reasoning, world_update, etc.)
          groups.push({
            title: event.type,
            events: [event],
            standalone: true
          })
        }
      }
    })

    if (currentGroup.length > 0) {
      groups.push({
        title: `Tool Execution #${groupIndex + 1}`,
        events: currentGroup
      })
    }

    return groups
  }

  // Calculate stats
  const stats = {
    total: events.length,
    toolCalls: events.filter(e => e.type === 'tool_call').length,
    successes: events.filter(e => e.type === 'tool_result' && e.success).length,
    errors: events.filter(e => e.type === 'error').length,
    worldUpdates: events.filter(e => e.type === 'world_update').length
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-pixel text-sm" style={{ color: 'var(--text-primary)' }}>
          Event Log
        </h3>
        {deploying && (
          <div className="flex items-center gap-2">
            <div className="pokeball-animation text-sm">⚽</div>
            <span className="font-pixel text-xs text-green-400">
              Live
            </span>
          </div>
        )}
      </div>

      {/* Controls */}
      {events.length > 0 && (
        <div className="flex gap-2 mb-3">
          <button
            onClick={onClear}
            disabled={deploying}
            className="px-2 py-1 text-xs font-pixel border-2 border-pokemon-red rounded hover:bg-pokemon-red hover:text-white transition-colors disabled:opacity-50"
            style={{ backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
          >
            Clear 🗑
          </button>
          <button
            onClick={() => setGroupingEnabled(!groupingEnabled)}
            className="px-2 py-1 text-xs font-pixel border-2 border-pokemon-green rounded hover:bg-pokemon-green hover:text-white transition-colors"
            style={{ backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
          >
            {groupingEnabled ? 'Ungroup' : 'Group'}
          </button>
        </div>
      )}

      {/* Event Stream */}
      <div
        ref={logRef}
        className="flex-1 bg-black text-green-400 font-mono text-xs rounded border-4 border-black overflow-y-auto"
        style={{ minHeight: '400px', maxHeight: '600px' }}
      >
        {events.length === 0 ? (
          <div className="text-gray-500 text-center py-8 px-4">
            <p>No events yet.</p>
            <p className="mt-2">Deploy an agent to see the action!</p>
          </div>
        ) : groupingEnabled ? (
          <div className="p-2">
            {groupEvents(events).map((group, i) => (
              group.standalone ? (
                <EventItem key={i} event={group.events[0]} />
              ) : (
                <EventGroup
                  key={i}
                  title={group.title}
                  events={group.events}
                  defaultExpanded={i === groupEvents(events).length - 1}
                />
              )
            ))}
          </div>
        ) : (
          <div className="p-2">
            {events.map((event, i) => (
              <EventItem key={i} event={event} />
            ))}
          </div>
        )}
      </div>

      {/* Stats */}
      {events.length > 0 && (
        <div className="mt-3 p-2 bg-gray-900 rounded border border-gray-700">
          <div className="font-pixel text-xs grid grid-cols-2 gap-2" style={{ color: 'var(--text-primary)' }}>
            <div>📊 Total: {stats.total}</div>
            <div>⚙️ Tools: {stats.toolCalls}</div>
            <div>✓ Success: {stats.successes}</div>
            <div>📍 Moves: {stats.worldUpdates}</div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-2 text-xs opacity-70" style={{ color: 'var(--text-primary)' }}>
        <p className="font-pixel">
          Legend: 🤔 Thinking • ⚙️ Tool • ✓ Success • 📍 Move
        </p>
      </div>
    </div>
  )
}

EventLogSidebar.propTypes = {
  events: PropTypes.array,
  deploying: PropTypes.bool,
  onClear: PropTypes.func.isRequired
}

EventLogSidebar.defaultProps = {
  events: [],
  deploying: false
}
