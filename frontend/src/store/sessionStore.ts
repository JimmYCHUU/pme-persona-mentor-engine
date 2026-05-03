/**
 * Session store — Zustand state for session management.
 */

import { create } from 'zustand'
import type { SessionSnapshot } from '../types'

interface SessionState {
    mode: 'deep_dive' | 'friend_mode'
    snapshot: SessionSnapshot | null
    resumeGreeting: string
    setMode: (m: 'deep_dive' | 'friend_mode') => void
    setSnapshot: (s: SessionSnapshot | null) => void
    setResumeGreeting: (g: string) => void
}

export const useSessionStore = create<SessionState>((set) => ({
    mode: 'deep_dive',
    snapshot: null,
    resumeGreeting: '',
    setMode: (m) => set({ mode: m }),
    setSnapshot: (s) => set({ snapshot: s }),
    setResumeGreeting: (g) => set({ resumeGreeting: g }),
}))
