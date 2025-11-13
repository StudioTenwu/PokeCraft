import { useState } from 'react'
import PropTypes from 'prop-types'
import PokemonButton from './PokemonButton'
import '../styles/personality-test.css'

const PersonalityTestScreen = ({ agent, onClose }) => {
  const [phase, setPhase] = useState('setup') // 'setup', 'testing', 'results'
  const [testType, setTestType] = useState(null) // 'tipi' or 'ipip50'
  const [useLunette, setUseLunette] = useState(true)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [totalQuestions, setTotalQuestions] = useState(0)
  const [thinking, setThinking] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const startTest = async () => {
    if (!testType) {
      setError('Please select a test type')
      return
    }

    setPhase('testing')
    setTotalQuestions(testType === 'tipi' ? 10 : 50)
    setCurrentQuestion(0)

    // TODO: Call backend API to start test
    // For now, simulate the test
    simulateTest()
  }

  const simulateTest = () => {
    const questions = testType === 'tipi' ? 10 : 50
    let current = 0

    const interval = setInterval(() => {
      setThinking(true)

      setTimeout(() => {
        current += 1
        setCurrentQuestion(current)
        setThinking(false)

        if (current >= questions) {
          clearInterval(interval)
          // Simulate results
          setResults({
            mbtiType: 'ENFP',
            mbtiTitle: 'The Campaigner',
            bigFive: {
              Extraversion: 5.2,
              Agreeableness: 4.8,
              Conscientiousness: 3.5,
              'Emotional Stability': 5.9,
              Openness: 6.0,
            },
            confidence: 0.87,
            testType: testType === 'tipi' ? 'TIPI-10' : 'IPIP-50',
            maxScore: testType === 'tipi' ? 7.0 : 5.0,
          })
          setPhase('results')
        }
      }, 1500) // 1.5 seconds per question
    }, 2000) // 2 seconds between questions
  }

  const retakeTest = () => {
    setPhase('setup')
    setTestType(null)
    setCurrentQuestion(0)
    setResults(null)
    setError(null)
  }

  const getPercentile = (score, maxScore) => {
    return Math.round((score / maxScore) * 100)
  }

  const getDimensionColor = (dimension) => {
    const colors = {
      Extraversion: 'bg-pokemon-orange',
      Agreeableness: 'bg-pokemon-green',
      Conscientiousness: 'bg-pokemon-blue',
      'Emotional Stability': 'bg-pokemon-brown',
      Neuroticism: 'bg-pokemon-brown',
      Openness: 'bg-pokemon-purple',
    }
    return colors[dimension] || 'bg-pokemon-gold'
  }

  return (
    <div className="min-h-screen bg-pokemon-cream p-4 md:p-8">
      {/* Header */}
      <div className="pokemon-container max-w-4xl mx-auto mb-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <button
            onClick={onClose}
            className="text-xl font-pixel hover:text-pokemon-red transition-colors"
          >
            ← Back
          </button>
          <h1 className="text-2xl md:text-3xl font-pixel text-center flex-1">
            🧠 Personality Test
          </h1>
          {agent && (
            <div className="flex items-center gap-3">
              <img
                src={agent.avatar_url}
                alt={agent.name}
                className="w-12 h-12 rounded-full border-4 border-black"
              />
              <span className="font-pixel text-sm">{agent.name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Setup Phase */}
      {phase === 'setup' && (
        <div className="pokemon-container max-w-2xl mx-auto space-y-8">
          {/* Agent Portrait */}
          {agent && (
            <div className="text-center space-y-4">
              <img
                src={agent.avatar_url}
                alt={agent.name}
                className="w-32 h-32 mx-auto rounded-full border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
              />
              <h2 className="text-2xl font-pixel">{agent.name}</h2>
              <p className="font-pixel text-sm text-pokemon-brown">
                Ready to discover your personality?
              </p>
            </div>
          )}

          {/* Test Selection */}
          <div className="space-y-4">
            <h3 className="text-xl font-pixel text-center mb-6">Choose Your Quest</h3>

            {/* TIPI-10 Option */}
            <div
              className={`pokemon-card cursor-pointer transition-all hover:scale-105 ${
                testType === 'tipi' ? 'ring-4 ring-pokemon-gold' : ''
              }`}
              onClick={() => setTestType('tipi')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setTestType('tipi')}
            >
              <div className="flex items-center gap-4">
                <div className="text-4xl">⚡</div>
                <div className="flex-1">
                  <h4 className="font-pixel text-lg mb-2">Quick Scan</h4>
                  <p className="font-pixel text-xs text-pokemon-brown">
                    10 questions • ~1 minute
                  </p>
                  <span className="personality-badge-orange mt-2 inline-block">TIPI-10</span>
                </div>
              </div>
            </div>

            {/* IPIP-50 Option */}
            <div
              className={`pokemon-card cursor-pointer transition-all hover:scale-105 ${
                testType === 'ipip50' ? 'ring-4 ring-pokemon-gold' : ''
              }`}
              onClick={() => setTestType('ipip50')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setTestType('ipip50')}
            >
              <div className="flex items-center gap-4">
                <div className="text-4xl">🔍</div>
                <div className="flex-1">
                  <h4 className="font-pixel text-lg mb-2">Deep Analysis</h4>
                  <p className="font-pixel text-xs text-pokemon-brown">
                    50 questions • ~5 minutes
                  </p>
                  <span className="personality-badge-purple mt-2 inline-block">IPIP-50</span>
                </div>
              </div>
            </div>
          </div>

          {/* Lunette Toggle */}
          <div className="pokemon-card">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={useLunette}
                onChange={(e) => setUseLunette(e.target.checked)}
                className="w-5 h-5"
              />
              <span className="font-pixel text-sm">Use Lunette for investigation</span>
            </label>
          </div>

          {error && (
            <div className="bg-pokemon-red text-white p-4 rounded border-4 border-black font-pixel text-sm text-center">
              {error}
            </div>
          )}

          <div className="text-center">
            <PokemonButton onClick={startTest} disabled={!testType}>
              Begin Test →
            </PokemonButton>
          </div>
        </div>
      )}

      {/* Testing Phase */}
      {phase === 'testing' && (
        <div className="pokemon-container max-w-3xl mx-auto space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between font-pixel text-sm">
              <span>Progress</span>
              <span>
                {currentQuestion}/{totalQuestions}
              </span>
            </div>
            <div className="h-8 bg-white border-4 border-black rounded overflow-hidden">
              <div
                className="h-full bg-pokemon-green transition-all duration-500"
                style={{ width: `${(currentQuestion / totalQuestions) * 100}%` }}
              />
            </div>
          </div>

          {/* Question Display */}
          <div className="pokemon-card text-center">
            <p className="font-pixel text-sm mb-4">
              {agent?.name || 'Agent'} is answering questions about their personality...
            </p>
            <div className="text-2xl font-pixel text-pokemon-blue">
              Question {currentQuestion + 1}
            </div>
          </div>

          {/* Thinking Indicator */}
          <div className="pokemon-card">
            <div className="flex items-center gap-4">
              <img
                src={agent?.avatar_url}
                alt={agent?.name}
                className="w-16 h-16 rounded-full border-4 border-black"
              />
              <div className="flex-1">
                <span className="font-pixel text-sm">
                  {thinking ? '💭 Thinking...' : '✓ Answered'}
                </span>
                {thinking && (
                  <div className="flex gap-1 mt-2">
                    <span className="animate-bounce">.</span>
                    <span className="animate-bounce delay-100">.</span>
                    <span className="animate-bounce delay-200">.</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Dimension Preview */}
          <div className="pokemon-card">
            <h4 className="font-pixel text-sm mb-4">Personality Dimensions</h4>
            <div className="space-y-3">
              {[
                'Extraversion',
                'Agreeableness',
                'Conscientiousness',
                'Neuroticism',
                'Openness',
              ].map((dimension) => (
                <div key={dimension} className="flex items-center gap-3">
                  <span className="font-pixel text-xs w-32 flex-shrink-0">{dimension}</span>
                  <div className="flex-1 h-6 bg-white border-2 border-black rounded">
                    <div className={`h-full ${getDimensionColor(dimension)} w-0`} />
                  </div>
                  <span className="font-pixel text-xs w-12 text-right">---</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Results Phase */}
      {phase === 'results' && results && (
        <div className="pokemon-container max-w-3xl mx-auto space-y-8">
          {/* MBTI Badge */}
          <div className="text-center space-y-4">
            <div className="inline-block bg-pokemon-gold text-black px-12 py-6 rounded-xl border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] font-pixel text-4xl">
              {results.mbtiType}
            </div>
            <div className="font-pixel text-xl">&quot;{results.mbtiTitle}&quot;</div>
            <div className="personality-badge-green">
              Confidence: {Math.round(results.confidence * 100)}%
            </div>
          </div>

          {/* Big Five Stats */}
          <div className="pokemon-card">
            <h3 className="font-pixel text-lg mb-6 text-center">Big Five Breakdown</h3>
            <div className="space-y-4">
              {Object.entries(results.bigFive).map(([dimension, score]) => (
                <div key={dimension} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-pixel text-sm">{dimension}</span>
                    <span className="font-pixel text-xs">
                      {score.toFixed(1)} / {results.maxScore.toFixed(1)}
                      <span className="ml-2 text-pokemon-brown">
                        ({getPercentile(score, results.maxScore)}th %ile)
                      </span>
                    </span>
                  </div>
                  <div className="h-8 bg-white border-4 border-black rounded overflow-hidden">
                    <div
                      className={`h-full ${getDimensionColor(dimension)} transition-all duration-1000`}
                      style={{ width: `${(score / results.maxScore) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Test Info */}
          <div className="pokemon-card text-center space-y-2">
            <p className="font-pixel text-sm">
              Test: <strong>{results.testType}</strong>
            </p>
            {useLunette && (
              <p className="font-pixel text-xs text-pokemon-green">
                ✓ Trajectory logged to Lunette for investigation
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex flex-wrap justify-center gap-4">
            {useLunette && (
              <PokemonButton onClick={() => alert('Opening Lunette... (TODO)')}>
                🔬 View in Lunette
              </PokemonButton>
            )}
            <PokemonButton onClick={retakeTest}>🔄 Retake Test</PokemonButton>
            <PokemonButton onClick={onClose}>← Back to Main</PokemonButton>
          </div>
        </div>
      )}
    </div>
  )
}

PersonalityTestScreen.propTypes = {
  agent: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    avatar_url: PropTypes.string,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default PersonalityTestScreen
