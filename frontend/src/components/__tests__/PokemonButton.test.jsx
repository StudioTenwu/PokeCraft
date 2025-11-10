import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '../../__tests__/test-utils'
import userEvent from '@testing-library/user-event'
import PokemonButton from '../PokemonButton'

describe('PokemonButton', () => {
  it('renders children correctly', () => {
    render(<PokemonButton>Click Me</PokemonButton>)
    expect(screen.getByRole('button', { name: 'Click Me' })).toBeInTheDocument()
  })

  it('calls onClick handler when clicked', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<PokemonButton onClick={handleClick}>Click Me</PokemonButton>)

    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when disabled', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<PokemonButton onClick={handleClick} disabled>Click Me</PokemonButton>)

    await user.click(screen.getByRole('button'))
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('applies default variant class', () => {
    render(<PokemonButton>Default</PokemonButton>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('pokemon-button')
  })

  it('applies red variant class', () => {
    render(<PokemonButton variant="red">Red Button</PokemonButton>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('pokemon-button-red')
  })

  it('applies green variant class', () => {
    render(<PokemonButton variant="green">Green Button</PokemonButton>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('pokemon-button-green')
  })

  it('applies custom className', () => {
    render(<PokemonButton className="custom-class">Button</PokemonButton>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
    expect(button).toHaveClass('pokemon-button')
  })

  it('is disabled when disabled prop is true', () => {
    render(<PokemonButton disabled>Disabled</PokemonButton>)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('is not disabled by default', () => {
    render(<PokemonButton>Enabled</PokemonButton>)
    const button = screen.getByRole('button')
    expect(button).not.toBeDisabled()
  })
})
