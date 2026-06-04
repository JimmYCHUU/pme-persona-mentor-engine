/**
 * useChat hook — manages sending messages and receiving responses.
 * Shows error messages in chat if the backend fails.
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
                const d = res.data as any
                const assistantMsg: ChatMessage = {
                    role: 'assistant',
                    content: d.response,
                    timestamp: new Date().toISOString(),
                    socratic_level: d.socratic_level,
                    vault_citation: d.vault_citation,
                }
                addMessage(assistantMsg)
                if (d.session_id) setSessionId(d.session_id)
            } else {
                // Backend returned an error — show it in chat
                const errorMsg: ChatMessage = {
                    role: 'assistant',
                    content: `⚠ ${res.error || 'The mentor could not respond. Please try again.'}`,
                    timestamp: new Date().toISOString(),
                }
                addMessage(errorMsg)
            }
        } catch (err) {
            console.error('Chat error:', err)
            const errorMsg: ChatMessage = {
                role: 'assistant',
                content: '⚠ Connection error — the backend may be unreachable. Check the terminal.',
                timestamp: new Date().toISOString(),
            }
            addMessage(errorMsg)
        } finally {
            setLoading(false)
        }
    }, [activePersona, currentSessionId, mode, addMessage, setLoading, setSessionId])

    return { messages, isLoading, send }
}
