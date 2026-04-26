import type { PersonaProfile } from '../../types'

export function PersonaCard({ persona, onClick, active }: { persona: PersonaProfile; onClick: () => void; active: boolean }) {
  return (
    <button onClick={onClick} style={{ width: '100%', textAlign: 'left', background: active ? 'var(--bg-raised)' : 'transparent', color: 'var(--text-primary)', border: '1px solid var(--bg-overlay)', borderRadius: 8, padding: 8 }}>
      <strong>{persona.name}</strong>
      <div>{persona.description}</div>
      <small>{persona.created_at ?? ''}</small>
    </button>
  )
}
