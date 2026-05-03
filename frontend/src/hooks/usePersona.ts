/**
 * usePersona hook — manages persona loading and selection.
 */

import { useCallback, useEffect } from 'react'
import { usePersonaStore } from '../store/personaStore'
import { listPersonas, createPersona } from '../api/client'

export function usePersona() {
    const { activePersona, personas, setActivePersona, setPersonas } = usePersonaStore()

    const loadPersonas = useCallback(async () => {
        const res = await listPersonas()
        if (res.success && res.data) {
            setPersonas(res.data)
        }
    }, [setPersonas])

    const create = useCallback(async (data: {
        name: string
        description?: string
        sliders?: Record<string, number>
    }) => {
        const res = await createPersona(data)
        if (res.success && res.data) {
            setActivePersona(res.data)
            await loadPersonas()
        }
        return res
    }, [setActivePersona, loadPersonas])

    useEffect(() => {
        loadPersonas()
    }, [loadPersonas])

    return { activePersona, personas, setActivePersona, create, loadPersonas }
}
