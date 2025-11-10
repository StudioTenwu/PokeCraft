import { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import PokemonButton from './PokemonButton'

/**
 * AgentRunner - Deploy agent with a goal and watch SSE stream in real-time with world visualization
 * @param {Object} props
 * @param {string} props.agentId - The agent ID to deploy
 * @param {string} props.worldId - The world ID to deploy in
 */
export default function AgentRunner({ agentId, worldId }) {
  const [goal, setGoal] = useState('')
  const [events, setEvents] = useState([])
  const [deploying, setDeploying] = useState(false)
  const [error, setError] = useState(null)
  const [worldState, setWorldState] = useState(null)

  const canvasRef = useRef(null)
  const eventSourceRef = useRef(null)
  const eventsEndRef = useRef(null)

  // Auto-scroll to bottom of events
  useEffect(() => {
    if (eventsEndRef.current && typeof eventsEndRef.current.scrollIntoView === 'function') {
      eventsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [events])

  // Clean up EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [])

  // Initialize canvas with world grid
  const initializeCanvas = (width, height) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    canvas.width = width * 32
    canvas.height = height * 32

    // Draw grid
    ctx.fillStyle = '#FFF4E6'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Draw grid lines
    ctx.strokeStyle = '#E0E0E0'
    ctx.lineWidth = 1

    for (let x = 0; x <= width; x++) {
      ctx.beginPath()
      ctx.moveTo(x * 32, 0)
      ctx.lineTo(x * 32, canvas.height)
      ctx.stroke()
    }

    for (let y = 0; y <= height; y++) {
      ctx.beginPath()
      ctx.moveTo(0, y * 32)
      ctx.lineTo(canvas.width, y * 32)
      ctx.stroke()
    }

    setWorldState({ width, height, agentPosition: [0, 0] })
  }

  // Update agent position on canvas (delta update)
  const updateAgentPosition = (fromPos, toPos) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')

    // Clear old position
    if (fromPos) {
      ctx.fillStyle = '#FFF4E6'
      ctx.fillRect(fromPos[0] * 32, fromPos[1] * 32, 32, 32)

      // Redraw grid lines for cleared cell
      ctx.strokeStyle = '#E0E0E0'
      ctx.lineWidth = 1
      ctx.strokeRect(fromPos[0] * 32, fromPos[1] * 32, 32, 32)
    }

    // Draw new position
    ctx.fillStyle = '#FFD700'
    ctx.fillRect(toPos[0] * 32, toPos[1] * 32, 32, 32)

    // Draw agent sprite
    ctx.font = '24px Arial'
    ctx.fillText('🤖', toPos[0] * 32 + 4, toPos[1] * 32 + 24)

    setWorldState(prev => ({
      ...prev,
      agentPosition: toPos
    }))
  }

  // Mark cell as visited (delta update)
  const markCellVisited = (position) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    ctx.globalAlpha = 0.3
    ctx.fillStyle = '#8BC34A'
    ctx.fillRect(position[0] * 32, position[1] * 32, 32, 32)
    ctx.globalAlpha = 1.0

    // Redraw agent if on this cell
    if (worldState?.agentPosition &&
        worldState.agentPosition[0] === position[0] &&
        worldState.agentPosition[1] === position[1]) {
      ctx.font = '24px Arial'
      ctx.fillText('🤖', position[0] * 32 + 4, position[1] * 32 + 24)
    }
  }

  // Render event in stream
  const renderEvent = (event) => {
    switch (event.type) {
      case 'reasoning':
        return <span className="text-yellow-400">🤔 {event.text}</span>
      case 'tool_call':
        return (
          <span className="text-blue-400">
            ⚙️ Using {event.tool_name}({JSON.stringify(event.parameters)})
          </span>
        )
      case 'tool_result':
        return (
          <span className={event.success ? "text-green-400" : "text-red-400"}>
            {event.success ? "✓" : "✗"} {event.result}
            {event.duration_ms && <span className="text-gray-400"> ({event.duration_ms}ms)</span>}
          </span>
        )
      case 'world_update':
        return (
          <span className="text-cyan-400">
            📍 Moved to [{event.agent_moved_to?.join(', ') || 'unknown'}]
          </span>
        )
      case 'error':
        return (
          <span className="text-red-400">
            ⚠️ {event.message}
            {event.recoverable && <span className="text-yellow-400"> (recoverable)</span>}
          </span>
        )
      case 'complete':
        return (
          <span className="text-green-400">
            🎉 Mission {event.status}!
            {event.total_steps && <span> (Steps: {event.total_steps})</span>}
          </span>
        )
      default:
        return <span className="text-gray-400">Unknown event: {event.type}</span>
    }
  }

  const deployAgent = () => {
    if (!goal.trim()) {
      setError('Please enter a mission goal!')
      return
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    setDeploying(true)
    setError(null)
    setEvents([])

    // Initialize canvas (assuming 10x10 grid for now)
    initializeCanvas(10, 10)

    const url = `http://localhost:8000/api/agents/deploy?agent_id=${encodeURIComponent(agentId)}&world_id=${encodeURIComponent(worldId)}&goal=${encodeURIComponent(goal)}`
    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.addEventListener('reasoning', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'reasoning', ...data }])
    })

    eventSource.addEventListener('tool_call', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'tool_call', ...data }])
    })

    eventSource.addEventListener('tool_result', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'tool_result', ...data }])
    })

    eventSource.addEventListener('world_update', (e) => {
      const data = JSON.parse(e.data)

      // Apply delta updates to canvas
      if (data.agent_moved_from && data.agent_moved_to) {
        updateAgentPosition(data.agent_moved_from, data.agent_moved_to)
      }

      if (data.cell_updated?.position) {
        markCellVisited(data.cell_updated.position)
      }

      setEvents(prev => [...prev, { type: 'world_update', ...data }])
    })

    eventSource.addEventListener('error', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'error', ...data }])
    })

    eventSource.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'complete', ...data }])
      eventSource.close()
      eventSourceRef.current = null
      setDeploying(false)
    })

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err)
      setError('Connection lost to server. Please try again.')
      eventSource.close()
      eventSourceRef.current = null
      setDeploying(false)
    }
  }

  const stopAgent = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setDeploying(false)
    setEvents(prev => [...prev, {
      type: 'error',
      message: 'Mission stopped by user',
      timestamp: new Date().toISOString()
    }])
  }

  const clearStream = () => {
    setEvents([])
    setError(null)
  }

  return (
    <div className="pokemon-container">
      <h2 className="font-pixel text-pokemon-gold text-xl mb-6 text-center"
          style={{ textShadow: '2px 2px 0px rgba(0,0,0,0.3)' }}>
        Mission Control 🚀
      </h2>

      {/* Goal Input */}
      <div className="mb-6">
        <label className="font-pixel text-sm mb-2 block" style={{ color: 'var(--text-primary)' }}>
          Mission Goal:
        </label>
        <input
          type="text"
          placeholder="Find the treasure..."
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          disabled={deploying}
          className="w-full p-3 border-4 border-pokemon-green rounded font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
          style={{ backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !deploying) {
              deployAgent()
            }
          }}
        />

        <div className="mt-3 flex gap-2">
          {!deploying ? (
            <PokemonButton onClick={deployAgent} disabled={!goal.trim()}>
              Deploy Agent 🚀
            </PokemonButton>
          ) : (
            <PokemonButton onClick={stopAgent} variant="red">
              Stop Mission ⏹
            </PokemonButton>
          )}

          {events.length > 0 && (
            <PokemonButton onClick={clearStream} disabled={deploying}>
              Clear Log 🗑
            </PokemonButton>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 border-4 border-pokemon-red bg-red-100 rounded">
          <p className="font-pixel text-xs text-pokemon-red">
            ⚠️ {error}
          </p>
        </div>
      )}

      {/* World Visualization */}
      {worldState && (
        <div className="mb-6">
          <h3 className="font-pixel text-sm mb-2" style={{ color: 'var(--text-primary)' }}>
            World View:
          </h3>
          <div className="flex justify-center">
            <canvas
              ref={canvasRef}
              className="border-4 border-pokemon-green rounded"
              style={{ imageRendering: 'pixelated' }}
            />
          </div>
        </div>
      )}

      {/* Stream Display */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-pixel text-sm" style={{ color: 'var(--text-primary)' }}>
            Event Stream:
          </h3>
          {deploying && (
            <div className="flex items-center gap-2">
              <div className="pokeball-animation text-xl">⚽</div>
              <span className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
                Running...
              </span>
            </div>
          )}
        </div>

        <div className="bg-black text-green-400 font-mono text-xs p-4 rounded h-96 overflow-y-auto border-4 border-black">
          {events.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              No events yet. Deploy an agent to see the action!
            </div>
          ) : (
            events.map((event, i) => (
              <div key={i} className="mb-2">
                <span className="text-gray-500">[{new Date(event.timestamp || Date.now()).toLocaleTimeString()}]</span>{' '}
                {renderEvent(event)}
              </div>
            ))
          )}
          <div ref={eventsEndRef} />
        </div>
      </div>

      {events.length > 0 && (
        <div className="mt-4 text-center">
          <p className="font-pixel text-xs opacity-70" style={{ color: 'var(--text-primary)' }}>
            💡 {events.length} event{events.length !== 1 ? 's' : ''} logged
          </p>
        </div>
      )}
    </div>
  )
}

AgentRunner.propTypes = {
  agentId: PropTypes.string.isRequired,
  worldId: PropTypes.string.isRequired
}
