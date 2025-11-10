# Avatar Display Issue - Root Cause Analysis

**Date**: 2025-11-10
**Status**: Issue Identified

---

## Problem Statement

Generated agent avatars are not being displayed in the frontend. Users only see the fallback emoji 🤖 instead of the actual generated images.

---

## Investigation Summary

### Files Examined

1. **Backend**:
   - `backend/src/avatar_generator.py` - Avatar generation logic
   - `backend/src/agent_service.py` - Agent creation service
   - `backend/src/main.py` - API endpoints

2. **Frontend**:
   - `frontend/src/components/AgentCard.jsx` - Avatar display component
   - `frontend/src/api.js` - API client
   - `frontend/src/components/AgentCreation.jsx` - Agent creation UI

### Evidence Collected

1. **Avatar directory exists but is empty**:
   ```bash
   $ ls -la backend/static/avatars/
   # Empty directory - no PNG files generated
   ```

2. **API endpoint exists**: `POST /api/agents/create/stream` (main.py:88-119)

3. **Missing service method**: `agent_service.create_agent_stream()` **does not exist**
   - Available methods: `init_db()`, `create_agent()`, `get_agent()`

4. **Frontend expects streaming**: Uses `api.createAgentStream()` with SSE callbacks

---

## Root Cause

**The streaming endpoint calls a non-existent method**:

```python
# backend/src/main.py:95
async for event in agent_service.create_agent_stream(request.description):
    # ❌ This method doesn't exist!
```

**What happens**:
1. Frontend calls `POST /api/agents/create/stream`
2. Backend tries to call `agent_service.create_agent_stream()`
3. Method doesn't exist → **AttributeError** is raised
4. Error gets caught and sent as SSE error event
5. Frontend never receives avatar URL
6. Falls back to emoji 🤖

---

## Why This Wasn't Obvious

1. **Silent failure**: The streaming endpoint has a try-catch that converts errors to SSE events
2. **Fallback behavior**: Frontend gracefully shows emoji when no avatar_url
3. **Empty directory**: No evidence of generation attempts
4. **No logs examined**: Would have shown the AttributeError

---

## Architecture Mismatch

### Current Implementation

**Backend** has TWO endpoints:
- `POST /api/agents/create` → Works, uses `create_agent()` ✅
- `POST /api/agents/create/stream` → Broken, calls non-existent method ❌

**Frontend** uses:
- `api.createAgentStream()` → Calls the broken streaming endpoint
- Uses SSE events for progress tracking
- Expects: `llm_start`, `llm_complete`, `avatar_start`, `avatar_progress`, `avatar_complete`, `complete`

### Missing Implementation

The `AgentService.create_agent_stream()` method needs to:
1. Emit `llm_start` event
2. Generate agent data with LLM
3. Emit `llm_complete` event with agent data
4. Emit `avatar_start` event
5. Generate avatar with progress tracking
6. Emit `avatar_progress` events during mflux generation
7. Emit `avatar_complete` event with avatar_url
8. Store in database
9. Emit `complete` event with full agent data

---

## Additional Issue: Avatar URL Format

Even if the streaming worked, there's a **secondary issue** in the frontend display logic.

**Backend** returns paths like:
- `/static/avatars/{agent_id}.png` (if mflux succeeds)
- `data:image/svg+xml,%3Csvg...` (fallback data URI)

**Frontend** (AgentCard.jsx:27-42) only handles:
- URLs starting with `http` → render as `<img>`
- URLs starting with `data:` → render as data URI
- **Everything else** → show emoji 🤖

**Problem**: The path `/static/avatars/...` doesn't start with `http`, so it falls through to emoji!

**Fix needed**: Add condition to handle relative paths:
```jsx
{agent.avatar_url && agent.avatar_url.startsWith('/static/') ? (
  <img
    src={`http://localhost:8000${agent.avatar_url}`}
    alt={agent.name}
    className="..."
  />
) : /* existing conditions */}
```

OR change backend to return full URLs:
```python
return f"http://localhost:8000/static/avatars/{agent_id}.png"
```

---

## Verification Steps

To confirm this diagnosis, check:

1. **Backend logs** for AttributeError when creating agent:
   ```bash
   tail -f backend/logs/app.log
   # Look for: AttributeError: 'AgentService' object has no attribute 'create_agent_stream'
   ```

2. **Browser console** for SSE error events:
   ```javascript
   // Should see: event: error
   // data: {"message": "AttributeError..."}
   ```

3. **Try non-streaming endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/agents/create \
     -H "Content-Type: application/json" \
     -d '{"description": "test"}'
   ```
   Should work and return agent with avatar_url.

---

## Fix Strategy

### Option 1: Implement Streaming Method (Recommended)

**Pros**:
- Matches frontend expectations
- Provides progress feedback during avatar generation
- Better UX

**Cons**:
- More complex implementation
- Needs to track mflux progress

**Files to modify**:
1. `backend/src/agent_service.py` - Add `create_agent_stream()` method
2. `backend/src/avatar_generator.py` - Make `generate_avatar()` async generator for progress
3. `frontend/src/components/AgentCard.jsx` - Fix URL handling

### Option 2: Use Non-Streaming Endpoint

**Pros**:
- Simple fix
- Endpoint already works

**Cons**:
- No progress feedback
- Worse UX for slow avatar generation

**Files to modify**:
1. `frontend/src/components/AgentCreation.jsx` - Use `api.createAgent()` instead
2. `frontend/src/components/AgentCard.jsx` - Fix URL handling

### Option 3: Quick Fix (Temporary)

Fix the URL handling first to see if regular endpoint works:

```jsx
// AgentCard.jsx
{agent.avatar_url && (
  agent.avatar_url.startsWith('http') ||
  agent.avatar_url.startsWith('/static/')
) ? (
  <img
    src={
      agent.avatar_url.startsWith('http')
        ? agent.avatar_url
        : `http://localhost:8000${agent.avatar_url}`
    }
    alt={agent.name}
    className="..."
  />
) : agent.avatar_url?.startsWith('data:') ? (
  /* data URI handling */
) : (
  /* fallback emoji */
)}
```

---

## Recommended Solution

**Phase 1: Quick Fix** (5 minutes)
1. Fix frontend URL handling in AgentCard.jsx
2. Change frontend to use non-streaming endpoint temporarily
3. Verify avatars display (even if no progress bar)

**Phase 2: Implement Streaming** (30-60 minutes)
1. Implement `AgentService.create_agent_stream()`
2. Make avatar generation track progress
3. Test SSE streaming end-to-end
4. Switch frontend back to streaming endpoint

---

## Testing Checklist

After fix:
- [ ] Avatar PNG files appear in `backend/static/avatars/`
- [ ] Avatar displays in frontend (not emoji)
- [ ] Fallback emoji shows when generation fails
- [ ] Progress bar works during generation
- [ ] Data URI fallback displays if mflux unavailable
- [ ] Multiple agents show different avatars

---

## Related Files

**Backend**:
- `backend/src/agent_service.py:46-94` - `create_agent()` method
- `backend/src/avatar_generator.py:15-66` - `generate_avatar()` method
- `backend/src/main.py:88-119` - Streaming endpoint
- `backend/src/main.py:40-43` - Static file serving

**Frontend**:
- `frontend/src/components/AgentCard.jsx:27-42` - Avatar display logic
- `frontend/src/api.js:30-115` - Streaming API client
- `frontend/src/components/AgentCreation.jsx` - Agent creation UI with progress

---

## Questions to Resolve

1. **Is mflux working?** Can we run `mflux-generate` manually to test?
2. **What should progress events look like?** mflux outputs steps - can we parse them?
3. **Should we cache avatars?** Or regenerate on demand?
4. **API base URL**: Should be environment variable instead of hardcoded `localhost:8000`
