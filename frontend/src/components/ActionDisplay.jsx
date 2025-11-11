import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

/**
 * ActionDisplay - Shows available actions for a selected world
 * @param {Object} props
 * @param {string} props.worldId - The world ID to fetch actions for
 */
export default function ActionDisplay({ worldId }) {
  const [actions, setActions] = useState({})  // Object with categories, not array
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!worldId) {
      setActions({})
      setLoading(false)
      setError(null)
      return
    }

    const fetchActions = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`http://localhost:8000/api/actions/${worldId}`)

        if (!response.ok) {
          throw new Error('Failed to fetch actions')
        }

        const data = await response.json()

        // The API returns {world: {...}, actions: {...}}
        // Extract the actions object
        if (data && data.actions) {
          setActions(data.actions)
        } else {
          setActions({})
        }
      } catch (err) {
        setError('Failed to load actions')
        console.error('Error fetching actions:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchActions()
  }, [worldId])

  if (!worldId) {
    return (
      <div className="pokemon-container">
        <p className="font-pixel text-xs text-center" style={{ color: 'var(--text-primary)' }}>
          Select a world to see available actions
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="pokemon-container">
        <p className="font-pixel text-xs text-center" style={{ color: 'var(--text-primary)' }}>
          Loading actions...
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

  if (actions.length === 0) {
    return (
      <div className="pokemon-container">
        <p className="font-pixel text-xs text-center" style={{ color: 'var(--text-primary)' }}>
          No actions available for this world
        </p>
      </div>
    )
  }

  return (
    <div className="pokemon-container">
      <h3 className="font-pixel text-sm mb-3" style={{ color: 'var(--text-primary)' }}>
        Available Actions:
      </h3>
      <div className="space-y-4">
        {/* Actions is an object with categories like {Movement: [...], Perception: [...]} */}
        {Object.entries(actions).map(([category, categoryActions]) => (
          <div key={category}>
            <h4 className="font-pixel text-xs font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
              {category}
            </h4>
            <div className="space-y-2">
              {categoryActions.map((action) => (
                <div
                  key={action.action_id}
                  className="p-3 border-2 border-pokemon-blue bg-blue-50 rounded"
                >
                  <p className="font-pixel text-xs font-bold text-pokemon-blue mb-1">
                    {action.name}
                  </p>
                  <p className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
                    {action.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

ActionDisplay.propTypes = {
  worldId: PropTypes.string
}
