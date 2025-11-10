**Task: Implement mflux Progress Indicator with SSE Streaming**

**Problem:** Avatar generation takes 30-40 seconds with no visual feedback. Users see "Hatching your companion..." but don't know if it's working or how long it will take.

**Goal:** Parse mflux output in real-time and stream progress updates to frontend, showing step-by-step generation progress.

## Success Criteria
- [ ] Real-time progress updates during 30-40 second avatar generation
- [ ] User sees percentage/step counter (e.g., "Step 1/2 - 50%")
- [ ] Animated egg emoji transitions: 🥚 → 🐣 based on progress
- [ ] Pokémon-themed progress bar with gold/cream colors
- [ ] Graceful fallback if mflux fails
- [ ] All existing tests pass + new tests for streaming

## Backend Implementation

### 1. Modify `backend/src/avatar_generator.py`
- Replace `subprocess.run()` with `subprocess.Popen()` for real-time output
- Use: `Popen(cmd, stdout=PIPE, stderr=STDOUT, text=True, bufsize=1)`
- Read output line-by-line: `for line in process.stdout:`
- Parse mflux progress (discover format first by running manually)
- Convert to generator: `def generate_avatar_stream(agent_id: str, prompt: str) -> Generator[dict, None, str]:`
- Yield: `{"type": "progress", "step": 1, "total": 2, "percent": 50, "message": "..."}`
- Final return: avatar URL or fallback

### 2. Add SSE endpoint in `backend/src/main.py`
- Create `POST /api/agents/create/stream` endpoint
- Accept `CreateAgentRequest` body
- Return `StreamingResponse(media_type="text/event-stream")`
- Stream events in SSE format: `f"event: {name}\ndata: {json.dumps(data)}\n\n"`
- Event types:
  - `llm_start`: {"message": "Generating personality..."}
  - `llm_complete`: {"name": "...", "backstory": "..."}
  - `avatar_start`: {"message": "Creating avatar..."}
  - `avatar_progress`: {"step": 1, "total": 2, "percent": 50}
  - `avatar_complete`: {"avatar_url": "/static/avatars/..."}
  - `complete`: {"agent": {...full agent data...}}
  - `error`: {"message": "..."}

### 3. Update `backend/src/agent_service.py`
- Add `async def create_agent_stream(description: str) -> AsyncGenerator[dict, None]:`
- Yield progress from LLM generation
- Yield progress from avatar generation (iterate over generator)
- Save to database after both complete
- Yield final complete event

## Frontend Implementation

### 1. Update `frontend/src/components/AgentCreation.jsx`
- Add EventSource API integration for SSE
- Replace current fetch with:
```javascript
const eventSource = new EventSource(
  `http://localhost:8000/api/agents/create/stream`,
  { method: 'POST', body: JSON.stringify({description}) }
)
```
- Note: May need to use fetch-event-source library since native EventSource doesn't support POST
- Track progress state: `{phase: 'llm'|'avatar', step: 0, total: 2, percent: 0, message: ''}`
- Update UI based on events

### 2. Enhance loading state
- Show phase-specific messages:
  - LLM: "Dreaming up your companion..."
  - Avatar: "Hatching your companion... (Step 1/2)"
- Add Pokémon-themed progress bar component
- Animate egg emoji based on progress
- Show percentage counter

## TDD Approach

**Step 1: Discover mflux output format**
- Run `mflux-generate` manually in terminal
- Observe stdout/stderr format
- Document patterns to parse
- Write regex/parsing logic

**Step 2: Backend Tests (Red-Green-Refactor-Commit)**
1. Test mflux output parsing with mock subprocess
2. Test SSE event formatting
3. Test generator yields correct events
4. Test error handling (mflux fails)
5. Test database saving after completion

**Step 3: Backend Implementation**
- Implement each component following tests
- Commit after each Red-Green-Refactor cycle

**Step 4: Frontend Tests**
- Test EventSource connection/disconnection
- Test progress state updates
- Test error handling

**Step 5: Frontend Implementation**
- Implement EventSource integration
- Implement progress UI components
- Commit after each cycle

**Step 6: E2E Manual Testing**
- Test full flow from button click to agent display
- Verify progress updates appear smoothly
- Test with slow connection
- Test error scenarios

## Technical Notes

**mflux Output Format** (to be discovered):
- Look for patterns like "Step 1/2", "Progress: 50%", or progress bars
- Parse using regex: `r"Step (\d+)/(\d+)"` or similar
- Handle stderr vs stdout

**SSE Event Format**:
```
event: avatar_progress
data: {"step": 1, "total": 2, "percent": 50, "message": "Generating..."}

(blank line required between events)
```

**Error Handling**:
- Timeout: 60s overall
- Graceful degradation: Use fallback avatar if mflux fails
- Frontend: Close EventSource on complete/error
- Backend: Ensure database save happens even on avatar failure

**Dependencies**:
- Backend: No new dependencies needed
- Frontend: May need `@microsoft/fetch-event-source` for POST support

## Files to Modify
- `backend/src/avatar_generator.py`
- `backend/src/agent_service.py`
- `backend/src/main.py`
- `frontend/src/components/AgentCreation.jsx`
- `frontend/src/api.js` (if exists)
- `backend/tests/unit/test_avatar_generator.py`
- `backend/tests/integration/test_streaming.py` (new)

**Priority**: This is a user-visible feature blocking the user experience. Complete this BEFORE SQLAlchemy migration.

**Working Directory**: You're in an isolated git worktree. Make changes, test thoroughly, and report completion when done.