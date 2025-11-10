Implement Phase 2: World Creation

## Goal
Allow children to describe a world in natural language, LLM generates a 2D grid layout, render it with PixiJS/Canvas, and place the agent (who can't move yet - no tools).

## Requirements from designer.md
- Child describes world → LLM generates grid layout
- 2D top-down rendering (PixiJS/Canvas) 
- Agent appears in world but can't move (no tools taught yet)
- Follow Pokémon Retro aesthetic (cream #FFF4E6, gold #FFD700, GB green #8BC34A)
- Minimum features - keep it simple for MVP

## Technical Spec

### Backend (/backend/src/)

1. **world_service.py** - New service for world generation
   - `async def create_world(agent_id: str, description: str) -> dict[str, Any]`
   - Returns: `{ id, name, grid (2D array), width, height, agent_position }`

2. **llm_world_generator.py** - LLM world generation
   - Use Anthropic SDK to generate world from description
   - Output JSON: `{ name, description, grid: [[tile_type]], agent_start: [x, y] }`
   - Tile types: "grass", "wall", "water", "path", "goal"
   - Grid size: 10x10 for MVP (keep simple)

3. **main.py** - Add endpoints
   - `POST /api/worlds/create` - Create world for agent
   - `GET /api/worlds/{world_id}` - Get world data

4. **Database** - Add worlds table
   ```sql
   CREATE TABLE worlds (
     id TEXT PRIMARY KEY,
     agent_id TEXT,
     name TEXT,
     description TEXT,
     grid_data TEXT,  -- JSON string
     width INTEGER,
     height INTEGER,
     created_at DATETIME
   )
   ```

### Frontend (/frontend/src/)

1. **components/WorldCanvas.jsx** - PixiJS renderer
   - Use @pixi/react or raw PixiJS
   - Render 2D grid with top-down view
   - Tile sprites for each type (grass, wall, water, etc.)
   - Agent sprite at starting position
   - Pixel-perfect rendering (`image-rendering: pixelated`)

2. **components/WorldCreation.jsx** - World creation UI
   - Text input for world description
   - "Create World" button
   - Shows loading state while LLM generates
   - Displays WorldCanvas when ready

3. **Update App.jsx**
   - Add world creation flow after agent creation
   - Show agent card + world creation input
   - When world created, show WorldCanvas with agent in it

4. **Sprites/Assets** - Simple pixel art tiles
   - Use emoji or simple colored squares for MVP
   - Grass: 🟩 or green square
   - Wall: 🟫 or brown square
   - Water: 🟦 or blue square
   - Agent: Use created avatar or 😊 emoji

## Implementation Approach (TDD)

1. **Write tests first** (backend/tests/)
   - test_llm_world_generator.py - Test LLM world generation
   - test_world_service.py - Test world creation and retrieval
   - test_world_endpoints.py - Test API endpoints

2. **Implement backend**
   - Create llm_world_generator.py with Claude integration
   - Create world_service.py with database operations
   - Add endpoints to main.py
   - Run tests, iterate until passing

3. **Implement frontend**
   - Create WorldCanvas with PixiJS (or Canvas if simpler)
   - Create WorldCreation UI component
   - Wire up API calls
   - Manual browser testing

4. **End-to-end test**
   - Write Playwright test: create agent → create world → see world rendered

## Key Constraints
- Keep grid size small (10x10) for MVP
- Use simple tile types (5 max: grass, wall, water, path, goal)
- Agent can't move yet (Phase 3 adds movement tools)
- Focus on minimum viable feature - just render the world

## Success Criteria
- [ ] User enters world description
- [ ] LLM generates 10x10 grid layout
- [ ] World saved to database
- [ ] PixiJS/Canvas renders 2D top-down view
- [ ] Agent appears at starting position
- [ ] Pokémon Retro aesthetic maintained
- [ ] All backend tests passing
- [ ] E2E test passes

## Notes
- Follow existing patterns from Phase 1 (Pydantic models, SSE for progress if needed)
- Keep prompts similar style to agent generation
- Type hints required for all Python code
- Use the existing Pokemon theme CSS

Start by writing backend tests, then implement backend, then frontend. Report back when ready to merge.