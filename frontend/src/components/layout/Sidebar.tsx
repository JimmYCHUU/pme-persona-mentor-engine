/**
 * Sidebar — persona selector + mastery map + mode toggle.
 */

import { usePersona } from '../../hooks/usePersona'
import { useSession } from '../../hooks/useSession'
import type { PersonaProfile } from '../../types'

export function Sidebar() {
    const { personas, activePersona, setActivePersona } = usePersona()
    const { mode, toggleMode } = useSession()

    return (
        <aside className="sidebar glass-card" style={{
            width: 'var(--sidebar-w)',
            minWidth: 'var(--sidebar-w)',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 0,
            borderRight: '1px solid var(--glass-border)',
            padding: '16px 12px',
            gap: '16px',
            overflow: 'auto',
        }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                paddingBottom: '12px',
                borderBottom: '1px solid var(--glass-border)',
            }}>
                <span style={{
                    fontFamily: 'var(--font-heading)',
                    fontSize: '1.1rem',
                    color: 'var(--accent)',
                    letterSpacing: '0.02em',
                }}>
                    PME
                </span>
                <span style={{
                    fontSize: '0.7rem',
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                }}>
                    v1.0
                </span>
            </div>

            {/* Persona List */}
            <div>
                <h3 style={{
                    fontSize: '0.7rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    color: 'var(--text-muted)',
                    marginBottom: '8px',
                    fontFamily: 'var(--font-sans)',
                    fontWeight: 600,
                }}>
                    Mentors
                </h3>
                {personas.map((p: PersonaProfile) => (
                    <button
                        key={p.persona_id}
                        onClick={() => setActivePersona(p)}
                        style={{
                            display: 'block',
                            width: '100%',
                            padding: '8px 10px',
                            background: activePersona?.persona_id === p.persona_id
                                ? 'var(--accent-glow)'
                                : 'transparent',
                            border: activePersona?.persona_id === p.persona_id
                                ? '1px solid var(--accent-dim)'
                                : '1px solid transparent',
                            borderRadius: 'var(--radius-md)',
                            color: activePersona?.persona_id === p.persona_id
                                ? 'var(--accent)'
                                : 'var(--text-secondary)',
                            cursor: 'pointer',
                            textAlign: 'left',
                            fontFamily: 'var(--font-sans)',
                            fontSize: '0.85rem',
                            transition: 'all var(--transition-fast)',
                            marginBottom: '4px',
                        }}
                    >
                        {p.name}
                    </button>
                ))}
                {personas.length === 0 && (
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontStyle: 'italic' }}>
                        No mentors yet. Create one to begin.
                    </p>
                )}
            </div>

            {/* Mode Toggle */}
            <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid var(--glass-border)' }}>
                <button
                    onClick={toggleMode}
                    className="btn btn-ghost"
                    style={{
                        width: '100%',
                        fontSize: '0.75rem',
                        fontFamily: 'var(--font-mono)',
                    }}
                >
                    {mode === 'deep_dive' ? '🔥 Deep Dive' : '💬 Friend Mode'}
                </button>
            </div>
        </aside>
    )
}
