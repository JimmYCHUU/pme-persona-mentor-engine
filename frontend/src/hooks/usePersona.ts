/**
 * usePersona hook — manages persona loading, selection, and deletion.
 */

import { useCallback, useEffect } from 'react'
import { usePersonaStore } from '../store/personaStore'
import { listPersonas, createPersona, deletePersona } from '../api/client'

export function usePersona() {
    const { activePersona, personas, setActivePersona, setPersonas } = usePersonaStore()

    const loadPersonas = useCallback(async () => {
        const res = await listPersonas()
        if (res.success && res.data) {
            setPersonas(res.data as any)
        }
    }, [setPersonas])

    const create = useCallback(async (data: {
        name: string
        description?: string
        sliders?: Record<string, number>
    }) => {
        const res = await createPersona(data)
        if (res.success && res.data) {
            setActivePersona(res.data as any)
            await loadPersonas()
        }
        return res
    }, [setActivePersona, loadPersonas])

    const remove = useCallback(async (personaId: string) => {
        const res = await deletePersona(personaId)
        if (res.success) {
            if (activePersona?.persona_id === personaId) {
                setActivePersona(null as any)
            }
            await loadPersonas()
        }
        return res
    }, [activePersona, setActivePersona, loadPersonas])

    useEffect(() => {
        loadPersonas()
    }, [loadPersonas])

    return { activePersona, personas, setActivePersona, create, remove, loadPersonas }
}
