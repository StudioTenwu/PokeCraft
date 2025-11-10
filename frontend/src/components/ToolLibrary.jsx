import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

/**
 * ToolLibrary - Display all tools the agent has learned, color-coded by category
 * @param {Object} props
 * @param {string} props.agentId - The agent ID to fetch tools for
 * @param {Function} props.onToolDeleted - Callback when tool is deleted
 */
export default function ToolLibrary({ agentId, onToolDeleted }) {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expandedTool, setExpandedTool] = useState(null)
  const [deletingTool, setDeletingTool] = useState(null)

  const categoryColors = {
    Movement: 'bg-blue-100 border-blue-500',
    Perception: 'bg-green-100 border-green-500',
    Interaction: 'bg-purple-100 border-purple-500',
    Advanced: 'bg-orange-100 border-orange-500',
    Default: 'bg-gray-100 border-gray-500'
  }

  const fetchTools = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`http://localhost:8000/api/tools/agent/${agentId}`)

      if (!response.ok) {
        throw new Error('Failed to fetch tools')
      }

      const data = await response.json()
      setTools(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Failed to load tools')
      console.error('Tool fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (agentId) {
      fetchTools()
    }
  }, [agentId])

  const deleteTool = async (toolName) => {
    const confirmed = window.confirm('Are you sure you want to forget this skill? This cannot be undone.')

    if (!confirmed) return

    try {
      setDeletingTool(toolName)
      const response = await fetch(`http://localhost:8000/api/tools/${toolName}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete tool')
      }

      // Remove from local state
      setTools(tools.filter(tool => tool.name !== toolName))

      if (onToolDeleted) {
        onToolDeleted(toolName)
      }

      // Close expanded view if deleted tool was open
      if (expandedTool === toolName) {
        setExpandedTool(null)
      }
    } catch (err) {
      alert(`Error deleting tool: ${err.message}`)
      console.error('Tool delete error:', err)
    } finally {
      setDeletingTool(null)
    }
  }

  const toggleCode = (toolName) => {
    setExpandedTool(expandedTool === toolName ? null : toolName)
  }

  const getCategoryColor = (category) => {
    return categoryColors[category] || categoryColors.Default
  }

  if (loading) {
    return (
      <div className="pokemon-container text-center py-8">
        <div className="pokeball-animation inline-block text-4xl mb-2">⚽</div>
        <p className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
          Loading tools...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="pokemon-container">
        <div className="p-4 border-4 border-pokemon-red bg-red-100 rounded">
          <p className="font-pixel text-xs text-pokemon-red">
            ⚠️ {error}
          </p>
          <button
            onClick={fetchTools}
            className="mt-2 font-pixel text-xs underline text-pokemon-red"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="pokemon-container">
      <h2 className="font-pixel text-pokemon-gold text-xl mb-6 text-center"
          style={{ textShadow: '2px 2px 0px rgba(0,0,0,0.3)' }}>
        Tool Library 📚
      </h2>

      {tools.length === 0 ? (
        <div className="text-center py-8">
          <p className="font-pixel text-sm mb-2" style={{ color: 'var(--text-primary)' }}>
            No tools yet!
          </p>
          <p className="font-pixel text-xs opacity-70" style={{ color: 'var(--text-primary)' }}>
            Create your first tool above ↑
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tools.map((tool) => (
            <div
              key={tool.name}
              className={`border-4 rounded-lg p-4 transition-all ${getCategoryColor(tool.category)}`}
            >
              <div className="mb-3">
                <h3 className="font-pixel text-sm mb-2 break-words">
                  {tool.name}
                </h3>
                {tool.category && (
                  <span className="inline-block px-2 py-1 text-xs font-pixel bg-white border-2 border-black rounded">
                    {tool.category}
                  </span>
                )}
              </div>

              {tool.description && (
                <p className="text-xs mb-3 font-mono" style={{ color: 'var(--text-primary)' }}>
                  {tool.description}
                </p>
              )}

              <div className="flex justify-between items-center gap-2">
                <button
                  onClick={() => toggleCode(tool.name)}
                  className="text-xs underline font-pixel flex-1 text-left"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {expandedTool === tool.name ? 'Hide Code' : 'View Code'}
                </button>
                <button
                  onClick={() => deleteTool(tool.name)}
                  disabled={deletingTool === tool.name}
                  className="bg-pokemon-red text-white px-3 py-1 rounded text-xs font-pixel border-2 border-black disabled:opacity-50"
                >
                  {deletingTool === tool.name ? '...' : 'Delete'}
                </button>
              </div>

              {expandedTool === tool.name && tool.code && (
                <div className="mt-4">
                  <pre className="p-3 border-2 border-black rounded bg-black text-green-400 font-mono text-xs overflow-x-auto max-h-64 overflow-y-auto">
                    <code>{tool.code}</code>
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tools.length > 0 && (
        <div className="mt-4 text-center">
          <p className="font-pixel text-xs opacity-70" style={{ color: 'var(--text-primary)' }}>
            💡 {tools.length} skill{tools.length !== 1 ? 's' : ''} learned
          </p>
        </div>
      )}
    </div>
  )
}

ToolLibrary.propTypes = {
  agentId: PropTypes.string.isRequired,
  onToolDeleted: PropTypes.func
}
