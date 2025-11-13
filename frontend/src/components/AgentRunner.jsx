import { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import PokemonButton from './PokemonButton'
import GameWorldView from './GameWorldView'
import EventLogSidebar from './EventLogSidebar'
import ThinkingPanel from './ThinkingPanel'
import { getWorld } from '../api'

/**
 * AgentRunner - Deploy agent with a goal and watch SSE stream in real-time with world visualization
 * @param {Object} props
 * @param {string} props.agentId - The agent ID to deploy
 * @param {string} props.worldId - The world ID to deploy in
 * @param {string} props.avatarUrl - The agent's avatar URL
 */
export default function AgentRunner({ agentId, worldId, avatarUrl }) {
  const [goal, setGoal] = useState('')
  const [events, setEvents] = useState([])
  const [thinkingEvents, setThinkingEvents] = useState([])
  const [deploying, setDeploying] = useState(false)
  const [error, setError] = useState(null)
  const [worldState, setWorldState] = useState(null)
  const [loadingWorld, setLoadingWorld] = useState(true)

  const eventSourceRef = useRef(null)

  // Load world data on mount
  useEffect(() => {
    const loadWorld = async () => {
      try {
        setLoadingWorld(true)
        const world = await getWorld(worldId)

        // Initialize world state with actual world data
        setWorldState({
          id: world.id,
          name: world.name,
          description: world.description,
          width: world.width,
          height: world.height,
          grid: world.grid,
          agentPosition: world.agent_position || [0, 0],
          game_type: world.game_type
        })

        setLoadingWorld(false)
      } catch (err) {
        console.error('Failed to load world:', err)
        setError('Failed to load world. Please try refreshing.')
        setLoadingWorld(false)
      }
    }

    loadWorld()
  }, [worldId])

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

    if (!worldState) {
      setError('World not loaded yet. Please wait.')
      return
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    setDeploying(true)
    setError(null)
    setEvents([])
    setThinkingEvents([])

    const url = `http://localhost:8000/api/agents/deploy?agent_id=${encodeURIComponent(agentId)}&world_id=${encodeURIComponent(worldId)}&goal=${encodeURIComponent(goal)}`
    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    // NEW EVENT TYPES: system, text, thinking
    eventSource.addEventListener('system', (e) => {
      const data = JSON.parse(e.data)
      setThinkingEvents(prev => [...prev, { type: 'system', ...data }])
    })

    eventSource.addEventListener('text', (e) => {
      const data = JSON.parse(e.data)
      setThinkingEvents(prev => [...prev, { type: 'text', ...data }])
    })

    eventSource.addEventListener('thinking', (e) => {
      const data = JSON.parse(e.data)
      setThinkingEvents(prev => [...prev, { type: 'thinking', ...data }])
    })

    // EXISTING EVENT TYPES (kept for EventLogSidebar compatibility)
    eventSource.addEventListener('reasoning', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'reasoning', ...data }])
    })

    eventSource.addEventListener('tool_call', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'tool_call', ...data }])
      setThinkingEvents(prev => [...prev, { type: 'tool_call', ...data }])
    })

    eventSource.addEventListener('tool_result', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'tool_result', ...data }])
      setThinkingEvents(prev => [...prev, { type: 'tool_result', ...data }])
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
      setThinkingEvents(prev => [...prev, { type: 'world_update', ...data }])
    })

    eventSource.addEventListener('error', (e) => {
      try {
        // Only parse if data exists (actual error event from backend)
        if (e.data) {
          const data = JSON.parse(e.data)
          setEvents(prev => [...prev, { type: 'error', ...data }])
          setThinkingEvents(prev => [...prev, { type: 'error', ...data }])
        }
      } catch (err) {
        console.error('Failed to parse error event:', err)
      }
    })

    eventSource.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data)
      setEvents(prev => [...prev, { type: 'complete', ...data }])
      setThinkingEvents(prev => [...prev, { type: 'complete', ...data }])
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
    setThinkingEvents([])
    setError(null)
  }

  // Show loading state while world is being fetched
  if (loadingWorld) {
    return (
      <div className="pokemon-container">
        <div className="text-center py-12">
          <div className="text-6xl mb-4 animate-bounce">🗺️</div>
          <p className="font-pixel text-pokemon-gold">Loading world...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="pokemon-container">
      <h2 className="font-pixel text-pokemon-gold text-xl mb-6 text-center"
          style={{ textShadow: '2px 2px 0px rgba(0,0,0,0.3)' }}>
        Mission Control 🚀
      </h2>

      {/* World info */}
      {worldState && (
        <div className="mb-4 p-3 bg-pokemon-gold/10 border-2 border-pokemon-gold rounded">
          <p className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
            🗺️ <strong>{worldState.name}</strong> ({worldState.width}x{worldState.height} • {worldState.game_type})
          </p>
        </div>
      )}

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
          disabled={deploying || loadingWorld}
          className="w-full p-3 border-4 border-pokemon-green rounded font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
          style={{ backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !deploying && !loadingWorld) {
              deployAgent()
            }
          }}
        />

        <div className="mt-3 flex gap-2">
          {!deploying ? (
            <PokemonButton onClick={deployAgent} disabled={!goal.trim() || loadingWorld}>
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

      {/* Three-column layout: ThinkingPanel (left 30%) + GameWorldView (center 45%) + EventLogSidebar (right 25%) */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: ThinkingPanel (30%) */}
        <div className="lg:w-[30%]">
          <ThinkingPanel
            events={thinkingEvents}
            isActive={deploying}
          />
        </div>

        {/* Center: Game World (45%) */}
        <div className="lg:w-[45%]">
          <GameWorldView
            worldState={worldState}
            events={events}
            deploying={deploying}
            avatarUrl={avatarUrl}
          />
        </div>

        {/* Right: Event Log (25%) */}
        <div className="lg:w-[25%]">
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
  worldId: PropTypes.string.isRequired,
  avatarUrl: PropTypes.string
}
