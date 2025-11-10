# Plan: Real-Time Percentage Progress for Hatching

**Goal:** Display accurate real-time percentage progress during agent creation (hatching), with LLM generation at 25% and avatar generation at 75% of total time.

---

## 🧪 Testing Results

### mflux Progress Tracking ✅ CONFIRMED WORKING

**Test Command:**
```bash
mflux-generate --model schnell --path ~/.AICraft/models/schnell-3bit \
  --prompt "test pokemon" --steps 2 --output test.png
```

**Output (captured from stderr):**
```
  0%|          | 0/2 [00:00<?, ?it/s]
 50%|█████     | 1/2 [00:14<00:14, 14.18s/it]
100%|██████████| 2/2 [00:34<00:00, 17.96s/it]
```

**Key Finding:** mflux uses `tqdm` library which outputs progress to **stderr** with percentage updates at each step.

**Regex Pattern to Extract Progress:**
```python
import re
pattern = re.compile(r'(\d+)%\|')
match = pattern.search(stderr_line)
if match:
    percentage = int(match.group(1))  # e.g., 0, 50, 100
```

**Real-Time Capture Method:** Use `subprocess.Popen()` with `stderr=subprocess.PIPE` and read line-by-line.

---

## 📊 Progress Distribution

| Phase | Progress Range | Duration (Approx) | Description |
|-------|---------------|-------------------|-------------|
| **LLM Generation** | 0% → 25% | 5-15 seconds | Claude Agent SDK generates backstory |
| **Backstory Complete** | 25% | Instant | Emit "Backstory generated" milestone |
| **Avatar Generation** | 25% → 100% | 20-35 seconds | mflux creates image (75% of total) |
| **Database Save** | 100% | <1 second | Save to SQLite (included in avatar phase) |

**Total Estimated Time:** 25-50 seconds per agent

---

## 🎯 Implementation Plan (NO CODE, PLAN ONLY)

### **Phase 1: Create Streaming LLM Client**

**File:** `backend/src/llm_client.py`

**New Method:** `generate_agent_stream(description: str) -> AsyncGenerator[dict, None]`

**Approach:**
1. Create async generator that yields progress events
2. Track streaming chunks from `claude_agent_sdk.query()`
3. Emit progress events based on:
   - **0%**: Start of LLM query
   - **10-20%**: As chunks arrive (estimate based on typical response length ~500 tokens)
   - **25%**: When `ResultMessage` with `.result` is received (backstory complete)

**Event Schema:**
```python
# Progress during generation
yield {
    "type": "llm_progress",
    "progress": 15,  # 0-25
    "message": "Generating personality..."
}

# Backstory complete milestone
yield {
    "type": "backstory_complete",
    "progress": 25,
    "message": "Backstory generated",
    "agent_data": AgentData(...)  # Pydantic model
}
```

**Challenges:**
- Claude Agent SDK streaming is NOT chunked by tokens (only yields final `ResultMessage`)
- **Solution:** Emit heartbeat events every 2-3 seconds during LLM wait
  - 0% at start
  - 12% after 3 seconds
  - 18% after 6 seconds
  - 25% when result arrives

---

### **Phase 2: Create Streaming Avatar Generator**

**File:** `backend/src/avatar_generator.py`

**New Method:** `generate_avatar_stream(agent_id: str, prompt: str) -> AsyncGenerator[dict, None]`

**Approach:**
1. Replace `subprocess.run()` with `subprocess.Popen()` for real-time stderr capture
2. Read stderr line-by-line using `async for line in process.stderr:`
3. Parse tqdm progress bars with regex: `r'(\d+)%\|'`
4. Map mflux progress (0→100%) to overall progress (25→100%):
   ```python
   # mflux reports: 0%, 50%, 100% (for --steps 2)
   mflux_pct = int(match.group(1))
   overall_pct = 25 + (mflux_pct * 0.75)  # Map to 25-100 range
   ```

**Event Schema:**
```python
yield {
    "type": "avatar_progress",
    "progress": 62,  # 25-100 (mapped from mflux 50%)
    "message": f"Drawing avatar... ({mflux_pct}%)"
}
```

**Implementation Details:**
- Use `asyncio.create_subprocess_exec()` for async subprocess
- Set `stderr=asyncio.subprocess.PIPE`
- Read stderr with: `async for line in process.stderr:`
- Handle timeout (60 seconds)
- Fallback to default avatar if process fails

**Expected Progress Events (for --steps 2):**
- 25%: Avatar generation started
- 62.5%: mflux 50% complete (step 1/2 done)
- 100%: mflux 100% complete (step 2/2 done)

---

### **Phase 3: Wire Streaming to AgentService**

**File:** `backend/src/agent_service.py`

**Modified Method:** `create_agent_stream(description: str)` (already exists, needs update)

**Changes:**
1. Replace `await self.llm_client.generate_agent(description)` with:
   ```python
   async for event in self.llm_client.generate_agent_stream(description):
       yield event  # Forward LLM progress events to SSE

   # Extract final AgentData from last event
   agent_data = event["agent_data"]
   ```

2. Replace `self.avatar_generator.generate_avatar(...)` with:
   ```python
   async for event in self.avatar_generator.generate_avatar_stream(...):
       yield event  # Forward avatar progress events to SSE

   # Extract final avatar_url from last event
   avatar_url = event["avatar_url"]
   ```

3. Emit database save event (quick, no intermediate progress needed):
   ```python
   yield {
       "event": "progress",
       "data": {"progress": 100, "message": "Saving to Pokédex..."}
   }
   ```

4. Final completion event:
   ```python
   yield {
       "event": "complete",
       "data": {"agent": {...}, "progress": 100}
   }
   ```

**Error Handling:**
- If LLM fails, emit error event and stop at <25%
- If avatar fails, use fallback avatar and jump to 100%
- If database fails, emit error at 100%

---

### **Phase 4: Update Frontend Event Handlers**

**File:** `frontend/src/components/AgentCreation.jsx`

**Changes:**

1. **Remove frontend progress estimation logic** (currently estimates based on phase timing)

2. **Add new event listeners:**
   ```javascript
   // LLM progress (0-25%)
   eventSource.addEventListener('llm_progress', (e) => {
       const { progress, message } = JSON.parse(e.data);
       setProgress(progress);  // Use server value directly
       setPhaseMessage(message);
       setCurrentEmoji('🥚');  // Egg during LLM
   });

   // Backstory complete milestone (25%)
   eventSource.addEventListener('backstory_complete', (e) => {
       const { progress, message } = JSON.parse(e.data);
       setProgress(25);
       setPhaseMessage(message);  // "Backstory generated"
       setCurrentEmoji('🐣');  // Hatching emoji
   });

   // Avatar progress (25-100%)
   eventSource.addEventListener('avatar_progress', (e) => {
       const { progress, message } = JSON.parse(e.data);
       setProgress(progress);  // 25-100
       setPhaseMessage(message);
       setCurrentEmoji('🐣');  // Still hatching
   });

   // Keep existing 'complete' listener
   eventSource.addEventListener('complete', (e) => {
       const { agent } = JSON.parse(e.data);
       setProgress(100);
       setCurrentEmoji('✨');  // Success!
       // ... rest of completion logic
   });
   ```

3. **Add progress bar smoothness:**
   ```jsx
   <div className="progress-bar" style={{
       width: `${progress}%`,
       transition: 'width 0.5s ease-out'  // Smooth transitions
   }} />
   ```

4. **Prevent progress regression:**
   ```javascript
   const setProgress = (newProgress) => {
       setProgressState(prev => Math.max(prev, newProgress));  // Never go backward
   };
   ```

---

### **Phase 5: Update SSE Endpoint**

**File:** `backend/src/main.py`

**Endpoint:** `GET /api/agents/create/stream`

**Changes:**
1. Update SSE formatting to handle new event types:
   ```python
   async for event in service.create_agent_stream(description):
       event_type = event.get("type", "progress")
       event_data = event.get("data", event)

       yield f"event: {event_type}\n"
       yield f"data: {json.dumps(event_data)}\n\n"
   ```

2. Ensure proper event names match frontend listeners:
   - `llm_progress`
   - `backstory_complete`
   - `avatar_progress`
   - `complete`
   - `error`

**No changes needed to endpoint signature** (already streaming, just need to forward new event types)

---

## 🧪 Testing Strategy

### **Unit Tests**

**File:** `backend/tests/unit/test_avatar_generator_streaming.py`

**Tests:**
1. `test_mflux_progress_parsing()` - Verify regex extracts percentages correctly
2. `test_progress_mapping()` - Ensure mflux 0-100% maps to overall 25-100%
3. `test_fallback_on_error()` - Avatar generation fails → fallback avatar at 100%

**File:** `backend/tests/unit/test_llm_streaming.py`

**Tests:**
1. `test_llm_progress_events()` - Mock Agent SDK, verify events emitted
2. `test_backstory_complete_event()` - Verify 25% milestone
3. `test_heartbeat_during_wait()` - Ensure progress updates during long LLM wait

### **Integration Tests**

**File:** `backend/tests/integration/test_agent_creation_streaming.py`

**Tests:**
1. `test_full_streaming_progress()` - End-to-end: verify progress goes 0→25→100
2. `test_progress_never_regresses()` - Assert each event.progress >= previous
3. `test_no_progress_gaps()` - Ensure updates within 5-second intervals

### **Manual Testing**

1. **Browser DevTools** - Network tab, monitor EventSource messages
2. **Slow connection simulation** - Throttle to 3G, ensure progress updates
3. **Multiple concurrent creations** - Test 3 agents at once, verify no cross-talk
4. **Error scenarios:**
   - Kill mflux mid-generation → verify fallback
   - Invalid LLM response → verify error at <25%

---

## 📝 Event Flow Diagram

```
User clicks "Create Agent"
         ↓
Frontend opens EventSource → GET /api/agents/create/stream?description=...
         ↓
Backend: AgentService.create_agent_stream()
         ↓
┌────────────────────────────────────────────────────────────────┐
│ Phase 1: LLM Generation (0% → 25%)                            │
├────────────────────────────────────────────────────────────────┤
│ Event: llm_progress      | progress: 0   | "Starting..."      │
│ Event: llm_progress      | progress: 12  | "Generating..."    │
│ Event: llm_progress      | progress: 18  | "Generating..."    │
│ Event: backstory_complete| progress: 25  | "Backstory ready!" │
└────────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────────┐
│ Phase 2: Avatar Generation (25% → 100%)                       │
├────────────────────────────────────────────────────────────────┤
│ Event: avatar_progress   | progress: 25  | "Drawing (0%)"     │
│ Event: avatar_progress   | progress: 62  | "Drawing (50%)"    │
│ Event: avatar_progress   | progress: 100 | "Drawing (100%)"   │
└────────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────────┐
│ Phase 3: Database Save (<1 second)                            │
├────────────────────────────────────────────────────────────────┤
│ Event: progress          | progress: 100 | "Saving..."        │
│ Event: complete          | progress: 100 | agent: {...}       │
└────────────────────────────────────────────────────────────────┘
         ↓
Frontend displays completed agent + avatar
```

---

## ⚠️ Edge Cases & Error Handling

| Scenario | Behavior | Progress |
|----------|----------|----------|
| **LLM timeout (>30s)** | Fallback agent data | Jump to 25% |
| **LLM returns invalid XML** | Fallback agent data | Jump to 25% |
| **mflux process crashes** | Fallback avatar (SVG emoji) | Jump to 100% |
| **mflux timeout (>60s)** | Kill process, use fallback | Jump to 100% |
| **Database write fails** | Emit error event | Stay at 100%, show error |
| **User closes browser mid-creation** | EventSource auto-closes, backend logs | N/A |
| **Network interruption** | EventSource reconnects (browser auto) | Resume from last event |

**Error Event Format:**
```python
yield {
    "event": "error",
    "data": {
        "message": "Avatar generation failed",
        "progress": 62,  # Where error occurred
        "fallback": True  # Using fallback avatar
    }
}
```

---

## 🔧 Technical Decisions

### **Why async generators over callbacks?**
- Cleaner code (no callback hell)
- Natural streaming with `async for`
- Easy error propagation with try/except
- FastAPI StreamingResponse works seamlessly

### **Why stderr for mflux instead of polling file size?**
- **Real-time:** tqdm updates stderr instantly
- **Accurate:** Exact percentage, not estimation
- **Reliable:** No race conditions with file writes
- **Standard:** tqdm is the standard Python progress library

### **Why heartbeats during LLM instead of silence?**
- User sees continuous progress (better UX)
- Prevents timeout concerns
- Shows system is working, not frozen
- Aligns with "always show activity" design pattern

### **Why 25/75 split instead of 50/50?**
- **Reality check:** Avatar generation (mflux) takes 2-3x longer than LLM
- **Typical timing:**
  - LLM: 5-15 seconds
  - Avatar: 20-35 seconds
- **User expectation:** Progress matches actual work being done
- **Option to adjust:** Can be configured in `Config` if timing changes

---

## 📦 Files to Modify (Summary)

### **Backend** (5 files)

1. **`backend/src/llm_client.py`**
   - Add `generate_agent_stream()` method
   - Emit `llm_progress` and `backstory_complete` events

2. **`backend/src/avatar_generator.py`**
   - Add `generate_avatar_stream()` method
   - Parse mflux stderr with regex
   - Emit `avatar_progress` events

3. **`backend/src/agent_service.py`**
   - Update `create_agent_stream()` to use new streaming methods
   - Forward all progress events to SSE

4. **`backend/src/main.py`**
   - Update SSE formatting to handle new event types
   - No endpoint signature changes needed

5. **`backend/src/config.py`** (optional)
   - Add `LLM_PROGRESS_WEIGHT = 0.25`
   - Add `AVATAR_PROGRESS_WEIGHT = 0.75`

### **Frontend** (1 file)

1. **`frontend/src/components/AgentCreation.jsx`**
   - Remove estimation logic
   - Add event listeners for `llm_progress`, `backstory_complete`, `avatar_progress`
   - Add smooth progress bar transitions
   - Prevent progress regression

### **Tests** (3 new files)

1. **`backend/tests/unit/test_llm_streaming.py`**
2. **`backend/tests/unit/test_avatar_generator_streaming.py`**
3. **`backend/tests/integration/test_streaming_progress.py`**

---

## ✅ Acceptance Criteria

- [ ] LLM generation shows 0% → 25% progress with updates every 2-3 seconds
- [ ] "Backstory generated" event emits at exactly 25% progress
- [ ] Avatar generation shows 25% → 100% with real mflux progress (0%, 50%, 100%)
- [ ] Progress bar never goes backward
- [ ] No progress gaps longer than 5 seconds
- [ ] All existing tests still pass
- [ ] New streaming tests achieve >80% coverage
- [ ] Manual browser test shows smooth progress bar animation
- [ ] Error scenarios (LLM fail, avatar fail) handled gracefully

---

## 🚀 Implementation Order

1. **Backend: Avatar streaming** (hardest, most critical)
   - Test mflux stderr parsing standalone first
   - Add `generate_avatar_stream()` method
   - Unit test with mocked subprocess

2. **Backend: LLM streaming** (medium difficulty)
   - Add heartbeat logic
   - Emit backstory_complete event
   - Unit test with mocked Agent SDK

3. **Backend: Service integration** (easy)
   - Wire up both generators
   - Update `create_agent_stream()`

4. **Frontend: Event handlers** (easy)
   - Add new event listeners
   - Remove estimation code
   - Add progress bar CSS transition

5. **Testing** (validation)
   - Integration tests
   - Manual browser testing
   - Error scenario testing

---

## 📊 Expected Timeline

- **Phase 1 (Avatar streaming):** 2-3 hours
- **Phase 2 (LLM streaming):** 1-2 hours
- **Phase 3 (Service integration):** 30 minutes
- **Phase 4 (Frontend):** 30 minutes
- **Phase 5 (Testing):** 1-2 hours

**Total:** ~5-8 hours (1 day of focused work)

---

## 🎯 Success Metrics

**Before (Current):**
- Progress jumps: 0% → 50% (long pause) → 100%
- User anxiety during 30-second avatar generation silence
- Frontend estimation ≠ actual backend work

**After (Target):**
- Smooth progress: 0% → 12% → 18% → 25% → 62% → 100%
- Real-time updates from actual work progress
- User confidence: "The system is working"
- Accurate progress bar matches backend reality

---

## 🔍 Potential Future Enhancements

1. **Fine-grained LLM progress** - If Agent SDK exposes token streaming in future
2. **Configurable progress weights** - Let users adjust 25/75 split via config
3. **Progress analytics** - Track average creation time, optimize slow phases
4. **Cancel button** - Allow user to abort mid-creation (kill subprocess)
5. **Queue system** - Show "3 agents ahead of you" if system busy

---

**END OF PLAN**
