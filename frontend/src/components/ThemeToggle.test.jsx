import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '../test-utils';
import userEvent from '@testing-library/user-event';
import ThemeToggle from './ThemeToggle';

describe('ThemeToggle', () => {
  beforeEach(() => {
    // Reset localStorage mock to return null by default
    localStorage.getItem.mockReturnValue(null);
    localStorage.setItem.mockClear();
    localStorage.clear.mockClear();
    // Clear any theme attribute
    document.documentElement.removeAttribute('data-theme');
  });

  it('renders with moon icon by default (light mode)', () => {
    render(<ThemeToggle />);
    const button = screen.getByRole('button', { name: 'Toggle theme' });
    expect(button).toHaveTextContent('🌙');
  });

  it('renders with sun icon when dark theme is stored', () => {
    localStorage.getItem.mockReturnValue('dark');
    render(<ThemeToggle />);
    const button = screen.getByRole('button', { name: 'Toggle theme' });
    expect(button).toHaveTextContent('☀️');
  });

  it('toggles icon on click', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole('button', { name: 'Toggle theme' });

    // Initially shows moon (light mode)
    expect(button).toHaveTextContent('🌙');

    // Click to switch to dark mode
    await user.click(button);
    expect(button).toHaveTextContent('☀️');

    // Click again to switch back to light mode
    await user.click(button);
    expect(button).toHaveTextContent('🌙');
  });

  it('updates localStorage when toggled to dark', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole('button', { name: 'Toggle theme' });
    await user.click(button);

    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
  });

  it('updates localStorage when toggled to light', async () => {
    localStorage.getItem.mockReturnValue('dark');
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole('button', { name: 'Toggle theme' });
    await user.click(button);

    expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
  });

  it('sets data-theme attribute on document when dark', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole('button', { name: 'Toggle theme' });
    await user.click(button);

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('removes data-theme attribute when light', async () => {
    localStorage.getItem.mockReturnValue('dark');
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole('button', { name: 'Toggle theme' });
    await user.click(button);

    expect(document.documentElement.getAttribute('data-theme')).toBeNull();
  });

  it('has correct title attribute for accessibility', () => {
    render(<ThemeToggle />);
    const button = screen.getByRole('button', { name: 'Toggle theme' });
    expect(button).toHaveAttribute('title', 'Switch to dark mode');
  });

  it('changes title when toggled', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByRole('button', { name: 'Toggle theme' });
    expect(button).toHaveAttribute('title', 'Switch to dark mode');

    await user.click(button);
    expect(button).toHaveAttribute('title', 'Switch to light mode');
  });
});
