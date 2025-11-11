# ✅ Chrome Extension Test Checklist

Use this checklist to verify the extension works correctly.

---

## 🔧 Installation Tests

- [ ] **Step 1:** Opened chrome://extensions/
- [ ] **Step 2:** Enabled "Developer mode" toggle
- [ ] **Step 3:** Clicked "Load unpacked"
- [ ] **Step 4:** Selected the `pikachu-extension` folder
- [ ] **Step 5:** Extension appears in the list
- [ ] **Step 6:** No error messages shown

**Extension Info:**
- [ ] Name shows: "AICraft Companion: Pikachu"
- [ ] Version shows: "1.0.0"
- [ ] Description shows Pikachu's backstory
- [ ] Status is "Enabled" (toggle is ON)

---

## 🎨 Visual Tests

### Panel Opening
- [ ] Extension icon visible in toolbar (or puzzle menu 🧩)
- [ ] Clicking icon opens the side panel
- [ ] Panel opens on the right side of the browser
- [ ] Panel has the green Game Boy Color theme

### UI Elements Present
- [ ] **Header Section:**
  - [ ] Circular avatar image (yellow Pikachu)
  - [ ] Agent name "Pikachu" displayed
  - [ ] Header has dark green background

- [ ] **Chat Area:**
  - [ ] Large green chat area in middle
  - [ ] Initial system message shows (dotted border)
  - [ ] Scrollable area works

- [ ] **Input Section:**
  - [ ] Message input box visible
  - [ ] "Send" button present (green)
  - [ ] Input has focus indicator

---

## 💬 Functional Tests

### Sending Messages
1. [ ] Click in message input box
2. [ ] Type: "Hello, Pikachu!"
3. [ ] Press Enter OR click Send button
4. [ ] Message appears in chat area (right side, dark green bubble)

### Receiving Responses
5. [ ] Agent response appears (left side, darker bubble)
6. [ ] Response is different each time (random mock)
7. [ ] No JavaScript errors in console (F12)

### Multiple Messages
8. [ ] Send 3-5 different messages
9. [ ] All messages display correctly
10. [ ] Chat area scrolls automatically to bottom
11. [ ] User messages on right, agent on left

---

## 🎯 Advanced Tests

### Persistence
- [ ] Close the side panel
- [ ] Reopen the panel
- [ ] Chat history persists (messages still visible)

### Manifest Check
Open browser console (F12) and run:
```javascript
chrome.runtime.getManifest().name
```
- [ ] Returns: "AICraft Companion: Pikachu"

### Service Worker
- [ ] Go to chrome://extensions/
- [ ] Click "service worker" link under the extension
- [ ] DevTools opens showing background.js
- [ ] No errors in console

### Icons
- [ ] Extension icon shows in toolbar (16x16)
- [ ] Extension card shows icon (48x48)
- [ ] All icons display correctly (not broken images)

---

## 🐛 Error Checking

### Console Check
1. [ ] Open panel
2. [ ] Open DevTools (F12)
3. [ ] Check Console tab
4. [ ] No red errors visible
5. [ ] Only info/debug logs (if any)

### Network Check
1. [ ] Go to Network tab in DevTools
2. [ ] Send a message
3. [ ] No failed network requests (mock chat is local)

---

## 📊 Performance Tests

- [ ] Panel opens quickly (< 1 second)
- [ ] No lag when typing messages
- [ ] Send button responds immediately
- [ ] Messages render without delay
- [ ] No memory leaks (check Task Manager after 10+ messages)

---

## 🎨 Styling Tests

### Color Scheme
- [ ] Background: Game Boy green (#9BBC0F)
- [ ] Header: Darker green (#8BAC0F)
- [ ] User messages: Dark green (#306230)
- [ ] Agent messages: Darkest green (#0F380F)
- [ ] Text: Readable contrast

### Fonts
- [ ] Pixelated retro font (if available)
- [ ] Or fallback to Courier New/monospace
- [ ] Text size readable

### Responsive
- [ ] Panel width is appropriate
- [ ] No horizontal scrolling
- [ ] Elements don't overflow
- [ ] Works with different panel widths

---

## 📝 Notes Section

Write any issues or observations here:

**Installation:**
```
[Your notes here]
```

**Visual appearance:**
```
[Your notes here]
```

**Functionality:**
```
[Your notes here]
```

**Performance:**
```
[Your notes here]
```

**Bugs found:**
```
[Your notes here]
```

---

## ✨ Success Criteria

All must be ✅ to pass:

1. [ ] Extension installs without errors
2. [ ] Panel opens and displays correctly
3. [ ] All UI elements present and styled
4. [ ] Chat functionality works (send/receive)
5. [ ] No console errors
6. [ ] Retro theme looks good
7. [ ] Service worker runs without errors

---

**Test completed by:** _______________  
**Date:** _______________  
**Chrome version:** _______________  
**OS:** _______________  

**Overall result:** [ ] PASS  [ ] FAIL  [ ] NEEDS WORK
