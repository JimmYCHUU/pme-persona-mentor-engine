/**
 * PersonaBuilder — multi-step wizard for creating a persona.
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { usePersona } from '../../hooks/usePersona'

export function PersonaBuilder() {
    const { create } = usePersona()
    const [step, setStep] = useState(0)
    const [name, setName] = useState('')
    const [description, setDescription] = useState('')
    const [abrasiveness, setAbrasiveness] = useState(50)
    const [proactivity, setProactivity] = useState(50)
    const [explainDepth, setExplainDepth] = useState(50)
    const [isCreating, setIsCreating] = useState(false)

    const steps = [
        { title: 'Name Your Mentor', subtitle: 'Who is the expert you want to learn from?' },
        { title: 'Describe Their Expertise', subtitle: 'What makes them unique?' },
        { title: 'Set Communication Style', subtitle: 'How should they interact with you?' },
    ]

    const handleComplete = async () => {
        setIsCreating(true)
        await create({
            name,
            description,
            sliders: { abrasiveness, proactivity, explainDepth },
        })
        setIsCreating(false)
    }

    const canNext = step === 0 ? name.trim().length > 0 : true
    const isLast = step === steps.length - 1

    return (
        <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '32px',
        }}>
            <motion.div
                className="glass-card"
                style={{
                    maxWidth: '500px',
                    width: '100%',
                    padding: '32px',
                }}
            >
                {/* Progress dots */}
                <div style={{
                    display: 'flex',
                    gap: '8px',
                    justifyContent: 'center',
                    marginBottom: '24px',
                }}>
                    {steps.map((_, i) => (
                        <span key={i} style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            background: i <= step ? 'var(--accent)' : 'var(--bg-overlay)',
                            transition: 'background var(--transition-normal)',
                        }} />
                    ))}
                </div>

                <AnimatePresence mode="wait">
                    <motion.div
                        key={step}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                    >
                        <h2 style={{
                            fontFamily: 'var(--font-heading)',
                            color: 'var(--text-heading)',
                            fontSize: '1.3rem',
                            marginBottom: '4px',
                        }}>
                            {steps[step].title}
                        </h2>
                        <p style={{
                            color: 'var(--text-muted)',
                            fontSize: '0.85rem',
                            marginBottom: '20px',
                        }}>
                            {steps[step].subtitle}
                        </p>

                        {/* Step 0: Name */}
                        {step === 0 && (
                            <input
                                className="input"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="e.g. Network Chuck, John Carmack"
                                style={{ width: '100%' }}
                                autoFocus
                            />
                        )}

                        {/* Step 1: Description */}
                        {step === 1 && (
                            <textarea
                                className="input"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="e.g. A cybersecurity expert who teaches with coffee metaphors and blunt humor..."
                                rows={4}
                                style={{ width: '100%', resize: 'none' }}
                                autoFocus
                            />
                        )}

                        {/* Step 2: Sliders */}
                        {step === 2 && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                <SliderField
                                    label="Abrasiveness"
                                    value={abrasiveness}
                                    onChange={setAbrasiveness}
                                    leftLabel="Gentle"
                                    rightLabel="Drill Sergeant"
                                />
                                <SliderField
                                    label="Proactivity"
                                    value={proactivity}
                                    onChange={setProactivity}
                                    leftLabel="Silent"
                                    rightLabel="Interrupts"
                                />
                                <SliderField
                                    label="Explain Depth"
                                    value={explainDepth}
                                    onChange={setExplainDepth}
                                    leftLabel="Just do it"
                                    rightLabel="Deep theory"
                                />
                            </div>
                        )}
                    </motion.div>
                </AnimatePresence>

                {/* Navigation buttons */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginTop: '24px',
                    gap: '12px',
                }}>
                    <button
                        className="btn btn-ghost"
                        onClick={() => setStep(s => Math.max(0, s - 1))}
                        disabled={step === 0}
                        style={{ opacity: step === 0 ? 0.3 : 1 }}
                    >
                        Back
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={isLast ? handleComplete : () => setStep(s => s + 1)}
                        disabled={!canNext || isCreating}
                    >
                        {isCreating ? 'Creating...' : isLast ? 'Create Mentor' : 'Next'}
                    </button>
                </div>
            </motion.div>
        </div>
    )
}

function SliderField({ label, value, onChange, leftLabel, rightLabel }: {
    label: string
    value: number
    onChange: (v: number) => void
    leftLabel: string
    rightLabel: string
}) {
    return (
        <div>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
            }}>
                <span style={{
                    fontSize: '0.8rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-secondary)',
                }}>{label}</span>
                <span style={{
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--accent)',
                }}>{value}</span>
            </div>
            <input
                type="range"
                min={0}
                max={100}
                value={value}
                onChange={(e) => onChange(Number(e.target.value))}
                style={{
                    width: '100%',
                    accentColor: 'var(--accent)',
                }}
            />
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.65rem',
                color: 'var(--text-muted)',
                marginTop: '2px',
            }}>
                <span>{leftLabel}</span>
                <span>{rightLabel}</span>
            </div>
        </div>
    )
}
