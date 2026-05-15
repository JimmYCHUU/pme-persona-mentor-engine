/**
 * StatusBar — bottom bar showing LLM provider status and session info.
 * Uses sessionStore for provider status (polled by WorkspaceShell).
 */

import { useSessionStore } from '../../store/sessionStore'

export function StatusBar() {
    const { isOpenRouterOnline, isOllamaOnline, personaModel } = useSessionStore()

    const { dot, label } = getStatusDisplay(isOpenRouterOnline, isOllamaOnline, personaModel)

    return (
        <div className="status-bar" style={{
            height: 'var(--statusbar-h)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 16px',
            background: 'var(--bg-surface)',
            borderTop: '1px solid var(--border-subtle)',
            fontSize: '0.7rem',
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-muted)',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className={isOpenRouterOnline || isOllamaOnline ? 'pulse-dot' : ''} style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: dot,
                    display: 'inline-block',
                    transition: 'background 0.5s ease',
                }} />
                <span>{label}</span>
            </div>
            <div>
                <span>PME v2.0 · Cinematic Editorial</span>
            </div>
        </div>
    )
}

function getStatusDisplay(
    openrouter: boolean, ollama: boolean, model: string
): { dot: string; label: string } {
    if (openrouter) {
        const shortModel = model.split('/').pop()?.replace(':free', '') || 'OpenRouter'
        return { dot: 'var(--success)', label: `OpenRouter · ${shortModel}` }
    }
    if (ollama) {
        return { dot: 'var(--warning)', label: 'Ollama · llama3.2:3b (fallback)' }
    }
    return { dot: 'var(--danger)', label: 'Connecting…' }
}
