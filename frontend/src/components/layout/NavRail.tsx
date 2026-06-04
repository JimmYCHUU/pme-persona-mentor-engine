/**
 * NavRail — 64px vertical icon rail for workspace navigation.
 * Uses clean SVG-style icons instead of Unicode glyphs.
 */

import { useSessionStore } from '../../store/sessionStore'

const NAV_ITEMS = [
    {
        label: 'Session', path: '/',
        icon: (active: boolean) => (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={active ? 'var(--accent-bright)' : 'currentColor'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
        ),
    },
    {
        label: 'Dashboard', path: '/dashboard',
        icon: (active: boolean) => (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={active ? 'var(--accent-bright)' : 'currentColor'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="7" height="9" rx="1" />
                <rect x="14" y="3" width="7" height="5" rx="1" />
                <rect x="14" y="12" width="7" height="9" rx="1" />
                <rect x="3" y="16" width="7" height="5" rx="1" />
            </svg>
        ),
    },
    {
        label: 'Mentors', path: '/mentors',
        icon: (active: boolean) => (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={active ? 'var(--accent-bright)' : 'currentColor'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
            </svg>
        ),
    },
    {
        label: 'Settings', path: '/settings',
        icon: (active: boolean) => (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={active ? 'var(--accent-bright)' : 'currentColor'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
        ),
    },
]

interface Props {
    activePath: string
    onNavigate: (path: string) => void
}

export function NavRail({ activePath, onNavigate }: Props) {
    const { isOllamaOnline, isOpenRouterOnline } = useSessionStore()

    const isOnline = isOpenRouterOnline || isOllamaOnline
    const provider = isOpenRouterOnline ? 'OpenRouter' : isOllamaOnline ? 'Ollama' : 'Offline'

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
                            {item.icon(active)}
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
