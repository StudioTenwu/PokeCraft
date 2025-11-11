# Testing Guide for Markdown Parser & Custom Agent Upload

## Overview
This guide covers testing for two new features:
1. **Markdown Rendering** - Rich text formatting in agent messages
2. **Custom Agent Upload** - Upload custom agent JSON files

---

## Feature 1: Markdown Rendering

### What was implemented
- **marked.js** library for parsing markdown to HTML
- **DOMPurify** library for XSS protection
- Markdown rendering for agent responses only (user messages remain plain text)
- CSS styling for all markdown elements (bold, italic, code, links, lists, etc.)

### Test Cases

#### Test 1: Bold Text
1. Start a chat with Pikachu
2. Ask: "Can you use **bold text** in your response?"
3. **Expected**: Agent response contains bolded text with yellow highlight color

#### Test 2: Italic Text
1. Ask: "Can you use *italic text* in your response?"
2. **Expected**: Agent response contains italicized text

#### Test 3: Code Blocks
1. Ask: "Can you show me a code example with `inline code`?"
2. **Expected**: Inline code has different background color and monospace font

#### Test 4: Links
1. Ask: "Can you include a link like [Google](https://google.com)?"
2. **Expected**: Link is clickable and styled with yellow color

#### Test 5: Lists
1. Ask: "Can you give me a numbered list?"
2. **Expected**: Ordered list renders correctly with proper indentation

#### Test 6: XSS Protection
1. Send a message with `<script>alert('xss')</script>`
2. **Expected**: Script tag is stripped/escaped, no alert appears

### Manual Testing Steps

1. **Load the extension** in Chrome:
   ```
   1. Open chrome://extensions/
   2. Enable "Developer mode"
   3. Click "Load unpacked"
   4. Select pikachu-extension/ folder
   ```

2. **Start the backend** (required for real responses):
   ```bash
   cd chrome_extension
   python backend_server.py
   ```

3. **Open the extension panel** and chat with Pikachu

4. **Ask for markdown examples**:
   - "Can you give me an example with **bold**, *italic*, and `code`?"
   - "Show me a list of your favorite things"
   - "Include a link to https://pokemon.com in your response"

### Expected Results
✅ Bold text is highlighted in yellow
✅ Italic text is styled correctly
✅ Code blocks have different background
✅ Links are clickable and styled
✅ Lists have proper bullets/numbers
✅ XSS attempts are sanitized

---

## Feature 2: Custom Agent Upload

### What was implemented
- Upload button in header ("📁 Upload")
- File validation (JSON syntax, schema, size, security)
- Agent data storage in chrome.storage.local
- Backup of original agent for reset capability
- Error handling with user-friendly messages

### Test Cases

#### Test 1: Valid Agent Upload
1. Click "📁 Upload" button
2. Select `test-agent-valid.json` (Charmander)
3. **Expected**:
   - "Validating agent..." message appears
   - "Agent 'Charmander' loaded successfully!" message appears
   - Extension reloads with Charmander avatar and name
   - Chat history is cleared

#### Test 2: Invalid JSON - Missing Fields
1. Click "📁 Upload" button
2. Select `test-agent-invalid.json`
3. **Expected**: Error message "Missing required field: avatar_url"

#### Test 3: Invalid JSON - Syntax Error
1. Create a file with invalid JSON: `{ "name": "Test", }`
2. Upload the file
3. **Expected**: Error message "Invalid JSON: ..."

#### Test 4: Wrong File Type
1. Try to upload a .txt or .pdf file
2. **Expected**: Error message "Please upload a .json file"

#### Test 5: File Too Large
1. Create a JSON file > 100KB
2. Upload the file
3. **Expected**: Error message "File too large (max 100KB)"

#### Test 6: Empty Personality Traits
1. Create JSON with `"personality_traits": []`
2. Upload the file
3. **Expected**: Error message "personality_traits must contain at least one trait"

### Test Files Provided

**test-agent-valid.json** (Charmander):
```json
{
  "id": "charmander",
  "name": "Charmander",
  "avatar_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png",
  "backstory": "I'm Charmander, a Fire-type Pokémon...",
  "personality_traits": ["determined", "hot-headed", "courageous", "competitive", "passionate"]
}
```

**test-agent-invalid.json** (Missing fields):
```json
{
  "id": "missing-fields",
  "name": "Test Agent"
}
```

### Manual Testing Steps

1. **Prepare test files**:
   - Valid: `pikachu-extension/test-agent-valid.json`
   - Invalid: `pikachu-extension/test-agent-invalid.json`
   - More examples: `chrome_extension/example_agents.json`

2. **Test valid upload**:
   ```
   1. Open extension panel
   2. Click "📁 Upload" button
   3. Select test-agent-valid.json
   4. Verify success message and reload
   5. Confirm Charmander appears
   6. Test chat with new personality
   ```

3. **Test invalid upload**:
   ```
   1. Click "📁 Upload" button
   2. Select test-agent-invalid.json
   3. Verify error message appears
   4. Confirm original agent (Pikachu) is still loaded
   ```

4. **Test custom agent from example_agents.json**:
   ```
   1. Create a new JSON file from one of the 8 agents in example_agents.json
   2. Upload it
   3. Verify the new agent loads
   4. Chat and confirm personality matches
   ```

### Expected Results
✅ Valid agents upload successfully
✅ Invalid JSON shows clear error messages
✅ File size limits enforced
✅ Original agent is backed up
✅ Chat history clears on agent change
✅ Extension reloads with new agent
✅ No security vulnerabilities (XSS prevention)

---

## Integration Testing

### Combined Test: Markdown + Custom Agent
1. Upload Charmander (hot-headed personality)
2. Ask: "Tell me about your fire abilities with **bold** and `code` examples"
3. **Expected**:
   - Charmander's personality shows (determined, passionate tone)
   - Response includes markdown formatting (bold, code)
   - Markdown renders correctly with yellow theme styling

### Example Agents to Test
From `example_agents.json`:
- **Pikachu** - energetic, playful
- **Charmander** - determined, hot-headed
- **Bulbasaur** - calm, nurturing
- **Inspector Whiskers** - sarcastic, sophisticated

---

## Security Testing

### XSS Prevention Tests
1. **Markdown XSS**:
   - Ask agent to include: `<script>alert('xss')</script>`
   - Expected: Script is sanitized

2. **Agent Upload XSS**:
   - Upload JSON with `"name": "<img src=x onerror=alert('xss')>"`
   - Expected: HTML is escaped in agent name

3. **URL Validation**:
   - Upload JSON with `"avatar_url": "javascript:alert('xss')"`
   - Expected: Error "Invalid avatar_url"

### All Security Tests Should Pass
✅ XSS attempts in markdown are blocked
✅ XSS attempts in uploaded JSON are sanitized
✅ Only https://, http://, and data:// URLs allowed
✅ File size limits enforced (100KB max)
✅ JSON validation prevents malformed data

---

## Troubleshooting

### Markdown not rendering?
- Check browser console for errors
- Verify marked.min.js and purify.min.js loaded
- Ensure agent messages use markdown syntax

### Upload button not working?
- Check browser console for errors
- Verify agent-upload.js is loaded
- Ensure Chrome extension permissions allow storage

### Backend not responding?
- Verify backend_server.py is running on port 8080
- Check firewall settings
- Extension falls back to mock responses if backend unavailable

---

## Success Criteria

### Phase 1: Markdown Rendering
- ✅ All markdown elements render correctly
- ✅ XSS prevention working
- ✅ CSS styling matches yellow Pikachu theme
- ✅ User messages remain plain text (security)
- ✅ Agent messages support full markdown

### Phase 2: Custom Agent Upload
- ✅ Upload button visible and functional
- ✅ Valid JSON uploads successfully
- ✅ Invalid JSON shows clear errors
- ✅ Agent data persists across sessions
- ✅ Extension reloads with new agent
- ✅ Security validations prevent malicious uploads
- ✅ Backup system allows reset to default

---

## Performance Notes

**File Sizes:**
- marked.min.js: 39KB
- purify.min.js: 23KB
- Total overhead: ~62KB (acceptable for extension)

**Load Time Impact:**
- Minimal - libraries load asynchronously
- Markdown parsing is fast (<1ms per message)
- Agent validation takes <100ms

---

## Next Steps (Future Enhancements)

Not implemented in this version:
1. User markdown input (allow users to format their messages)
2. Agent gallery (browse/select from multiple custom agents)
3. Export current agent (download as JSON)
4. Markdown preview (live preview when typing)
5. Syntax highlighting (for code blocks)
6. Reset to default agent button (UI element)

---

## Contact

For issues or questions, check:
- Browser console (F12) for error messages
- Backend logs (if using backend_server.py)
- Extension manifest.json for permissions
