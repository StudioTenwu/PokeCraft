import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import ThemeToggle from '../ThemeToggle'

describe('ThemeToggle', () => {
  beforeEach(() => {
    // Reset localStorage and DOM before each test
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
  })

  it('renders with moon icon by default (light mode)', () => {
    localStorage.getItem.mockReturnValue('light')
    render(<ThemeToggle />)
    expect(screen.getByRole('button')).toHaveTextContent('🌙')
  })

  it('renders with sun icon when dark mode is stored', () => {
    localStorage.getItem.mockReturnValue('dark')
    render(<ThemeToggle />)
    expect(screen.getByRole('button')).toHaveTextContent('☀️')
  })

  it('has correct aria-label', () => {
    render(<ThemeToggle />)
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Toggle theme')
  })

  it('shows correct title for light mode', () => {
    localStorage.getItem.mockReturnValue('light')
    render(<ThemeToggle />)
    expect(screen.getByRole('button')).toHaveAttribute('title', 'Switch to dark mode')
  })

  it('shows correct title for dark mode', () => {
    localStorage.getItem.mockReturnValue('dark')
    render(<ThemeToggle />)
    expect(screen.getByRole('button')).toHaveAttribute('title', 'Switch to light mode')
  })

  it('toggles from light to dark mode when clicked', async () => {
    localStorage.getItem.mockReturnValue('light')
    const user = userEvent.setup()

    render(<ThemeToggle />)
    const button = screen.getByRole('button')

    expect(button).toHaveTextContent('🌙')

    await user.click(button)

    expect(button).toHaveTextContent('☀️')
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('toggles from dark to light mode when clicked', async () => {
    localStorage.getItem.mockReturnValue('dark')
    const user = userEvent.setup()

    render(<ThemeToggle />)
    const button = screen.getByRole('button')

    expect(button).toHaveTextContent('☀️')

    await user.click(button)

    expect(button).toHaveTextContent('🌙')
    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light')
    expect(document.documentElement.getAttribute('data-theme')).toBeNull()
  })

  it('sets dark theme attribute on mount when localStorage has dark', () => {
    localStorage.getItem.mockReturnValue('dark')
    render(<ThemeToggle />)
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('removes theme attribute on mount when localStorage has light', () => {
    localStorage.getItem.mockReturnValue('light')
    render(<ThemeToggle />)
    expect(document.documentElement.getAttribute('data-theme')).toBeNull()
  })

  it('applies correct CSS classes', () => {
    render(<ThemeToggle />)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('pokemon-button', 'font-pixel', 'text-xl', 'p-3')
  })
})
