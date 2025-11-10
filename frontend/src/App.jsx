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
      className="min-h-screen p-4 sm:p-6"
      style={{
        background: 'linear-gradient(to bottom, var(--bg-primary), var(--bg-secondary))',
        transition: 'background 0.3s ease'
      }}
    >
      {/* Header */}
      <header className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-4">
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
                className="font-pixel text-2xl sm:text-3xl text-pokemon-gold"
                style={{ textShadow: '3px 3px 0px rgba(0,0,0,0.3)' }}
              >
                AICraft <span className="text-xl">⚽ Pokémon Edition</span>
              </h1>
            </div>

            {/* Agent selector - only show when agents exist and not creating */}
            {agents.length > 0 && !showAgentCreation && (
              <div className="flex items-center gap-2">
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
            )}

            {/* New Agent button - only show when not already creating */}
            {!showAgentCreation && (
              <PokemonButton onClick={() => setShowAgentCreation(true)}>
                + New Agent
              </PokemonButton>
            )}

            {/* Cancel button - show when creating new agent and have existing agents */}
            {showAgentCreation && agents.length > 0 && (
              <PokemonButton onClick={() => setShowAgentCreation(false)}>
                Cancel
              </PokemonButton>
            )}
          </div>

          <ThemeToggle />
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        {/* Deployment View */}
        {showDeployment && selectedAgent && selectedWorld ? (
          <div className="max-w-4xl mx-auto">
            <div className="pokemon-container">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-pixel text-xl" style={{ color: 'var(--text-primary)' }}>
                  🚀 {selectedAgent.name} in Action
                </h2>
                <PokemonButton onClick={() => setShowDeployment(false)}>
                  ← Back to Workshop
                </PokemonButton>
              </div>
              <AgentRunner
                agentId={selectedAgent.id}
                worldId={selectedWorld.id}
              />
            </div>
          </div>
        ) : showCreationForm ? (
          /* Agent Creation - Full Screen */
          <div className="max-w-4xl mx-auto">
            <div className="pokemon-container">
              <h2 className="font-pixel text-2xl mb-6 text-center" style={{ color: 'var(--text-primary)' }}>
                {agents.length === 0 ? '⚽ Hatch Your First Companion' : '✨ Create New Agent'}
              </h2>
              <AgentCreation onAgentCreated={handleAgentCreated} />
            </div>
          </div>
        ) : !selectedAgent ? (
          /* No agent selected - show selection prompt */
          <div className="pokemon-container text-center py-16">
            <h2 className="font-pixel text-2xl mb-4" style={{ color: 'var(--text-primary)' }}>
              Select an agent to continue ⬆️
            </h2>
            <p className="font-pixel text-sm mb-6" style={{ color: 'var(--text-primary)', opacity: 0.8 }}>
              Choose an agent from the dropdown or create a new one
            </p>
          </div>
        ) : (
          /* Main Spatial Layout: Agent | World + Tools */
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Left: Agent Panel (1 column on large screens) */}
            <div className="lg:col-span-1">
              <AgentPanel
                agent={selectedAgent}
                equippedTools={selectedTools}
                onDeploy={selectedWorld ? handleDeploy : undefined}
                onToolRemove={handleToolRemove}
              />
            </div>

            {/* Right: World and Tools (3 columns on large screens) */}
            <div className="lg:col-span-3 space-y-6">
              {/* World Viewport */}
              <div className="pokemon-container">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="font-pixel text-lg" style={{ color: 'var(--text-primary)' }}>
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
                  onToolCreated={handleToolCreated}
                  onToolDeleted={handleToolDeleted}
                />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <div
          className="inline-block border-2 px-6 py-3 rounded"
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderColor: 'var(--border-color)',
            transition: 'border-color 0.3s ease'
          }}
        >
          <p className="font-pixel text-xs text-white/90">
            Backend: http://localhost:8000 • Frontend: Port 3000
          </p>
          {agents.length > 0 && (
            <p className="font-pixel text-xs text-pokemon-gold mt-2">
              ✨ {agents.length} companion{agents.length > 1 ? 's' : ''} hatched
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
