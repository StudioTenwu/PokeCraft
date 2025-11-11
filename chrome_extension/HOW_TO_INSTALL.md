# 🎮 How to Install AICraft Companion Extension in Chrome

Your Pikachu companion extension is ready! Follow these simple steps:

---

## 📋 Quick Steps

### 1. Open Chrome Extensions Page

In your Chrome browser, go to:
```
chrome://extensions/
```

Or click: Menu (⋮) → Extensions → Manage Extensions

### 2. Enable Developer Mode

Look for the **"Developer mode"** toggle in the **top-right corner** and turn it **ON**.

### 3. Load the Extension

Click the **"Load unpacked"** button (it appears after enabling Developer mode).

### 4. Select the Extension Folder

Navigate to and select this folder:
```
/Users/wz/.orchestra/subagents/AICraft-extension-export/chrome_extension/pikachu-extension
```

**Tip:** You can copy the path above and paste it into the file browser's address bar (Cmd+Shift+G on Mac).

### 5. Verify Installation

You should see "AICraft Companion: Pikachu" appear in your extensions list with:
- ✅ Name: AICraft Companion: Pikachu
- ✅ Version: 1.0.0
- ✅ Status: Enabled

---

## 🚀 Using the Extension

### Opening the Side Panel

**Method 1:** Click the extension icon
1. Find the puzzle piece icon (🧩) in Chrome's toolbar
2. Pin "AICraft Companion: Pikachu" for easy access
3. Click the Pikachu icon
4. The side panel will open on the right

**Method 2:** Right-click method (if available)
1. Right-click anywhere on a webpage
2. Look for extension options in the context menu

### Chat with Pikachu

1. The side panel shows:
   - 🖼️ Pikachu's avatar (top-left)
   - 💬 Chat area (middle)
   - ⌨️ Message input (bottom)
   
2. Type a message like "Hello, Pikachu!"
3. Click "Send" or press Enter
4. See Pikachu's response!

---

## 🎨 What You'll See

The extension has a **retro Pokémon Game Boy Color theme**:
- 🟩 Classic green palette
- 🎮 Pixelated retro styling
- ⚡ Pikachu yellow avatar
- 💬 Bubble-style chat messages

---

## 🔧 Troubleshooting

### Extension doesn't load?
- ✅ Make sure Developer mode is ON
- ✅ Check you selected the correct folder (pikachu-extension)
- ✅ Look for error messages in chrome://extensions/

### Can't find the extension icon?
- ✅ Click the puzzle piece (🧩) icon
- ✅ Pin the extension for quick access
- ✅ The icon should appear in your toolbar

### Side panel doesn't open?
- ✅ Chrome version must support Side Panel API (Chrome 114+)
- ✅ Update Chrome to the latest version if needed
- ✅ Try reloading the extension

### Chat not working?
- ✅ Currently uses mock responses (this is normal!)
- ✅ For real Claude AI, the backend needs to be running
- ✅ Check browser console (F12) for errors

---

## 📦 Files Included

Your extension folder contains:

```
pikachu-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker
├── panel.html            # Side panel UI
├── panel.js              # UI controller
├── chat.js               # Chat logic
├── styles.css            # Pokémon retro theme
└── assets/
    ├── icon16.png        # 16x16 toolbar icon
    ├── icon48.png        # 48x48 icon
    └── icon128.png       # 128x128 extension store icon
```

---

## 🎯 Next Steps

### For Development:
1. Edit files in `pikachu-extension/` folder
2. Go to chrome://extensions/
3. Click the refresh icon (🔄) on your extension
4. Changes will reload immediately

### For Real AI Chat:
1. Start the AICraft backend server
2. Update `chat.js` to connect to the backend
3. Integrate with Claude Agent SDK

### To Share:
1. Zip the `pikachu-extension` folder
2. Share the zip file
3. Others can follow these same installation steps

---

## 💡 Tips

- **Keep it pinned**: Pin the extension for easy access
- **Try different messages**: The mock responses vary
- **Check the styling**: Notice the retro Game Boy theme!
- **Inspect the code**: All files are readable JavaScript/HTML/CSS

---

## 📸 Expected Look

When you open the panel, you should see:
- 🟩 Green Game Boy Color background
- 🟡 Yellow Pikachu avatar (circular, top-left)
- 📝 "TestBot" name in pixelated font
- 💬 Chat area with retro message bubbles
- ⌨️ Input box and green "Send" button

---

**Enjoy chatting with your AICraft companion!** ⚡🎮

Need help? Check the browser console (F12) for error messages.
