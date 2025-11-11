# Pokemon-Style Font Setup Guide

## Option A: Manual Download Pokemon GB Font (Recommended - Most Authentic)

### Step 1: Download the Font
1. Visit: https://www.fontspace.com/pokemon-gb-font-f9621
2. Click the "Download" button
3. Extract the ZIP file - you'll get `Pokemon GB.ttf`

### Step 2: Convert to Web Formats
You have two choices:

**Method 1: Use Online Converter (Easiest)**
1. Go to: https://cloudconvert.com/ttf-to-woff2
2. Upload `Pokemon GB.ttf`
3. Convert to WOFF2
4. Also convert to WOFF (for older browser support)

**Method 2: Use FontSquirrel Webfont Generator**
1. Go to: https://www.fontsquirrel.com/tools/webfont-generator
2. Upload `Pokemon GB.ttf`
3. Select "Optimal" settings
4. Download the kit (includes WOFF2, WOFF, and CSS)

### Step 3: Place Files
Copy the converted files to:
```
/Users/wz/Desktop/zPersonalProjects/AICraft/frontend/public/fonts/
```

File structure should be:
```
frontend/public/fonts/
├── pokemon-gb.woff2
├── pokemon-gb.woff
└── pokemon-gb.ttf (optional, for desktop testing)
```

---

## Option B: Use Google Fonts Alternative (Instant, No Download)

### Available Straight-Edge Pixel Fonts on Google Fonts:

1. **Silkscreen** - Clean, straight-edge pixel font
2. **VT323** - Monospace pixel font, very straight
3. **Pixelify Sans** - Modern pixel font with multiple weights
4. **DotGothic16** - Japanese-style pixel font, very geometric

### Implementation:
Just update your `frontend/index.html`:

```html
<!-- Replace Press Start 2P with one of these: -->

<!-- Option: Silkscreen (Most similar to Pokemon GB) -->
<link href="https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&display=swap" rel="stylesheet">

<!-- Option: VT323 (Monospace, very straight) -->
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">

<!-- Option: Pixelify Sans (Modern, multiple weights) -->
<link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400..700&display=swap" rel="stylesheet">

<!-- Option: DotGothic16 (Japanese-style, very geometric) -->
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
```

---

## CSS Setup (For Both Options)

### For Option A (Pokemon GB - Manual):

```css
/* Add to pokemon-theme.css */

@font-face {
  font-family: 'Pokemon GB';
  src: url('/fonts/pokemon-gb.woff2') format('woff2'),
       url('/fonts/pokemon-gb.woff') format('woff');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}

.pokemon-text {
  font-family: 'Pokemon GB', monospace;
  font-size: 20px; /* Use multiples of 10px: 10, 20, 30, 40 */

  /* Critical: Disable anti-aliasing for sharp pixels */
  font-smooth: never;
  -webkit-font-smoothing: none;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeSpeed;
  image-rendering: pixelated;
}

/* Size variants */
.pokemon-text-sm { font-size: 10px; }
.pokemon-text-md { font-size: 20px; }
.pokemon-text-lg { font-size: 30px; }
.pokemon-text-xl { font-size: 40px; }
```

### For Option B (Google Fonts):

```css
/* Example with Silkscreen */
.pokemon-text {
  font-family: 'Silkscreen', monospace;
  font-size: 16px; /* Use multiples of 8px: 8, 16, 24, 32 */

  /* Critical: Disable anti-aliasing */
  font-smooth: never;
  -webkit-font-smoothing: none;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeSpeed;
}
```

---

## Testing

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
  <link href="https://fonts.googleapis.com/css2?family=Silkscreen&display=swap" rel="stylesheet">
  <style>
    body { background: #000; color: #0f0; padding: 20px; }
    .test {
      font-family: 'Silkscreen', monospace;
      font-smooth: never;
      -webkit-font-smoothing: none;
    }
    .size-10 { font-size: 10px; }
    .size-20 { font-size: 20px; }
    .size-30 { font-size: 30px; }
  </style>
</head>
<body>
  <h1 class="test size-30">Pokemon Font Test</h1>
  <p class="test size-20">The quick brown fox jumps over the lazy dog.</p>
  <p class="test size-20">HP: 45/45 | ATK: 49 | DEF: 49</p>
  <p class="test size-10">Small text for stats and details</p>
</body>
</html>
```

---

## My Recommendation

**For fastest results:** Use **Silkscreen** from Google Fonts (Option B)
- No download/conversion needed
- Very similar to Pokemon GB style
- Straighter edges than Press Start 2P
- Free and commercial-friendly

**For most authentic:** Download Pokemon GB font (Option A)
- True Pokemon Game Boy font
- Requires manual setup
- Worth it for authentic feel

---

## Next Steps

Let me know which option you want to use:
1. **Option A**: I'll walk you through the manual download
2. **Option B**: I'll implement Silkscreen right now (2 minutes)
3. **Option C**: Test multiple Google Fonts options to pick the best one
