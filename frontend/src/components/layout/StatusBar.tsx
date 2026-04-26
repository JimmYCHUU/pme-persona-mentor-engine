import { useEffect, useState } from 'react'
import { api } from '../../api/client'
import { useMasteryStore } from '../../store/masteryStore'
import { useSessionStore } from '../../store/sessionStore'
import { useSession } from '../../hooks/useSession'

export function StatusBar() {
  const { mode } = useSessionStore()
  const { concepts } = useMasteryStore()
  const [online, setOnline] = useState(false)
  const { savedSecondsAgo } = useSession()

  useEffect(() => {
    const ping = async () => {
      const h = await api.health()
      setOnline(h.ollama_online)
    }
    void ping()
    const id = setInterval(() => void ping(), 30000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className='status-bar' style={{ position: 'fixed', bottom: 0, left: 0, right: 0, height: 'var(--statusbar-h)', background: 'var(--bg-surface)', borderTop: '1px solid var(--bg-overlay)', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', alignItems: 'center', padding: '0 10px', fontSize: 12 }}>
      <div style={{ color: online ? 'var(--success)' : 'var(--accent)' }}>{online ? '● Ollama online' : '● Model offline — run: ollama serve'}</div>
      <div style={{ textAlign: 'center', color: mode === 'deep_dive' ? 'var(--accent)' : 'var(--info)' }}>{mode === 'deep_dive' ? 'Deep Dive' : 'Friend Mode'}</div>
      <div style={{ textAlign: 'right' }}>{savedSecondsAgo == null ? 'Auto-save idle' : `Saved ${savedSecondsAgo}s ago`}</div>
    </div>
  )
}
