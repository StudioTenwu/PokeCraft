import { useState } from 'react'
import AgentCreation from './components/AgentCreation'
import AgentCard from './components/AgentCard'

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
    <div className="min-h-screen bg-gradient-to-b from-pokemon-cream to-pokemon-gold/30 p-4 sm:p-8">
      {/* Header with Pokémon vibes */}
      <header className="text-center mb-12">
        <div className="inline-block bg-white border-4 border-black px-8 py-4
                        shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] mb-4">
          <h1 className="font-pixel text-3xl sm:text-5xl text-pokemon-gold mb-2"
              style={{textShadow: '4px 4px 0px rgba(0,0,0,0.3)'}}>
            AICraft
          </h1>
          <div className="flex items-center justify-center gap-2">
            <span className="text-2xl">⚽</span>
            <p className="font-pixel text-xs sm:text-sm text-black">Pokémon Edition</p>
            <span className="text-2xl">✨</span>
          </div>
        </div>

        <p className="font-pixel text-xs text-black/80 max-w-2xl mx-auto px-4">
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
          <div className="inline-block bg-black/80 border-2 border-black px-6 py-3 rounded">
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
