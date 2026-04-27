import { useMemo } from 'react'
import { usePersona } from '../../hooks/usePersona'
import { useSessionStore } from '../../store/sessionStore'
import { useMasteryStore } from '../../store/masteryStore'
import { PersonaCard } from '../persona/PersonaCard'
import { Button } from '../shared/Button'

export function Sidebar({ onToggleMastery, onExit }: { onToggleMastery: () => void; onExit: () => void }) {
  const { personas, activeId, setActive } = usePersona()
  const { mode, toggleMode } = useSessionStore()
  const { concepts } = useMasteryStore()

  const struggling = useMemo(() => concepts.filter((c) => c.status === 'struggling').length, [concepts])

  return (
    <aside className='sidebar' style={{ width: 'var(--sidebar-w)', borderRight: '1px solid var(--bg-overlay)', padding: 10, display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'grid', gap: 8 }}>
        {personas.map((p) => (
          <PersonaCard key={p.persona_id} persona={p} active={p.persona_id === activeId} onClick={() => setActive(p.persona_id)} />
        ))}
      </div>
      <button onClick={onToggleMastery} style={{ background: 'transparent', color: 'var(--text-primary)', border: '1px solid var(--bg-overlay)', borderRadius: 8, padding: 8, textAlign: 'left' }}>
        Mastery Map {struggling > 0 ? `(${struggling})` : ''}
      </button>
      <div style={{ marginTop: 'auto' }}>
        <Button variant={mode === 'friend_mode' ? 'primary' : 'ghost'} onClick={toggleMode}>Friend Mode</Button>
        <div style={{ height: 8 }} />
        <Button variant='ghost' onClick={onExit}>Exit Session</Button>
      </div>
    </aside>
  )
}
