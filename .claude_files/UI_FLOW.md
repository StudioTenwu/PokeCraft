# User Experience Flow: Avatar Progress Indicator

## Before Implementation
```
User clicks "Hatch Companion"
    ↓
[Static spinning Pokéball ⚽]
"Hatching your companion..."
    ↓
(30-40 seconds of silence)
    ↓
Agent appears suddenly
```

**Problem**: No feedback, no idea if it's working or how long it will take

---

## After Implementation

### Phase 1: LLM Generation (2-5 seconds)
```
User clicks "Hatch Companion"
    ↓
╔════════════════════════════════╗
║          🥚                     ║
║                                 ║
║  Dreaming up your companion... ║
╚════════════════════════════════╝
```

**SSE Event**: `llm_start`

---

### Phase 2: Avatar Generation Start
```
╔════════════════════════════════╗
║          🥚                     ║
║                                 ║
║  Hatching your companion...    ║
╚════════════════════════════════╝
```

**SSE Event**: `avatar_start`

---

### Phase 3: Avatar Progress - Step 1/2 (0-49%)
```
╔════════════════════════════════╗
║          🥚                     ║
║                                 ║
║  Hatching... Step 1/2          ║
║                                 ║
║  Step 1/2 - 25%                ║
║  ┌────────────────────────┐   ║
║  │████████░░░░░░░░░░░░░░░░│   ║
║  │        25%             │   ║
║  └────────────────────────┘   ║
╚════════════════════════════════╝
```

**SSE Event**: `avatar_progress` with `{step: 1, total: 2, percent: 25}`

---

### Phase 4: Avatar Progress - Step 2/2 (50%+)
```
╔════════════════════════════════╗
║          🐣 ← EGG HATCHING!    ║
║                                 ║
║  Hatching... Step 2/2          ║
║                                 ║
║  Step 2/2 - 75%                ║
║  ┌────────────────────────┐   ║
║  │████████████████████░░░░│   ║
║  │        75%             │   ║
║  └────────────────────────┘   ║
╚════════════════════════════════╝
```

**SSE Event**: `avatar_progress` with `{step: 2, total: 2, percent: 75}`

---

### Phase 5: Complete (100%)
```
╔════════════════════════════════╗
║          🐣                     ║
║                                 ║
║  Hatching... Step 2/2          ║
║                                 ║
║  Step 2/2 - 100%               ║
║  ┌────────────────────────┐   ║
║  │████████████████████████│   ║
║  │        100%            │   ║
║  └────────────────────────┘   ║
╚════════════════════════════════╝
```

**SSE Event**: `avatar_complete` with avatar URL

---

### Phase 6: Agent Card Display
```
╔════════════════════════════════╗
║   Companion Hatched! ✨        ║
╚════════════════════════════════╝

┌──────────────────────────────┐
│  [Generated Avatar Image]     │
│                                │
│  Name: Sparky                 │
│  Backstory: A curious...      │
│  Traits: Brave, Smart, Kind   │
└──────────────────────────────┘

      [Hatch Another]
```

**SSE Event**: `complete` with full agent data

---

## Visual Elements

### Emoji Animation
- **0-49%**: 🥚 (Egg - still forming)
- **50-100%**: 🐣 (Hatching - breaking out!)

### Progress Bar
```
┌────────────────────────┐
│███████████░░░░░░░░░░░░│  ← Gold (#FFD700)
│       50%             │  ← Black text
└────────────────────────┘
  ↑ Black border (4px)
  Background: Cream (#FFFACD)
```

### Phase Messages
1. `"Dreaming up your companion..."` - During LLM generation
2. `"Hatching your companion..."` - Avatar generation starts
3. `"Hatching... Step 1/2"` - During mflux step 1
4. `"Hatching... Step 2/2"` - During mflux step 2

---

## Error Handling

### If mflux fails:
```
╔════════════════════════════════╗
║          🤖                     ║
║                                 ║
║  Your companion is ready!      ║
║  (Using placeholder avatar)    ║
╚════════════════════════════════╝
```

**Fallback**: Golden emoji SVG (🤖 in gold square)

---

## Technical Details

### SSE Event Sequence
1. `llm_start` → "Dreaming up..."
2. `llm_complete` → Agent name/backstory ready
3. `avatar_start` → "Hatching..."
4. `avatar_progress` (step 1) → Progress bar 0-49%
5. `avatar_progress` (step 2) → Progress bar 50-99%
6. `avatar_complete` → Avatar URL ready
7. `complete` → Full agent data, save to DB, display card

### Timing
- **LLM Phase**: 2-5 seconds
- **Avatar Phase**: 30-40 seconds
  - Step 1: ~15 seconds
  - Step 2: ~15 seconds
- **Total**: 32-45 seconds

### Network Events
```
Browser                    Backend
   |                          |
   |-- POST /create/stream -->|
   |                          |
   |<-- SSE: llm_start -------|
   |<-- SSE: llm_complete ----|
   |<-- SSE: avatar_start ----|
   |<-- SSE: avatar_progress -| (multiple times)
   |<-- SSE: avatar_complete -|
   |<-- SSE: complete ---------|
   |                          |
   [Display agent card]       [Close stream]
```

---

## Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Feedback** | None | Real-time updates |
| **Progress** | Unknown | Step X/Y - Z% |
| **Visual** | Static ⚽ | Animated 🥚→🐣 |
| **Time estimate** | None | Progress bar |
| **User confidence** | Uncertain | High (see progress) |
| **Perceived speed** | Slow | Faster (engaged) |

---

## Pokémon Theme Consistency

✅ **Gold/Cream color scheme** - Matches Pokémon game aesthetic
✅ **Pixel-style fonts** - Retro Game Boy feel
✅ **Egg hatching metaphor** - Pokémon breeding mechanic
✅ **Step-by-step reveal** - Like Pokémon evolution screen
✅ **Companion terminology** - Pokémon-style language

---

**Result**: Users feel engaged and informed throughout the entire 30-40 second process, dramatically improving perceived performance and reducing anxiety about whether the system is working.
