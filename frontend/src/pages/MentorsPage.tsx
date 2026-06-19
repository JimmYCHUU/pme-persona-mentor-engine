/**
 * MentorsPage — browse pre-built gallery + custom personas.
 * Two tabs: "Gallery" (pre-built mentors) and "My Mentors" (custom).
 */

import { useState, useEffect } from 'react'
import { MentorGallery } from '../components/gallery/MentorGallery'
import { CreateMentorModal } from '../components/gallery/CreateMentorModal'
import { usePersonaStore } from '../store/personaStore'

interface Props {
    onNavigateToChat?: () => void
}

export function MentorsPage({ onNavigateToChat }: Props) {
    const [tab, setTab] = useState<'gallery' | 'custom'>('gallery')
    const [showCreate, setShowCreate] = useState(false)
    const { personas, activePersona, setActive, loadPersonas } = usePersonaStore()

    useEffect(() => {
        loadPersonas()
    }, [])

    const handleMentorActivated = (personaId: string, _mentorName: string) => {
        // Reload personas so the new mentor appears in the list
        loadPersonas().then(() => {
            // Set the activated mentor as active
            setActive(personaId)
            // Navigate to chat
            onNavigateToChat?.()
        })
    }

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <div style={{
                padding: '20px 32px 0',
                background: 'var(--bg-surface)',
            }}>
                <h1 style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '28px', fontWeight: 400,
                    color: 'var(--text-primary)',
                    marginBottom: '16px',
                }}>
                    Mentors
                </h1>

                {/* Tab switcher */}
                <div style={{ display: 'flex', gap: '0px' }}>
                    {[
                        { key: 'gallery' as const, label: 'Gallery', icon: '🎓' },
                        { key: 'custom' as const, label: 'My Mentors', icon: '✦' },
                    ].map(t => {
                        const active = tab === t.key
                        return (
                            <button
                                key={t.key}
                                onClick={() => setTab(t.key)}
                                style={{
                                    padding: '10px 20px',
                                    background: 'transparent',
                                    border: 'none',
                                    borderBottom: active
                                        ? '2px solid var(--accent-bright)'
                                        : '2px solid transparent',
                                    color: active ? 'var(--text-primary)' : 'var(--text-muted)',
                                    fontFamily: 'var(--font-body)',
                                    fontSize: '14px',
                                    fontWeight: active ? 500 : 400,
                                    cursor: 'pointer',
                                    transition: 'all var(--t-fast)',
                                    display: 'flex', alignItems: 'center', gap: '8px',
                                }}
                            >
                                <span style={{ fontSize: '14px' }}>{t.icon}</span>
                                {t.label}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Content area */}
            <div style={{ flex: 1, overflow: 'hidden' }}>
                {tab === 'gallery' ? (
                    <MentorGallery onMentorActivated={handleMentorActivated} />
                ) : (
                    <div style={{ height: '100%', overflow: 'auto', padding: '24px 32px' }}>
                        {/* Custom persona grid */}
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                            gap: '16px',
                        }}>
                            {personas.map(p => (
                                <div
                                    key={p.persona_id}
                                    onClick={() => {
                                        setActive(p.persona_id)
                                        onNavigateToChat?.()
                                    }}
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
                            <div
                                onClick={() => setShowCreate(true)}
                                style={{
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
                                }}
                            >
                                + New Mentor
                            </div>
                        </div>

                        {personas.length === 0 && (
                            <div style={{
                                textAlign: 'center',
                                padding: '64px 0',
                                color: 'var(--text-muted)',
                                fontSize: '14px',
                            }}>
                                <p style={{ marginBottom: '8px' }}>No custom mentors yet.</p>
                                <p>Browse the <button
                                    onClick={() => setTab('gallery')}
                                    style={{
                                        background: 'none', border: 'none',
                                        color: 'var(--accent-bright)',
                                        cursor: 'pointer', textDecoration: 'underline',
                                        fontFamily: 'var(--font-body)', fontSize: '14px',
                                    }}
                                >Gallery</button> to activate a pre-built mentor.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Create Mentor Modal */}
            <CreateMentorModal
                open={showCreate}
                onClose={() => setShowCreate(false)}
                onCreated={(personaId) => {
                    setShowCreate(false)
                    loadPersonas().then(() => {
                        setActive(personaId)
                        onNavigateToChat?.()
                    })
                }}
            />
        </div>
    )
}
