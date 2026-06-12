/**
 * MentorCard — displays a pre-built mentor profile in the gallery grid.
 * Glassmorphic card with avatar emoji, name, description, tags, and activate button.
 */

import { useState } from 'react'
import type { MentorProfile } from '../../types'

interface Props {
    mentor: MentorProfile
    category: string
    onActivate: (category: string, mentorId: string) => void
    onCardClick: (mentor: MentorProfile) => void
    isActivating: boolean
}

export function MentorCard({ mentor, category, onActivate, onCardClick, isActivating }: Props) {
    const [hovered, setHovered] = useState(false)

    return (
        <div
            onClick={() => onCardClick(mentor)}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            style={{
                background: hovered ? 'var(--bg-raised)' : 'var(--bg-surface)',
                border: `1px solid ${hovered ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                borderRadius: '14px',
                padding: '24px 20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                transition: 'all var(--t-normal)',
                cursor: 'pointer',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: hovered ? 'var(--shadow-accent)' : 'none',
            }}
        >
            {/* Glow effect on hover */}
            {hovered && (
                <div style={{
                    position: 'absolute', top: 0, left: 0, right: 0, height: '100px',
                    background: 'linear-gradient(to bottom, var(--accent-glow), transparent)',
                    pointerEvents: 'none', borderRadius: '14px 14px 0 0',
                }} />
            )}

            {/* Header: emoji + name */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', position: 'relative' }}>
                <div style={{
                    width: '44px', height: '44px',
                    borderRadius: '12px',
                    background: 'var(--accent-glow)',
                    border: '1px solid var(--border-accent)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '22px',
                    flexShrink: 0,
                }}>
                    {mentor.avatar_emoji}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: '20px', fontWeight: 400,
                        color: hovered ? 'var(--accent-bright)' : 'var(--text-primary)',
                        transition: 'color var(--t-fast)',
                        lineHeight: 1.2,
                    }}>
                        {mentor.display_name}
                    </h3>
                    <p style={{
                        fontSize: '11px', color: 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                        letterSpacing: '0.04em',
                    }}>
                        {mentor.subscriber_count} subscribers
                    </p>
                </div>
            </div>

            {/* Description */}
            <p style={{
                fontSize: '13px', color: 'var(--text-secondary)',
                lineHeight: 1.55,
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                position: 'relative',
            }}>
                {mentor.description}
            </p>

            {/* Teaching level badge */}
            <div style={{
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                color: 'var(--accent-bright)',
                letterSpacing: '0.05em',
            }}>
                {mentor.teaching_level}
            </div>

            {/* Best for tags */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {mentor.best_for.slice(0, 4).map(tag => (
                    <span key={tag} style={{
                        fontSize: '10px',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        background: 'var(--bg-overlay)',
                        color: 'var(--text-secondary)',
                        border: '1px solid var(--border-subtle)',
                        fontFamily: 'var(--font-mono)',
                        letterSpacing: '0.02em',
                    }}>
                        {tag}
                    </span>
                ))}
                {mentor.best_for.length > 4 && (
                    <span style={{
                        fontSize: '10px', padding: '3px 8px',
                        color: 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                    }}>
                        +{mentor.best_for.length - 4}
                    </span>
                )}
            </div>

            {/* Activate button */}
            <button
                onClick={(e) => {
                    e.stopPropagation()
                    onActivate(category, mentor.id)
                }}
                disabled={isActivating}
                style={{
                    marginTop: '4px',
                    padding: '10px 0',
                    borderRadius: '8px',
                    background: isActivating ? 'var(--bg-overlay)' : 'transparent',
                    border: '1px solid var(--border-accent)',
                    color: isActivating ? 'var(--text-muted)' : 'var(--accent-bright)',
                    fontFamily: 'var(--font-body)',
                    fontSize: '13px',
                    fontWeight: 500,
                    letterSpacing: '0.05em',
                    cursor: isActivating ? 'wait' : 'pointer',
                    transition: 'all var(--t-fast)',
                    width: '100%',
                }}
                onMouseEnter={e => {
                    if (!isActivating) {
                        e.currentTarget.style.background = 'var(--accent-glow)'
                        e.currentTarget.style.borderColor = 'var(--accent-bright)'
                    }
                }}
                onMouseLeave={e => {
                    if (!isActivating) {
                        e.currentTarget.style.background = 'transparent'
                        e.currentTarget.style.borderColor = 'var(--border-accent)'
                    }
                }}
            >
                {isActivating ? 'Activating…' : 'Activate Mentor'}
            </button>
        </div>
    )
}
