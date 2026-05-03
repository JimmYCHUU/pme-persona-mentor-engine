/**
 * Persona store — Zustand state for active persona.
 */

import { create } from 'zustand'
import type { PersonaProfile } from '../types'

interface PersonaState {
    activePersona: PersonaProfile | null
    personas: PersonaProfile[]
    setActivePersona: (p: PersonaProfile | null) => void
    setPersonas: (ps: PersonaProfile[]) => void
}

export const usePersonaStore = create<PersonaState>((set) => ({
    activePersona: null,
    personas: [],
    setActivePersona: (p) => set({ activePersona: p }),
    setPersonas: (ps) => set({ personas: ps }),
}))
