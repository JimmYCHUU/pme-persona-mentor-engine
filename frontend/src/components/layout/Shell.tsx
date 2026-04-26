import { useState } from 'react'
import { ChatPane } from '../chat/ChatPane'
import { MasteryMap } from '../mastery/MasteryMap'
import { PersonaBuilder } from '../persona/PersonaBuilder'
import { Sidebar } from './Sidebar'
import { StatusBar } from './StatusBar'

export function Shell() {
  const [showMastery, setShowMastery] = useState(false)
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'var(--sidebar-w) 1fr auto', minHeight: '100vh', paddingBottom: 'var(--statusbar-h)' }}>
      <Sidebar onToggleMastery={() => setShowMastery((v) => !v)} />
      <main style={{ display: 'grid', gridTemplateRows: 'auto 1fr', gap: 10, padding: 10 }}>
        <PersonaBuilder />
        <ChatPane />
      </main>
      {showMastery && <aside style={{ width: 320, borderLeft: '1px solid var(--bg-overlay)', padding: 10 }}><MasteryMap /></aside>}
      <StatusBar />
    </div>
  )
}
