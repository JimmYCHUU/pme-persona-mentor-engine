import { Button } from '../shared/Button'
import { StepRoadmap } from './StepRoadmap'

export function ResumeModal({ snapshot, onContinue, onStartFresh }: { snapshot: any; onContinue: () => void; onStartFresh: () => void }) {
  const assessment = snapshot?.mentor_assessment ?? {}
  const nextSteps = assessment.next_steps ?? []
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'grid', placeItems: 'center' }}>
      <div style={{ background: 'var(--bg-surface)', padding: 20, width: 480, borderRadius: 12 }}>
        <h2>Resume session</h2>
        <p>{assessment.summary ?? 'Your mentor prepared a summary.'}</p>
        <StepRoadmap next_steps={nextSteps} />
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <Button variant='ghost' onClick={onStartFresh}>Start Fresh</Button>
          <Button onClick={onContinue}>Continue</Button>
        </div>
      </div>
    </div>
  )
}
