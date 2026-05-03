/**
 * Message — a single chat message bubble with SocraticBadge.
 */

import { SocraticBadge } from './SocraticBadge'
import type { ChatMessage } from '../../types'

interface Props {
    message: ChatMessage
    mentorName: string
}

export function Message({ message, mentorName }: Props) {
    const isUser = message.role === 'user'

    return (
        <div className="animate-slide-up" style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: isUser ? 'flex-end' : 'flex-start',
            maxWidth: '80%',
            alignSelf: isUser ? 'flex-end' : 'flex-start',
        }}>
            {/* Author label */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '4px',
            }}>
                <span style={{
                    fontSize: '0.7rem',
                    fontFamily: 'var(--font-mono)',
                    color: isUser ? 'var(--text-muted)' : 'var(--accent)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                }}>
                    {isUser ? 'You' : mentorName}
                </span>
                {!isUser && message.socratic_level !== undefined && (
                    <SocraticBadge level={message.socratic_level as 0 | 1 | 2 | 3 | 4} />
                )}
            </div>

            {/* Message bubble */}
            <div style={{
                padding: '12px 16px',
                background: isUser ? 'var(--bg-raised)' : 'var(--bg-surface)',
                border: isUser
                    ? '1px solid var(--glass-border)'
                    : `1px solid ${message.socratic_level && message.socratic_level > 0
                        ? 'var(--accent-dim)' : 'var(--glass-border)'}`,
                borderRadius: 'var(--radius-lg)',
                fontSize: '0.9rem',
                lineHeight: 1.65,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
            }}>
                {message.content}
            </div>

            {/* Vault citation */}
            {!isUser && message.vault_citation && (
                <div style={{
                    marginTop: '6px',
                    fontSize: '0.7rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    fontStyle: 'italic',
                    maxWidth: '100%',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                }}>
                    📚 {message.vault_citation}
                </div>
            )}
        </div>
    )
}
