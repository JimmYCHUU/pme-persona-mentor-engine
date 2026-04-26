import { create } from 'zustand'
import type { Message } from '../types'

interface ChatState {
  messages: Message[]
  isStreaming: boolean
  sessionId: string | null
  addMessage: (message: Message) => void
  setStreaming: (isStreaming: boolean) => void
  setSessionId: (sessionId: string) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  sessionId: null,
  addMessage: (message) => set((s) => ({ messages: [...s.messages, message] })),
  setStreaming: (isStreaming) => set({ isStreaming }),
  setSessionId: (sessionId) => set({ sessionId }),
}))
