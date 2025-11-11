# Chrome Extension Testing Checklist

## ⚠️ IMPORTANT: Manual Testing Required

The extension code is complete, but **requires manual testing in Chrome browser** to verify functionality.

---

## Prerequisites

1. **Start Backend Server:**
   ```bash
   cd /Users/wz/.orchestra/subagents/AICraft-extension-export/chrome_extension
   python backend_server.py
   ```
   - Should see: "🎮 Starting AICraft Extension Backend Server..."
   - Backend runs on: http://localhost:8080

2. **Load Extension in Chrome:**
   - Navigate to: `chrome://extensions/`
   - Enable "Developer mode" (top right toggle)
   - Click "Load unpacked"
   - Select folder: `/Users/wz/.orchestra/subagents/AICraft-extension-export/chrome_extension/pikachu-extension/`
   - Extension should appear in toolbar

3. **Open Extension:**
   - Click extension icon in toolbar
   - Side panel should open on the right

---

## Test 1: Backend Haiku Model ✅ (Tested via curl)

**Status:** ✅ CONFIRMED WORKING

**Backend Test Results:**
```bash
$ curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What is your name?",
    "agent_data": {
      "name": "Pikachu",
      "backstory": "I am Pikachu...",
      "personality_traits": ["energetic", "loyal", "brave"]
    }
  }'

# Response: ~3 seconds
# Model: haiku (confirmed)
```

**✅ PASSED** - Backend uses Haiku model for fast responses

---

## Test 2: Thinking Bubble Animation ⚠️ (Requires Chrome)

**Status:** ⚠️ NEEDS USER VERIFICATION

### Steps to Test:

1. **Open extension side panel**
2. **Type a message:** "Hello Pikachu!"
3. **Click "Send" button**

### Expected Behavior:

✅ Thinking bubble appears immediately after clicking Send
✅ Bubble shows active Pokemon's sprite (Pikachu initially)
✅ Pokemon sprite bounces up and down smoothly
✅ Three dots (•••) animate in sequence (left → middle → right)
✅ Bubble has yellow background (#FFD700)
✅ Bubble has speech tail pointing down
✅ Bubble disappears when response arrives
✅ If error occurs, bubble still disappears

### What to Check:

**Visual Appearance:**
- [ ] Thinking bubble is visible
- [ ] Pokemon sprite is 32x32px, pixelated style
- [ ] Three dots are visible and large enough
- [ ] Yellow/brown Pikachu theme colors
- [ ] Speech bubble tail points downward

**Animation:**
- [ ] Pokemon sprite bounces smoothly (1 second loop)
- [ ] Dots bounce in sequence (0s, 0.2s, 0.4s delay)
- [ ] No jittering or stuttering
- [ ] Animation stops when bubble disappears

**Timing:**
- [ ] Bubble appears < 50ms after clicking Send
- [ ] Bubble disappears when response arrives
- [ ] Bubble disappears if network error occurs

### Screenshots Needed:

📸 **Screenshot 1:** Thinking bubble with Pikachu sprite
📸 **Screenshot 2:** Thinking bubble mid-animation (dots at different heights)

### Console Check:

1. Open Chrome DevTools (F12)
2. Check Console tab
3. Verify NO errors related to:
   - `showThinkingBubble is not defined`
   - `hideThinkingBubble is not defined`
   - `Cannot read property 'remove' of null`

---

## Test 3: Multi-Agent Dropdown System ⚠️ (Requires Chrome)

**Status:** ⚠️ NEEDS USER VERIFICATION

### Steps to Test:

1. **Open extension side panel**
2. **Locate dropdown button** (should say "Pikachu ▼")
3. **Click dropdown button**

### Expected Behavior:

✅ Dropdown menu opens below button
✅ 4 Pokemon appear in list:
   - Pikachu (Electric-type)
   - Charmander (Fire-type)
   - Bulbasaur (Grass/Poison-type)
   - Squirtle (Water-type)
✅ Active Pokemon is highlighted (darker background)
✅ Each option shows 24x24px sprite + name
✅ Hovering over option highlights it (yellow background)
✅ Arrow rotates 180° when dropdown opens

### What to Check:

**Dropdown Appearance:**
- [ ] Dropdown button is visible in header
- [ ] Button shows current Pokemon name
- [ ] Arrow (▼) points down when closed
- [ ] Arrow points up (▲) when open
- [ ] Dropdown menu appears below button
- [ ] All 4 Pokemon are listed
- [ ] Active Pokemon has darker background
- [ ] Pokemon sprites are visible (24x24px)

**Dropdown Interaction:**
- [ ] Click button to open dropdown
- [ ] Click button again to close dropdown
- [ ] Click outside dropdown to close it
- [ ] Hover over options highlights them
- [ ] Click a Pokemon switches to that agent

### Screenshots Needed:

📸 **Screenshot 3:** Dropdown menu open showing all 4 Pokemon
📸 **Screenshot 4:** Active Pokemon highlighted in dropdown

---

## Test 4: Agent Switching ⚠️ (Requires Chrome)

**Status:** ⚠️ NEEDS USER VERIFICATION

### Steps to Test:

1. **Chat with Pikachu:**
   - Send message: "Hello! What's your type?"
   - Wait for response (should mention Electric-type)
   - Send another message: "Tell me about yourself"
   - Wait for response

2. **Switch to Charmander:**
   - Click dropdown button
   - Select "Charmander"
   - Verify avatar changes to Charmander sprite
   - Verify dropdown shows "Charmander"

3. **Verify chat history cleared:**
   - Chat area should be EMPTY (no Pikachu messages)
   - Send message: "Hello! What's your type?"
   - Wait for response (should mention Fire-type)

4. **Switch back to Pikachu:**
   - Click dropdown button
   - Select "Pikachu"
   - Verify avatar changes back to Pikachu sprite

5. **Verify chat history restored:**
   - Chat area should show OLD Pikachu messages
   - Pikachu's conversation should be exactly as before
   - No Charmander messages should appear

### Expected Behavior:

✅ Avatar image changes when switching agents
✅ Dropdown text updates to show active agent
✅ Chat history is EMPTY when switching to new agent
✅ Chat history is RESTORED when switching back
✅ Each agent maintains separate conversation history
✅ Thinking bubble shows ACTIVE agent's sprite

### What to Check:

**Avatar Updates:**
- [ ] Avatar image changes when switching
- [ ] Avatar matches selected Pokemon
- [ ] Dropdown text updates to Pokemon name

**Chat History Isolation:**
- [ ] Pikachu's chat: Shows only Pikachu messages
- [ ] Charmander's chat: Shows only Charmander messages
- [ ] Switching back restores old messages
- [ ] No cross-contamination between agents

**Agent Personalities:**
- [ ] Pikachu mentions Electric-type, energetic personality
- [ ] Charmander mentions Fire-type, determined personality
- [ ] Bulbasaur mentions Grass-type, calm personality
- [ ] Squirtle mentions Water-type, cool personality

### Screenshots Needed:

📸 **Screenshot 5:** Pikachu agent with chat history
📸 **Screenshot 6:** Charmander agent (empty chat, different avatar)
📸 **Screenshot 7:** Back to Pikachu (old chat restored)

---

## Test 5: Custom Agent Upload ⚠️ (Requires Chrome)

**Status:** ⚠️ NEEDS USER VERIFICATION

### Steps to Test:

1. **Upload Valid Agent:**
   - Click "📁 Upload" button in header
   - File picker should open
   - Select file: `test-agent-valid.json`
   - Wait for validation

2. **Verify Success:**
   - Green success message appears: "Agent 'Charmander' loaded successfully!"
   - Extension reloads automatically (~1 second delay)
   - New agent should be active (Charmander shown)

3. **Check Dropdown:**
   - Click dropdown button
   - Verify 5 Pokemon now appear (4 original + 1 custom)
   - Custom agent should be marked (could have different styling if implemented)

4. **Switch Between Agents:**
   - Switch from custom agent to Pikachu
   - Switch from Pikachu to custom agent
   - Verify all agents work correctly

5. **Upload Invalid Agent:**
   - Click "📁 Upload" button
   - Select file: `test-agent-invalid.json`
   - Red error message should appear with specific error details

### Expected Behavior:

✅ File picker opens when clicking Upload button
✅ Valid JSON uploads successfully
✅ Success message displays in green
✅ Extension reloads with new agent
✅ Custom agent appears in dropdown (5th option)
✅ Original 4 Pokemon are preserved (not replaced)
✅ Invalid JSON shows specific error message
✅ File size > 100KB rejected
✅ Non-.json files rejected

### What to Check:

**Upload Flow:**
- [ ] "📁 Upload" button is visible
- [ ] Clicking button opens file picker
- [ ] File picker filters to .json files
- [ ] Upload processes (loading message shows)

**Success Case (test-agent-valid.json):**
- [ ] Green success message appears
- [ ] Message says: "Agent 'Charmander' loaded successfully!"
- [ ] Extension reloads automatically
- [ ] New agent is active (avatar + name updated)
- [ ] New agent appears in dropdown
- [ ] Can switch between all 5 agents

**Error Cases (test-agent-invalid.json):**
- [ ] Red error message appears
- [ ] Error message is specific (e.g., "Missing required field: name")
- [ ] Current agent is preserved (no changes)
- [ ] Can try uploading again

**Validation Errors to Test:**
- [ ] Missing field: "Missing required field: X"
- [ ] Invalid URL: "Invalid avatar_url..."
- [ ] File too large: "File too large (max 100KB)"
- [ ] Wrong file type: "Please upload a .json file"
- [ ] Invalid JSON syntax: "Invalid JSON: ..."

### Screenshots Needed:

📸 **Screenshot 8:** Success message after upload
📸 **Screenshot 9:** Dropdown showing 5 agents (4 + custom)
📸 **Screenshot 10:** Error message for invalid agent

---

## Test 6: Chrome DevTools Console ⚠️ (Requires Chrome)

**Status:** ⚠️ NEEDS USER VERIFICATION

### Steps to Test:

1. **Open Chrome DevTools:**
   - Press F12 (or Cmd+Option+I on Mac)
   - Click "Console" tab

2. **Perform all actions:**
   - Send a message
   - Switch agents
   - Upload a custom agent
   - Interact with dropdown

3. **Check for errors:**
   - Look for red error messages
   - Look for yellow warnings

### Expected Behavior:

✅ NO red errors in console
✅ NO yellow warnings related to extension code
✅ Backend API calls succeed (200 status)
✅ No "Uncaught TypeError" errors
✅ No "Cannot read property of undefined" errors
✅ Storage API calls succeed

### What to Check:

**Console Logs (informational - OK to see):**
- [ ] "AICraft Companion extension event: install" (first time only)
- [ ] "Initialized 4 Pokemon agents" (first time only)
- [ ] "Multi-agent system already initialized" (subsequent loads)

**Network Tab (API Calls):**
- [ ] POST to http://localhost:8080/chat returns 200
- [ ] Response contains {"response": "..."}
- [ ] No CORS errors
- [ ] Response time < 5 seconds

**Errors to Watch For:**
- [ ] ❌ "agentData is not defined" → Schema migration failed
- [ ] ❌ "Cannot read property 'avatar_url' of undefined" → Agent loading failed
- [ ] ❌ "showThinkingBubble is not defined" → Function not loaded
- [ ] ❌ "Failed to fetch" → Backend not running
- [ ] ❌ "CORS policy" → CORS misconfiguration

### Screenshots Needed:

📸 **Screenshot 11:** Console with NO errors after all tests

---

## Test 7: Extension Persistence ⚠️ (Requires Chrome)

**Status:** ⚠️ NEEDS USER VERIFICATION

### Steps to Test:

1. **Chat with Pikachu:**
   - Send 2-3 messages
   - Get responses

2. **Close Extension:**
   - Close the side panel
   - Or close Chrome entirely

3. **Reopen Extension:**
   - Click extension icon
   - Or restart Chrome and open extension

4. **Verify Data Persisted:**
   - Pikachu should still be active
   - Chat history should be preserved
   - Dropdown should still show 4 Pokemon
   - If custom agent was uploaded, it should still be there

### Expected Behavior:

✅ Active agent persists across sessions
✅ Chat history persists across sessions
✅ Custom agents persist (if uploaded)
✅ Extension state fully restored

### What to Check:

- [ ] Active agent same as before closing
- [ ] Chat history intact (all messages preserved)
- [ ] Dropdown shows same agents
- [ ] Custom uploaded agents still available
- [ ] No data loss

---

## Summary Checklist

### Code Implementation: ✅ COMPLETE

- [x] Feature 1: Multi-Agent System (4 Pokemon)
- [x] Feature 2: Thinking Bubble Animation
- [x] Feature 3: Backend Haiku Model
- [x] Storage schema migration
- [x] Separate chat histories per agent
- [x] Custom agent upload integration

### Backend Testing: ✅ COMPLETE

- [x] Backend API tested with curl
- [x] Haiku model confirmed working
- [x] Response time ~3 seconds
- [x] JSON response format correct

### Chrome Extension Testing: ⚠️ REQUIRES USER

- [ ] Test 1: Backend Haiku Model (✅ tested via curl)
- [ ] Test 2: Thinking Bubble Animation
- [ ] Test 3: Multi-Agent Dropdown System
- [ ] Test 4: Agent Switching
- [ ] Test 5: Custom Agent Upload
- [ ] Test 6: Chrome DevTools Console
- [ ] Test 7: Extension Persistence

---

## 📸 Required Evidence

Please provide the following to confirm all tests pass:

1. **11 Screenshots total:**
   - Thinking bubble (2 screenshots)
   - Dropdown menu (2 screenshots)
   - Agent switching (3 screenshots)
   - Custom upload (3 screenshots)
   - Console with no errors (1 screenshot)

2. **Console Output:**
   - Copy/paste Chrome DevTools console output
   - Should show no red errors

3. **Confirmation Statement:**
   - "I tested all 7 test scenarios"
   - "All expected behaviors were observed"
   - "No errors in Chrome DevTools console"

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to fetch" error
**Solution:** Backend not running. Start with `python backend_server.py`

### Issue: Dropdown doesn't open
**Solution:** Check console for JavaScript errors. May need to reload extension.

### Issue: Thinking bubble doesn't appear
**Solution:** Check console for errors. Verify backend is responding.

### Issue: Chat history not persisting
**Solution:** Check chrome.storage.local in DevTools → Application → Storage

### Issue: Custom agent upload fails
**Solution:** Check JSON file is valid. Use `test-agent-valid.json` first.

### Issue: Avatar doesn't change when switching
**Solution:** Clear browser cache and reload extension.

---

## 📝 Test Results Form

After completing all tests, fill out:

```
Date Tested: ___________
Chrome Version: ___________
Extension Version: AICraft Companion

Test 1 (Backend): ✅ PASS / ❌ FAIL
Test 2 (Thinking Bubble): ✅ PASS / ❌ FAIL
Test 3 (Dropdown): ✅ PASS / ❌ FAIL
Test 4 (Agent Switching): ✅ PASS / ❌ FAIL
Test 5 (Custom Upload): ✅ PASS / ❌ FAIL
Test 6 (DevTools Console): ✅ PASS / ❌ FAIL
Test 7 (Persistence): ✅ PASS / ❌ FAIL

Issues Found:
1. ___________
2. ___________

Screenshots Attached: YES / NO
Console Output Attached: YES / NO
```

---

**END OF TESTING CHECKLIST**
