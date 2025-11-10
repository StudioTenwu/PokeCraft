import { useState } from 'react'
import PropTypes from 'prop-types'
import { createWorld } from '../api'
import WorldCanvas from './WorldCanvas'

export default function WorldCreation({ agent, onWorldCreated }) {
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [world, setWorld] = useState(null)
  const [error, setError] = useState(null)

  const handleCreateWorld = async (e) => {
    e.preventDefault()
    if (!description.trim() || !agent?.id) return

    setLoading(true)
    setError(null)

    try {
      const worldData = await createWorld(agent.id, description)
      setWorld(worldData)
      setDescription('') // Clear input after success

      // Call callback if provided
      if (onWorldCreated) {
        onWorldCreated(worldData)
      }
    } catch (err) {
      setError(err.message || 'Failed to create world')
      console.error('Error creating world:', err)
    } finally {
      setLoading(false)
    }
  }

  // If world was created, show it
  if (world) {
    return <WorldCanvas world={world} />
  }

  return (
    <div className="pokemon-container">
      <h2 className="font-pixel text-lg mb-4" style={{ color: 'var(--text-primary)' }}>
        🌍 Create a World for {agent?.name}
      </h2>

      <form onSubmit={handleCreateWorld} className="space-y-4">
        <div>
          <label
            htmlFor="world-description"
            className="block font-pixel text-xs mb-2"
            style={{ color: 'var(--text-primary)' }}
          >
            Describe the world:
          </label>
          <textarea
            id="world-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., a peaceful meadow with a small pond..."
            className="w-full px-4 py-3 border-4 font-pixel text-xs"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
              color: 'var(--text-primary)',
              transition: 'all 0.3s ease'
            }}
            rows={4}
            disabled={loading}
            required
          />
        </div>

        {error && (
          <div
            className="p-3 border-2 font-pixel text-xs"
            style={{
              backgroundColor: '#ffebee',
              borderColor: '#f44336',
              color: '#c62828'
            }}
          >
            ⚠️ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !description.trim()}
          className="pokemon-button"
        >
          {loading ? '🌱 Generating World...' : '✨ Create World'}
        </button>
      </form>

      {loading && (
        <div className="mt-4 font-pixel text-xs text-center" style={{ color: 'var(--text-primary)' }}>
          <p className="mb-2">🎨 Drawing the world...</p>
          <div className="flex justify-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#8BC34A' }}></span>
            <span className="inline-block w-2 h-2 rounded-full animate-pulse" style={{ animationDelay: '0.2s', backgroundColor: '#FFD700' }}></span>
            <span className="inline-block w-2 h-2 rounded-full animate-pulse" style={{ animationDelay: '0.4s', backgroundColor: '#42A5F5' }}></span>
          </div>
        </div>
      )}
    </div>
  )
}

WorldCreation.propTypes = {
  agent: PropTypes.object.isRequired,
  onWorldCreated: PropTypes.func
}
