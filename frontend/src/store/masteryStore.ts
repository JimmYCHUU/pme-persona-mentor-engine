import { create } from 'zustand'
import { api } from '../api/client'
import type { ConceptEntry, MasteryCertificate } from '../types'

interface MasteryState {
  concepts: ConceptEntry[]
  pendingCerts: MasteryCertificate[]
  isLoading: boolean
  fetchLedger: (personaId: string) => Promise<void>
  fetchPendingCerts: (personaId: string) => Promise<void>
  markCertDelivered: (personaId: string, certId: string) => Promise<void>
}

export const useMasteryStore = create<MasteryState>((set, get) => ({
  concepts: [],
  pendingCerts: [],
  isLoading: false,
  fetchLedger: async (personaId) => {
    set({ isLoading: true })
    const concepts = await api.getLedger(personaId)
    set({ concepts, isLoading: false })
  },
  fetchPendingCerts: async (personaId) => {
    const pendingCerts = await api.getPendingCerts(personaId)
    set({ pendingCerts })
  },
  markCertDelivered: async (personaId, certId) => {
    await api.markCertDelivered(personaId, certId)
    set({ pendingCerts: get().pendingCerts.filter((c) => c.cert_id !== certId) })
  },
}))
