/**
 * SettingsPage — model selection + persona sliders.
 */

import { useSessionStore } from '../store/sessionStore'
import { usePersonaStore } from '../store/personaStore'
import { SliderPanel } from '../components/persona/SliderPanel'

const FREE_MODELS = [
    { id: 'nvidia/llama-3.1-nemotron-ultra-253b-v1:free', label: 'Nemotron Ultra 253B (free) — Best overall' },
    { id: 'nvidia/llama-3.3-nemotron-super-49b-v1:free', label: 'Nemotron Super 49B (free) — Fast, strong reasoning' },
    { id: 'nvidia/nemotron-3-super-120b-a12b:free', label: 'Nemotron 120B (free) — Current default' },
    { id: 'meta-llama/llama-3.3-70b-instruct:free', label: 'Llama 3.3 70B (free) — Reliable backup' },
    { id: 'ollama/llama3.2:3b', label: 'Llama 3.2 3B — Local (Ollama required)' },
]

export function SettingsPage() {
    const { personaModel, reasoningModel, setModels } = useSessionStore()
    const { activeId, sliders, updateSliders } = usePersonaStore()

    return (
        <div style={{ height: '100%', overflow: 'auto', padding: '32px' }}>
            <h1 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '28px', fontWeight: 400,
                marginBottom: '40px',
            }}>Settings</h1>

            {/* Model selection section */}
            <section style={{ marginBottom: '48px' }}>
                <h2 style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px', letterSpacing: '0.15em',
                    textTransform: 'uppercase',
                    color: 'var(--text-muted)',
                    marginBottom: '20px',
                }}>
                    Model Configuration
                </h2>

                {/* Persona model */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{
                        display: 'block', fontSize: '13px', fontWeight: 500,
                        color: 'var(--text-secondary)', marginBottom: '8px',
                    }}>
                        Persona Model
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 400, marginLeft: '8px' }}>
                            — used for all mentor voice responses
                        </span>
                    </label>
                    <select
                        value={personaModel}
                        onChange={e => setModels({ personaModel: e.target.value })}
                        style={{
                            width: '100%', maxWidth: '480px',
                            padding: '10px 14px',
                            background: 'var(--bg-surface)',
                            border: '1px solid var(--border-default)',
                            borderRadius: '8px',
                            color: 'var(--text-primary)',
                            fontFamily: 'var(--font-body)',
                            fontSize: '14px',
                            cursor: 'pointer',
                            outline: 'none',
                        }}
                    >
                        {FREE_MODELS.map(m => (
                            <option key={m.id} value={m.id}>{m.label}</option>
                        ))}
                    </select>
                </div>

                {/* Reasoning model */}
                <div>
                    <label style={{
                        display: 'block', fontSize: '13px', fontWeight: 500,
                        color: 'var(--text-secondary)', marginBottom: '8px',
                    }}>
                        Reasoning Model
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 400, marginLeft: '8px' }}>
                            — used for Socratic scoring and concept analysis
                        </span>
                    </label>
                    <select
                        value={reasoningModel}
                        onChange={e => setModels({ reasoningModel: e.target.value })}
                        style={{
                            width: '100%', maxWidth: '480px',
                            padding: '10px 14px',
                            background: 'var(--bg-surface)',
                            border: '1px solid var(--border-default)',
                            borderRadius: '8px',
                            color: 'var(--text-primary)',
                            fontFamily: 'var(--font-body)',
                            fontSize: '14px',
                            cursor: 'pointer',
                            outline: 'none',
                        }}
                    >
                        {FREE_MODELS.map(m => (
                            <option key={m.id} value={m.id}>{m.label}</option>
                        ))}
                    </select>
                </div>
            </section>

            {/* Persona sliders section */}
            {activeId && (
                <section>
                    <h2 style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '11px', letterSpacing: '0.15em',
                        textTransform: 'uppercase',
                        color: 'var(--text-muted)',
                        marginBottom: '20px',
                    }}>
                        Active Mentor Behaviour
                    </h2>
                    <SliderPanel sliders={sliders} onChange={updateSliders} />
                </section>
            )}
        </div>
    )
}
