/**
 * SessionPage — the chat workspace.
 * Wraps Sidebar + ChatPane (existing), or shows PersonaBuilder if no active persona.
 */

import { Sidebar } from '../components/layout/Sidebar'
import { ChatPane } from '../components/chat/ChatPane'
import { PersonaBuilder } from '../components/persona/PersonaBuilder'
import { usePersonaStore } from '../store/personaStore'

export function SessionPage() {
    const { activePersona } = usePersonaStore()

    return (
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
    )
}
