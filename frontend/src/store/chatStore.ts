/**
 * Chat store — Zustand state for chat messages and interaction.
 */

import { create } from 'zustand'
import type { ChatMessage } from '../types'

interface ChatState {
    messages: ChatMessage[]
    isLoading: boolean
    currentSessionId: string | null
    addMessage: (msg: ChatMessage) => void
    setMessages: (msgs: ChatMessage[]) => void
    setLoading: (loading: boolean) => void
    setSessionId: (id: string) => void
    clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
    messages: [],
    isLoading: false,
    currentSessionId: null,
    addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
    setMessages: (msgs) => set({ messages: msgs }),
    setLoading: (loading) => set({ isLoading: loading }),
    setSessionId: (id) => set({ currentSessionId: id }),
    clearMessages: () => set({ messages: [] }),
}))
