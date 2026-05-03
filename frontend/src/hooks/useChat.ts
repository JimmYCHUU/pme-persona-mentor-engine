/**
 * useChat hook — manages sending messages and receiving responses.
 */

import { useCallback } from 'react'
import { useChatStore } from '../store/chatStore'
import { usePersonaStore } from '../store/personaStore'
import { useSessionStore } from '../store/sessionStore'
import { sendMessage } from '../api/client'
import type { ChatMessage } from '../types'

export function useChat() {
    const { messages, isLoading, addMessage, setLoading, setSessionId, currentSessionId } = useChatStore()
    const { activePersona } = usePersonaStore()
    const { mode } = useSessionStore()

    const send = useCallback(async (text: string) => {
        if (!activePersona || !text.trim()) return

        const userMsg: ChatMessage = {
            role: 'user',
            content: text,
            timestamp: new Date().toISOString(),
        }
        addMessage(userMsg)
        setLoading(true)

        try {
            const res = await sendMessage(
                activePersona.persona_id,
                text,
                currentSessionId || undefined,
                mode,
            )

            if (res.success && res.data) {
                const assistantMsg: ChatMessage = {
                    role: 'assistant',
                    content: res.data.response,
                    timestamp: new Date().toISOString(),
                    socratic_level: res.data.socratic_level,
                    vault_citation: res.data.vault_citation,
                }
                addMessage(assistantMsg)
                if (res.data.session_id) setSessionId(res.data.session_id)
            }
        } catch (err) {
            console.error('Chat error:', err)
        } finally {
            setLoading(false)
        }
    }, [activePersona, currentSessionId, mode, addMessage, setLoading, setSessionId])

    return { messages, isLoading, send }
}
