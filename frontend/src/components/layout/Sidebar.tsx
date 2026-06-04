/**
 * Sidebar — persona selector + delete + mode toggle.
 * Deep Dive / Friend Mode buttons with accent colors, no emojis.
 */

import { useState } from 'react'
import { usePersona } from '../../hooks/usePersona'
import { useSession } from '../../hooks/useSession'
import type { PersonaProfile } from '../../types'

export function Sidebar() {
    const { personas, activePersona, setActivePersona, remove } = usePersona()
    const { mode, toggleMode } = useSession()
    const [confirmDelete, setConfirmDelete] = useState<string | null>(null)

    const isDeep = mode === 'deep_dive'

    const handleDelete = async (personaId: string) => {
        await remove(personaId)
        setConfirmDelete(null)
    }

    return (
        <aside className="sidebar" style={{
            width: 'var(--sidebar-w)',
            minWidth: 'var(--sidebar-w)',
            display: 'flex',
            flexDirection: 'column',
            borderRight: '1px solid var(--border-subtle)',
            padding: '16px 12px',
            gap: '16px',
            overflow: 'auto',
            background: 'var(--bg-surface)',
        }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                paddingBottom: '12px',
                borderBottom: '1px solid var(--border-subtle)',
            }}>
                <span style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '1.1rem',
                    color: 'var(--accent-bright)',
                    letterSpacing: '0.02em',
                }}>
                    PME
                </span>
                <span style={{
                    fontSize: '0.65rem',
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                    padding: '1px 6px',
                    background: 'var(--bg-overlay)',
                    borderRadius: '4px',
                }}>
                    v2.0
                </span>
            </div>

            {/* Persona List */}
            <div>
                <h3 style={{
                    fontSize: '0.65rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.15em',
                    color: 'var(--text-muted)',
                    marginBottom: '8px',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 500,
                }}>
                    Mentors
                </h3>
                {personas.map((p: PersonaProfile) => (
                    <div key={p.persona_id} style={{ position: 'relative', marginBottom: '4px' }}>
                        <button
                            onClick={() => setActivePersona(p)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                width: '100%',
                                padding: '8px 10px',
                                background: activePersona?.persona_id === p.persona_id
                                    ? 'var(--accent-glow)'
                                    : 'transparent',
                                border: activePersona?.persona_id === p.persona_id
                                    ? '1px solid var(--border-accent)'
                                    : '1px solid transparent',
                                borderRadius: '8px',
                                color: activePersona?.persona_id === p.persona_id
                                    ? 'var(--accent-bright)'
                                    : 'var(--text-secondary)',
                                cursor: 'pointer',
                                textAlign: 'left',
                                fontFamily: 'var(--font-body)',
                                fontSize: '0.85rem',
                                transition: 'all var(--t-fast)',
                            }}
                        >
                            <span>{p.name}</span>
                            {/* Delete icon */}
                            <span
                                onClick={(e) => {
                                    e.stopPropagation()
                                    setConfirmDelete(p.persona_id)
                                }}
                                title="Delete mentor"
                                style={{
                                    opacity: 0.4,
                                    fontSize: '11px',
                                    cursor: 'pointer',
                                    transition: 'opacity var(--t-fast)',
                                    padding: '2px 4px',
                                    borderRadius: '4px',
                                    color: 'var(--text-muted)',
                                }}
                                onMouseEnter={e => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.color = 'var(--danger)' }}
                                onMouseLeave={e => { e.currentTarget.style.opacity = '0.4'; e.currentTarget.style.color = 'var(--text-muted)' }}
                            >
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                                    <polyline points="3 6 5 6 21 6" />
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                </svg>
                            </span>
                        </button>

                        {/* Delete confirmation */}
                        {confirmDelete === p.persona_id && (
                            <div style={{
                                position: 'absolute',
                                top: '100%',
                                left: 0,
                                right: 0,
                                padding: '8px',
                                background: 'var(--bg-raised)',
                                border: '1px solid var(--danger)',
                                borderRadius: '8px',
                                zIndex: 100,
                                display: 'flex',
                                gap: '6px',
                                marginTop: '2px',
                            }}>
                                <button
                                    onClick={() => handleDelete(p.persona_id)}
                                    style={{
                                        flex: 1, padding: '5px',
                                        background: 'var(--danger)',
                                        border: 'none', borderRadius: '6px',
                                        color: '#fff', fontSize: '0.7rem',
                                        fontWeight: 500, cursor: 'pointer',
                                    }}
                                >
                                    Delete
                                </button>
                                <button
                                    onClick={() => setConfirmDelete(null)}
                                    style={{
                                        flex: 1, padding: '5px',
                                        background: 'transparent',
                                        border: '1px solid var(--border-default)',
                                        borderRadius: '6px',
                                        color: 'var(--text-muted)', fontSize: '0.7rem',
                                        cursor: 'pointer',
                                    }}
                                >
                                    Cancel
                                </button>
                            </div>
                        )}
                    </div>
                ))}
                {personas.length === 0 && (
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontStyle: 'italic' }}>
                        No mentors yet. Create one to begin.
                    </p>
                )}
            </div>

            {/* Mode Toggle — styled buttons, no emojis */}
            <div style={{
                marginTop: 'auto',
                paddingTop: '12px',
                borderTop: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px',
            }}>
                <span style={{
                    fontSize: '0.6rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.15em',
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                    marginBottom: '4px',
                }}>
                    Session Mode
                </span>
                <button
                    onClick={() => { if (!isDeep) toggleMode() }}
                    style={{
                        width: '100%',
                        padding: '8px 12px',
                        background: isDeep ? 'var(--accent-glow)' : 'transparent',
                        border: isDeep ? '1px solid var(--border-accent)' : '1px solid var(--border-subtle)',
                        borderRadius: '8px',
                        color: isDeep ? 'var(--accent-bright)' : 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.72rem',
                        letterSpacing: '0.06em',
                        cursor: 'pointer',
                        transition: 'all var(--t-fast)',
                        textAlign: 'left',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                    }}
                >
                    <span style={{
                        width: '6px', height: '6px',
                        borderRadius: '50%',
                        background: isDeep ? 'var(--accent-bright)' : 'var(--text-disabled)',
                        boxShadow: isDeep ? '0 0 6px var(--accent)' : 'none',
                        transition: 'all var(--t-fast)',
                    }} />
                    Deep Dive
                </button>
                <button
                    onClick={() => { if (isDeep) toggleMode() }}
                    style={{
                        width: '100%',
                        padding: '8px 12px',
                        background: !isDeep ? 'rgba(14,165,233,0.12)' : 'transparent',
                        border: !isDeep ? '1px solid rgba(14,165,233,0.35)' : '1px solid var(--border-subtle)',
                        borderRadius: '8px',
                        color: !isDeep ? 'var(--friend-accent)' : 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.72rem',
                        letterSpacing: '0.06em',
                        cursor: 'pointer',
                        transition: 'all var(--t-fast)',
                        textAlign: 'left',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                    }}
                >
                    <span style={{
                        width: '6px', height: '6px',
                        borderRadius: '50%',
                        background: !isDeep ? 'var(--friend-accent)' : 'var(--text-disabled)',
                        boxShadow: !isDeep ? '0 0 6px var(--friend-accent)' : 'none',
                        transition: 'all var(--t-fast)',
                    }} />
                    Friend Mode
                </button>
            </div>
        </aside>
    )
}
