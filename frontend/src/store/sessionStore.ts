/**
 * Session store — Zustand state for session management + provider status.
 */

import { create } from 'zustand'
import type { SessionSnapshot } from '../types'

interface SessionState {
    mode: 'deep_dive' | 'friend_mode'
    snapshot: SessionSnapshot | null
    resumeGreeting: string
    isOpenRouterOnline: boolean
    isOllamaOnline: boolean
    primaryProvider: string
    personaModel: string
    reasoningModel: string
    setMode: (m: 'deep_dive' | 'friend_mode') => void
    setSnapshot: (s: SessionSnapshot | null) => void
    setResumeGreeting: (g: string) => void
    setProviderStatus: (s: { openrouter: boolean; ollama: boolean; primary: string }) => void
    setModels: (m: { personaModel?: string; reasoningModel?: string }) => void
}

export const useSessionStore = create<SessionState>((set) => ({
    mode: 'deep_dive',
    snapshot: null,
    resumeGreeting: '',
    isOpenRouterOnline: false,
    isOllamaOnline: false,
    primaryProvider: 'none',
    personaModel: 'nvidia/nemotron-3-super-120b-a12b:free',
    reasoningModel: 'nvidia/nemotron-3-super-120b-a12b:free',
    setMode: (m) => set({ mode: m }),
    setSnapshot: (s) => set({ snapshot: s }),
    setResumeGreeting: (g) => set({ resumeGreeting: g }),
    setProviderStatus: (s) => set({
        isOpenRouterOnline: s.openrouter,
        isOllamaOnline: s.ollama,
        primaryProvider: s.primary,
    }),
    setModels: (m) => set((state) => ({
        personaModel: m.personaModel ?? state.personaModel,
        reasoningModel: m.reasoningModel ?? state.reasoningModel,
    })),
}))
