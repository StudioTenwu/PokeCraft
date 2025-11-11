import { useEffect, useRef } from 'react'

const TILE_SIZE = 32 // pixels
const COLORS = {
  grass: '#8BC34A', // Pokemon GB green
  wall: '#6D4C41',  // Brown
  water: '#42A5F5', // Blue
  path: '#FFF4E6',  // Cream
  goal: '#FFD700',  // Gold
  agent: '#FF5722'  // Agent color (orange-red)
}

export default function WorldCanvas({ world }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    if (!world || !world.grid) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const { grid, agent_position } = world

    // Set canvas size
    canvas.width = grid[0].length * TILE_SIZE
    canvas.height = grid.length * TILE_SIZE

    // Enable pixel-perfect rendering
    ctx.imageSmoothingEnabled = false

    // Draw grid
    grid.forEach((row, y) => {
      row.forEach((tile, x) => {
        // Draw tile
        ctx.fillStyle = COLORS[tile] || COLORS.grass
        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        // Draw tile border for pixel art effect
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
        ctx.lineWidth = 1
        ctx.strokeRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
      })
    })

    // Draw agent
    if (agent_position) {
      const [agentX, agentY] = agent_position
      ctx.fillStyle = COLORS.agent
      ctx.beginPath()
      ctx.arc(
        agentX * TILE_SIZE + TILE_SIZE / 2,
        agentY * TILE_SIZE + TILE_SIZE / 2,
        TILE_SIZE / 3,
        0,
        Math.PI * 2
      )
      ctx.fill()

      // Agent border
      ctx.strokeStyle = '#FFFFFF'
      ctx.lineWidth = 2
      ctx.stroke()
    }
  }, [world])

  if (!world) {
    return null
  }

  return (
    <div className="pokemon-container">
      <h3 className="font-pixel text-sm mb-4" style={{ color: 'var(--text-primary)' }}>
        🗺️ {world.name}
      </h3>
      <p className="font-pixel text-xs mb-4 opacity-80" style={{ color: 'var(--text-primary)' }}>
        {world.description}
      </p>
      <div className="border-4 inline-block"
           style={{
             borderColor: 'var(--border-color)',
             boxShadow: '8px 8px 0px 0px var(--shadow-color)',
             backgroundColor: 'var(--bg-card)'
           }}>
        <canvas
          ref={canvasRef}
          style={{
            imageRendering: 'pixelated',
            display: 'block'
          }}
        />
      </div>
      <div className="mt-4 font-pixel text-xs" style={{ color: 'var(--text-primary)', opacity: 0.7 }}>
        <p>🟩 Grass  🟫 Wall  🟦 Water  ⬜ Path  🟨 Goal  🔴 Agent</p>
      </div>
    </div>
  )
}
