import { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import PokemonButton from './PokemonButton'
import GameWorldView from './GameWorldView'
import EventLogSidebar from './EventLogSidebar'

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

  const eventSourceRef = useRef(null)

  // Clean up EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [])

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

    // Initialize world state (assuming 10x10 grid for now)
    setWorldState({ width: 10, height: 10, agentPosition: [0, 0] })

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

      // Update world state if agent moved
      if (data.agent_moved_to) {
        setWorldState(prev => ({
          ...prev,
          agentPosition: data.agent_moved_to
        }))
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

      {/* Two-column layout: Game World (left 65%) + Event Log (right 35%) */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: Game World (65%) */}
        <div className="lg:w-2/3">
          <GameWorldView
            worldState={worldState}
            events={events}
            deploying={deploying}
          />
        </div>

        {/* Right: Event Log (35%) */}
        <div className="lg:w-1/3">
          <EventLogSidebar
            events={events}
            deploying={deploying}
            onClear={clearStream}
          />
        </div>
      </div>
    </div>
  )
}

AgentRunner.propTypes = {
  agentId: PropTypes.string.isRequired,
  worldId: PropTypes.string.isRequired
}
