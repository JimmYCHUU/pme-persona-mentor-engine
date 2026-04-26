import { useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import { useMastery } from '../../hooks/useMastery'
import { useSessionStore } from '../../store/sessionStore'
import { MasteryCertModal } from '../mastery/MasteryCertModal'
import { OpeningRitual } from '../session/OpeningRitual'
import { ResumeModal } from '../session/ResumeModal'
import { Shell } from './Shell'

type RitualState = 'opening' | 'cert' | 'resume' | 'workspace'

export function WorkspaceShell() {
  const [ritualState, setRitualState] = useState<RitualState>('opening')
  const { mode, snapshot } = useSessionStore()
  const { pendingCerts, markDelivered } = useMastery()

  const handleRitualComplete = () =>
    setRitualState(pendingCerts.length > 0 ? 'cert' : snapshot ? 'resume' : 'workspace')

  const handleCertClose = async (certId: string) => {
    await markDelivered(certId)
    setRitualState(snapshot ? 'resume' : 'workspace')
  }

  const handleResumeClose = () => setRitualState('workspace')

  if (mode === 'deep_dive') {
    document.body.classList.add('focus-mode')
    document.body.classList.remove('friend-mode')
  } else {
    document.body.classList.remove('focus-mode')
    document.body.classList.add('friend-mode')
  }

  return (
    <div className={`workspace-root ${mode === 'friend_mode' ? 'friend-mode' : ''}`}>
      <AnimatePresence mode='wait'>
        {ritualState === 'opening' && <OpeningRitual key='ritual' onComplete={handleRitualComplete} />}
        {ritualState === 'cert' && pendingCerts[0] && (
          <MasteryCertModal key='cert' cert={pendingCerts[0]} onClose={() => void handleCertClose(pendingCerts[0].cert_id)} />
        )}
        {ritualState === 'resume' && snapshot && (
          <ResumeModal key='resume' snapshot={snapshot} onContinue={handleResumeClose} onStartFresh={handleResumeClose} />
        )}
        {ritualState === 'workspace' && <Shell key='shell' />}
      </AnimatePresence>
    </div>
  )
}
