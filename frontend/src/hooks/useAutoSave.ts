/**
 * useAutoSave hook — auto-saves session every 60 seconds.
 * Also saves on beforeunload.
 */

import { useEffect, useRef } from 'react'
import { useChatStore } from '../store/chatStore'
import { usePersonaStore } from '../store/personaStore'
import { useSessionStore } from '../store/sessionStore'
import { saveSession } from '../api/client'

const AUTO_SAVE_INTERVAL_MS = 60_000

export function useAutoSave() {
    const savedRef = useRef(false)

    useEffect(() => {
        const interval = setInterval(async () => {
            const { messages, currentSessionId } = useChatStore.getState()
            const { activePersona } = usePersonaStore.getState()
            const { mode } = useSessionStore.getState()

            if (!currentSessionId || !activePersona || messages.length === 0) return

            try {
                await saveSession(currentSessionId, activePersona.persona_id, {
                    session_id: currentSessionId,
                    persona_id: activePersona.persona_id,
                    mode,
                    chat_history: messages,
                    updated_at: new Date().toISOString(),
                })
            } catch {
                /* silent fail — don't interrupt chat */
            }
        }, AUTO_SAVE_INTERVAL_MS)

        // Save on tab close
        const handleBeforeUnload = () => {
            if (savedRef.current) return
            savedRef.current = true
            const { messages, currentSessionId } = useChatStore.getState()
            const { activePersona } = usePersonaStore.getState()
            const { mode } = useSessionStore.getState()
            if (currentSessionId && activePersona && messages.length > 0) {
                navigator.sendBeacon(
                    'http://localhost:8000/session/save',
                    JSON.stringify({
                        session_id: currentSessionId,
                        persona_id: activePersona.persona_id,
                        snapshot: { session_id: currentSessionId, persona_id: activePersona.persona_id, mode, chat_history: messages },
                    })
                )
            }
        }

        window.addEventListener('beforeunload', handleBeforeUnload)
        return () => {
            clearInterval(interval)
            window.removeEventListener('beforeunload', handleBeforeUnload)
        }
    }, [])
}
