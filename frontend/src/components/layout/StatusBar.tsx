/**
 * StatusBar — bottom bar showing Ollama status and session info.
 */

import { useState, useEffect } from 'react'
import { checkHealth } from '../../api/client'

export function StatusBar() {
    const [ollamaOnline, setOllamaOnline] = useState(false)

    useEffect(() => {
        const check = async () => {
            try {
                const res = await checkHealth()
                setOllamaOnline(res.success && res.data?.ollama_online)
            } catch {
                setOllamaOnline(false)
            }
        }
        check()
        const interval = setInterval(check, 15000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="status-bar" style={{
            height: 'var(--statusbar-h)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 16px',
            background: 'var(--bg-surface)',
            borderTop: '1px solid var(--glass-border)',
            fontSize: '0.7rem',
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-muted)',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: ollamaOnline ? 'var(--success)' : 'var(--danger)',
                    display: 'inline-block',
                }} />
                <span>Ollama {ollamaOnline ? 'Connected' : 'Offline'}</span>
            </div>
            <div>
                <span>PME v1.0 · Cinematic Editorial</span>
            </div>
        </div>
    )
}
