import { useState } from 'react'
import PropTypes from 'prop-types'
import { createWorld } from '../api'
import WorldCanvas from './WorldCanvas'

const EXAMPLE_WORLDS = [
  "A sparkling crystal cave filled with colorful gems, mysterious passages, and glowing rock formations",
  "An ancient library tower with moving bookshelves, riddles carved in stone, and hidden chambers",
  "A cozy village where items mysteriously disappear and reappear, with friendly neighbors and a magic fountain",
  "An enchanted forest with creatures to help, glowing mushrooms, hidden paths, and magical springs"
]

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

  const handleExampleClick = (example) => {
    // If textarea has content, ask for confirmation before replacing
    if (description.trim() && !window.confirm('Replace your current description?')) return

    setDescription(example)
    setError(null)
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

      {/* Example worlds */}
      <div className="mt-12 p-6 bg-pokemon-green/20 border-2 border-pokemon-green rounded"
           role="region" aria-label="Example world descriptions">
        <p className="font-pixel text-sm text-pokemon-green mb-4 text-center">
          ✨ Example Worlds - Click to try!
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {EXAMPLE_WORLDS.map((example, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleExampleClick(example)}
              className="text-left px-4 py-3 hover:bg-pokemon-cream hover:scale-105
                       text-xs border-2 border-pokemon-green transition-all
                       font-sans rounded"
              style={{ backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
              disabled={loading}
              aria-label={`Use example world: ${example.slice(0, 50)}...`}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

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
