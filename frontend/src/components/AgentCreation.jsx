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
      setError('Please describe your companion!')
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
          message: data.message || 'Dreaming up your companion...'
        }))
      },

      onLLMComplete: (data) => {
        console.log('LLM complete:', data)
      },

      onAvatarStart: (data) => {
        setProgress(prev => ({
          ...prev,
          phase: 'avatar',
          message: data.message || 'Hatching your companion...',
          avatarStep: 0,
          avatarTotal: 2,
          avatarPercent: 0
        }))
      },

      onAvatarProgress: (data) => {
        setProgress(prev => ({
          ...prev,
          phase: 'avatar',
          message: data.message || `Hatching... Step ${data.step}/${data.total}`,
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
        setError('Failed to hatch your companion. Make sure the backend is running!')
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
        <p className="text-sm font-pixel" style={{color: 'var(--text-primary)'}}>
          Describe your AI partner...
        </p>
      </div>

      {/* Input area */}
      <div className="pokemon-container mb-6">
        <label className="block font-pixel text-xs mb-3" style={{color: 'var(--text-primary)'}}>
          Describe your companion:
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="A brave explorer who loves solving puzzles and helping others..."
          className="pokemon-input h-32 resize-none font-sans"
          disabled={loading}
        />

        <div className="mt-4 text-xs font-sans" style={{color: 'var(--text-secondary)'}}>
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
            {/* Animated egg emoji based on progress */}
            <div className="text-6xl">
              {progress.phase === 'llm' && '🥚'}
              {progress.phase === 'avatar' && progress.avatarPercent < 50 && '🥚'}
              {progress.phase === 'avatar' && progress.avatarPercent >= 50 && '🐣'}
            </div>

            {/* Progress message */}
            <p className="font-pixel text-sm text-pokemon-gold">
              {progress.message || 'Hatching your companion...'}
            </p>

            {/* Progress bar for avatar generation */}
            {progress.phase === 'avatar' && (
              <div className="max-w-md mx-auto space-y-2">
                {/* Step counter */}
                <p className="font-pixel text-xs text-black">
                  Step {progress.avatarStep}/{progress.avatarTotal} - {progress.avatarPercent}%
                </p>

                {/* Pokémon-themed progress bar */}
                <div className="w-full h-6 bg-pokemon-cream border-4 border-black relative overflow-hidden">
                  <div
                    className="h-full bg-pokemon-gold transition-all duration-300 ease-out"
                    style={{ width: `${progress.avatarPercent}%` }}
                  >
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="font-pixel text-xs text-black mix-blend-difference">
                        {progress.avatarPercent}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
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
              className="w-full text-left px-3 py-2 hover:bg-pokemon-cream
                       text-xs border-2 border-pokemon-green transition-colors
                       font-sans"
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
