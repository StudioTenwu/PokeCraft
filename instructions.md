**Task: Fix Personality Tag Colors - Make Each Unique**

**Problem:** Currently only the first two personality traits have different colors. All other traits use the same color. The user wants each personality tag to have slightly different colors.

**Goal:** Assign unique colors to all personality trait badges in the AgentCard component with Pokémon Retro aesthetic.

## Success Criteria
- [ ] Each personality trait has a unique color
- [ ] Colors match Pokémon Retro theme (warm, nostalgic palette)
- [ ] Good contrast/readability on cream background
- [ ] Colors cycle if there are more traits than colors in palette
- [ ] Visual polish with pixel aesthetic maintained

## Current State
File: `frontend/src/components/AgentCard.jsx`

The personality badges are currently rendered with limited color variation. User mentioned "See SCREENSHOT ~1" - the first two have colors, rest are same.

## Implementation Plan

### 1. Define Color Palette
Create a Pokémon-themed color palette in `AgentCard.jsx` or `pokemon-theme.css`:

**Suggested Palette** (Game Boy Color inspired):
- Red: `#FF6B6B` (Charizard red)
- Blue: `#4ECDC4` (Squirtle blue)
- Yellow: `#FFE66D` (Pikachu yellow)
- Green: `#95E1D3` (Bulbasaur green)
- Purple: `#C7CEEA` (Gengar purple)
- Orange: `#FFA07A` (Charmander orange)
- Pink: `#FFB6D9` (Jigglypuff pink)
- Brown: `#D4A574` (Eevee brown)

All with good contrast on cream background (#FFF4E6).

### 2. Modify AgentCard.jsx
Update the personality badge rendering logic:

```javascript
const PERSONALITY_COLORS = [
  'bg-red-400',
  'bg-blue-400', 
  'bg-yellow-400',
  'bg-green-400',
  'bg-purple-400',
  'bg-orange-400',
  'bg-pink-400',
  'bg-amber-400'
];

// In render:
{agent.personality_traits.map((trait, index) => (
  <span 
    key={trait}
    className={`
      ${PERSONALITY_COLORS[index % PERSONALITY_COLORS.length]}
      px-3 py-1 rounded-full text-xs font-pixel 
      border-2 border-black shadow-pixel
    `}
  >
    {trait}
  </span>
))}
```

### 3. Alternative: Custom Color Mapping
If specific traits should have specific colors:

```javascript
const TRAIT_COLORS = {
  brave: 'bg-red-400',
  curious: 'bg-blue-400',
  friendly: 'bg-green-400',
  clever: 'bg-purple-400',
  energetic: 'bg-yellow-400',
  calm: 'bg-blue-300',
  creative: 'bg-pink-400',
  loyal: 'bg-amber-400',
  // fallback for unknown traits
  default: 'bg-gray-400'
};

const getTraitColor = (trait) => {
  return TRAIT_COLORS[trait.toLowerCase()] || TRAIT_COLORS.default;
};
```

### 4. Ensure Pixel Aesthetic
Maintain existing pixel styling:
- `border-2 border-black` for retro outline
- `shadow-pixel` class for depth
- `font-pixel` for Press Start 2P font
- `rounded-full` for pill shape

## Testing

**Manual Testing:**
1. Create agents with 2-8 different personality traits
2. Verify each trait has a unique color
3. Test with more traits than colors (should cycle)
4. Check contrast/readability on cream background
5. Verify on both light and future dark mode

**Visual Check:**
- Compare with user's SCREENSHOT ~1 reference
- Ensure improvement over current state
- Get user approval on color choices

## Files to Modify
- `frontend/src/components/AgentCard.jsx`
- Possibly `frontend/src/styles/pokemon-theme.css` (if adding custom colors)

## TDD Note
This is primarily a visual/styling task. Testing strategy:
1. Manual visual inspection
2. Screenshot comparison before/after
3. User approval
4. Consider snapshot tests if time permits

**Priority**: This is a quick frontend polish task that can be done in parallel with the mflux progress indicator.

**Working Directory**: You're in an isolated git worktree. Make changes and report completion when done.