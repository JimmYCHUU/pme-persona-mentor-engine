/**
 * SocraticBadge — always visible on mentor messages.
 * DO NOT hide this badge for any reason.
 */

const BADGE_CONFIG = {
    0: { label: 'silent', color: 'var(--socratic-0)' },
    1: { label: 'nudge', color: 'var(--socratic-1)' },
    2: { label: 'hint', color: 'var(--socratic-2)' },
    3: { label: 'critique', color: 'var(--socratic-3)' },
    4: { label: 'reveal', color: 'var(--socratic-4)' },
} as const

export function SocraticBadge({ level }: { level: 0 | 1 | 2 | 3 | 4 }) {
    const config = BADGE_CONFIG[level]

    return (
        <span style={{
            backgroundColor: config.color + '22',
            color: config.color,
            border: `1px solid ${config.color}`,
            borderRadius: 'var(--radius-sm)',
            padding: '1px 6px',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            fontWeight: 500,
        }}>
            {config.label}
        </span>
    )
}
