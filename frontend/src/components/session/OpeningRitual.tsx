import { useState, useEffect, useRef } from 'react'

interface Props {
    onComplete: () => void
    mentorName?: string
}

// 16 particles spread radially from orb centre
const PARTICLES = Array.from({ length: 16 }, (_, i) => {
    const angle = (i / 16) * 360 + (Math.random() - 0.5) * 15
    const rad = (angle * Math.PI) / 180
    const dist = 100 + Math.random() * 220
    return {
        id: i,
        dx: `${Math.cos(rad) * dist}px`,
        dy: `${Math.sin(rad) * dist}px`,
        duration: `${2.5 + Math.random() * 3.5}s`,
        delay: `${Math.random() * 1.2}s`,
        size: `${2 + Math.random() * 3}px`,
    }
})

export function OpeningRitual({ onComplete, mentorName = 'Your Mentor' }: Props) {
    const [phase, setPhase] = useState<
        'void' | 'orb' | 'rings' | 'particles' | 'typing' | 'ready' | 'exit'
    >('void')
    const [displayedName, setDisplayedName] = useState('')
    const [displayedSub, setDisplayedSub] = useState('')
    const subtitle = 'Your mentor is present.'
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

    useEffect(() => {
        const t1 = setTimeout(() => setPhase('orb'), 600)
        const t2 = setTimeout(() => setPhase('rings'), 1200)
        const t3 = setTimeout(() => setPhase('particles'), 2200)
        const t4 = setTimeout(() => setPhase('typing'), 3000)
        return () => { [t1, t2, t3, t4].forEach(clearTimeout) }
    }, [])

    // Typewriter: name first, then subtitle
    useEffect(() => {
        if (phase !== 'typing') return
        let i = 0
        timerRef.current = setInterval(() => {
            i++
            setDisplayedName(mentorName.slice(0, i))
            if (i >= mentorName.length) {
                clearInterval(timerRef.current!)
                let j = 0
                const t = setInterval(() => {
                    j++
                    setDisplayedSub(subtitle.slice(0, j))
                    if (j >= subtitle.length) { clearInterval(t); setPhase('ready') }
                }, 38)
            }
        }, 72)
        return () => { if (timerRef.current) clearInterval(timerRef.current) }
    }, [phase, mentorName])

    // Enter key shortcut
    useEffect(() => {
        const fn = (e: KeyboardEvent) => {
            if (e.key === 'Enter' && phase === 'ready') handleEnter()
        }
        window.addEventListener('keydown', fn)
        return () => window.removeEventListener('keydown', fn)
    }, [phase])

    const handleEnter = () => {
        setPhase('exit')
        setTimeout(onComplete, 700)
    }

    const showOrb = phase !== 'void'
    const showRings = ['rings', 'particles', 'typing', 'ready'].includes(phase)
    const showParticles = ['particles', 'typing', 'ready'].includes(phase)
    const showContent = ['typing', 'ready'].includes(phase)

    return (
        <div style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            background: 'var(--bg-void)',
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            overflow: 'hidden',
            opacity: phase === 'exit' ? 0 : 1,
            transition: 'opacity 700ms ease',
        }}>

            {/* ── Orb layers ── */}
            <div style={{
                position: 'absolute', inset: 0,
                opacity: showOrb ? 1 : 0,
                transition: 'opacity 1400ms ease',
                pointerEvents: 'none',
            }}>
                {showRings && <div className="orb-ring-2" />}
                {showRings && <div className="orb-ring-1" />}
                <div className="orb-core" />
            </div>

            {/* ── Particles ── */}
            {showParticles && PARTICLES.map(p => (
                <div
                    key={p.id}
                    className="particle"
                    style={{
                        top: '50%', left: '50%',
                        width: p.size, height: p.size,
                        '--dx': p.dx,
                        '--dy': p.dy,
                        '--duration': p.duration,
                        '--delay': p.delay,
                    } as React.CSSProperties}
                />
            ))}

            {/* ── Text content ── */}
            <div style={{
                position: 'relative', zIndex: 10,
                textAlign: 'center',
                padding: '0 24px',
                maxWidth: '680px',
                opacity: showContent ? 1 : 0,
                transition: 'opacity 800ms ease',
            }}>
                {/* Eyebrow label */}
                <p style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    letterSpacing: '0.25em',
                    textTransform: 'uppercase',
                    color: 'var(--text-muted)',
                    marginBottom: '44px',
                }}>
                    Persona Mentor Engine
                </p>

                {/* Mentor name — Cormorant Garamond with shimmer */}
                <h1 style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: 'clamp(52px, 9vw, 92px)',
                    fontWeight: 300,
                    lineHeight: 1.0,
                    letterSpacing: '-0.015em',
                    minHeight: '1em',
                    marginBottom: '28px',
                }}>
                    <span className="shimmer-text">{displayedName}</span>
                    {phase === 'typing' && <span className="cursor" />}
                </h1>

                {/* Subtitle */}
                <p style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '16px',
                    fontWeight: 300,
                    color: 'var(--text-secondary)',
                    letterSpacing: '0.05em',
                    minHeight: '24px',
                    marginBottom: '60px',
                }}>
                    {displayedSub}
                </p>

                {/* Enter button */}
                <div style={{
                    opacity: phase === 'ready' ? 1 : 0,
                    transform: phase === 'ready' ? 'translateY(0)' : 'translateY(14px)',
                    transition: 'opacity 600ms ease, transform 600ms ease',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '14px',
                }}>
                    <button
                        className="glow"
                        onClick={handleEnter}
                        style={{
                            background: 'transparent',
                            border: '1px solid var(--border-accent)',
                            borderRadius: '10px',
                            padding: '14px 52px',
                            color: 'var(--accent-bright)',
                            fontFamily: 'var(--font-body)',
                            fontSize: '14px',
                            fontWeight: 500,
                            letterSpacing: '0.08em',
                            cursor: 'pointer',
                            transition: 'all var(--t-fast)',
                        }}
                        onMouseEnter={e => {
                            e.currentTarget.style.background = 'var(--accent-glow)'
                            e.currentTarget.style.borderColor = 'var(--accent-bright)'
                        }}
                        onMouseLeave={e => {
                            e.currentTarget.style.background = 'transparent'
                            e.currentTarget.style.borderColor = 'var(--border-accent)'
                        }}
                    >
                        Enter workspace
                    </button>
                    <span style={{
                        fontSize: '11px',
                        color: 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                    }}>
                        press Enter ↵
                    </span>
                </div>
            </div>
        </div>
    )
}
