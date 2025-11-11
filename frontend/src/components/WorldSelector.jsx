import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

/**
 * WorldSelector - Dropdown to select a world for tool creation
 * @param {Object} props
 * @param {Function} props.onWorldSelect - Callback when world is selected
 */
export default function WorldSelector({ onWorldSelect }) {
  const [worlds, setWorlds] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedWorld, setSelectedWorld] = useState('')

  useEffect(() => {
    const fetchWorlds = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/worlds')

        if (!response.ok) {
          throw new Error('Failed to fetch worlds')
        }

        const data = await response.json()
        setWorlds(data)
        setError(null)
      } catch (err) {
        setError('Failed to load worlds')
        console.error('Error fetching worlds:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchWorlds()
  }, [])

  const handleWorldChange = (e) => {
    const worldId = e.target.value
    setSelectedWorld(worldId)

    if (onWorldSelect) {
      onWorldSelect(worldId)
    }
  }

  if (loading) {
    return (
      <div className="pokemon-container">
        <p className="font-pixel text-xs text-center" style={{ color: 'var(--text-primary)' }}>
          Loading worlds...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="pokemon-container">
        <p className="font-pixel text-xs text-center text-pokemon-red">
          ⚠️ {error}
        </p>
      </div>
    )
  }

  return (
    <div className="pokemon-container">
      <label
        htmlFor="world-select"
        className="font-pixel text-sm mb-2 block"
        style={{ color: 'var(--text-primary)' }}
      >
        Select a World:
      </label>
      <select
        id="world-select"
        className="w-full p-3 border-4 border-pokemon-green rounded font-pixel text-sm bg-white text-black focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
        value={selectedWorld}
        onChange={handleWorldChange}
      >
        <option value="">-- Choose a world --</option>
        {worlds.map((world) => (
          <option key={world.id} value={world.id}>
            {world.name}
          </option>
        ))}
      </select>
    </div>
  )
}

WorldSelector.propTypes = {
  onWorldSelect: PropTypes.func.isRequired
}
