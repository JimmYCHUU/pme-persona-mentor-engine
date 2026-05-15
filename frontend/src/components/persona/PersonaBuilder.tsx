/**
 * PersonaBuilder — 5-step wizard for creating a mentor persona.
 *
 * Step 1: Identity (name + handles + domain)
 * Step 2: Public Sources (YouTube/social URLs)
 * Step 3: Private Vault (drag-and-drop file upload)
 * Step 4: Ingestion Progress (live polling)
 * Step 5: Personality Calibration (sliders + gap-fill)
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { usePersonaStore } from '../../store/personaStore'

const API = 'http://localhost:8000'

export function PersonaBuilder() {
    const [step, setStep] = useState(1)
    const [personaId, setPersonaId] = useState<string | null>(null)
    const [identity, setIdentity] = useState({
        name: '', youtubeChannel: '', twitterHandle: '',
        linkedinUrl: '', domain: '',
    })
    const [sources, setSources] = useState<string[]>([])
    const [sourceInput, setSourceInput] = useState('')
    const [vaultFiles, setVaultFiles] = useState<File[]>([])
    const [ingestionStatus, setIngestionStatus] = useState<string>('pending')
    const [ingestionFiles, setIngestionFiles] = useState<string[]>([])
    const [gapFillAnswers, setGapFillAnswers] = useState<Record<string, string>>({})
    const [sliders, setSliders] = useState({ abrasiveness: 50, proactivity: 50, explainDepth: 50 })
    const [loading, setLoading] = useState(false)
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

    // Step 1 → 2: Create pending persona
    const handleStep1Next = async () => {
        if (!identity.name.trim()) return
        setLoading(true)
        try {
            const res = await fetch(`${API}/persona/create-pending`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: identity.name, domain: identity.domain }),
            })
            const { data } = await res.json()
            setPersonaId(data.persona_id)
            setStep(2)
        } catch (e) { console.error(e) }
        setLoading(false)
    }

    // Add source URL
    const addSource = () => {
        const url = sourceInput.trim()
        if (url && !sources.includes(url)) {
            setSources([...sources, url])
            setSourceInput('')
        }
    }

    // Step 3 → 4: Begin ingestion
    const handleBeginIngestion = async () => {
        setStep(4)
        setLoading(true)

        // Trigger fingerprint ingestion for each source
        for (const url of sources) {
            try {
                await fetch(`${API}/ingest/fingerprint`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, persona_id: personaId }),
                })
            } catch { /* continue */ }
        }

        // Trigger vault ingestion for each file
        for (const file of vaultFiles) {
            const formData = new FormData()
            formData.append('file', file)
            formData.append('persona_id', personaId!)
            try {
                await fetch(`${API}/ingest/vault`, {
                    method: 'POST',
                    body: formData,
                })
            } catch { /* continue */ }
        }

        setLoading(false)
        startPolling()
    }

    // Poll ingestion status
    const startPolling = useCallback(() => {
        if (pollRef.current) clearInterval(pollRef.current)
        pollRef.current = setInterval(async () => {
            try {
                const res = await fetch(`${API}/ingest/status/${personaId}`)
                const { data } = await res.json()
                setIngestionStatus(data.status)
                setIngestionFiles(data.files_uploaded || [])
                if (data.status === 'done') {
                    if (pollRef.current) clearInterval(pollRef.current)
                }
            } catch { /* retry */ }
        }, 2000)
    }, [personaId])

    useEffect(() => {
        return () => { if (pollRef.current) clearInterval(pollRef.current) }
    }, [])

    // Step 5: Activate persona
    const handleActivate = async () => {
        setLoading(true)
        try {
            await fetch(`${API}/persona/${personaId}/activate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sliders, gap_fill_answers: gapFillAnswers }),
            })
            await usePersonaStore.getState().loadPersonas()
            usePersonaStore.getState().setActive(personaId!)
        } catch (e) { console.error(e) }
        setLoading(false)
    }

    // File drop handler
    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        const files = Array.from(e.dataTransfer.files)
        setVaultFiles(prev => [...prev, ...files])
    }

    const GAP_FILL_QUESTIONS = [
        'How does this person typically react when a student gets something wrong?',
        'What phrases or expressions do they use frequently?',
        'How do they explain complex topics — step by step, analogies, or examples?',
    ]

    return (
        <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            overflow: 'auto', padding: '40px 32px',
        }}>
            {/* Progress bar */}
            <div style={{ marginBottom: '40px' }}>
                <div style={{
                    display: 'flex', justifyContent: 'space-between', marginBottom: '8px',
                }}>
                    {[1, 2, 3, 4, 5].map(s => (
                        <span key={s} style={{
                            fontSize: '11px',
                            fontFamily: 'var(--font-mono)',
                            color: s <= step ? 'var(--accent-bright)' : 'var(--text-muted)',
                            fontWeight: s === step ? 600 : 400,
                        }}>
                            {['Identity', 'Sources', 'Vault', 'Ingesting', 'Calibrate'][s - 1]}
                        </span>
                    ))}
                </div>
                <div style={{
                    height: '3px', background: 'var(--bg-overlay)', borderRadius: '2px',
                }}>
                    <div style={{
                        height: '100%', width: `${(step / 5) * 100}%`,
                        background: 'var(--accent)', borderRadius: '2px',
                        transition: 'width var(--t-normal)',
                    }} />
                </div>
            </div>

            {/* Step 1: Identity */}
            {step === 1 && (
                <div style={{ maxWidth: '480px' }}>
                    <h2 style={headingStyle}>Who is your mentor?</h2>
                    <p style={subtitleStyle}>Enter their real identity. We'll use this to find their public content.</p>

                    <InputField label="Full Name *" value={identity.name}
                        onChange={v => setIdentity({ ...identity, name: v })} placeholder="e.g. NetworkChuck" />
                    <InputField label="YouTube Channel URL" value={identity.youtubeChannel}
                        onChange={v => setIdentity({ ...identity, youtubeChannel: v })} placeholder="https://youtube.com/@networkchuck" />
                    <InputField label="Twitter/X Handle" value={identity.twitterHandle}
                        onChange={v => setIdentity({ ...identity, twitterHandle: v })} placeholder="@networkchuck" />
                    <InputField label="LinkedIn URL" value={identity.linkedinUrl}
                        onChange={v => setIdentity({ ...identity, linkedinUrl: v })} placeholder="https://linkedin.com/in/..." />
                    <InputField label="Domain/Expertise" value={identity.domain}
                        onChange={v => setIdentity({ ...identity, domain: v })} placeholder="e.g. networking, cybersecurity" />

                    <WizardButton onClick={handleStep1Next} disabled={!identity.name.trim() || loading}>
                        {loading ? 'Creating…' : 'Next →'}
                    </WizardButton>
                </div>
            )}

            {/* Step 2: Public Sources */}
            {step === 2 && (
                <div style={{ maxWidth: '520px' }}>
                    <h2 style={headingStyle}>Public Sources</h2>
                    <p style={subtitleStyle}>Add YouTube videos or social media URLs from this person. At least 1 required.</p>

                    <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                        <input
                            value={sourceInput}
                            onChange={e => setSourceInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && addSource()}
                            placeholder="Paste a YouTube or social URL…"
                            style={inputStyle}
                        />
                        <button onClick={addSource} style={{
                            ...btnBaseStyle, padding: '10px 16px', flexShrink: 0,
                        }}>Add</button>
                    </div>

                    {sources.map((url, i) => (
                        <div key={i} style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            padding: '10px 14px', marginBottom: '8px',
                            background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)',
                            borderRadius: '8px', fontSize: '13px', color: 'var(--text-secondary)',
                        }}>
                            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
                                {url}
                            </span>
                            <button onClick={() => setSources(sources.filter((_, j) => j !== i))} style={{
                                background: 'none', border: 'none', color: 'var(--danger)',
                                cursor: 'pointer', fontSize: '14px', marginLeft: '8px',
                            }}>✕</button>
                        </div>
                    ))}

                    <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                        <WizardButton onClick={() => setStep(1)} ghost>← Back</WizardButton>
                        <WizardButton onClick={() => setStep(3)} disabled={sources.length === 0}>
                            Next →
                        </WizardButton>
                    </div>
                </div>
            )}

            {/* Step 3: Private Vault */}
            {step === 3 && (
                <div style={{ maxWidth: '520px' }}>
                    <h2 style={headingStyle}>Private Vault</h2>
                    <p style={subtitleStyle}>Drag & drop course files, PDFs, or notes. These never leave your machine. Optional.</p>

                    <div
                        onDrop={handleDrop}
                        onDragOver={e => e.preventDefault()}
                        style={{
                            padding: '40px', textAlign: 'center',
                            border: '2px dashed var(--border-default)', borderRadius: '12px',
                            background: 'var(--bg-surface)', marginBottom: '16px',
                            color: 'var(--text-muted)', fontSize: '14px', cursor: 'pointer',
                        }}
                        onClick={() => {
                            const input = document.createElement('input')
                            input.type = 'file'
                            input.multiple = true
                            input.accept = '.pdf,.mp4,.mp3,.docx,.txt'
                            input.onchange = () => {
                                if (input.files) setVaultFiles(prev => [...prev, ...Array.from(input.files!)])
                            }
                            input.click()
                        }}
                    >
                        Drop files here or click to browse
                        <br />
                        <span style={{ fontSize: '11px', color: 'var(--text-disabled)' }}>
                            PDF, MP4, MP3, DOCX, TXT
                        </span>
                    </div>

                    {vaultFiles.map((f, i) => (
                        <div key={i} style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            padding: '8px 14px', marginBottom: '6px',
                            background: 'var(--bg-raised)', borderRadius: '8px',
                            fontSize: '13px', color: 'var(--text-secondary)',
                        }}>
                            <span>{f.name}</span>
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                {(f.size / 1024 / 1024).toFixed(1)} MB
                            </span>
                        </div>
                    ))}

                    <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                        <WizardButton onClick={() => setStep(2)} ghost>← Back</WizardButton>
                        <WizardButton onClick={() => vaultFiles.length === 0 && sources.length > 0 ? handleBeginIngestion() : handleBeginIngestion()}>
                            {vaultFiles.length === 0 ? 'Skip & Ingest Sources →' : 'Begin Ingestion →'}
                        </WizardButton>
                    </div>
                </div>
            )}

            {/* Step 4: Ingestion Progress */}
            {step === 4 && (
                <div style={{ maxWidth: '520px' }}>
                    <h2 style={headingStyle}>Ingesting Materials</h2>
                    <p style={subtitleStyle}>Building your mentor's knowledge base…</p>

                    {/* Sources */}
                    {sources.map((url, i) => (
                        <ProgressRow key={`s-${i}`} label={url} status={ingestionStatus === 'done' ? 'done' : 'processing'} />
                    ))}

                    {/* Files */}
                    {ingestionFiles.map((f, i) => (
                        <ProgressRow key={`f-${i}`} label={f} status="done" />
                    ))}
                    {vaultFiles.filter(f => !ingestionFiles.includes(f.name)).map((f, i) => (
                        <ProgressRow key={`p-${i}`} label={f.name} status="processing" />
                    ))}

                    {loading && (
                        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '16px' }}>
                            Uploading files…
                        </p>
                    )}

                    <WizardButton
                        onClick={() => setStep(5)}
                        disabled={ingestionStatus === 'pending' && !loading}
                        style={{ marginTop: '24px' }}
                    >
                        Continue to Calibration →
                    </WizardButton>
                </div>
            )}

            {/* Step 5: Personality Calibration */}
            {step === 5 && (
                <div style={{ maxWidth: '520px' }}>
                    <h2 style={headingStyle}>Personality Calibration</h2>
                    <p style={subtitleStyle}>Help us fill the gaps. Answer what you know — these shape how your mentor behaves.</p>

                    {GAP_FILL_QUESTIONS.map((q, i) => (
                        <div key={i} style={{ marginBottom: '20px' }}>
                            <label style={{
                                display: 'block', fontSize: '13px', fontWeight: 500,
                                color: 'var(--text-secondary)', marginBottom: '6px',
                            }}>{q}</label>
                            <textarea
                                value={gapFillAnswers[`q${i}`] || ''}
                                onChange={e => setGapFillAnswers({ ...gapFillAnswers, [`q${i}`]: e.target.value })}
                                placeholder="Type your answer…"
                                style={{
                                    ...inputStyle, minHeight: '60px', resize: 'vertical',
                                    fontFamily: 'var(--font-body)',
                                }}
                            />
                        </div>
                    ))}

                    <h3 style={{
                        fontFamily: 'var(--font-mono)', fontSize: '11px',
                        letterSpacing: '0.15em', textTransform: 'uppercase',
                        color: 'var(--text-muted)', margin: '28px 0 16px',
                    }}>Behaviour Sliders</h3>

                    {(['abrasiveness', 'proactivity', 'explainDepth'] as const).map(key => (
                        <div key={key} style={{ marginBottom: '16px' }}>
                            <div style={{
                                display: 'flex', justifyContent: 'space-between', marginBottom: '4px',
                            }}>
                                <span style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                                    {key.replace(/([A-Z])/g, ' $1')}
                                </span>
                                <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                                    {sliders[key]}
                                </span>
                            </div>
                            <input
                                type="range" min={0} max={100}
                                value={sliders[key]}
                                onChange={e => setSliders({ ...sliders, [key]: Number(e.target.value) })}
                                style={{ width: '100%', accentColor: 'var(--accent)' }}
                            />
                        </div>
                    ))}

                    <div style={{ display: 'flex', gap: '12px', marginTop: '28px' }}>
                        <WizardButton onClick={() => setStep(4)} ghost>← Back</WizardButton>
                        <WizardButton onClick={handleActivate} disabled={loading}>
                            {loading ? 'Activating…' : 'Activate Mentor ✦'}
                        </WizardButton>
                    </div>
                </div>
            )}
        </div>
    )
}

/* ── Shared styles ── */

const headingStyle: React.CSSProperties = {
    fontFamily: 'var(--font-display)', fontSize: '28px', fontWeight: 400,
    marginBottom: '8px',
}

const subtitleStyle: React.CSSProperties = {
    fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '28px', lineHeight: 1.6,
}

const inputStyle: React.CSSProperties = {
    width: '100%', padding: '10px 14px',
    background: 'var(--bg-surface)', border: '1px solid var(--border-default)',
    borderRadius: '8px', color: 'var(--text-primary)',
    fontFamily: 'var(--font-body)', fontSize: '14px', outline: 'none',
}

const btnBaseStyle: React.CSSProperties = {
    background: 'var(--accent-glow)', border: '1px solid var(--border-accent)',
    borderRadius: '8px', color: 'var(--accent-bright)',
    fontFamily: 'var(--font-body)', fontSize: '13px', fontWeight: 500,
    cursor: 'pointer', transition: 'all var(--t-fast)',
}

/* ── Sub-components ── */

function InputField({ label, value, onChange, placeholder }: {
    label: string; value: string; onChange: (v: string) => void; placeholder?: string
}) {
    return (
        <div style={{ marginBottom: '16px' }}>
            <label style={{
                display: 'block', fontSize: '13px', fontWeight: 500,
                color: 'var(--text-secondary)', marginBottom: '6px',
            }}>{label}</label>
            <input
                value={value} onChange={e => onChange(e.target.value)}
                placeholder={placeholder} style={inputStyle}
            />
        </div>
    )
}

function WizardButton({ children, onClick, disabled, ghost, style }: {
    children: React.ReactNode; onClick: () => void; disabled?: boolean
    ghost?: boolean; style?: React.CSSProperties
}) {
    return (
        <button
            onClick={onClick} disabled={disabled}
            style={{
                padding: '12px 28px',
                background: ghost ? 'transparent' : 'var(--accent-glow)',
                border: ghost ? '1px solid var(--border-default)' : '1px solid var(--border-accent)',
                borderRadius: '10px',
                color: ghost ? 'var(--text-secondary)' : 'var(--accent-bright)',
                fontFamily: 'var(--font-body)', fontSize: '14px', fontWeight: 500,
                cursor: disabled ? 'not-allowed' : 'pointer',
                opacity: disabled ? 0.5 : 1,
                transition: 'all var(--t-fast)', letterSpacing: '0.03em',
                ...style,
            }}
        >
            {children}
        </button>
    )
}

function ProgressRow({ label, status }: { label: string; status: 'queued' | 'processing' | 'done' | 'error' }) {
    const colors = { queued: 'var(--text-muted)', processing: 'var(--info)', done: 'var(--success)', error: 'var(--danger)' }
    const icons = { queued: '○', processing: '◌', done: '✓', error: '✕' }
    return (
        <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '10px 14px', marginBottom: '6px',
            background: 'var(--bg-raised)', borderRadius: '8px',
            fontSize: '13px',
        }}>
            <span style={{ color: colors[status], fontSize: '14px' }}>{icons[status]}</span>
            <span style={{ flex: 1, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {label.split('/').pop()}
            </span>
            <span style={{
                fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.1em',
                color: colors[status], fontFamily: 'var(--font-mono)',
            }}>
                {status}
            </span>
        </div>
    )
}
