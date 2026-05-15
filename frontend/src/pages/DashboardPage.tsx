/**
 * DashboardPage — 3 tabs: Mastery Map, Session Journal, Mentor Profile.
 */

import { useState } from 'react'
import { MasteryMap } from '../components/mastery/MasteryMap'
import { usePersonaStore } from '../store/personaStore'

type Tab = 'mastery' | 'journal' | 'profile'

const TABS: { key: Tab; label: string }[] = [
    { key: 'mastery', label: 'Mastery Map' },
    { key: 'journal', label: 'Session Journal' },
    { key: 'profile', label: 'Mentor Profile' },
]

export function DashboardPage() {
    const [tab, setTab] = useState<Tab>('mastery')
    const { activePersona } = usePersonaStore()

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <div style={{
                padding: '24px 32px 0',
                borderBottom: '1px solid var(--border-subtle)',
                background: 'var(--bg-surface)',
            }}>
                <h1 style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '28px', fontWeight: 400,
                    color: 'var(--text-primary)',
                    marginBottom: '20px',
                }}>
                    Dashboard
                </h1>
                {/* Tab bar */}
                <div style={{ display: 'flex', gap: '0' }}>
                    {TABS.map(t => (
                        <button
                            key={t.key}
                            onClick={() => setTab(t.key)}
                            style={{
                                padding: '10px 20px',
                                background: 'transparent',
                                border: 'none',
                                borderBottom: tab === t.key
                                    ? '2px solid var(--accent)'
                                    : '2px solid transparent',
                                color: tab === t.key ? 'var(--accent-bright)' : 'var(--text-muted)',
                                fontFamily: 'var(--font-body)',
                                fontSize: '13px',
                                fontWeight: 500,
                                cursor: 'pointer',
                                transition: 'all var(--t-fast)',
                                letterSpacing: '0.03em',
                            }}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab content */}
            <div style={{ flex: 1, overflow: 'auto', padding: '32px' }}>
                {tab === 'mastery' && <MasteryMapTab />}
                {tab === 'journal' && <SessionJournalTab />}
                {tab === 'profile' && <MentorProfileTab />}
            </div>
        </div>
    )
}

function MasteryMapTab() {
    const { activePersona } = usePersonaStore()
    if (!activePersona) {
        return <EmptyState text="Select a mentor first to see mastery data." />
    }
    return <MasteryMap personaId={activePersona.persona_id} />
}

function SessionJournalTab() {
    return (
        <div style={{
            display: 'flex', flexDirection: 'column', gap: '16px',
        }}>
            <EmptyState text="Session journal coming soon — each session will appear here with timestamps, concept coverage, and Socratic level progression." />
        </div>
    )
}

function MentorProfileTab() {
    const { activePersona } = usePersonaStore()
    if (!activePersona) {
        return <EmptyState text="No mentor selected." />
    }
    return (
        <div style={{
            display: 'flex', flexDirection: 'column', gap: '20px',
            maxWidth: '520px',
        }}>
            <div style={{
                padding: '24px',
                background: 'var(--bg-raised)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
            }}>
                <h2 style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '24px', fontWeight: 400,
                    marginBottom: '12px',
                }}>
                    {activePersona.name}
                </h2>
                <p style={{
                    fontSize: '14px',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.7,
                }}>
                    {activePersona.description || 'No description provided.'}
                </p>
            </div>
        </div>
    )
}

function EmptyState({ text }: { text: string }) {
    return (
        <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            minHeight: '200px', color: 'var(--text-muted)',
            fontSize: '14px', fontStyle: 'italic',
        }}>
            {text}
        </div>
    )
}
