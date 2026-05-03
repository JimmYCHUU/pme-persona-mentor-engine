/**
 * Shell — the main workspace layout: sidebar + chat pane + status bar.
 */

import { Sidebar } from './Sidebar'
import { StatusBar } from './StatusBar'
import { ChatPane } from '../chat/ChatPane'
import { PersonaBuilder } from '../persona/PersonaBuilder'
import { usePersonaStore } from '../../store/personaStore'

export function Shell() {
    const { activePersona } = usePersonaStore()

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            width: '100vw',
            background: 'var(--bg-base)',
        }}>
            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                <Sidebar />
                <main style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'hidden',
                }}>
                    {activePersona ? <ChatPane /> : <PersonaBuilder />}
                </main>
            </div>
            <StatusBar />
        </div>
    )
}
