import type { ConceptEntry } from '../../types'

export function ConceptCard({ concept }: { concept: ConceptEntry }) {
  return (
    <div style={{ border: '1px solid var(--bg-overlay)', borderRadius: 8, padding: 10 }}>
      <strong>{concept.concept_label}</strong>
      <div style={{ marginTop: 6, height: 8, background: 'var(--bg-overlay)', borderRadius: 999 }}>
        <div style={{ width: `${Math.round(concept.mastery_score * 100)}%`, height: 8, background: 'var(--accent)', borderRadius: 999 }} />
      </div>
      <span style={{ color: `var(--mastery-${concept.status})` }}>{concept.status}</span>
    </div>
  )
}
