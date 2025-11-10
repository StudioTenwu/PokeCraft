import { useState } from 'react'
import AgentCreation from './components/AgentCreation'
import AgentCard from './components/AgentCard'
import ThemeToggle from './components/ThemeToggle'

function App() {
  // Mock agent for testing personality colors
  const mockAgent = {
    name: "Pixel Pal",
    backstory: "A brave companion born from retro gaming magic, ready to explore the digital world with curiosity and creativity!",
    personality_traits: [
      "Brave",
      "Curious",
      "Helpful",
      "Creative",
      "Friendly",
      "Energetic",
      "Loyal",
      "Playful",
      "Clever",
      "Kind",
      "Adventurous",
      "Patient"
    ],
    avatar_url: null
  }

  const [agents, setAgents] = useState([])

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
        {/* Test Agent Card */}
        <div>
          <h2 className="font-pixel text-sm mb-4 text-center">🎨 Testing Personality Colors</h2>
          <AgentCard agent={mockAgent} />
        </div>

        <div className="pokemon-container">
          <AgentCreation
            onAgentCreated={(newAgent) => {
              setAgents([...agents, newAgent])
            }}
          />
        </div>

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
