/**
 * ChatPane — premium chat interface with gradient background and refined spacing.
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
            {/* Messages area */}
            <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '32px 40px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
            }}>
                {messages.length === 0 && (
                    <div className="fade-up" style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flex: 1,
                        gap: '16px',
                    }}>
                        {/* Decorative orb */}
                        <div style={{
                            width: '80px', height: '80px',
                            borderRadius: '50%',
                            background: 'radial-gradient(circle at 40% 40%, var(--orb-core), var(--orb-mid) 60%, transparent 100%)',
                            filter: 'blur(12px)',
                            opacity: 0.6,
                            marginBottom: '8px',
                        }} />
                        <h2 style={{
                            fontFamily: 'var(--font-display)',
                            color: 'var(--accent-bright)',
                            fontSize: '1.8rem',
                            fontWeight: 300,
                            letterSpacing: '-0.01em',
                        }}>
                            {activePersona?.name || 'Mentor'}
                        </h2>
                        <p style={{
                            fontSize: '0.85rem',
                            maxWidth: '380px',
                            textAlign: 'center',
                            lineHeight: 1.7,
                            color: 'var(--text-muted)',
                            fontWeight: 300,
                        }}>
                            Begin your session. Your mentor is present and listening.
                        </p>
                    </div>
                )}
                {messages.map((msg, i) => (
                    <Message key={i} message={msg} mentorName={activePersona?.name || 'Mentor'} />
                ))}
                {isLoading && (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '16px 20px',
                    }}>
                        {[0, 1, 2].map((i) => (
                            <span key={i} style={{
                                width: '5px',
                                height: '5px',
                                borderRadius: '50%',
                                background: 'var(--accent)',
                                opacity: 0.6,
                                animation: `pulseDot 1.4s ease-in-out ${i * 0.2}s infinite`,
                            }} />
                        ))}
                        <span style={{
                            fontSize: '0.7rem',
                            color: 'var(--text-muted)',
                            fontFamily: 'var(--font-mono)',
                            marginLeft: '6px',
                        }}>
                            thinking…
                        </span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <InputBar onSend={send} disabled={isLoading} />
        </div>
    )
}
