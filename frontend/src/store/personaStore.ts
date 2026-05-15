/**
 * Persona store — Zustand state for active persona.
 */

import { create } from 'zustand'
import type { PersonaProfile } from '../types'
import { listPersonas } from '../api/client'

interface PersonaState {
    activePersona: PersonaProfile | null
    activeId: string | null
    personas: PersonaProfile[]
    sliders: { abrasiveness: number; proactivity: number; explainDepth: number }
    setActivePersona: (p: PersonaProfile | null) => void
    setActive: (id: string) => void
    setPersonas: (ps: PersonaProfile[]) => void
    loadPersonas: () => Promise<void>
    updateSliders: (s: Partial<{ abrasiveness: number; proactivity: number; explainDepth: number }>) => void
}

export const usePersonaStore = create<PersonaState>((set, get) => ({
    activePersona: null,
    activeId: null,
    personas: [],
    sliders: { abrasiveness: 50, proactivity: 50, explainDepth: 50 },
    setActivePersona: (p) => set({ activePersona: p, activeId: p?.persona_id ?? null }),
    setActive: (id) => {
        const persona = get().personas.find(p => p.persona_id === id) ?? null
        set({ activePersona: persona, activeId: id })
    },
    setPersonas: (ps) => set({ personas: ps }),
    loadPersonas: async () => {
        try {
            const res = await listPersonas()
            if (res.success && res.data) {
                set({ personas: res.data })
            }
        } catch { /* silent */ }
    },
    updateSliders: (s) => set((state) => ({
        sliders: { ...state.sliders, ...s },
    })),
}))
