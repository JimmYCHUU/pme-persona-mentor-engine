/**
 * MasteryCertModal — full-screen modal for Proof of Mastery certificates.
 */

import { motion } from 'framer-motion'
import type { MasteryCert } from '../../types'

interface Props {
    cert: MasteryCert
    onClose: () => void
}

export function MasteryCertModal({ cert, onClose }: Props) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0,0,0,0.85)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 100,
            }}
        >
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.15, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="glass-card"
                style={{
                    maxWidth: '520px',
                    width: '90%',
                    padding: '32px',
                    border: '1px solid var(--accent-dim)',
                    textAlign: 'center',
                }}
            >
                <div style={{
                    fontSize: '0.7rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--accent)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.15em',
                    marginBottom: '8px',
                }}>
                    Proof of Mastery
                </div>

                <h2 style={{
                    fontFamily: 'var(--font-heading)',
                    color: 'var(--text-heading)',
                    fontSize: '1.5rem',
                    marginBottom: '16px',
                }}>
                    {cert.concept_label}
                </h2>

                <p style={{
                    color: 'var(--text-secondary)',
                    fontSize: '0.9rem',
                    lineHeight: 1.7,
                    fontStyle: 'italic',
                    marginBottom: '20px',
                    whiteSpace: 'pre-wrap',
                }}>
                    "{cert.mentor_statement}"
                </p>

                <div style={{
                    fontSize: '0.7rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    marginBottom: '24px',
                }}>
                    Issued: {new Date(cert.issued_at).toLocaleDateString()}
                </div>

                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                    <button className="btn btn-ghost" onClick={onClose}>Close</button>
                    <button className="btn btn-primary" onClick={() => window.print()}>Export as PDF</button>
                </div>
            </motion.div>
        </motion.div>
    )
}
