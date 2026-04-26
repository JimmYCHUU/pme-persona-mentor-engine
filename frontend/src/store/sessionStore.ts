import { create } from 'zustand'
import type { SessionSnapshot } from '../types'

type Mode = 'deep_dive' | 'friend_mode'

interface SessionState {
  snapshot: SessionSnapshot | null
  showResume: boolean
  mode: Mode
  setSnapshot: (snapshot: SessionSnapshot | null) => void
  toggleMode: () => void
  setMode: (mode: Mode) => void
}

export const useSessionStore = create<SessionState>((set) => ({
  snapshot: null,
  showResume: false,
  mode: 'deep_dive',
  setSnapshot: (snapshot) => set({ snapshot, showResume: !!snapshot }),
  toggleMode: () => set((s) => ({ mode: s.mode === 'deep_dive' ? 'friend_mode' : 'deep_dive' })),
  setMode: (mode) => set({ mode }),
}))
