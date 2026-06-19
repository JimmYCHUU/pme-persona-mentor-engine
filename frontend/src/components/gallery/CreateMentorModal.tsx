/**
 * CreateMentorModal — glassmorphic modal for creating a custom mentor persona.
 * Collects name, field of expertise, description, and teaching tone.
 */

import { useState } from 'react'

interface Props {
    open: boolean
    onClose: () => void
    onCreated: (personaId: string) => void
}

const FIELD_PRESETS = [
    'Data Science', 'Mathematics', 'Physics', 'Finance',
    'Marketing', 'Music Production', 'Philosophy', 'Psychology',
    'Machine Learning', 'DevOps', 'Mobile Development', 'Game Development',
]

const TONE_PRESETS = [
    'Helpful and encouraging',
    'Direct and no-nonsense',
    'Patient and methodical',
    'Energetic and enthusiastic',
    'Calm and Socratic',
    'Witty and playful',
]

export function CreateMentorModal({ open, onClose, onCreated }: Props) {
    const [name, setName] = useState('')
    const [field, setField] = useState('')
    const [description, setDescription] = useState('')
    const [tone, setTone] = useState('Helpful and encouraging')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    if (!open) return null

    const handleCreate = async () => {
        if (!name.trim()) { setError('Name is required'); return }
        if (!field.trim()) { setError('Field of expertise is required'); return }

        setLoading(true)
        setError('')
        try {
            const res = await fetch('http://localhost:8000/persona/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name.trim(),
                    field: field.trim(),
                    description: description.trim(),
                    tone: tone.trim(),
                }),
            })
            const data = await res.json()
            if (data.success) {
                onCreated(data.data.persona_id)
                // Reset form
                setName('')
                setField('')
                setDescription('')
                setTone('Helpful and encouraging')
            } else {
                setError(data.error || 'Failed to create mentor')
            }
        } catch (e) {
            setError('Network error. Is the backend running?')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div
            onClick={onClose}
            style={{
                position: 'fixed', inset: 0,
                background: 'rgba(0,0,0,0.7)',
                backdropFilter: 'blur(8px)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                zIndex: 1000,
                animation: 'fadeIn 0.2s ease',
            }}
        >
            <div
                onClick={e => e.stopPropagation()}
                style={{
                    background: 'var(--bg-raised)',
                    border: '1px solid var(--border-accent)',
                    borderRadius: '16px',
                    padding: '32px',
                    maxWidth: '520px',
                    width: '90%',
                    maxHeight: '85vh',
                    overflow: 'auto',
                    boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
                }}
            >
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                    <h2 style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: '22px',
                        fontWeight: 400,
                        color: 'var(--text-primary)',
                    }}>
                        ✦ Create Custom Mentor
                    </h2>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none', border: 'none',
                            color: 'var(--text-muted)', cursor: 'pointer',
                            fontSize: '20px', padding: '0',
                        }}
                    >✕</button>
                </div>

                {/* Name */}
                <label style={labelStyle}>Mentor Name</label>
                <input
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="e.g. Professor Maxwell, DataSciGuru"
                    style={inputStyle}
                />

                {/* Field */}
                <label style={labelStyle}>Field of Expertise</label>
                <input
                    value={field}
                    onChange={e => setField(e.target.value)}
                    placeholder="e.g. Data Science, Philosophy"
                    style={inputStyle}
                />
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px', marginBottom: '16px' }}>
                    {FIELD_PRESETS.map(f => (
                        <button
                            key={f}
                            onClick={() => setField(f)}
                            style={{
                                padding: '4px 10px',
                                background: field === f ? 'var(--accent-glow)' : 'var(--bg-surface)',
                                border: `1px solid ${field === f ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                                borderRadius: '20px',
                                color: field === f ? 'var(--accent-bright)' : 'var(--text-muted)',
                                fontSize: '11px',
                                cursor: 'pointer',
                                fontFamily: 'var(--font-body)',
                                transition: 'all 0.15s',
                            }}
                        >{f}</button>
                    ))}
                </div>

                {/* Description */}
                <label style={labelStyle}>Description <span style={{ color: 'var(--text-muted)' }}>(optional)</span></label>
                <textarea
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    placeholder="Describe your mentor's background, expertise, and teaching approach..."
                    rows={3}
                    style={{
                        ...inputStyle,
                        resize: 'vertical',
                        minHeight: '80px',
                    }}
                />

                {/* Tone */}
                <label style={labelStyle}>Teaching Tone</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '24px' }}>
                    {TONE_PRESETS.map(t => (
                        <button
                            key={t}
                            onClick={() => setTone(t)}
                            style={{
                                padding: '6px 14px',
                                background: tone === t ? 'var(--accent-glow)' : 'var(--bg-surface)',
                                border: `1px solid ${tone === t ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                                borderRadius: '20px',
                                color: tone === t ? 'var(--accent-bright)' : 'var(--text-muted)',
                                fontSize: '12px',
                                cursor: 'pointer',
                                fontFamily: 'var(--font-body)',
                                transition: 'all 0.15s',
                            }}
                        >{t}</button>
                    ))}
                </div>

                {/* Error */}
                {error && (
                    <p style={{ color: '#ef4444', fontSize: '13px', marginBottom: '12px' }}>
                        ⚠ {error}
                    </p>
                )}

                {/* Create button */}
                <button
                    onClick={handleCreate}
                    disabled={loading}
                    style={{
                        width: '100%',
                        padding: '14px',
                        background: loading
                            ? 'var(--bg-surface)'
                            : 'linear-gradient(135deg, var(--accent-primary), var(--accent-bright))',
                        border: 'none',
                        borderRadius: '12px',
                        color: '#fff',
                        fontSize: '15px',
                        fontWeight: 600,
                        fontFamily: 'var(--font-body)',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s',
                        opacity: loading ? 0.6 : 1,
                    }}
                >
                    {loading ? '⏳ Creating mentor...' : '⚡ Create & Start Chatting'}
                </button>
            </div>
        </div>
    )
}

const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '12px',
    fontWeight: 500,
    color: 'var(--text-secondary)',
    marginBottom: '6px',
    fontFamily: 'var(--font-body)',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
}

const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '10px 14px',
    background: 'var(--bg-surface)',
    border: '1px solid var(--border-default)',
    borderRadius: '8px',
    color: 'var(--text-primary)',
    fontSize: '14px',
    fontFamily: 'var(--font-body)',
    outline: 'none',
    marginBottom: '16px',
    boxSizing: 'border-box',
}
