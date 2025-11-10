# Hatching Implementation - Quick Reference

## File Locations at a Glance

### Frontend
```
frontend/src/
├── components/
│   └── AgentCreation.jsx           ← Main UI component with progress tracking
├── api.js                          ← EventSource client (createAgentStream)
└── types/
    └── streaming.js                ← Event contract definitions
```

### Backend
```
backend/src/
├── main.py                         ← GET /api/agents/create/stream endpoint
├── agent_service.py                ← create_agent_stream() async generator
├── avatar_generator.py             ← mflux integration
├── llm_client.py                   ← Claude Agent SDK wrapper
└── models/
    ├── agent.py                    ← AgentData Pydantic model
    └── db_models.py                ← AgentDB SQLAlchemy model
```

### Tests
```
backend/tests/
├── unit/
│   └── test_agent_service.py       ← Agent creation tests
├── integration/
│   └── test_agent_deployment.py    ← Integration tests
```

---

## The 4-Phase Hatching Process

### 1️⃣ **Initialization** (Frontend)
- User enters agent description
- Clicks "Hatch Companion" button
- Opens EventSource connection to `/api/agents/create/stream`

### 2️⃣ **LLM Generation** (Backend)
- Claude Agent SDK generates: name, backstory, personality traits, avatar prompt
- Events sent: `progress` (status: generating) → `progress` (status: generated)
- Takes: ~5-30 seconds (depends on Claude response time)

### 3️⃣ **Avatar Generation** (Backend)
- mflux generates image from prompt using 2 inference steps
- Saves to `/backend/static/avatars/{agent_id}.png`
- Events sent: `progress` (status: avatar) → `progress` (status: saving)
- **⚠️ NO intermediate events during this phase**
- Takes: ~10-30 seconds (GPU dependent)

### 4️⃣ **Persistence** (Backend)
- Saves agent to SQLite database
- Returns complete agent object
- Events sent: `complete` with full agent data
- Takes: <1 second

---

## Progress Tracking Breakdown

### What Frontend Receives from Backend
```
Event Name     │ Event Type │ Data Fields
───────────────┼────────────┼─────────────────────────────
progress       │ progress   │ status, message
progress       │ progress   │ status, message
progress       │ progress   │ status, message
progress       │ progress   │ status, message
⚠️ MISSING     │ ---        │ (no step/percent events!)
progress       │ progress   │ status, message
complete       │ complete   │ agent object
```

### Frontend Progress State Structure
```javascript
{
  phase: 'llm' | 'avatar' | null,
  message: 'User-friendly text',
  avatarStep: 0,              // Hardcoded: 0-2
  avatarTotal: 2,             // Hardcoded: always 2
  avatarPercent: 0            // ⚠️ Frontend-estimated, not from server
}
```

---

## Key Architectural Decisions

### Why EventSource/SSE?
- Browser native support (no library needed)
- One-way communication (server → client)
- Perfect for progress updates
- Auto-reconnect on connection loss
- Headers prevent caching/buffering

### Why Claude Agent SDK (not direct API)?
1. No API key management (uses Claude Code CLI credentials)
2. Tool use integration (can use Claude Code tools)
3. Streaming support
4. Proper session handling

### Why Async Generators?
- Efficient resource usage
- Can yield events as they happen
- Cleans up automatically
- Testable with pytest-asyncio

### Why Pydantic Models?
- Type validation
- Auto-serialization to JSON
- Clear contracts between layers
- IDE autocomplete support

---

## Important Implementation Details

### Avatar Prompt Enhancement (avatar_generator.py)
```python
# Original: "A brave wizard with blue robes"
# Enhanced: "A brave wizard with blue robes, Game Boy Color style, 
#            retro pixel art, colorful, nostalgic 90s gaming aesthetic"
```
This ensures Pokemon Game Boy aesthetic across all avatars.

### Event Stream Format (SSE)
```
event: progress
data: {"status":"generating","message":"..."}

event: complete
data: {"id":"...","name":"...","avatar_url":"..."}
```

### Fallback Avatar
If mflux fails:
- Returns robot emoji SVG: `data:image/svg+xml,...`
- Logged as warning, doesn't fail the entire hatching

### Event Cleanup (Frontend)
```javascript
const cleanup = api.createAgentStream(description, callbacks)
// Later:
cleanup()  // Closes EventSource, prevents memory leak
```

---

## Current Gaps & TODOs

### Priority: HIGH
- [ ] Backend should emit `avatar_progress` events during mflux generation
- [ ] Include actual step count and percentage from backend
- [ ] Add cancellation support (abort in-progress hatching)

### Priority: MEDIUM
- [ ] Stream LLM tokens during generation (show Claude thinking)
- [ ] Add retry logic for failed avatar generation
- [ ] Improve error messages with actionable steps

### Priority: LOW
- [ ] Add streaming event tests
- [ ] Expose total time estimate to user
- [ ] Add analytics (which agent types are popular?)

---

## Testing the Hatching Flow

### Manual Testing
```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn src.main:app --reload

# Terminal 2: Check streaming endpoint
curl "http://localhost:8000/api/agents/create/stream?description=A%20brave%20knight"

# Terminal 3: Test frontend
cd frontend
npm run dev
# Open http://localhost:5173 in browser
```

### Automated Testing
```bash
# Run tests
cd backend
pytest tests/unit/test_agent_service.py -v

# With coverage
pytest tests/unit/test_agent_service.py --cov=src
```

---

## Debugging Tips

### If hatching hangs:
1. Check backend logs: `Agent created: ...` message?
2. Check browser console for EventSource errors
3. Verify mflux-generate is installed: `which mflux-generate`
4. Check GPU memory: `nvidia-smi` or `metal status`

### If avatar doesn't appear:
1. Check `/backend/static/avatars/` directory exists
2. Verify file permissions: `ls -la backend/static/avatars/`
3. Check backend logs for "Avatar generated" message
4. Try fallback: Does robot emoji show?

### If SSE connection closes:
1. Browser console should show error message
2. Check backend for exceptions
3. Verify `/api/agents/create/stream` endpoint is responding
4. Check network tab in DevTools

---

## Performance Characteristics

| Phase | Time | Bottleneck | Notes |
|-------|------|------------|-------|
| LLM | 5-30s | Claude API latency | Depends on prompt size & server load |
| Avatar | 10-30s | GPU inference | Flux Schnell + 2 steps = fast |
| Database | <1s | Disk I/O | SQLite is usually instant |
| **Total** | **15-60s** | LLM + Avatar | Parallel processing could improve |

### Optimization Opportunities
1. Parallel LLM + Avatar generation (after LLM completes, start avatar before DB save)
2. Cache common avatar prompts
3. Use lightweight model quantization (3-bit is already good)
4. Reduce mflux steps to 1 for faster drafts

---

## Event Flow Reference

```
User Input
    ↓
EventSource.open() → /api/agents/create/stream
    ↓
Backend: create_agent_stream()
    ├─ yield progress(status: generating)
    ├─ call llm_client.generate_agent()
    ├─ yield progress(status: generated)
    ├─ yield progress(status: avatar)
    ├─ call avatar_generator.generate_avatar()
    ├─ [⚠️ NO EVENTS HERE - mflux blocks]
    ├─ yield progress(status: saving)
    ├─ save to database
    ├─ yield complete(agent data)
    └─ [EventSource closes]
    ↓
Frontend: Receive events, update progress UI
    ↓
Display: "Companion Hatched! ✨" with agent card
```

---

## Code Snippets for Quick Reference

### Frontend Progress State Update
```javascript
setProgress(prev => ({
  ...prev,
  phase: 'avatar',
  message: data.message || 'Hatching...',
  avatarStep: data.step || 0,
  avatarTotal: data.total || 2,
  avatarPercent: data.percent || 0
}))
```

### Backend Event Yield
```python
yield {
    "event": "progress",
    "data": {
        "status": "generating",
        "message": "Consulting with Claude..."
    }
}
```

### Avatar Generation Call
```python
avatar_url = self.avatar_generator.generate_avatar(
    agent_id, 
    agent_data.avatar_prompt
)
```

### Database Persistence
```python
async with async_session_factory() as session:
    db_agent = AgentDB(
        id=agent_id,
        name=agent_data.name,
        backstory=agent_data.backstory,
        personality_traits=agent_data.personality_traits,
        avatar_url=avatar_url,
    )
    session.add(db_agent)
    await session.commit()
```

