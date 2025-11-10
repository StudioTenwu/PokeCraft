export default function AgentCard({ agent }) {
  const getBadgeClass = (trait) => {
    const traitLower = trait.toLowerCase()
    if (traitLower.includes('brave')) return 'personality-badge-brave'
    if (traitLower.includes('curious')) return 'personality-badge-curious'
    if (traitLower.includes('helpful')) return 'personality-badge-helpful'
    if (traitLower.includes('creative')) return 'personality-badge-creative'
    if (traitLower.includes('friendly')) return 'personality-badge-friendly'
    return 'personality-badge-default'
  }

  return (
    <div className="pokemon-card">
      <div className="flex flex-col md:flex-row gap-6">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {agent.avatar_url && agent.avatar_url.startsWith('http') ? (
            <img
              src={agent.avatar_url}
              alt={agent.name}
              className="w-32 h-32 object-cover border-4 border-black rounded pixel-header"
            />
          ) : agent.avatar_url && agent.avatar_url.startsWith('data:') ? (
            <div
              className="w-32 h-32 border-4 border-black rounded"
              dangerouslySetInnerHTML={{__html: `<img src="${agent.avatar_url}" alt="${agent.name}" class="w-full h-full" />`}}
            />
          ) : (
            <div className="w-32 h-32 bg-pokemon-gold border-4 border-black rounded flex items-center justify-center">
              <span className="text-6xl">🤖</span>
            </div>
          )}
        </div>

        {/* Agent Info */}
        <div className="flex-1">
          <h2 className="font-pixel text-2xl mb-4 text-pokemon-gold" style={{textShadow: '3px 3px 0px rgba(0,0,0,0.3)'}}>
            {agent.name}
          </h2>
          <p className="text-sm mb-4 leading-relaxed font-sans" style={{color: 'var(--text-primary)'}}>
            {agent.backstory}
          </p>

          {/* Personality Traits */}
          {agent.personality_traits && agent.personality_traits.length > 0 && (
            <div>
              <p className="font-pixel text-xs mb-2" style={{color: 'var(--text-primary)'}}>Personality:</p>
              <div className="flex flex-wrap gap-2">
                {agent.personality_traits.map((trait, i) => (
                  <span key={i} className={getBadgeClass(trait)}>
                    {trait}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
