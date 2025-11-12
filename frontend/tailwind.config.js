/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'pokemon-cream': '#FFF4E6',
        'pokemon-gold': '#FFD700',
        'pokemon-green': '#8BC34A',
        'pokemon-red': '#E74C3C',
        'pokemon-blue': '#3498DB',
        'pokemon-purple': '#9B59B6',
        'pokemon-orange': '#FFA07A',
        'pokemon-pink': '#FFB6D9',
        'pokemon-brown': '#D4A574',
        'pokemon-teal': '#4ECDC4',
        'pokemon-yellow': '#FFE66D',
        'pokemon-mint': '#95E1D3',
      },
      fontFamily: {
        'pixel': ['"Press Start 2P"', 'cursive'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
