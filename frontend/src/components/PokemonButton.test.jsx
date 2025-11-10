import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../test-utils';
import userEvent from '@testing-library/user-event';
import PokemonButton from './PokemonButton';

describe('PokemonButton', () => {
  it('renders with children text', () => {
    render(<PokemonButton>Click Me</PokemonButton>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  it('renders with default variant', () => {
    render(<PokemonButton>Default</PokemonButton>);
    const button = screen.getByRole('button', { name: 'Default' });
    expect(button).toHaveClass('pokemon-button');
  });

  it('renders with red variant', () => {
    render(<PokemonButton variant="red">Red Button</PokemonButton>);
    const button = screen.getByRole('button', { name: 'Red Button' });
    expect(button).toHaveClass('pokemon-button-red');
  });

  it('renders with green variant', () => {
    render(<PokemonButton variant="green">Green Button</PokemonButton>);
    const button = screen.getByRole('button', { name: 'Green Button' });
    expect(button).toHaveClass('pokemon-button-green');
  });

  it('calls onClick handler when clicked', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(<PokemonButton onClick={handleClick}>Click Me</PokemonButton>);

    const button = screen.getByRole('button', { name: 'Click Me' });
    await user.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(
      <PokemonButton onClick={handleClick} disabled>
        Disabled
      </PokemonButton>
    );

    const button = screen.getByRole('button', { name: 'Disabled' });
    expect(button).toBeDisabled();

    await user.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('applies custom className', () => {
    render(
      <PokemonButton className="custom-class">Custom</PokemonButton>
    );
    const button = screen.getByRole('button', { name: 'Custom' });
    expect(button).toHaveClass('custom-class');
  });

  it('handles missing onClick gracefully', () => {
    render(<PokemonButton>No Handler</PokemonButton>);
    const button = screen.getByRole('button', { name: 'No Handler' });
    expect(button).toBeInTheDocument();
  });
});
