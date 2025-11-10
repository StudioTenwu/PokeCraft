import { useState, useEffect } from 'react'

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(
    localStorage.getItem('theme') === 'dark'
  )

  useEffect(() => {
    if (isDark) {
      document.documentElement.setAttribute('data-theme', 'dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="font-pixel text-2xl p-3 border-4 rounded hover:scale-110 transition-transform"
      style={{
        backgroundColor: isDark ? '#1a1a1a' : '#fff',
        borderColor: isDark ? '#FFD700' : '#000',
        color: isDark ? '#FFD700' : '#000',
        boxShadow: '4px 4px 0px 0px rgba(0,0,0,0.3)'
      }}
      aria-label="Toggle theme"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? '☀️' : '🌙'}
    </button>
  )
}
