import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '../shared/Button'

export function OpeningRitual({ onComplete }: { onComplete: () => void }) {
  const mentorName = 'Persona Mentor Engine'
  const [visible, setVisible] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      let i = 0
      const id = setInterval(() => {
        i += 1
        setVisible(mentorName.slice(0, i))
        if (i >= mentorName.length) clearInterval(id)
      }, 80)
    }, 1000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <motion.div style={{ minHeight: '100vh', background: 'var(--bg-base)', display: 'grid', placeItems: 'center' }} exit={{ opacity: 0 }}>
      <div style={{ textAlign: 'center', padding: 30, boxShadow: `0 0 30px var(--accent-glow)`, border: '1px solid var(--accent-dim)' }}>
        <h1>{visible}</h1>
        {visible.length === mentorName.length && <Button onClick={onComplete}>Enter workspace →</Button>}
      </div>
    </motion.div>
  )
}
