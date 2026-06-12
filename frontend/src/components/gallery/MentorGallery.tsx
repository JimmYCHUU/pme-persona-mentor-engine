/**
 * MentorGallery — category-based mentor browsing with filtering.
 * Displays 8 category tabs, a grid of MentorCards, and a profile modal.
 */

import { useState, useEffect } from 'react'
import { MentorCard } from './MentorCard'
import { MentorProfileModal } from './MentorProfileModal'
import { getCategories, getCategoryMentors, activateMentor } from '../../api/client'
import type { MentorCategory, MentorProfile } from '../../types'

interface Props {
    onMentorActivated?: (personaId: string, mentorName: string) => void
}

export function MentorGallery({ onMentorActivated }: Props) {
    const [categories, setCategories] = useState<MentorCategory[]>([])
    const [activeCategory, setActiveCategory] = useState<string | null>(null)
    const [mentors, setMentors] = useState<MentorProfile[]>([])
    const [loading, setLoading] = useState(true)
    const [activatingId, setActivatingId] = useState<string | null>(null)
    const [selectedMentor, setSelectedMentor] = useState<MentorProfile | null>(null)

    // Load categories on mount
    useEffect(() => {
        (async () => {
            try {
                const res = await getCategories()
                if (res.success && res.data) {
                    setCategories(res.data as MentorCategory[])
                    if ((res.data as MentorCategory[]).length > 0) {
                        setActiveCategory((res.data as MentorCategory[])[0].id)
                    }
                }
            } catch { /* silent */ }
            setLoading(false)
        })()
    }, [])

    // Load mentors when category changes
    useEffect(() => {
        if (!activeCategory) return
        setLoading(true)
            ; (async () => {
                try {
                    const res = await getCategoryMentors(activeCategory)
                    if (res.success && res.data) {
                        setMentors(res.data as MentorProfile[])
                    }
                } catch { /* silent */ }
                setLoading(false)
            })()
    }, [activeCategory])

    const handleActivate = async (category: string, mentorId: string) => {
        setActivatingId(mentorId)
        try {
            const res = await activateMentor(category, mentorId)
            if (res.success && res.data) {
                const data = res.data as { persona_id: string; mentor_name: string }
                setSelectedMentor(null) // Close modal
                onMentorActivated?.(data.persona_id, data.mentor_name)
            }
        } catch { /* silent */ }
        setActivatingId(null)
    }

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Category tabs */}
            <div style={{
                display: 'flex', gap: '4px', padding: '0 32px',
                overflowX: 'auto',
                borderBottom: '1px solid var(--border-subtle)',
                background: 'var(--bg-surface)',
                flexShrink: 0,
            }}>
                {categories.map(cat => {
                    const active = activeCategory === cat.id
                    return (
                        <button
                            key={cat.id}
                            onClick={() => setActiveCategory(cat.id)}
                            style={{
                                padding: '12px 16px',
                                background: 'transparent',
                                border: 'none',
                                borderBottom: active
                                    ? '2px solid var(--accent-bright)'
                                    : '2px solid transparent',
                                color: active ? 'var(--accent-bright)' : 'var(--text-muted)',
                                fontFamily: 'var(--font-body)',
                                fontSize: '13px',
                                fontWeight: active ? 500 : 400,
                                cursor: 'pointer',
                                transition: 'all var(--t-fast)',
                                whiteSpace: 'nowrap',
                                display: 'flex', alignItems: 'center', gap: '6px',
                            }}
                            onMouseEnter={e => {
                                if (!active) e.currentTarget.style.color = 'var(--text-secondary)'
                            }}
                            onMouseLeave={e => {
                                if (!active) e.currentTarget.style.color = 'var(--text-muted)'
                            }}
                        >
                            <span>{cat.emoji}</span>
                            <span>{cat.label}</span>
                            <span style={{
                                fontSize: '10px',
                                padding: '1px 5px',
                                borderRadius: '4px',
                                background: active ? 'var(--accent-glow)' : 'var(--bg-overlay)',
                                color: active ? 'var(--accent-bright)' : 'var(--text-muted)',
                                fontFamily: 'var(--font-mono)',
                            }}>
                                {cat.mentor_count}
                            </span>
                        </button>
                    )
                })}
            </div>

            {/* Mentor grid */}
            <div style={{
                flex: 1, overflow: 'auto',
                padding: '24px 32px',
            }}>
                {loading ? (
                    <div style={{
                        display: 'flex', justifyContent: 'center',
                        padding: '64px 0', color: 'var(--text-muted)',
                    }}>
                        <div style={{
                            width: '24px', height: '24px',
                            border: '2px solid var(--border-default)',
                            borderTopColor: 'var(--accent)',
                            borderRadius: '50%',
                            animation: 'spin 0.8s linear infinite',
                        }} />
                    </div>
                ) : (
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                        gap: '16px',
                    }}>
                        {mentors.map(m => (
                            <MentorCard
                                key={m.id}
                                mentor={m}
                                category={activeCategory || ''}
                                onActivate={handleActivate}
                                onCardClick={setSelectedMentor}
                                isActivating={activatingId === m.id}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Profile Modal */}
            {selectedMentor && (
                <MentorProfileModal
                    mentor={selectedMentor}
                    category={activeCategory || ''}
                    onClose={() => setSelectedMentor(null)}
                    onActivate={handleActivate}
                    isActivating={activatingId === selectedMentor.id}
                />
            )}
        </div>
    )
}
