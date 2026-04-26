export function Spinner() {
  return (
    <span
      style={{
        width: 16,
        height: 16,
        border: '2px solid var(--accent)',
        borderTopColor: 'transparent',
        borderRadius: '50%',
        display: 'inline-block',
        animation: 'spin 0.8s linear infinite',
      }}
    />
  )
}
