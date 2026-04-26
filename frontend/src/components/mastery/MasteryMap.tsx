import { useMastery } from '../../hooks/useMastery'
import { ConceptCard } from './ConceptCard'

export function MasteryMap() {
  const { concepts } = useMastery()
  if (concepts.length === 0) {
    return <div>No concepts tracked yet</div>
  }
  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {concepts.map((c) => (
        <ConceptCard key={c.concept_id} concept={c} />
      ))}
    </div>
  )
}
