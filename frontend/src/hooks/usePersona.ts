import { useEffect } from 'react'
import { usePersonaStore } from '../store/personaStore'

export function usePersona() {
  const store = usePersonaStore()

  useEffect(() => {
    void store.loadPersonas()
  }, [])

  return store
}
