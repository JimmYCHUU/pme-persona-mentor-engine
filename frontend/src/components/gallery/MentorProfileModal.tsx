/**
 * MentorProfileModal — full-screen overlay showing mentor details.
 * Displays all profile information and an activate button.
 */

import type { MentorProfile } from '../../types'

interface Props {
    mentor: MentorProfile
    category: string
    onClose: () => void
    onActivate: (category: string, mentorId: string) => void
    isActivating: boolean
}

export function MentorProfileModal({ mentor, category, onClose, onActivate, isActivating }: Props) {
    return (
        <div
            onClick={onClose}
            style={{
                position: 'fixed', inset: 0,
                background: 'rgba(0, 0, 0, 0.7)',
                backdropFilter: 'blur(8px)',
                WebkitBackdropFilter: 'blur(8px)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                zIndex: 1000,
                padding: '24px',
                animation: 'fadeIn 0.2s ease',
            }}
        >
            <div
                onClick={e => e.stopPropagation()}
                style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-accent)',
                    borderRadius: '18px',
                    padding: '36px',
                    maxWidth: '560px',
                    width: '100%',
                    maxHeight: '80vh',
                    overflow: 'auto',
                    position: 'relative',
                    boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
                }}
            >
                {/* Close button */}
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute', top: '16px', right: '16px',
                        background: 'var(--bg-overlay)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '8px',
                        width: '32px', height: '32px',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        fontSize: '16px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        transition: 'all var(--t-fast)',
                    }}
                    onMouseEnter={e => {
                        e.currentTarget.style.color = 'var(--text-primary)'
                        e.currentTarget.style.borderColor = 'var(--border-accent)'
                    }}
                    onMouseLeave={e => {
                        e.currentTarget.style.color = 'var(--text-muted)'
                        e.currentTarget.style.borderColor = 'var(--border-subtle)'
                    }}
                >
                    ✕
                </button>

                {/* Avatar + Name */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                    <div style={{
                        width: '64px', height: '64px',
                        borderRadius: '16px',
                        background: 'var(--accent-glow)',
                        border: '1px solid var(--border-accent)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '32px',
                        flexShrink: 0,
                    }}>
                        {mentor.avatar_emoji}
                    </div>
                    <div>
                        <h2 style={{
                            fontFamily: 'var(--font-display)',
                            fontSize: '26px', fontWeight: 400,
                            color: 'var(--accent-bright)',
                            lineHeight: 1.2,
                        }}>
                            {mentor.display_name}
                        </h2>
                        <p style={{
                            fontSize: '13px', color: 'var(--text-muted)',
                            fontFamily: 'var(--font-mono)',
                            marginTop: '4px',
                        }}>
                            {mentor.real_name} · {mentor.subscriber_count} subscribers
                        </p>
                    </div>
                </div>

                {/* Field & Speciality */}
                <div style={{
                    display: 'flex', gap: '8px',
                    marginBottom: '16px',
                    flexWrap: 'wrap',
                }}>
                    <span style={{
                        fontSize: '11px', padding: '4px 10px',
                        borderRadius: '6px',
                        background: 'var(--accent-glow)',
                        color: 'var(--accent-bright)',
                        border: '1px solid var(--border-accent)',
                        fontFamily: 'var(--font-mono)',
                        letterSpacing: '0.05em',
                        textTransform: 'uppercase',
                    }}>
                        {mentor.field}
                    </span>
                    {mentor.sub_speciality && (
                        <span style={{
                            fontSize: '11px', padding: '4px 10px',
                            borderRadius: '6px',
                            background: 'var(--bg-overlay)',
                            color: 'var(--text-secondary)',
                            border: '1px solid var(--border-subtle)',
                            fontFamily: 'var(--font-mono)',
                        }}>
                            {mentor.sub_speciality}
                        </span>
                    )}
                </div>

                {/* Description */}
                <p style={{
                    fontSize: '14px',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.65,
                    marginBottom: '20px',
                }}>
                    {mentor.description}
                </p>

                {/* Teaching Level */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{
                        fontSize: '10px', color: 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                        letterSpacing: '0.1em',
                        textTransform: 'uppercase',
                        display: 'block',
                        marginBottom: '6px',
                    }}>
                        Teaching Level
                    </label>
                    <p style={{
                        fontSize: '13px', color: 'var(--accent-bright)',
                        fontFamily: 'var(--font-mono)',
                    }}>
                        {mentor.teaching_level}
                    </p>
                </div>

                {/* Best For */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{
                        fontSize: '10px', color: 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                        letterSpacing: '0.1em',
                        textTransform: 'uppercase',
                        display: 'block',
                        marginBottom: '8px',
                    }}>
                        Best For
                    </label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {mentor.best_for.map(tag => (
                            <span key={tag} style={{
                                fontSize: '11px', padding: '4px 10px',
                                borderRadius: '6px',
                                background: 'var(--bg-overlay)',
                                color: 'var(--text-secondary)',
                                border: '1px solid var(--border-subtle)',
                                fontFamily: 'var(--font-mono)',
                            }}>
                                {tag}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Personality Tags */}
                {mentor.personality_tags?.length > 0 && (
                    <div style={{ marginBottom: '24px' }}>
                        <label style={{
                            fontSize: '10px', color: 'var(--text-muted)',
                            fontFamily: 'var(--font-mono)',
                            letterSpacing: '0.1em',
                            textTransform: 'uppercase',
                            display: 'block',
                            marginBottom: '8px',
                        }}>
                            Personality
                        </label>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {mentor.personality_tags.map(tag => (
                                <span key={tag} style={{
                                    fontSize: '11px', padding: '4px 10px',
                                    borderRadius: '6px',
                                    background: 'rgba(139, 92, 246, 0.08)',
                                    color: 'var(--accent)',
                                    border: '1px solid rgba(139, 92, 246, 0.15)',
                                    fontFamily: 'var(--font-mono)',
                                }}>
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Activate Button */}
                <button
                    onClick={() => onActivate(category, mentor.id)}
                    disabled={isActivating}
                    style={{
                        width: '100%',
                        padding: '14px 0',
                        borderRadius: '10px',
                        background: isActivating
                            ? 'var(--bg-overlay)'
                            : 'linear-gradient(135deg, var(--accent) 0%, var(--accent-bright) 100%)',
                        border: 'none',
                        color: isActivating ? 'var(--text-muted)' : '#fff',
                        fontFamily: 'var(--font-body)',
                        fontSize: '15px',
                        fontWeight: 600,
                        letterSpacing: '0.04em',
                        cursor: isActivating ? 'wait' : 'pointer',
                        transition: 'all var(--t-fast)',
                        boxShadow: isActivating ? 'none' : '0 4px 20px rgba(139, 92, 246, 0.3)',
                    }}
                    onMouseEnter={e => {
                        if (!isActivating) {
                            e.currentTarget.style.boxShadow = '0 6px 28px rgba(139, 92, 246, 0.5)'
                            e.currentTarget.style.transform = 'translateY(-1px)'
                        }
                    }}
                    onMouseLeave={e => {
                        if (!isActivating) {
                            e.currentTarget.style.boxShadow = '0 4px 20px rgba(139, 92, 246, 0.3)'
                            e.currentTarget.style.transform = 'translateY(0)'
                        }
                    }}
                >
                    {isActivating ? 'Activating…' : '⚡ Activate & Start Chatting'}
                </button>
            </div>
        </div>
    )
}
