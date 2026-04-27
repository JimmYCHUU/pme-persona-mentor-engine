import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '../shared/Button'

export function OpeningRitual({ onComplete }: { onComplete: () => void }) {
  const mentorName = 'Persona Mentor Engine'
  const [visible, setVisible] = useState('')
  const [stage, setStage] = useState<'black' | 'glow' | 'typing'>('black')

  useEffect(() => {
    let typeId: ReturnType<typeof setInterval> | null = null
    const blackTimer = setTimeout(() => setStage('glow'), 350)
    const glowTimer = setTimeout(() => {
      setStage('typing')
      let i = 0
      typeId = setInterval(() => {
        i += 1
        setVisible(mentorName.slice(0, i))
        if (i >= mentorName.length && typeId) clearInterval(typeId)
      }, 55)
    }, 700)
    return () => {
      clearTimeout(blackTimer)
      clearTimeout(glowTimer)
      if (typeId) clearInterval(typeId)
    }
  }, [])

  return (
    <motion.div
      style={{
        minHeight: '100vh',
        background: '#000',
        display: 'grid',
        placeItems: 'center',
        transition: 'background 450ms ease',
      }}
      animate={{ background: stage === 'black' ? '#000' : 'var(--bg-base)' }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        animate={{ boxShadow: stage === 'black' ? '0 0 0 var(--accent-glow)' : `0 0 34px var(--accent-glow)` }}
        style={{ textAlign: 'center', padding: 30, border: '1px solid var(--accent-dim)' }}
      >
        <h1>{visible}</h1>
        {visible.length === mentorName.length && <Button onClick={onComplete}>Enter workspace →</Button>}
      </motion.div>
    </motion.div>
  )
}
