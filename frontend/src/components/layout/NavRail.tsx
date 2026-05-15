/**
 * NavRail — 64px vertical icon rail for workspace navigation.
 */

import { useSessionStore } from '../../store/sessionStore'

const NAV_ITEMS = [
    { icon: '◈', label: 'Session', path: '/' },
    { icon: '⬡', label: 'Dashboard', path: '/dashboard' },
    { icon: '◉', label: 'Mentors', path: '/mentors' },
    { icon: '◫', label: 'Settings', path: '/settings' },
]

interface Props {
    activePath: string
    onNavigate: (path: string) => void
}

export function NavRail({ activePath, onNavigate }: Props) {
    const { isOllamaOnline, isOpenRouterOnline } = useSessionStore()

    const isOnline = isOpenRouterOnline || isOllamaOnline
    const provider = isOpenRouterOnline ? 'OR' : isOllamaOnline ? 'OL' : '✕'

    return (
        <nav className="nav-rail" style={{
            width: 'var(--nav-w)',
            height: '100%',
            background: 'var(--bg-surface)',
            borderRight: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            padding: '16px 0',
            flexShrink: 0,
            zIndex: 10,
        }}>
            {/* Logo */}
            <div style={{
                width: '36px', height: '36px',
                borderRadius: '10px',
                background: 'var(--accent-glow)',
                border: '1px solid var(--border-accent)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontFamily: 'var(--font-display)',
                fontSize: '18px',
                color: 'var(--accent-bright)',
                marginBottom: '24px',
                cursor: 'pointer',
            }} onClick={() => onNavigate('/')}>
                Ψ
            </div>

            {/* Nav items */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {NAV_ITEMS.map(item => {
                    const active = activePath === item.path ||
                        (item.path !== '/' && activePath.startsWith(item.path))
                    return (
                        <button
                            key={item.path}
                            title={item.label}
                            onClick={() => onNavigate(item.path)}
                            style={{
                                width: '40px', height: '40px',
                                borderRadius: '10px',
                                background: active ? 'var(--accent-glow)' : 'transparent',
                                border: active
                                    ? '1px solid var(--border-accent)'
                                    : '1px solid transparent',
                                color: active ? 'var(--accent-bright)' : 'var(--text-muted)',
                                fontSize: '16px',
                                cursor: 'pointer',
                                transition: 'all var(--t-fast)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}
                            onMouseEnter={e => {
                                if (!active) {
                                    e.currentTarget.style.background = 'var(--bg-overlay)'
                                    e.currentTarget.style.color = 'var(--text-secondary)'
                                }
                            }}
                            onMouseLeave={e => {
                                if (!active) {
                                    e.currentTarget.style.background = 'transparent'
                                    e.currentTarget.style.color = 'var(--text-muted)'
                                }
                            }}
                        >
                            {item.icon}
                        </button>
                    )
                })}
            </div>

            {/* Status dot at bottom */}
            <div
                className={isOnline ? 'pulse-dot' : ''}
                title={`Provider: ${provider}`}
                style={{
                    width: '8px', height: '8px',
                    borderRadius: '50%',
                    background: isOpenRouterOnline
                        ? 'var(--success)'
                        : isOllamaOnline
                            ? 'var(--warning)'
                            : 'var(--danger)',
                }}
            />
        </nav>
    )
}
