/**
 * useChat hook — manages sending messages via SSE streaming.
 * Shows responses token-by-token as they arrive from the backend.
 * Automatically switches message history when active persona changes.
 */

import { useCallback, useEffect } from 'react'
import { useChatStore } from '../store/chatStore'
import { usePersonaStore } from '../store/personaStore'
import { useSessionStore } from '../store/sessionStore'
import type { ChatMessage } from '../types'

export function useChat() {
    const {
        messages, isLoading, addMessage, appendToLastMessage,
        setLoading, setSessionId, currentSessionId, switchPersona,
    } = useChatStore()
    const { activePersona } = usePersonaStore()
    const { mode } = useSessionStore()

    // Switch message history when active persona changes
    useEffect(() => {
        if (activePersona?.persona_id) {
            switchPersona(activePersona.persona_id)
        }
    }, [activePersona?.persona_id, switchPersona])

    const send = useCallback(async (text: string) => {
        if (!activePersona || !text.trim()) return

        const userMsg: ChatMessage = {
            role: 'user',
            content: text,
            timestamp: new Date().toISOString(),
        }
        addMessage(userMsg)
        setLoading(true)

        // Add empty assistant message that will be filled by streaming
        const assistantMsg: ChatMessage = {
            role: 'assistant',
            content: '',
            timestamp: new Date().toISOString(),
        }
        addMessage(assistantMsg)

        try {
            const response = await fetch('http://localhost:8000/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    persona_id: activePersona.persona_id,
                    message: text,
                    session_id: currentSessionId || undefined,
                    mode,
                }),
            })

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }

            const reader = response.body?.getReader()
            if (!reader) throw new Error('No reader available')

            const decoder = new TextDecoder()
            let buffer = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                // Keep the last incomplete line in buffer
                buffer = lines.pop() || ''

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue
                    const data = line.slice(6).trim()
                    if (data === '[DONE]') continue

                    try {
                        const parsed = JSON.parse(data)
                        if (parsed.type === 'meta') {
                            // Update metadata on the last message
                            if (parsed.session_id) setSessionId(parsed.session_id)
                            // We'll set socratic_level via a store update
                            useChatStore.setState((s) => {
                                const msgs = [...s.messages]
                                const last = msgs[msgs.length - 1]
                                if (last?.role === 'assistant') {
                                    msgs[msgs.length - 1] = {
                                        ...last,
                                        socratic_level: parsed.socratic_level,
                                        vault_citation: parsed.vault_citation,
                                    }
                                }
                                const pid = s.activePersonaId
                                return {
                                    messages: msgs,
                                    ...(pid ? { messagesByPersona: { ...s.messagesByPersona, [pid]: msgs } } : {}),
                                }
                            })
                        } else if (parsed.type === 'token') {
                            appendToLastMessage(parsed.content)
                        } else if (parsed.type === 'error') {
                            appendToLastMessage(`⚠ ${parsed.content}`)
                        }
                    } catch {
                        // Skip malformed JSON lines
                    }
                }
            }
        } catch (err) {
            console.error('Stream error:', err)
            // Update the empty assistant message with error
            appendToLastMessage('⚠ Connection error — the backend may be unreachable. Check the terminal.')
        } finally {
            setLoading(false)
        }
    }, [activePersona, currentSessionId, mode, addMessage, appendToLastMessage, setLoading, setSessionId])

    return { messages, isLoading, send }
}
