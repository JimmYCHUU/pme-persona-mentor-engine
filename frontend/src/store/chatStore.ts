/**
 * Chat store — Zustand state for chat messages, isolated per persona.
 * Supports streaming by allowing incremental updates to the last message.
 */

import { create } from 'zustand'
import type { ChatMessage } from '../types'

interface ChatState {
    /** Current active persona's messages (derived from messagesByPersona) */
    messages: ChatMessage[]
    /** All messages keyed by persona_id */
    messagesByPersona: Record<string, ChatMessage[]>
    /** Currently active persona id for message lookup */
    activePersonaId: string | null
    isLoading: boolean
    currentSessionId: string | null

    /** Switch to a persona's message history */
    switchPersona: (personaId: string) => void
    addMessage: (msg: ChatMessage) => void
    /** Append content to the last assistant message (for streaming) */
    appendToLastMessage: (content: string) => void
    setMessages: (msgs: ChatMessage[]) => void
    setLoading: (loading: boolean) => void
    setSessionId: (id: string) => void
    clearMessages: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
    messages: [],
    messagesByPersona: {},
    activePersonaId: null,
    isLoading: false,
    currentSessionId: null,

    switchPersona: (personaId) => {
        const { messagesByPersona } = get()
        set({
            activePersonaId: personaId,
            messages: messagesByPersona[personaId] || [],
        })
    },

    addMessage: (msg) => set((s) => {
        const pid = s.activePersonaId
        if (!pid) return { messages: [...s.messages, msg] }
        const updated = [...(s.messagesByPersona[pid] || []), msg]
        return {
            messages: updated,
            messagesByPersona: { ...s.messagesByPersona, [pid]: updated },
        }
    }),

    appendToLastMessage: (content) => set((s) => {
        const pid = s.activePersonaId
        const msgs = pid ? (s.messagesByPersona[pid] || []) : s.messages
        if (msgs.length === 0) return s
        const last = msgs[msgs.length - 1]
        if (last.role !== 'assistant') return s
        const updated = [...msgs.slice(0, -1), { ...last, content: last.content + content }]
        if (!pid) return { messages: updated }
        return {
            messages: updated,
            messagesByPersona: { ...s.messagesByPersona, [pid]: updated },
        }
    }),

    setMessages: (msgs) => set((s) => {
        const pid = s.activePersonaId
        if (!pid) return { messages: msgs }
        return {
            messages: msgs,
            messagesByPersona: { ...s.messagesByPersona, [pid]: msgs },
        }
    }),

    setLoading: (loading) => set({ isLoading: loading }),
    setSessionId: (id) => set({ currentSessionId: id }),
    clearMessages: () => set((s) => {
        const pid = s.activePersonaId
        if (!pid) return { messages: [] }
        return {
            messages: [],
            messagesByPersona: { ...s.messagesByPersona, [pid]: [] },
        }
    }),
}))
