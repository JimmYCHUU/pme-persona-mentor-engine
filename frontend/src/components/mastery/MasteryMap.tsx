/** MasteryMap — mastery ledger view with concept cards. */

import { useEffect } from 'react'
import { useMastery } from '../../hooks/useMastery'

interface Props {
    personaId: string
}

const STATUS_COLORS: Record<string, string> = {
    encountered: 'var(--mastery-encountered)',
    attempted: 'var(--mastery-attempted)',
    struggling: 'var(--mastery-struggling)',
    mastered: 'var(--mastery-mastered)',
}

export function MasteryMap({ personaId }: Props) {
    const { concepts, loadLedger } = useMastery()

    useEffect(() => {
        loadLedger(personaId)
    }, [personaId, loadLedger])

    if (concepts.length === 0) {
        return (
            <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                minHeight: '200px', color: 'var(--text-muted)',
                fontSize: '14px', fontStyle: 'italic',
            }}>
                No concepts tracked yet. Start a conversation to build your mastery map.
            </div>
        )
    }

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '12px',
        }}>
            {concepts.map((c: any) => (
                <div key={c.concept_key} style={{
                    padding: '16px',
                    background: 'var(--bg-raised)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '10px',
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)' }}>
                            {c.concept_key.replace(/_/g, ' ')}
                        </span>
                        <span style={{
                            fontSize: '10px',
                            padding: '2px 8px',
                            borderRadius: '999px',
                            background: STATUS_COLORS[c.status] || 'var(--text-muted)',
                            color: 'var(--bg-base)',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                        }}>
                            {c.status}
                        </span>
                    </div>
                    {/* Score bar */}
                    <div style={{
                        height: '4px',
                        background: 'var(--bg-overlay)',
                        borderRadius: '2px',
                        overflow: 'hidden',
                    }}>
                        <div style={{
                            height: '100%',
                            width: `${(c.score ?? 0) * 100}%`,
                            background: STATUS_COLORS[c.status] || 'var(--accent)',
                            borderRadius: '2px',
                            transition: 'width var(--t-normal)',
                        }} />
                    </div>
                </div>
            ))}
        </div>
    )
}
