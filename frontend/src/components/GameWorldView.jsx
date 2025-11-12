import { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'

// Phase 2: Enhanced rendering constants
const TILE_SIZE = 64  // Upgraded from 32px
const CANVAS_SIZE = 640  // 10 tiles * 64px

// Enhanced tile colors
const TILE_COLORS = {
  grass: '#90EE90',      // Light green
  wall: '#8B4513',       // Brown
  water: '#4682B4',      // Steel blue
  path: '#F5DEB3',       // Wheat
  goal: '#FFD700',       // Gold
  visited: '#98FB98',    // Pale green
  background: '#FFF4E6'  // Default background
}

/**
 * GameWorldView - Canvas rendering of the game world (Phase 3: With animations)
 * @param {Object} props
 * @param {Object} props.worldState - World state with agent position, width, height
 * @param {Array} props.events - Events array
 * @param {boolean} props.deploying - Whether agent is currently deploying
 * @param {string} props.avatarUrl - Agent avatar URL to display
 */
export default function GameWorldView({ worldState, events, deploying, avatarUrl }) {
  const canvasRef = useRef(null)
  const avatarImageRef = useRef(null)

  // Phase 3: Animation state
  const [animatingMove, setAnimatingMove] = useState(false)
  const [displayPosition, setDisplayPosition] = useState(null)

  // Load avatar image when avatarUrl changes
  useEffect(() => {
    if (avatarUrl) {
      const img = new Image()
      img.src = avatarUrl
      img.onload = () => {
        avatarImageRef.current = img
      }
    }
  }, [avatarUrl])

  // Helper function to draw agent (avatar or emoji fallback)
  const drawAgent = (ctx, x, y) => {
    if (avatarImageRef.current) {
      // Draw avatar image centered in tile
      ctx.drawImage(
        avatarImageRef.current,
        x * TILE_SIZE,
        y * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE
      )
    } else {
      // Fallback to emoji
      ctx.font = '48px serif'
      ctx.fillText('🤖', x * TILE_SIZE + 8, y * TILE_SIZE + 48)
    }
  }

  // Initialize canvas with world grid (Phase 2: Enhanced 640x640 rendering)
  useEffect(() => {
    if (!worldState || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return // Guard against test environment

    // Phase 2: Use new canvas size
    canvas.width = CANVAS_SIZE
    canvas.height = CANVAS_SIZE

    // Draw background with enhanced color
    ctx.fillStyle = TILE_COLORS.background
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)

    // Draw the actual world grid tiles if available
    if (worldState.grid && Array.isArray(worldState.grid)) {
      worldState.grid.forEach((row, y) => {
        row.forEach((tile, x) => {
          // Draw tile with color based on type
          ctx.fillStyle = TILE_COLORS[tile] || TILE_COLORS.background
          ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        })
      })
    }

    // Phase 2: Subtle grid borders
    ctx.strokeStyle = '#00000020'
    ctx.lineWidth = 1

    for (let i = 0; i <= 10; i++) {
      ctx.beginPath()
      ctx.moveTo(i * TILE_SIZE, 0)
      ctx.lineTo(i * TILE_SIZE, CANVAS_SIZE)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(0, i * TILE_SIZE)
      ctx.lineTo(CANVAS_SIZE, i * TILE_SIZE)
      ctx.stroke()
    }

    // Draw initial agent position if available
    if (worldState.agentPosition) {
      const [agentX, agentY] = worldState.agentPosition
      drawAgent(ctx, agentX, agentY)
      setDisplayPosition(worldState.agentPosition)
    }
  }, [worldState, avatarUrl])

  // Phase 3: Helper function to redraw grid
  const redrawGrid = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear and redraw background
    ctx.fillStyle = TILE_COLORS.background
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)

    // Redraw the actual world grid tiles if available
    if (worldState?.grid && Array.isArray(worldState.grid)) {
      worldState.grid.forEach((row, y) => {
        row.forEach((tile, x) => {
          // Draw tile with color based on type
          ctx.fillStyle = TILE_COLORS[tile] || TILE_COLORS.background
          ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        })
      })
    }

    // Redraw grid lines
    ctx.strokeStyle = '#00000020'
    ctx.lineWidth = 1

    for (let i = 0; i <= 10; i++) {
      ctx.beginPath()
      ctx.moveTo(i * TILE_SIZE, 0)
      ctx.lineTo(i * TILE_SIZE, CANVAS_SIZE)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(0, i * TILE_SIZE)
      ctx.lineTo(CANVAS_SIZE, i * TILE_SIZE)
      ctx.stroke()
    }

    // Redraw agent at current position if available
    if (displayPosition) {
      ctx.font = '48px serif'
      ctx.fillText('🤖', displayPosition[0] * TILE_SIZE + 8, displayPosition[1] * TILE_SIZE + 48)
    }
  }

  // Phase 4: Flash cell on tool call
  const flashCell = (x, y, color = '#FFFF00') => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.fillStyle = color + '80'  // Semi-transparent
    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    setTimeout(() => redrawGrid(), 150)
  }

  // Phase 4: Show success/error particles
  const showParticle = (x, y, type) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const particle = type === 'success' ? '✓' : '✗'
    const color = type === 'success' ? '#00FF00' : '#FF0000'

    ctx.font = '32px serif'
    ctx.fillStyle = color
    ctx.fillText(particle, x * TILE_SIZE + 16, y * TILE_SIZE + 32)

    setTimeout(() => redrawGrid(), 300)
  }

  // Phase 4: Show thinking bubble above agent
  const showThinking = (x, y) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.font = '24px serif'
    ctx.fillText('💭', x * TILE_SIZE + 40, y * TILE_SIZE - 10)

    setTimeout(() => redrawGrid(), 500)
  }

  // Phase 3: Smooth movement animation
  const animateMove = (fromPos, toPos) => {
    const duration = 300  // ms
    const startTime = performance.now()

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)

      // Interpolate position
      const x = fromPos[0] + (toPos[0] - fromPos[0]) * eased
      const y = fromPos[1] + (toPos[1] - fromPos[1]) * eased

      setDisplayPosition([x, y])

      // Render frame
      const canvas = canvasRef.current
      if (canvas) {
        const ctx = canvas.getContext('2d')
        if (ctx) {
          // Clear previous agent position
          redrawGrid()

          // Draw agent at interpolated position
          ctx.fillStyle = TILE_COLORS.goal
          ctx.fillRect(Math.floor(x) * TILE_SIZE, Math.floor(y) * TILE_SIZE, TILE_SIZE, TILE_SIZE)

          drawAgent(ctx, x, y)
        }
      }

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        setAnimatingMove(false)
        setDisplayPosition(toPos)
      }
    }

    setAnimatingMove(true)
    requestAnimationFrame(animate)
  }

  // Update agent position on canvas (Phase 2: Enhanced with 64px tiles)
  const updateAgentPosition = (fromPos, toPos) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return // Guard against test environment

    // Clear old position
    if (fromPos) {
      ctx.fillStyle = TILE_COLORS.background
      ctx.fillRect(fromPos[0] * TILE_SIZE, fromPos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

      // Redraw grid lines for cleared cell
      ctx.strokeStyle = '#00000020'
      ctx.lineWidth = 1
      ctx.strokeRect(fromPos[0] * TILE_SIZE, fromPos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    }

    // Draw new position with enhanced color
    ctx.fillStyle = TILE_COLORS.goal
    ctx.fillRect(toPos[0] * TILE_SIZE, toPos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    // Phase 2: Larger agent sprite (48px instead of 24px)
    ctx.font = '48px serif'
    ctx.fillText('🤖', toPos[0] * TILE_SIZE + 8, toPos[1] * TILE_SIZE + 48)
  }

  // Mark cell as visited (Phase 2: Enhanced with 64px tiles and colors)
  const markCellVisited = (position) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return // Guard against test environment

    ctx.globalAlpha = 0.3
    ctx.fillStyle = TILE_COLORS.visited
    ctx.fillRect(position[0] * TILE_SIZE, position[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    ctx.globalAlpha = 1.0

    // Redraw agent if on this cell
    if (worldState?.agentPosition &&
        worldState.agentPosition[0] === position[0] &&
        worldState.agentPosition[1] === position[1]) {
      drawAgent(ctx, position[0], position[1])
    }
  }

  // Phase 3-4: Listen for events and trigger animations and visual indicators
  useEffect(() => {
    if (!events || events.length === 0) return

    const lastEvent = events[events.length - 1]

    // Phase 4: Show thinking bubble on reasoning
    if (lastEvent?.type === 'reasoning' && displayPosition) {
      showThinking(displayPosition[0], displayPosition[1])
    }

    // Phase 4: Flash cell on tool call
    if (lastEvent?.type === 'tool_call' && displayPosition) {
      flashCell(displayPosition[0], displayPosition[1])
    }

    // Phase 4: Show particle on tool result
    if (lastEvent?.type === 'tool_result' && displayPosition) {
      showParticle(
        displayPosition[0],
        displayPosition[1],
        lastEvent.success ? 'success' : 'error'
      )
    }

    // Phase 3: Animate movement on world_update
    if (lastEvent?.type === 'world_update') {
      if (lastEvent.agent_moved_from && lastEvent.agent_moved_to) {
        if (!animatingMove) {
          animateMove(lastEvent.agent_moved_from, lastEvent.agent_moved_to)
        }
      }

      if (lastEvent.cell_updated?.position) {
        markCellVisited(lastEvent.cell_updated.position)
      }
    }
  }, [events, animatingMove, displayPosition])

  return (
    <div className="flex flex-col items-center">
      <h3 className="font-pixel text-sm mb-3" style={{ color: 'var(--text-primary)' }}>
        Game World
      </h3>
      <div className="relative">
        <canvas
          ref={canvasRef}
          className="border-4 border-pokemon-green rounded shadow-lg"
          style={{ imageRendering: 'pixelated' }}
        />
        {/* Phase 6: Loading state overlay */}
        {deploying && (
          <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center rounded">
            <div className="text-2xl">⏳ Deploying...</div>
          </div>
        )}
      </div>
      {worldState && (
        <div className="mt-3 text-center">
          <p className="font-pixel text-xs opacity-70" style={{ color: 'var(--text-primary)' }}>
            🗺️ {worldState.width}x{worldState.height} grid
            {worldState.agentPosition && ` • Agent at [${worldState.agentPosition[0]}, ${worldState.agentPosition[1]}]`}
          </p>
        </div>
      )}
    </div>
  )
}

GameWorldView.propTypes = {
  worldState: PropTypes.shape({
    agentPosition: PropTypes.arrayOf(PropTypes.number),
    width: PropTypes.number,
    height: PropTypes.number,
    grid: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string))
  }),
  events: PropTypes.array,
  deploying: PropTypes.bool,
  avatarUrl: PropTypes.string
}

GameWorldView.defaultProps = {
  events: [],
  deploying: false
}
