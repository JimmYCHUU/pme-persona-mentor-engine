/** ConceptCard — single concept in the mastery ledger. Stub. */
import type { ConceptEntry } from '../../types'
export function ConceptCard({ concept }: { concept: ConceptEntry }) {
    return (
        <div style={{ padding: '8px', borderBottom: '1px solid var(--glass-border)' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{concept.concept_label}</span>
        </div>
    )
}
