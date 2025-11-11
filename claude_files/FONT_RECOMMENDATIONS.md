# Font Usage Recommendations: Press Start 2P vs Silkscreen

## Current Analysis

Based on reviewing the codebase, here's what's using `.font-pixel` (currently defaults to Silkscreen):

### 🎯 Should Use Press Start 2P (`.font-title`)

**Major Headings & Titles:**
1. ✅ **Main App Header** - "PokéCraft" (DONE)
2. **Agent Name** - `AgentPanel.jsx:55` - The Pokémon's name display
3. **Section Headings:**
   - "🚀 {name} in Action" - `App.jsx:203`
   - "🌍 {name}'s World" - `App.jsx:248`
   - "Select an agent to continue" - `App.jsx:224`

**Why Press Start 2P here:**
- These are **primary focal points** - names and major sections
- Press Start 2P is **curved and friendly** - perfect for Pokémon personality
- Creates **visual hierarchy** - titles stand out from body text

---

### ✓ Keep Using Silkscreen (`.font-ui`)

**UI Elements & Stats:**
1. **Buttons** - Info button, agent selector, world buttons
2. **Labels** - "Agent:", "Backend:", "Frontend:"
3. **Small Text** - Tool descriptions, backstory text
4. **Stats/Numbers** - "✨ X pokémons hatched"
5. **Body Content** - Descriptions, backstory expansions

**Why Silkscreen here:**
- **Readable at small sizes** - straight edges are clearer
- **UI clarity** - buttons and controls need to be scannable
- **Technical info** - URLs, numbers, stats benefit from monospace

---

## Recommended Changes

### High Priority: Pokémon Names

**File:** `frontend/src/components/AgentPanel.jsx:55`

**Current:**
```jsx
<h2 className="font-pixel text-xl mb-2 text-center"
    style={{ color: 'var(--text-primary)' }}>
  {agent.name}
</h2>
```

**Recommended:**
```jsx
<h2 className="font-title text-xl mb-2 text-center"
    style={{ color: 'var(--text-primary)' }}>
  {agent.name}
</h2>
```

**Reason:** The Pokémon's name is THE most important piece of info in the panel. Press Start 2P's friendly, curved style makes it feel more like a character name (like in actual Pokémon games).

---

### Medium Priority: Section Headings

**Files:** `frontend/src/App.jsx`

**1. Deployment Header (line 203):**
```jsx
// Current
<h2 className="font-pixel text-xl" style={{ color: 'var(--text-primary)' }}>
  🚀 {selectedAgent.name} in Action
</h2>

// Recommended
<h2 className="font-title text-xl" style={{ color: 'var(--text-primary)' }}>
  🚀 {selectedAgent.name} in Action
</h2>
```

**2. World Header (line 248):**
```jsx
// Current
<h2 className="font-pixel text-lg" style={{ color: 'var(--text-primary)' }}>
  🌍 {selectedAgent.name}'s World
</h2>

// Recommended
<h2 className="font-title text-lg" style={{ color: 'var(--text-primary)' }}>
  🌍 {selectedAgent.name}'s World
</h2>
```

**3. No Agent Selected (line 224):**
```jsx
// Current
<h2 className="font-pixel text-2xl mb-4" style={{ color: 'var(--text-primary)' }}>
  Select an agent to continue ⬆️
</h2>

// Recommended
<h2 className="font-title text-2xl mb-4" style={{ color: 'var(--text-primary)' }}>
  Select an agent to continue ⬆️
</h2>
```

**Reason:** These are section headers that introduce major UI areas. Press Start 2P gives them prominence and character.

---

### Low Priority: Subheadings

**File:** `frontend/src/components/AgentPanel.jsx`

**Traits Label (line 81):**
```jsx
// Current
<h3 className="font-pixel text-xs mb-2" style={{ color: 'var(--text-primary)' }}>
  Traits:
</h3>

// Could use font-title, but font-ui is fine too
```

**Equipped Tools Label (line 107):**
```jsx
// Current
<h3 className="font-pixel text-xs mb-2" style={{ color: 'var(--text-primary)' }}>
  📦 Equipped Tools:
</h3>

// Keep as font-ui - it's a functional label
```

**Reason:** These are minor subheadings. Could go either way, but Silkscreen keeps them distinct from the main Pokémon name.

---

## Visual Hierarchy Guide

```
┌────────────────────────────────────────┐
│         PokéCraft                      │ ← Press Start 2P (App title)
├────────────────────────────────────────┤
│  [Agent: Sparkeon ▾] [Info] [Theme]   │ ← Silkscreen (UI controls)
├────────────────────────────────────────┤
│ ┌──────────────────────────────────┐   │
│ │       Sparkeon                    │   │ ← Press Start 2P (Pokémon name)
│ │  "A spark of joy..."              │   │ ← Silkscreen (description)
│ │  • friendly • curious             │   │ ← Silkscreen (traits)
│ └──────────────────────────────────┘   │
│                                         │
│  🚀 Sparkeon in Action                 │ ← Press Start 2P (section header)
│  [Deploy] [Stop] [Clear]               │ ← Silkscreen (buttons)
└────────────────────────────────────────┘
```

---

## Implementation Priority

### ✅ Must Change (Strong Recommendation):
1. **Pokémon Name** in AgentPanel - This is the Pokémon's identity

### 🎯 Should Change (Recommended):
2. **Section Headers** - "in Action", "World", "Select an agent"

### 💡 Optional (Visual Preference):
3. **Subheadings** - "Traits:", "Equipped Tools:" could go either way

---

## Design Rationale

**Press Start 2P (Curved):**
- Friendly, nostalgic, playful
- Perfect for **character names** and **game-like headers**
- Evokes Pokémon Game Boy aesthetic
- Best at **medium to large sizes** (16px+)

**Silkscreen (Straight):**
- Clean, readable, modern
- Perfect for **UI controls** and **functional text**
- Better at **small sizes** (12px and below)
- Keeps interface scannable and usable

---

## Summary

Change these 4 elements to `.font-title`:
1. Pokémon name (AgentPanel.jsx:55) ⭐ PRIORITY
2. "🚀 {name} in Action" (App.jsx:203)
3. "🌍 {name}'s World" (App.jsx:248)
4. "Select an agent..." (App.jsx:224)

This creates a clear hierarchy:
- **Press Start 2P** = Names & major sections (character/personality)
- **Silkscreen** = Everything else (UI/functionality)
