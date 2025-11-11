import { useState, useRef } from 'react'
import { api } from '../api'
import AgentCard from './AgentCard'
import PokemonButton from './PokemonButton'

export default function AgentCreation({ onAgentCreated }) {
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [agent, setAgent] = useState(null)
  const [error, setError] = useState(null)

  // Progress tracking state
  const [progress, setProgress] = useState({
    phase: null,  // 'llm' | 'avatar' | null
    message: '',
    avatarStep: 0,
    avatarTotal: 2,
    avatarPercent: 0
  })

  const cleanupRef = useRef(null)

  const handleCreate = () => {
    if (!description.trim()) {
      setError('Please describe your Pokémon!')
      return
    }

    setLoading(true)
    setError(null)
    setProgress({
      phase: null,
      message: '',
      avatarStep: 0,
      avatarTotal: 2,
      avatarPercent: 0
    })

    // Clean up any existing stream
    if (cleanupRef.current) {
      cleanupRef.current()
    }

    // Start streaming agent creation
    cleanupRef.current = api.createAgentStream(description, {
      onLLMStart: (data) => {
        setProgress(prev => ({
          ...prev,
          phase: 'llm',
          message: data.message || 'Dreaming up your Pokémon...',
          avatarPercent: 0
        }))
      },

      onLLMProgress: (data) => {
        setProgress(prev => ({
          ...prev,
          phase: 'llm',
          message: data.message || `Dreaming up your Pokémon... (${data.percent}%)`,
          avatarPercent: data.percent || 0
        }))
      },

      onLLMComplete: (data) => {
        console.log('LLM complete:', data)
        setProgress(prev => ({
          ...prev,
          phase: 'llm',
          message: data.message || `Meet ${data.name}!`,
          avatarPercent: 33
        }))
      },

      onAvatarStart: (data) => {
        setProgress(prev => ({
          ...prev,
          phase: 'avatar',
          message: data.message || 'Hatching your Pokémon...',
          avatarStep: 0,
          avatarTotal: 2,
          avatarPercent: 33  // Stay at 33% when avatar starts
        }))
      },

      onAvatarProgress: (data) => {
        setProgress(prev => ({
          ...prev,
          phase: 'avatar',
          message: 'Generating Avatar',
          avatarStep: data.step || 0,
          avatarTotal: data.total || 2,
          avatarPercent: data.percent || 0
        }))
      },

      onAvatarComplete: (data) => {
        console.log('Avatar complete:', data.avatar_url)
      },

      onComplete: (data) => {
        setAgent(data.agent)
        setLoading(false)
        if (onAgentCreated) onAgentCreated(data.agent)
        cleanupRef.current = null
      },

      onError: (err) => {
        setError('Failed to hatch your Pokémon. Make sure the backend is running!')
        console.error(err)
        setLoading(false)
        cleanupRef.current = null
      }
    })
  }

  if (agent) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="font-pixel text-2xl text-pokemon-gold mb-4">
            Pokémon Hatched! ✨
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
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12 py-8">
        <div className="text-8xl mb-6">⚽</div>
        <h2 className="font-pixel text-4xl sm:text-5xl text-pokemon-gold mb-4"
            style={{textShadow: '4px 4px 0px rgba(0,0,0,0.3)'}}>
          Hatch Your First Pokémon
        </h2>
        <p className="text-base font-pixel" style={{color: 'var(--text-primary)', opacity: 0.9}}>
          Describe your dream Pokémon and watch them come to life!
        </p>
      </div>

      {/* Input area */}
      <div className="pokemon-container mb-8">
        <label className="block font-pixel text-sm mb-4" style={{color: 'var(--text-primary)'}}>
          Describe your Pokémon:
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="A brave explorer who loves solving puzzles and helping others..."
          className="pokemon-input h-40 resize-none font-pixel text-base"
          disabled={loading}
        />

        <div className="mt-6 p-4 rounded" style={{backgroundColor: 'rgba(0,0,0,0.05)'}}>
          <p className="mb-2 font-pixel text-xs" style={{color: 'var(--text-primary)', opacity: 0.8}}>💡 Try describing:</p>
          <ul className="list-disc list-inside space-y-2 ml-2 text-xs font-pixel" style={{color: 'var(--text-primary)', opacity: 0.7}}>
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

      <div className="text-center mb-12">
        {loading ? (
          <div className="space-y-6 py-8">
            {/* Animated emoji showing hatching progress */}
            <div className="text-8xl animate-bounce">
              {progress.avatarPercent < 33 && '🥚'}
              {progress.avatarPercent >= 33 && progress.avatarPercent < 66 && '🐣'}
              {progress.avatarPercent >= 66 && progress.avatarPercent < 100 && '🐥'}
              {progress.avatarPercent >= 100 && '🐦'}
            </div>

            {/* Progress message */}
            <p className="font-pixel text-base text-pokemon-gold">
              {progress.message || 'Hatching your Pokémon...'}
            </p>

            {/* Progress bar showing overall progress */}
            <div className="max-w-lg mx-auto space-y-3">
              {/* Progress percentage */}
              <p className="font-pixel text-sm" style={{color: 'var(--text-primary)'}}>
                {progress.avatarPercent}% Complete
              </p>

              {/* Pokemon-themed progress bar */}
              <div className="w-full h-8 bg-pokemon-cream border-4 border-black relative overflow-hidden rounded">
                <div
                  className="h-full bg-pokemon-gold transition-all duration-300 ease-out"
                  style={{ width: `${progress.avatarPercent}%` }}
                >
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="font-pixel text-sm text-black mix-blend-difference">
                      {progress.avatarPercent}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <PokemonButton
            onClick={handleCreate}
            variant="green"
            className="text-xl px-12 py-5"
          >
            🥚 Hatch Pokémon ✨
          </PokemonButton>
        )}
      </div>

      {/* Example pokemons */}
      <div className="mt-12 p-6 bg-pokemon-green/20 border-2 border-pokemon-green rounded">
        <p className="font-pixel text-sm text-pokemon-green mb-4 text-center">
          ✨ Example Pokémon - Click to try!
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            "A cheerful robot who loves exploring and collecting shiny gems",
            "A wise owl who enjoys solving puzzles and teaching others",
            "A playful cat who helps friends find lost items",
            "A brave knight who protects the forest and its creatures"
          ].map((example, i) => (
            <button
              key={i}
              onClick={() => setDescription(example)}
              className="text-left px-4 py-3 hover:bg-pokemon-cream hover:scale-105
                       text-xs border-2 border-pokemon-green transition-all
                       font-pixel rounded"
              style={{
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-primary)'
              }}
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
