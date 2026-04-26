import { useEffect } from 'react'
import { useMasteryStore } from '../store/masteryStore'
import { usePersonaStore } from '../store/personaStore'

export function useMastery() {
  const { activeId } = usePersonaStore()
  const { concepts, pendingCerts, isLoading, fetchLedger, fetchPendingCerts, markCertDelivered } = useMasteryStore()

  useEffect(() => {
    if (!activeId) return
    void fetchLedger(activeId)
    void fetchPendingCerts(activeId)
  }, [activeId])

  const markDelivered = async (certId: string) => {
    if (!activeId) return
    await markCertDelivered(activeId, certId)
  }

  const refetch = async () => {
    if (!activeId) return
    await fetchLedger(activeId)
    await fetchPendingCerts(activeId)
  }

  return { concepts, pendingCerts, isLoading, markDelivered, refetch }
}
