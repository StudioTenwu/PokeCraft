**Task: Add Simple Night Mode Toggle Button**

**Goal:** Add a simple toggle button to switch between light and dark mode while maintaining the Pokémon Retro aesthetic.

## Success Criteria
- [ ] Toggle button in header (top-right corner suggested)
- [ ] Smooth transition between light and dark themes
- [ ] Dark mode maintains Pokémon Retro vibe
- [ ] Preference saved to localStorage
- [ ] Pixel/retro styled toggle button

## Design Specifications

### Light Mode (Current)
- Background: Cream #FFF4E6
- Accent: Gold #FFD700
- Text: Dark colors
- GB Green accents #8BC34A

### Dark Mode (New)
**Pokémon Night Theme:**
- Background: Dark navy #1A1A2E (night sky)
- Secondary: Deep purple #16213E (twilight)
- Accent: Bright gold #FFD700 (moon/stars)
- Text: Cream #FFF4E6
- Accents: Moonlight blue #4ECCA3

## Implementation Plan

### 1. Create Dark Mode CSS in `pokemon-theme.css`
```css
:root {
  --bg-primary: #FFF4E6;
  --bg-secondary: #FFD700;
  --text-primary: #2C1810;
  --text-secondary: #5C4033;
  --accent: #8BC34A;
}

[data-theme="dark"] {
  --bg-primary: #1A1A2E;
  --bg-secondary: #16213E;
  --text-primary: #FFF4E6;
  --text-secondary: #D4AF37;
  --accent: #4ECCA3;
}

/* Update existing classes to use CSS variables */
.bg-pokemon-cream { background-color: var(--bg-primary); }
.text-pokemon-dark { color: var(--text-primary); }
/* etc... */
```

### 2. Create Toggle Component
File: `frontend/src/components/ThemeToggle.jsx`

```javascript
import { useState, useEffect } from 'react';

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(
    localStorage.getItem('theme') === 'dark'
  );

  useEffect(() => {
    if (isDark) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="font-pixel text-xl p-2 pokemon-button"
      aria-label="Toggle theme"
    >
      {isDark ? '☀️' : '🌙'}
    </button>
  );
}
```

### 3. Add Toggle to App Header
File: `frontend/src/App.jsx`

Add ThemeToggle component to header, positioned top-right:

```jsx
<header className="flex justify-between items-center mb-12">
  <div className="text-center flex-1">
    <h1 className="font-pixel text-3xl sm:text-5xl text-pokemon-gold">
      AICraft
    </h1>
    <p className="font-pixel text-xs text-white">Pokémon Edition</p>
  </div>
  <ThemeToggle />
</header>
```

### 4. Update All Color Classes
Systematically replace hardcoded colors with CSS variables throughout:
- `App.jsx`
- `AgentCard.jsx`
- `AgentCreation.jsx`
- `PokemonButton.jsx`

## Pixel Aesthetic Toggle Button

**Style Options:**

**Option A: Simple Emoji Toggle** (Recommended for MVP)
- Sun ☀️ / Moon 🌙 emoji
- Pixel border
- Pokémon button styling

**Option B: Game Boy Style Switch**
- Sliding toggle like Game Boy power switch
- More implementation time

**Option C: Pixel Icon Toggle**
- Custom pixel art day/night icons
- 16x16px sprites

Choose Option A for quick implementation.

## Testing

**Manual Tests:**
1. Toggle between light and dark modes
2. Verify localStorage persistence (refresh page)
3. Check all components in both themes
4. Verify readability/contrast in dark mode
5. Test responsive behavior on mobile

**Accessibility:**
- Ensure proper `aria-label` on toggle button
- Verify keyboard navigation works
- Check color contrast ratios (WCAG AA minimum)

## Files to Modify
- `frontend/src/styles/pokemon-theme.css` (add dark mode variables)
- `frontend/src/components/ThemeToggle.jsx` (new file)
- `frontend/src/App.jsx` (add toggle to header)
- Update color references in all components to use CSS variables

## Notes
- Keep dark mode colors warm and nostalgic (not harsh blue-black)
- Maintain pixel aesthetic in dark mode
- Smooth transition: `transition: background-color 0.3s ease`
- User mentioned "simple" - don't overcomplicate

**Priority**: Nice-to-have feature, lowest priority of the three tasks. Can be implemented quickly in parallel.

**Working Directory**: You're in an isolated git worktree. Make changes and report completion when done.