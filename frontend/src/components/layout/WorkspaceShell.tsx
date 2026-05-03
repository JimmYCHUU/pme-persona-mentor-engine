/**
 * WorkspaceShell — root component managing the opening ritual state machine.
 * OUTERMOST component per SDD Section 6.2.
 */

import { useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import { OpeningRitual } from '../session/OpeningRitual'
import { MasteryCertModal } from '../mastery/MasteryCertModal'
import { ResumeModal } from '../session/ResumeModal'
import { Shell } from './Shell'
import { useSessionStore } from '../../store/sessionStore'
import { useMasteryStore } from '../../store/masteryStore'
import { useMastery } from '../../hooks/useMastery'

type RitualState = 'opening' | 'cert' | 'resume' | 'workspace'

export function WorkspaceShell() {
    const [ritualState, setRitualState] = useState<RitualState>('opening')
    const { mode, snapshot } = useSessionStore()
    const { pendingCerts } = useMasteryStore()
    const { markDelivered } = useMastery()

    const handleRitualComplete = () =>
        setRitualState(
            pendingCerts.length > 0 ? 'cert' :
                snapshot ? 'resume' :
                    'workspace'
        )

    const handleCertClose = async (certId: string) => {
        await markDelivered(certId)
        setRitualState(snapshot ? 'resume' : 'workspace')
    }

    const handleResumeClose = () => setRitualState('workspace')

    return (
        <div className={`workspace-root ${mode === 'friend_mode' ? 'friend-mode' : ''}`}
            style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
            <AnimatePresence mode="wait">
                {ritualState === 'opening' && (
                    <OpeningRitual key="ritual" onComplete={handleRitualComplete} />
                )}
                {ritualState === 'cert' && pendingCerts[0] && (
                    <MasteryCertModal
                        key="cert"
                        cert={pendingCerts[0]}
                        onClose={() => handleCertClose(pendingCerts[0].cert_id)}
                    />
                )}
                {ritualState === 'resume' && snapshot && (
                    <ResumeModal
                        key="resume"
                        snapshot={snapshot}
                        onContinue={handleResumeClose}
                        onStartFresh={handleResumeClose}
                    />
                )}
                {ritualState === 'workspace' && (
                    <Shell key="shell" />
                )}
            </AnimatePresence>
        </div>
    )
}
