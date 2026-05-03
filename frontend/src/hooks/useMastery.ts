/**
 * useMastery hook — mastery ledger and pending cert management.
 */

import { useCallback } from 'react'
import { useMasteryStore } from '../store/masteryStore'
import { getMasteryLedger, getPendingCerts, markCertDelivered } from '../api/client'

export function useMastery() {
    const { concepts, pendingCerts, setConcepts, setPendingCerts, removePendingCert } = useMasteryStore()

    const loadLedger = useCallback(async (personaId: string) => {
        const res = await getMasteryLedger(personaId)
        if (res.success && res.data?.concepts) {
            setConcepts(res.data.concepts)
        }
    }, [setConcepts])

    const loadPendingCerts = useCallback(async (personaId: string) => {
        const res = await getPendingCerts(personaId)
        if (res.success && res.data?.certs) {
            setPendingCerts(res.data.certs)
        }
    }, [setPendingCerts])

    const markDelivered = useCallback(async (certId: string) => {
        const cert = pendingCerts.find(c => c.cert_id === certId)
        if (cert) {
            await markCertDelivered(cert.persona_id, certId)
            removePendingCert(certId)
        }
    }, [pendingCerts, removePendingCert])

    return { concepts, pendingCerts, loadLedger, loadPendingCerts, markDelivered }
}
