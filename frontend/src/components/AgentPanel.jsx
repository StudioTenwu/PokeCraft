import { useState } from 'react'
import PropTypes from 'prop-types'
import PokemonButton from './PokemonButton'

// Color palette for personality traits
const TRAIT_COLORS = [
  { bg: '#E3F2FD', border: '#42A5F5', text: '#1565C0' }, // Blue
  { bg: '#F3E5F5', border: '#AB47BC', text: '#6A1B9A' }, // Purple
  { bg: '#E8F5E9', border: '#66BB6A', text: '#2E7D32' }, // Green
  { bg: '#FFF3E0', border: '#FFA726', text: '#E65100' }, // Orange
  { bg: '#FCE4EC', border: '#EC407A', text: '#AD1457' }, // Pink
  { bg: '#FFF9C4', border: '#FFEB3B', text: '#F57F17' }, // Yellow
]

/**
 * AgentPanel - Left sidebar showing agent details and equipped tools
 * @param {Object} props
 * @param {Object} props.agent - The agent to display
 * @param {Array} props.equippedTools - Array of tools equipped to this agent
 * @param {Function} props.onToolRemove - Callback when tool is removed
 */
export default function AgentPanel({ agent, equippedTools = [], onToolRemove }) {
  const [isBackstoryExpanded, setIsBackstoryExpanded] = useState(false)
  const [exportStatus, setExportStatus] = useState(null) // null, 'loading', 'success', 'error'
  const [exportMessage, setExportMessage] = useState('')

  // Handle export to Chrome extension
  const handleExportToExtension = async () => {
    if (!agent) return

    setExportStatus('loading')
    setExportMessage('Sending to extension...')

    try {
      const response = await fetch('http://localhost:8080/agents/queue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: agent.id,
          name: agent.name,
          avatar_url: agent.avatar_url,
          backstory: agent.backstory,
          personality_traits: agent.personality_traits
        })
      })

      if (response.ok) {
        const data = await response.json()
        setExportStatus('success')
        setExportMessage(`✓ ${agent.name} queued! Open extension to load.`)

        // Clear success message after 4 seconds
        setTimeout(() => {
          setExportStatus(null)
          setExportMessage('')
        }, 4000)
      } else {
        throw new Error(`Server returned ${response.status}`)
      }
    } catch (error) {
      console.error('Export error:', error)
      setExportStatus('error')
      setExportMessage('❌ Extension server not running. Start it with: python chrome_extension/backend_server.py')

      // Clear error message after 6 seconds
      setTimeout(() => {
        setExportStatus(null)
        setExportMessage('')
      }, 6000)
    }
  }

  if (!agent) {
    return (
      <div className="pokemon-container h-full flex items-center justify-center">
        <p className="font-pixel text-xs text-center" style={{ color: 'var(--text-primary)', opacity: 0.7 }}>
          No agent selected.<br/>Create an agent to get started!
        </p>
      </div>
    )
  }

  return (
    <div className="pokemon-container h-full flex flex-col">
      {/* Avatar */}
      <div className="flex justify-center mb-4">
        <div className="w-48 h-48 border-4 rounded-lg overflow-hidden"
             style={{ borderColor: 'var(--border-color)' }}>
          {agent.avatar_url ? (
            <img
              src={agent.avatar_url}
              alt={agent.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-200">
              <span className="text-6xl">⚽</span>
            </div>
          )}
        </div>
      </div>

      {/* Agent Info */}
      <div className="mb-4">
        <h2 className="font-title text-xl mb-2 text-center"
            style={{ color: 'var(--text-primary)' }}>
          {agent.name}
        </h2>
        <div className="text-center">
          <p className="font-pixel text-xs mb-1"
             style={{ color: 'var(--text-primary)', opacity: 0.8 }}>
            {isBackstoryExpanded
              ? agent.backstory
              : `${agent.backstory?.substring(0, 80)}...`}
          </p>
          {agent.backstory && agent.backstory.length > 80 && (
            <button
              onClick={() => setIsBackstoryExpanded(!isBackstoryExpanded)}
              className="font-pixel text-xs underline hover:opacity-70 transition-opacity"
              style={{ color: 'var(--text-primary)', opacity: 0.6 }}
            >
              {isBackstoryExpanded ? 'Show less' : 'Read more'}
            </button>
          )}
        </div>
      </div>

      {/* Personality Traits */}
      {agent.personality_traits && agent.personality_traits.length > 0 && (
        <div className="mb-4">
          <h3 className="font-pixel text-xs mb-2" style={{ color: 'var(--text-primary)' }}>
            Traits:
          </h3>
          <div className="flex flex-wrap gap-2">
            {agent.personality_traits.map((trait, idx) => {
              const color = TRAIT_COLORS[idx % TRAIT_COLORS.length]
              return (
                <span
                  key={idx}
                  className="font-pixel text-xs px-2 py-1 border-2 rounded"
                  style={{
                    backgroundColor: color.bg,
                    borderColor: color.border,
                    color: color.text
                  }}
                >
                  • {trait}
                </span>
              )
            })}
          </div>
        </div>
      )}

      {/* Export to Extension */}
      <div className="mb-4">
        <PokemonButton
          onClick={handleExportToExtension}
          disabled={exportStatus === 'loading'}
          className="w-full"
        >
          {exportStatus === 'loading' ? '📤 Exporting...' : '📤 Export to Extension'}
        </PokemonButton>

        {exportMessage && (
          <p
            className="font-pixel text-xs mt-2 text-center"
            style={{
              color: exportStatus === 'success' ? '#4CAF50' : exportStatus === 'error' ? '#f44336' : 'var(--text-primary)',
              fontSize: '0.65rem',
              lineHeight: '1.4'
            }}
          >
            {exportMessage}
          </p>
        )}
      </div>

      {/* Equipped Tools */}
      <div className="mb-4 flex-1">
        <h3 className="font-pixel text-xs mb-2" style={{ color: 'var(--text-primary)' }}>
          📦 Equipped Tools:
        </h3>
        <div className="space-y-2">
          {equippedTools.length === 0 ? (
            <p className="font-pixel text-xs text-center py-4"
               style={{ color: 'var(--text-primary)', opacity: 0.5 }}>
              No tools equipped yet.<br/>Create some below!
            </p>
          ) : (
            equippedTools.map((tool, idx) => (
              <div
                key={idx}
                className="p-3 border-2 rounded flex justify-between items-center group"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-color)',
                  transition: 'all 0.2s'
                }}
              >
                <div className="flex-1 min-w-0">
                  <p className="font-pixel text-xs font-bold truncate" style={{ color: 'var(--text-primary)' }}>
                    {tool.tool_name || tool.name}
                  </p>
                  {tool.description && (
                    <p className="font-pixel text-xs mt-1 truncate"
                       style={{ color: 'var(--text-primary)', opacity: 0.7, fontSize: '0.65rem' }}>
                      {tool.description.substring(0, 50)}...
                    </p>
                  )}
                </div>
                {onToolRemove && (
                  <button
                    onClick={() => onToolRemove(tool)}
                    className="ml-2 font-pixel text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                    style={{ color: '#f44336' }}
                    title="Remove tool"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  )
}

AgentPanel.propTypes = {
  agent: PropTypes.object,
  equippedTools: PropTypes.array,
  onToolRemove: PropTypes.func
}
