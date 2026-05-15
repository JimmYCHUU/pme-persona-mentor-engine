/**
 * MentorsPage — list all personas with ability to create new ones.
 */

import { useEffect } from 'react'
import { usePersonaStore } from '../store/personaStore'
import { PersonaBuilder } from '../components/persona/PersonaBuilder'

export function MentorsPage() {
    const { personas, activePersona, setActive, loadPersonas } = usePersonaStore()

    useEffect(() => {
        loadPersonas()
    }, [])

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{
                padding: '24px 32px',
                borderBottom: '1px solid var(--border-subtle)',
                background: 'var(--bg-surface)',
            }}>
                <h1 style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '28px', fontWeight: 400,
                    color: 'var(--text-primary)',
                }}>
                    Mentors
                </h1>
            </div>

            <div style={{ flex: 1, overflow: 'auto', padding: '32px' }}>
                {/* Persona grid */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                    gap: '16px',
                    marginBottom: '32px',
                }}>
                    {personas.map(p => (
                        <div
                            key={p.persona_id}
                            onClick={() => setActive(p.persona_id)}
                            style={{
                                padding: '20px',
                                background: activePersona?.persona_id === p.persona_id
                                    ? 'var(--accent-glow)' : 'var(--bg-raised)',
                                border: `1px solid ${activePersona?.persona_id === p.persona_id
                                    ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                                borderRadius: '12px',
                                cursor: 'pointer',
                                transition: 'all var(--t-fast)',
                            }}
                        >
                            <h3 style={{
                                fontFamily: 'var(--font-display)',
                                fontSize: '20px', fontWeight: 400,
                                marginBottom: '8px',
                                color: activePersona?.persona_id === p.persona_id
                                    ? 'var(--accent-bright)' : 'var(--text-primary)',
                            }}>
                                {p.name}
                            </h3>
                            <p style={{
                                fontSize: '13px',
                                color: 'var(--text-secondary)',
                                lineHeight: 1.5,
                            }}>
                                {p.description || 'No description'}
                            </p>
                        </div>
                    ))}

                    {/* Create new card */}
                    <div style={{
                        padding: '20px',
                        background: 'var(--bg-surface)',
                        border: '1px dashed var(--border-default)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '120px',
                        cursor: 'pointer',
                        color: 'var(--text-muted)',
                        fontSize: '14px',
                        transition: 'all var(--t-fast)',
                    }}>
                        + New Mentor
                    </div>
                </div>
            </div>
        </div>
    )
}
