import { useState } from 'react'
import PropTypes from 'prop-types'
import PokemonButton from './PokemonButton'
import ActionDisplay from './ActionDisplay'

/**
 * ToolCreator - Let children describe tools in natural language and see the generated code
 * @param {Object} props
 * @param {string} props.agentId - The agent ID to create tools for
 * @param {string} props.worldId - The world ID to create context-aware tools for
 * @param {Function} props.onToolCreated - Callback when tool is created
 */
export default function ToolCreator({ agentId, worldId, onToolCreated }) {
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [generatedTool, setGeneratedTool] = useState(null)
  const [error, setError] = useState(null)
  const [showExplanation, setShowExplanation] = useState(false)

  const createTool = async () => {
    if (!description.trim()) {
      setError('Please describe what you want your pokemon to do!')
      return
    }

    setLoading(true)
    setError(null)
    setGeneratedTool(null)

    try {
      const response = await fetch('http://localhost:8000/api/tools/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          world_id: worldId,
          description: description.trim()
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create tool')
      }

      const data = await response.json()
      setGeneratedTool(data)
      setDescription('')

      if (onToolCreated) {
        onToolCreated(data)
      }
    } catch (err) {
      setError(err.message || 'Failed to create tool. Please try again.')
      console.error('Tool creation error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      createTool()
    }
  }

  return (
    <div className="pokemon-container">
      <h2 className="font-pixel text-pokemon-gold text-xl mb-4 text-center"
          style={{ textShadow: '2px 2px 0px rgba(0,0,0,0.3)' }}>
        Teach Your Pokemon a New Skill!
      </h2>

      {/* Show available actions for context */}
      <div className="mb-4">
        <ActionDisplay worldId={worldId} />
      </div>

      <div className="space-y-4">
        <textarea
          className="w-full p-4 border-4 border-pokemon-green rounded font-mono bg-white text-black focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
          placeholder="Describe what you want your pokemon to do... (e.g., 'make a tool that lets my pokemon jump over obstacles')"
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />

        <div className="flex gap-2">
          <PokemonButton
            onClick={createTool}
            disabled={loading || !description.trim()}
          >
            {loading ? 'Generating...' : 'Create Tool ✨'}
          </PokemonButton>
        </div>

        {loading && (
          <div className="text-center py-4">
            <div className="pokeball-animation inline-block text-4xl mb-2">⚽</div>
            <p className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
              Generating your tool...
            </p>
          </div>
        )}

        {error && (
          <div className="p-4 border-4 border-pokemon-red bg-red-100 rounded">
            <p className="font-pixel text-xs text-pokemon-red">
              ⚠️ {error}
            </p>
          </div>
        )}

        {generatedTool && (
          <div className="space-y-4 mt-6">
            <div className="p-4 border-4 border-pokemon-green bg-green-100 rounded">
              <p className="font-pixel text-xs text-pokemon-green mb-2">
                ✓ Tool created: {generatedTool.tool_name}
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="font-pixel text-sm" style={{ color: 'var(--text-primary)' }}>
                  Generated Code:
                </h3>
                <button
                  onClick={() => setShowExplanation(!showExplanation)}
                  className="font-pixel text-xs underline"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {showExplanation ? 'Hide' : 'Explain Tool'}
                </button>
              </div>

              <pre className="p-4 border-4 border-black rounded bg-black text-green-400 font-mono text-xs overflow-x-auto">
                <code>{generatedTool.code}</code>
              </pre>

              {showExplanation && generatedTool.explanation && (
                <div className="p-4 border-4 border-pokemon-blue bg-blue-100 rounded">
                  <h4 className="font-pixel text-xs text-pokemon-blue mb-2">
                    What does this tool do?
                  </h4>
                  <p className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
                    {generatedTool.explanation}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        <p className="font-pixel text-xs text-center opacity-70" style={{ color: 'var(--text-primary)' }}>
          💡 Tip: Press Ctrl+Enter to create tool
        </p>
      </div>
    </div>
  )
}

ToolCreator.propTypes = {
  agentId: PropTypes.string.isRequired,
  worldId: PropTypes.string,
  onToolCreated: PropTypes.func
}
