import { useState } from 'react'
import AgentCreation from './components/AgentCreation'
import AgentCard from './components/AgentCard'
import ThemeToggle from './components/ThemeToggle'
import WorldCreation from './components/WorldCreation'
import ToolCreator from './components/ToolCreator'
import ToolLibrary from './components/ToolLibrary'
import AgentRunner from './components/AgentRunner'

function App() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [worlds, setWorlds] = useState({}) // Store worlds by agent ID
  const [currentPhase, setCurrentPhase] = useState('agent') // 'agent', 'world', 'tools', 'deploy'

  return (
    <div className="min-h-screen bg-gradient-to-b from-pokemon-cream to-pokemon-gold/30 p-4 sm:p-8"
         style={{
           background: 'linear-gradient(to bottom, var(--bg-primary), var(--bg-secondary))',
           transition: 'background 0.3s ease'
         }}>
      {/* Header with Pokémon vibes */}
      <header className="mb-12">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1"></div>
          <div className="flex-1 flex justify-center">
            <div className="inline-block border-4 px-8 py-4"
                 style={{
                   backgroundColor: 'var(--bg-card)',
                   borderColor: 'var(--border-color)',
                   boxShadow: '8px 8px 0px 0px var(--shadow-color)',
                   transition: 'background-color 0.3s ease'
                 }}>
              <h1 className="font-pixel text-3xl sm:text-5xl text-pokemon-gold mb-2"
                  style={{textShadow: '4px 4px 0px rgba(0,0,0,0.3)'}}>
                AICraft
              </h1>
              <div className="flex items-center justify-center gap-2">
                <span className="text-2xl">⚽</span>
                <p className="font-pixel text-xs sm:text-sm" style={{color: 'var(--text-primary)'}}>Pokémon Edition</p>
                <span className="text-2xl">✨</span>
              </div>
            </div>
          </div>
          <div className="flex-1 flex justify-end">
            <ThemeToggle />
          </div>
        </div>

        <p className="font-pixel text-xs max-w-2xl mx-auto px-4 text-center"
           style={{color: 'var(--text-primary)', opacity: 0.8}}>
          Hatch your AI companion with retro Game Boy magic
        </p>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="pokemon-container">
          <AgentCreation
            onAgentCreated={(newAgent) => {
              setAgents([...agents, newAgent])
              setSelectedAgent(newAgent)
              setCurrentPhase('world') // Move to world creation
            }}
          />
        </div>

        {/* Phase 2: World creation for selected agent */}
        {selectedAgent && !worlds[selectedAgent.id] && currentPhase === 'world' && (
          <div>
            <WorldCreation
              agent={selectedAgent}
              onWorldCreated={(world) => {
                setWorlds({ ...worlds, [selectedAgent.id]: world })
                setCurrentPhase('tools')
              }}
            />
          </div>
        )}

        {/* Phase 3: Tool teaching */}
        {selectedAgent && worlds[selectedAgent.id] && currentPhase === 'tools' && (
          <div className="space-y-6">
            <div className="pokemon-container">
              <h2 className="font-pixel text-xl mb-4" style={{ color: 'var(--text-primary)' }}>
                🛠️ Teach {selectedAgent.name} New Skills
              </h2>
              <ToolCreator
                agentId={selectedAgent.id}
                onToolCreated={() => {
                  // Tool created, can view in library
                }}
              />
            </div>
            <div className="pokemon-container">
              <ToolLibrary
                agentId={selectedAgent.id}
                onToolDeleted={() => {
                  // Tool deleted
                }}
              />
            </div>
            <div className="text-center">
              <button
                onClick={() => setCurrentPhase('deploy')}
                className="font-pixel px-8 py-3 border-2 hover:scale-105 transition-transform"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-primary)',
                  boxShadow: '4px 4px 0px 0px var(--shadow-color)'
                }}
              >
                Deploy Agent 🚀
              </button>
            </div>
          </div>
        )}

        {/* Phase 3: Agent deployment */}
        {selectedAgent && worlds[selectedAgent.id] && currentPhase === 'deploy' && (
          <div className="pokemon-container">
            <AgentRunner
              agentId={selectedAgent.id}
              worldId={worlds[selectedAgent.id].id}
            />
            <div className="text-center mt-4">
              <button
                onClick={() => setCurrentPhase('tools')}
                className="font-pixel px-6 py-2 border-2 text-sm"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-primary)'
                }}
              >
                ← Back to Tools
              </button>
            </div>
          </div>
        )}

        {/* Show created agents */}
        {agents.length > 0 && (
          <div className="mt-8">
            <h2 className="font-pixel text-lg mb-4 text-center" style={{ color: 'var(--text-primary)' }}>
              Created Agents
            </h2>
            <div className="grid gap-4">
              {agents.map((agent) => (
                <div key={agent.id} className="flex flex-col gap-4">
                  <AgentCard agent={agent} />
                  {selectedAgent?.id === agent.id && !agent.world && (
                    <p className="font-pixel text-xs text-center" style={{ color: 'var(--text-primary)', opacity: 0.7 }}>
                      👆 Create a world for this agent above
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer info */}
        <div className="mt-8 text-center">
          <div className="inline-block border-2 px-6 py-3 rounded"
               style={{
                 backgroundColor: 'rgba(0, 0, 0, 0.8)',
                 borderColor: 'var(--border-color)',
                 transition: 'border-color 0.3s ease'
               }}>
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
    </div>
  )
}

export default App
