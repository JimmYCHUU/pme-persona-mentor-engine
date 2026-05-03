/**
 * OpeningRitual — the Sacred Space opening animation.
 * Black screen → mentor name types → Enter to continue.
 */

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { usePersonaStore } from '../../store/personaStore'

interface Props {
    onComplete: () => void
}

export function OpeningRitual({ onComplete }: Props) {
    const { activePersona } = usePersonaStore()
    const [typedText, setTypedText] = useState('')
    const [showEnter, setShowEnter] = useState(false)
    const name = activePersona?.name || 'Persona Mentor Engine'

    useEffect(() => {
        let i = 0
        const timer = setInterval(() => {
            if (i < name.length) {
                setTypedText(name.slice(0, i + 1))
                i++
            } else {
                clearInterval(timer)
                setTimeout(() => setShowEnter(true), 400)
            }
        }, 80)
        return () => clearInterval(timer)
    }, [name])

    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (e.key === 'Enter' && showEnter) onComplete()
        }
        window.addEventListener('keydown', handler)
        return () => window.removeEventListener('keydown', handler)
    }, [showEnter, onComplete])

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
            style={{
                width: '100vw',
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'var(--bg-base)',
                gap: '32px',
            }}
        >
            {/* Typewriter name */}
            <h1 style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '2.5rem',
                color: 'var(--accent)',
                letterSpacing: '0.02em',
                minHeight: '3.5rem',
            }}>
                {typedText}
                <span style={{
                    animation: 'typewriter-glow 1s ease-in-out infinite',
                    color: 'var(--accent)',
                }}>|</span>
            </h1>

            {/* Enter prompt */}
            {showEnter && (
                <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <button
                        className="btn btn-ghost"
                        onClick={onComplete}
                        style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '0.8rem',
                            letterSpacing: '0.1em',
                            textTransform: 'uppercase',
                        }}
                    >
                        Press Enter to begin
                    </button>
                </motion.div>
            )}
        </motion.div>
    )
}
