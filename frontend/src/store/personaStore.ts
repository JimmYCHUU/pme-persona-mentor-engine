import { create } from 'zustand'
import { api } from '../api/client'
import type { PersonaProfile } from '../types'

interface PersonaState {
  personas: PersonaProfile[]
  activeId: string | null
  sliders: Record<string, number>
  setActive: (id: string) => void
  updateSliders: (sliders: Record<string, number>) => Promise<void>
  loadPersonas: () => Promise<void>
}

export const usePersonaStore = create<PersonaState>((set, get) => ({
  personas: [],
  activeId: null,
  sliders: { abrasiveness: 50, proactivity: 50, explainDepth: 50 },
  setActive: (id) => set({ activeId: id }),
  updateSliders: async (sliders) => {
    const active = get().activeId
    if (!active) return
    set({ sliders })
    await api.updateSliders(active, sliders)
  },
  loadPersonas: async () => {
    const personas = await api.listPersonas()
    set({ personas })
  },
}))
