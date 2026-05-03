/**
 * Mastery store — Zustand state for mastery tracking.
 */

import { create } from 'zustand'
import type { ConceptEntry, MasteryCert } from '../types'

interface MasteryState {
    concepts: ConceptEntry[]
    pendingCerts: MasteryCert[]
    setConcepts: (c: ConceptEntry[]) => void
    setPendingCerts: (c: MasteryCert[]) => void
    removePendingCert: (certId: string) => void
}

export const useMasteryStore = create<MasteryState>((set) => ({
    concepts: [],
    pendingCerts: [],
    setConcepts: (c) => set({ concepts: c }),
    setPendingCerts: (c) => set({ pendingCerts: c }),
    removePendingCert: (certId) =>
        set((s) => ({
            pendingCerts: s.pendingCerts.filter((c) => c.cert_id !== certId),
        })),
}))
