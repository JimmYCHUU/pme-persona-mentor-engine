/** PersonaCard — displays a persona in the sidebar. Stub. */
import type { PersonaProfile } from '../../types'
export function PersonaCard({ persona }: { persona: PersonaProfile }) {
    return <div style={{ padding: '8px', color: 'var(--text-secondary)' }}>{persona.name}</div>
}
