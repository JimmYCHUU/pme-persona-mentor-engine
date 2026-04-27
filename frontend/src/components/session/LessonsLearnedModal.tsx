import { motion } from 'framer-motion'
import { Button } from '../shared/Button'

interface LessonsLearnedModalProps {
  onClose: () => void
  onGenerate: () => Promise<void>
  isGenerating: boolean
  lessonsPath: string | null
}

export function LessonsLearnedModal({ onClose, onGenerate, isGenerating, lessonsPath }: LessonsLearnedModalProps) {
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.72)', display: 'grid', placeItems: 'center', zIndex: 60 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--bg-overlay)', borderRadius: 12, width: 560, maxWidth: 'calc(100vw - 24px)', padding: 20 }}
      >
        <h3 style={{ marginTop: 0 }}>End session</h3>
        <p style={{ color: 'var(--text-secondary)' }}>
          Would you like a Lessons Learned summary before closing your workspace?
        </p>
        {lessonsPath && (
          <p style={{ margin: '10px 0', color: 'var(--success)' }}>
            Summary saved to: {lessonsPath}
          </p>
        )}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 12 }}>
          <Button variant='ghost' onClick={onClose}>
            Continue working
          </Button>
          <Button onClick={() => void onGenerate()} disabled={isGenerating}>
            {isGenerating ? 'Generating…' : 'Generate summary'}
          </Button>
        </div>
      </motion.div>
    </div>
  )
}
