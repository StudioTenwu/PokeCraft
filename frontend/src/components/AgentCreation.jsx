import { useState } from 'react'
import { api } from '../api'
import AgentCard from './AgentCard'
import PokemonButton from './PokemonButton'

export default function AgentCreation({ onAgentCreated }) {
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [agent, setAgent] = useState(null)
  const [error, setError] = useState(null)

  const handleCreate = async () => {
    if (!description.trim()) {
      setError('Please describe your companion!')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const newAgent = await api.createAgent(description)
      setAgent(newAgent)
      if (onAgentCreated) onAgentCreated(newAgent)
    } catch (err) {
      setError('Failed to hatch your companion. Make sure the backend is running!')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (agent) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="font-pixel text-2xl text-pokemon-gold mb-4">
            Companion Hatched! ✨
          </h2>
        </div>

        <AgentCard agent={agent} />

        <div className="text-center">
          <PokemonButton
            onClick={() => {
              setAgent(null)
              setDescription('')
            }}
            variant="green"
          >
            Hatch Another
          </PokemonButton>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="font-pixel text-3xl text-pokemon-gold mb-3"
            style={{textShadow: '4px 4px 0px rgba(0,0,0,0.3)'}}>
          Hatch Your Companion
        </h2>
        <p className="text-black text-sm font-pixel">
          Describe your AI partner...
        </p>
      </div>

      {/* Input area */}
      <div className="pokemon-container mb-6">
        <label className="block font-pixel text-xs mb-3 text-black">
          Describe your companion:
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="A brave explorer who loves solving puzzles and helping others..."
          className="pokemon-input h-32 resize-none font-sans"
          disabled={loading}
        />

        <div className="mt-4 text-xs text-gray-700 font-sans">
          <p className="mb-1">💡 Try describing:</p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Personality traits (brave, curious, clever)</li>
            <li>What they like to do</li>
            <li>Their goals or motivations</li>
          </ul>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-pokemon-red border-4 border-black text-white font-pixel text-xs">
          ⚠️ {error}
        </div>
      )}

      <div className="text-center">
        {loading ? (
          <div className="space-y-4">
            <div className="text-6xl pokeball-animation">⚽</div>
            <p className="font-pixel text-sm text-pokemon-gold">
              Hatching your companion...
            </p>
          </div>
        ) : (
          <PokemonButton
            onClick={handleCreate}
            variant="green"
            className="text-lg px-8 py-4"
          >
            Hatch Companion
          </PokemonButton>
        )}
      </div>

      {/* Example companions */}
      <div className="mt-8 p-4 bg-pokemon-green/20 border-2 border-pokemon-green rounded">
        <p className="font-pixel text-xs text-pokemon-green mb-3">
          Example Companions:
        </p>
        <div className="space-y-2">
          {[
            "A cheerful robot who loves exploring and collecting shiny gems",
            "A wise owl who enjoys solving puzzles and teaching others",
            "A playful cat who helps friends find lost items"
          ].map((example, i) => (
            <button
              key={i}
              onClick={() => setDescription(example)}
              className="w-full text-left px-3 py-2 bg-white hover:bg-pokemon-cream
                       text-black text-xs border-2 border-pokemon-green transition-colors
                       font-sans"
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
