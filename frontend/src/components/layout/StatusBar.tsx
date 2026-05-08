/**
 * StatusBar — bottom bar showing LLM provider status and session info.
 * Per ANTIGRAVITY_PROMPT Step 8:
 *   - openrouter_online → "OpenRouter · DeepSeek V3" (green)
 *   - only ollama_online → "Ollama · llama3.2:3b" (yellow — fallback)
 *   - neither → "No LLM available" (red)
 */

import { useState, useEffect } from 'react'
import { checkHealth } from '../../api/client'

interface HealthData {
    openrouter_online: boolean
    ollama_online: boolean
    primary_provider: string
    persona_model?: string
}

export function StatusBar() {
    const [health, setHealth] = useState<HealthData | null>(null)

    useEffect(() => {
        const check = async () => {
            try {
                const res = await checkHealth()
                if (res.success && res.data) {
                    setHealth(res.data as HealthData)
                }
            } catch {
                setHealth(null)
            }
        }
        check()
        const interval = setInterval(check, 15000)
        return () => clearInterval(interval)
    }, [])

    const { dot, label } = getStatusDisplay(health)

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
                    background: dot,
                    display: 'inline-block',
                    boxShadow: `0 0 4px ${dot}`,
                    transition: 'background 0.5s ease',
                }} />
                <span>{label}</span>
            </div>
            <div>
                <span>PME v1.0 · Cinematic Editorial</span>
            </div>
        </div>
    )
}

function getStatusDisplay(health: HealthData | null): { dot: string; label: string } {
    if (!health) {
        return { dot: 'var(--danger)', label: 'Connecting…' }
    }
    if (health.openrouter_online) {
        const model = health.persona_model?.split('/').pop()?.replace(':free', '') || 'DeepSeek V3'
        return { dot: 'var(--success)', label: `OpenRouter · ${model}` }
    }
    if (health.ollama_online) {
        return { dot: '#F59E0B', label: 'Ollama · llama3.2:3b (fallback)' }
    }
    return { dot: 'var(--danger)', label: 'No LLM available' }
}
