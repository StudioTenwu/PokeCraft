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
      },
      fontFamily: {
        'pixel': ['"Press Start 2P"', 'cursive'],
      }
    },
  },
  plugins: [],
}
