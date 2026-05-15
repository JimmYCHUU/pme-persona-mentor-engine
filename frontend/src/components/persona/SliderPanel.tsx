/** SliderPanel — persona behaviour sliders: Abrasiveness, Proactivity, Explain Depth. */

interface Sliders {
    abrasiveness: number
    proactivity: number
    explainDepth: number
}

interface Props {
    sliders: Sliders
    onChange: (s: Partial<Sliders>) => void
}

const SLIDER_DEFS = [
    { key: 'abrasiveness' as const, label: 'Abrasiveness', desc: 'How blunt or gentle the mentor is' },
    { key: 'proactivity' as const, label: 'Proactivity', desc: 'How often the mentor interrupts unprompted' },
    { key: 'explainDepth' as const, label: 'Explain Depth', desc: 'How detailed the explanations are' },
]

export function SliderPanel({ sliders, onChange }: Props) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '400px' }}>
            {SLIDER_DEFS.map(s => (
                <div key={s.key}>
                    <div style={{
                        display: 'flex', justifyContent: 'space-between',
                        marginBottom: '6px',
                    }}>
                        <label style={{
                            fontSize: '13px', fontWeight: 500,
                            color: 'var(--text-secondary)',
                        }}>
                            {s.label}
                        </label>
                        <span style={{
                            fontSize: '12px', fontFamily: 'var(--font-mono)',
                            color: 'var(--text-muted)',
                        }}>
                            {sliders[s.key]}
                        </span>
                    </div>
                    <input
                        type="range"
                        min={0}
                        max={100}
                        value={sliders[s.key]}
                        onChange={e => onChange({ [s.key]: Number(e.target.value) })}
                        style={{
                            width: '100%',
                            accentColor: 'var(--accent)',
                            cursor: 'pointer',
                        }}
                    />
                    <p style={{
                        fontSize: '11px',
                        color: 'var(--text-muted)',
                        marginTop: '4px',
                    }}>
                        {s.desc}
                    </p>
                </div>
            ))}
        </div>
    )
}
