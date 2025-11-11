// Pokemon-themed color palettes for dynamic theming
// Each Pokemon has a primary, secondary, and accent color

export const POKEMON_COLOR_PALETTES = {
  pikachu: {
    name: 'Pikachu Yellow',
    primary: '#FFD700',    // Bright yellow (body)
    secondary: '#FFC700',  // Medium yellow (header)
    accent: '#996600',     // Brown (borders)
    text: '#1A1A1A',       // Dark text
    lightText: '#FFFACD'   // Light text
  },
  charmander: {
    name: 'Charmander Orange',
    primary: '#FF6B3D',    // Bright orange (body)
    secondary: '#FF8C61',  // Light orange (header)
    accent: '#8B4513',     // Brown (borders)
    text: '#1A1A1A',       // Dark text
    lightText: '#FFE4D1'   // Light peach text
  },
  bulbasaur: {
    name: 'Bulbasaur Green',
    primary: '#78C850',    // Bright green (body)
    secondary: '#A8D898',  // Light green (header)
    accent: '#4E8234',     // Dark green (borders)
    text: '#1A1A1A',       // Dark text
    lightText: '#E8F5E9'   // Light green text
  },
  squirtle: {
    name: 'Squirtle Blue',
    primary: '#6890F0',    // Bright blue (body)
    secondary: '#9DB7F5',  // Light blue (header)
    accent: '#2E5E8E',     // Dark blue (borders)
    text: '#1A1A1A',       // Dark text
    lightText: '#E3F2FD'   // Light blue text
  },
  // Default/fallback palette
  default: {
    name: 'Default Yellow',
    primary: '#FFD700',
    secondary: '#FFC700',
    accent: '#996600',
    text: '#1A1A1A',
    lightText: '#FFFACD'
  }
};

/**
 * Get color palette for a Pokemon agent
 * @param {string} agentId - The agent's ID (e.g., "pikachu", "charmander")
 * @returns {Object} Color palette object
 */
export function getAgentColorPalette(agentId) {
  return POKEMON_COLOR_PALETTES[agentId] || POKEMON_COLOR_PALETTES.default;
}

/**
 * Apply color palette to the page by updating CSS variables
 * @param {string} agentId - The agent's ID
 */
export function applyAgentColors(agentId) {
  const colors = getAgentColorPalette(agentId);

  // Update CSS custom properties (variables)
  document.documentElement.style.setProperty('--primary-color', colors.primary);
  document.documentElement.style.setProperty('--secondary-color', colors.secondary);
  document.documentElement.style.setProperty('--accent-color', colors.accent);
  document.documentElement.style.setProperty('--text-color', colors.text);
  document.documentElement.style.setProperty('--light-text-color', colors.lightText);

  console.log(`Applied ${colors.name} color palette for ${agentId}`);
}

/**
 * Extract dominant color from an image (for custom agents)
 * Uses Canvas API to analyze pixel data
 * @param {string} imageUrl - URL of the Pokemon sprite
 * @returns {Promise<{r: number, g: number, b: number}>} RGB color object
 */
export async function extractDominantColor(imageUrl) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'Anonymous'; // Enable CORS

    img.onload = () => {
      // Create canvas and draw image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      // Get pixel data
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const pixels = imageData.data;

      let r = 0, g = 0, b = 0;
      let count = 0;

      // Average all non-white/transparent pixels
      for (let i = 0; i < pixels.length; i += 4) {
        const red = pixels[i];
        const green = pixels[i + 1];
        const blue = pixels[i + 2];
        const alpha = pixels[i + 3];

        // Skip white/transparent pixels (background)
        if (alpha > 128 && !(red > 240 && green > 240 && blue > 240)) {
          r += red;
          g += green;
          b += blue;
          count++;
        }
      }

      if (count > 0) {
        resolve({
          r: Math.round(r / count),
          g: Math.round(g / count),
          b: Math.round(b / count)
        });
      } else {
        // Fallback to default yellow
        resolve({ r: 255, g: 215, b: 0 });
      }
    };

    img.onerror = () => {
      console.error('Failed to load image for color extraction');
      // Fallback to default yellow
      resolve({ r: 255, g: 215, b: 0 });
    };

    img.src = imageUrl;
  });
}

/**
 * Find closest predefined color palette to a given RGB color
 * @param {{r: number, g: number, b: number}} rgb - RGB color object
 * @returns {string} Agent ID with closest color match
 */
export function findClosestPalette(rgb) {
  let closestAgentId = 'pikachu';
  let minDistance = Infinity;

  // Convert predefined palette primary colors to RGB and compare
  for (const [agentId, palette] of Object.entries(POKEMON_COLOR_PALETTES)) {
    if (agentId === 'default') continue;

    const paletteRgb = hexToRgb(palette.primary);
    const distance = colorDistance(rgb, paletteRgb);

    if (distance < minDistance) {
      minDistance = distance;
      closestAgentId = agentId;
    }
  }

  return closestAgentId;
}

/**
 * Convert hex color to RGB
 * @param {string} hex - Hex color (e.g., "#FFD700")
 * @returns {{r: number, g: number, b: number}} RGB object
 */
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 255, g: 215, b: 0 };
}

/**
 * Calculate color distance (Euclidean distance in RGB space)
 * @param {{r: number, g: number, b: number}} color1 - First RGB color
 * @param {{r: number, g: number, b: number}} color2 - Second RGB color
 * @returns {number} Distance value
 */
function colorDistance(color1, color2) {
  const rDiff = color1.r - color2.r;
  const gDiff = color1.g - color2.g;
  const bDiff = color1.b - color2.b;

  return Math.sqrt(rDiff * rDiff + gDiff * gDiff + bDiff * bDiff);
}

/**
 * Generate custom color palette from dominant color
 * Creates lighter and darker variations
 * @param {{r: number, g: number, b: number}} dominantRgb - Dominant RGB color
 * @returns {Object} Custom color palette
 */
export function generateCustomPalette(dominantRgb) {
  const primaryHex = rgbToHex(dominantRgb.r, dominantRgb.g, dominantRgb.b);

  // Create lighter version (secondary) - add 30 to each channel
  const secondaryRgb = {
    r: Math.min(255, dominantRgb.r + 40),
    g: Math.min(255, dominantRgb.g + 40),
    b: Math.min(255, dominantRgb.b + 40)
  };
  const secondaryHex = rgbToHex(secondaryRgb.r, secondaryRgb.g, secondaryRgb.b);

  // Create darker version (accent) - subtract 60 from each channel
  const accentRgb = {
    r: Math.max(0, dominantRgb.r - 80),
    g: Math.max(0, dominantRgb.g - 80),
    b: Math.max(0, dominantRgb.b - 80)
  };
  const accentHex = rgbToHex(accentRgb.r, accentRgb.g, accentRgb.b);

  return {
    name: 'Custom Palette',
    primary: primaryHex,
    secondary: secondaryHex,
    accent: accentHex,
    text: '#1A1A1A',
    lightText: '#FFFACD'
  };
}

/**
 * Convert RGB to hex color
 * @param {number} r - Red (0-255)
 * @param {number} g - Green (0-255)
 * @param {number} b - Blue (0-255)
 * @returns {string} Hex color (e.g., "#FFD700")
 */
function rgbToHex(r, g, b) {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
}
