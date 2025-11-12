import { useState } from 'react'
import AgentCreation from './components/AgentCreation'
import AgentPanel from './components/AgentPanel'
import ThemeToggle from './components/ThemeToggle'
import WorldCreation from './components/WorldCreation'
import ToolWorkshop from './components/ToolWorkshop'
import AgentRunner from './components/AgentRunner'
import WorldCanvas from './components/WorldCanvas'
import PokemonButton from './components/PokemonButton'

function App() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [worlds, setWorlds] = useState({}) // Store worlds by agent ID
  const [tools, setTools] = useState({}) // Store tools by agent ID
  const [showAgentCreation, setShowAgentCreation] = useState(false)
  const [showDeployment, setShowDeployment] = useState(false)
  const [showInfo, setShowInfo] = useState(false)

  const handleAgentCreated = (newAgent) => {
    setAgents([...agents, newAgent])
    setSelectedAgent(newAgent)
    setShowAgentCreation(false)
    setTools({ ...tools, [newAgent.id]: [] })
  }

  const handleWorldCreated = (world) => {
    if (selectedAgent) {
      setWorlds({ ...worlds, [selectedAgent.id]: world })
    }
  }

  const handleToolCreated = (tool) => {
    if (selectedAgent) {
      const agentTools = tools[selectedAgent.id] || []
      setTools({ ...tools, [selectedAgent.id]: [...agentTools, tool] })
    }
  }

  const handleToolDeleted = (deletedTool) => {
    if (selectedAgent) {
      const agentTools = tools[selectedAgent.id] || []
      setTools({
        ...tools,
        [selectedAgent.id]: agentTools.filter(t => t.id !== deletedTool.id)
      })
    }
  }

  const handleToolRemove = (tool) => {
    handleToolDeleted(tool)
  }

  const handleDeploy = () => {
    setShowDeployment(true)
  }

  const selectedWorld = selectedAgent ? worlds[selectedAgent.id] : null
  const selectedTools = selectedAgent ? (tools[selectedAgent.id] || []) : []

  // Determine what to show in the main content area
  const showWelcome = agents.length === 0 && !showAgentCreation
  const showCreationForm = showAgentCreation || agents.length === 0

  return (
    <div
      className="min-h-screen p-2 sm:p-4"
      style={{
        background: 'linear-gradient(to bottom, var(--bg-primary), var(--bg-secondary))',
        transition: 'background 0.3s ease'
      }}
    >
      {/* Header - Two Row Layout */}
      <header className="mb-4 max-w-[1600px] mx-auto">
        {/* Row 1: Title + Theme Toggle */}
        <div className="flex items-center mb-3">
          <div className="flex-1"></div>
          <div
            className="inline-block border-4 px-6 py-3"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
              boxShadow: '6px 6px 0px 0px var(--shadow-color)',
              transition: 'background-color 0.3s ease'
            }}
          >
            <h1
              className="font-title text-2xl sm:text-3xl text-pokemon-gold"
              style={{ textShadow: '3px 3px 0px rgba(0,0,0,0.3)' }}
            >
              PokéCraft
            </h1>
          </div>
          <div className="flex-1 flex justify-end items-center gap-2">
            <button
              onClick={() => setShowInfo(!showInfo)}
              className="font-pixel text-xs px-3 py-2 border-2 rounded hover:scale-105 transition-transform"
              style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: 'var(--border-color)',
                color: 'var(--text-primary)'
              }}
            >
              ℹ️ Info
            </button>
            <ThemeToggle />
          </div>
        </div>

        {/* Row 2: Action Buttons */}
        {agents.length > 0 && !showAgentCreation && (
          <div className="flex items-center gap-2 flex-wrap">
            {/* Agent selector */}
            <div className="flex items-center gap-2">
              <span className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
                Agent:
              </span>
              <select
                value={selectedAgent?.id || ''}
                onChange={(e) => {
                  const agent = agents.find(a => a.id === e.target.value)
                  setSelectedAgent(agent || null)
                  setShowDeployment(false)
                }}
                className="font-pixel text-xs px-3 py-2 border-2 rounded"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-primary)'
                }}
              >
                <option value="">Select Agent</option>
                {agents.map(agent => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name}
                  </option>
                ))}
              </select>
            </div>

            {/* New Agent button */}
            <PokemonButton onClick={() => setShowAgentCreation(true)}>
              + New Agent
            </PokemonButton>

            {/* Deploy button - only show when world exists */}
            {selectedAgent && selectedWorld && !showDeployment && (
              <PokemonButton onClick={handleDeploy}>
                🚀 Deploy
              </PokemonButton>
            )}
          </div>
        )}

        {/* Cancel button when creating new agent */}
        {showAgentCreation && agents.length > 0 && (
          <div className="flex items-center gap-2">
            <PokemonButton onClick={() => setShowAgentCreation(false)}>
              ← Cancel
            </PokemonButton>
          </div>
        )}

        {/* Info Panel */}
        {showInfo && (
          <div className="mt-3 pokemon-container">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
                  Backend:
                </span>
                <code className="font-mono text-xs px-2 py-1 rounded" style={{ backgroundColor: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)' }}>
                  http://localhost:8000
                </code>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-pixel text-xs" style={{ color: 'var(--text-primary)' }}>
                  Frontend:
                </span>
                <code className="font-mono text-xs px-2 py-1 rounded" style={{ backgroundColor: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)' }}>
                  Port 3000
                </code>
              </div>
              {agents.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="font-pixel text-xs text-pokemon-gold">
                    ✨ {agents.length} pokemon{agents.length > 1 ? 's' : ''} hatched
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto">
        {/* Deployment View */}
        {showDeployment && selectedAgent && selectedWorld ? (
          <div className="max-w-5xl mx-auto">
            <div className="pokemon-container">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-title text-xl" style={{ color: 'var(--text-primary)' }}>
                  🚀 {selectedAgent.name} in Action
                </h2>
                <PokemonButton onClick={() => setShowDeployment(false)}>
                  ← Back to Workshop
                </PokemonButton>
              </div>
              <AgentRunner
                agentId={selectedAgent.id}
                worldId={selectedWorld.id}
                avatarUrl={selectedAgent.avatar_url}
              />
            </div>
          </div>
        ) : showCreationForm ? (
          /* Agent Creation - Full Screen */
          <div className="pokemon-container">
            <AgentCreation onAgentCreated={handleAgentCreated} />
          </div>
        ) : !selectedAgent ? (
          /* No agent selected - show selection prompt */
          <div className="pokemon-container text-center py-16">
            <h2 className="font-title text-2xl mb-4" style={{ color: 'var(--text-primary)' }}>
              Select an agent to continue ⬆️
            </h2>
            <p className="font-pixel text-sm mb-6" style={{ color: 'var(--text-primary)', opacity: 0.8 }}>
              Choose an agent from the dropdown or create a new one
            </p>
          </div>
        ) : (
          /* Main Spatial Layout: Fixed Sidebar + Flexible World */
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Left: Agent Panel - Fixed Width */}
            <div className="w-full lg:w-80 flex-shrink-0">
              <AgentPanel
                agent={selectedAgent}
                equippedTools={selectedTools}
                onToolRemove={handleToolRemove}
              />
            </div>

            {/* Right: World and Tools - Flexible Width */}
            <div className="flex-1 min-w-0 space-y-4">
              {/* World Viewport */}
              <div className="pokemon-container">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="font-title text-lg" style={{ color: 'var(--text-primary)' }}>
                    🌍 {selectedAgent.name}'s World
                  </h2>
                </div>

                {!selectedWorld ? (
                  <WorldCreation
                    agent={selectedAgent}
                    onWorldCreated={handleWorldCreated}
                  />
                ) : (
                  <div>
                    <WorldCanvas world={selectedWorld} />
                    <div className="mt-4 text-center">
                      <button
                        onClick={() => {
                          // Remove world to recreate
                          const newWorlds = { ...worlds }
                          delete newWorlds[selectedAgent.id]
                          setWorlds(newWorlds)
                        }}
                        className="font-pixel text-xs px-4 py-2 border-2 rounded hover:scale-105 transition-transform"
                        style={{
                          backgroundColor: 'var(--bg-card)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-primary)'
                        }}
                      >
                        🔄 Regenerate World
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Tool Workshop (only show if world exists) */}
              {selectedWorld && (
                <ToolWorkshop
                  agentId={selectedAgent.id}
                  worldId={selectedWorld.id}
                  onToolCreated={handleToolCreated}
                  onToolDeleted={handleToolDeleted}
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
