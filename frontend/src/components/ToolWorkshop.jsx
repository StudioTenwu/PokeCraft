import { useState } from 'react'
import PropTypes from 'prop-types'
import ToolCreator from './ToolCreator'
import ToolLibrary from './ToolLibrary'

/**
 * ToolWorkshop - Collapsible bottom panel for creating and managing tools
 * @param {Object} props
 * @param {string} props.agentId - The agent ID to create tools for
 * @param {Function} props.onToolCreated - Callback when tool is created
 * @param {Function} props.onToolDeleted - Callback when tool is deleted
 */
export default function ToolWorkshop({ agentId, onToolCreated, onToolDeleted }) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [activeTab, setActiveTab] = useState('create') // 'create' or 'library'

  if (!agentId) {
    return null
  }

  return (
    <div className="pokemon-container">
      {/* Header with collapse button */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-pixel text-lg" style={{ color: 'var(--text-primary)' }}>
          🛠️ Tool Workshop
        </h2>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="font-pixel text-xs px-3 py-1 border-2 rounded"
          style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-color)',
            color: 'var(--text-primary)'
          }}
        >
          {isCollapsed ? 'Expand ▾' : 'Collapse ▴'}
        </button>
      </div>

      {!isCollapsed && (
        <>
          {/* Tabs */}
          <div className="flex gap-2 mb-4 border-b-2" style={{ borderColor: 'var(--border-color)' }}>
            <button
              onClick={() => setActiveTab('create')}
              className={`font-pixel text-xs px-4 py-2 border-2 border-b-0 transition-all ${
                activeTab === 'create' ? '' : 'opacity-60'
              }`}
              style={{
                backgroundColor: activeTab === 'create' ? 'var(--bg-card)' : 'transparent',
                borderColor: activeTab === 'create' ? 'var(--border-color)' : 'transparent',
                color: 'var(--text-primary)',
                marginBottom: '-2px'
              }}
            >
              ✨ Create New
            </button>
            <button
              onClick={() => setActiveTab('library')}
              className={`font-pixel text-xs px-4 py-2 border-2 border-b-0 transition-all ${
                activeTab === 'library' ? '' : 'opacity-60'
              }`}
              style={{
                backgroundColor: activeTab === 'library' ? 'var(--bg-card)' : 'transparent',
                borderColor: activeTab === 'library' ? 'var(--border-color)' : 'transparent',
                color: 'var(--text-primary)',
                marginBottom: '-2px'
              }}
            >
              📚 Library
            </button>
          </div>

          {/* Tab Content */}
          <div className="min-h-[200px]">
            {activeTab === 'create' ? (
              <ToolCreator
                agentId={agentId}
                onToolCreated={onToolCreated}
              />
            ) : (
              <ToolLibrary
                agentId={agentId}
                onToolDeleted={onToolDeleted}
              />
            )}
          </div>
        </>
      )}

      {isCollapsed && (
        <p className="font-pixel text-xs text-center py-2" style={{ color: 'var(--text-primary)', opacity: 0.6 }}>
          Click expand to create and manage tools
        </p>
      )}
    </div>
  )
}

ToolWorkshop.propTypes = {
  agentId: PropTypes.string,
  onToolCreated: PropTypes.func,
  onToolDeleted: PropTypes.func
}
