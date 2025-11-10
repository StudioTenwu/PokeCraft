export default function PokemonButton({ children, onClick, disabled, variant = 'default', className = '' }) {
  const variants = {
    default: 'pokemon-button',
    red: 'pokemon-button-red',
    green: 'pokemon-button-green'
  }

  return (
    <button
      className={`${variants[variant]} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
