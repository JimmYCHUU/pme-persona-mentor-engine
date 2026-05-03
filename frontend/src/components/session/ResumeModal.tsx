/**
 * ResumeModal — shows session resume greeting and continue/fresh options.
 */

import { motion } from 'framer-motion'
import type { SessionSnapshot } from '../../types'
import { useSessionStore } from '../../store/sessionStore'

interface Props {
    snapshot: SessionSnapshot
    onContinue: () => void
    onStartFresh: () => void
}

export function ResumeModal({ snapshot, onContinue, onStartFresh }: Props) {
    const { resumeGreeting } = useSessionStore()

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
                width: '100vw',
                height: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'var(--bg-base)',
            }}
        >
            <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="glass-card"
                style={{
                    maxWidth: '560px',
                    width: '90%',
                    padding: '32px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '20px',
                }}
            >
                <h2 style={{
                    fontFamily: 'var(--font-heading)',
                    color: 'var(--accent)',
                    fontSize: '1.3rem',
                }}>
                    Welcome Back
                </h2>

                {resumeGreeting && (
                    <p style={{
                        color: 'var(--text-secondary)',
                        fontSize: '0.9rem',
                        lineHeight: 1.7,
                        whiteSpace: 'pre-wrap',
                        borderLeft: '2px solid var(--accent-dim)',
                        paddingLeft: '16px',
                        fontStyle: 'italic',
                    }}>
                        {resumeGreeting}
                    </p>
                )}

                <div style={{
                    display: 'flex',
                    gap: '12px',
                    marginTop: '8px',
                }}>
                    <button className="btn btn-primary" onClick={onContinue} style={{ flex: 1 }}>
                        Continue Session
                    </button>
                    <button className="btn btn-ghost" onClick={onStartFresh} style={{ flex: 1 }}>
                        Start Fresh
                    </button>
                </div>
            </motion.div>
        </motion.div>
    )
}
