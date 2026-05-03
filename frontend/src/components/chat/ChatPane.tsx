/**
 * ChatPane — the main chat area with messages and input.
 */

import { useRef, useEffect } from 'react'
import { useChat } from '../../hooks/useChat'
import { Message } from './Message'
import { InputBar } from './InputBar'
import { usePersonaStore } from '../../store/personaStore'

export function ChatPane() {
    const { messages, isLoading, send } = useChat()
    const { activePersona } = usePersonaStore()
    const messagesEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            flex: 1,
            overflow: 'hidden',
            background: 'var(--bg-base)',
        }}>
            {/* Messages */}
            <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '24px 32px',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
            }}>
                {messages.length === 0 && (
                    <div className="animate-fade-in" style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flex: 1,
                        gap: '16px',
                        color: 'var(--text-muted)',
                    }}>
                        <h2 style={{
                            fontFamily: 'var(--font-heading)',
                            color: 'var(--accent)',
                            fontSize: '1.5rem',
                        }}>
                            {activePersona?.name || 'Mentor'}
                        </h2>
                        <p style={{ fontSize: '0.9rem', maxWidth: '400px', textAlign: 'center', lineHeight: 1.6 }}>
                            Begin your session. Your mentor is ready.
                        </p>
                    </div>
                )}
                {messages.map((msg, i) => (
                    <Message key={i} message={msg} mentorName={activePersona?.name || 'Mentor'} />
                ))}
                {isLoading && (
                    <div style={{
                        display: 'flex',
                        gap: '4px',
                        padding: '12px 16px',
                    }}>
                        {[0, 1, 2].map((i) => (
                            <span key={i} style={{
                                width: '6px',
                                height: '6px',
                                borderRadius: '50%',
                                background: 'var(--accent-dim)',
                                animation: `typewriter-glow 1.2s ease-in-out ${i * 0.2}s infinite`,
                            }} />
                        ))}
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <InputBar onSend={send} disabled={isLoading} />
        </div>
    )
}
