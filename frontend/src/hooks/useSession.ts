/**
 * useSession hook — handles session resume and save.
 */

import { useCallback } from 'react'
import { useSessionStore } from '../store/sessionStore'
import { useChatStore } from '../store/chatStore'
import { resumeSession, saveSession } from '../api/client'

export function useSession() {
    const { mode, snapshot, resumeGreeting, setMode, setSnapshot, setResumeGreeting } = useSessionStore()
    const { setMessages, setSessionId } = useChatStore()

    const resume = useCallback(async (personaId: string) => {
        const res = await resumeSession(personaId)
        if (res.success && res.data) {
            setSnapshot(res.data.snapshot)
            setResumeGreeting(res.data.resume_greeting)
            if (res.data.session_id) setSessionId(res.data.session_id)
            if (res.data.snapshot?.chat_history) {
                setMessages(res.data.snapshot.chat_history)
            }
            if (res.data.snapshot?.mode) {
                setMode(res.data.snapshot.mode)
            }
        }
        return res
    }, [setSnapshot, setResumeGreeting, setSessionId, setMessages, setMode])

    const save = useCallback(async (sessionId: string, personaId: string) => {
        const { messages } = useChatStore.getState()
        const snap = {
            session_id: sessionId,
            persona_id: personaId,
            mode,
            chat_history: messages,
            updated_at: new Date().toISOString(),
        }
        return saveSession(sessionId, personaId, snap)
    }, [mode])

    const toggleMode = useCallback(() => {
        setMode(mode === 'deep_dive' ? 'friend_mode' : 'deep_dive')
    }, [mode, setMode])

    return { mode, snapshot, resumeGreeting, resume, save, toggleMode }
}
