/**
 * Message — premium chat message with gradient accents, refined typography.
 */

import { SocraticBadge } from './SocraticBadge'
import type { ChatMessage } from '../../types'

interface Props {
    message: ChatMessage
    mentorName: string
}

export function Message({ message, mentorName }: Props) {
    const isUser = message.role === 'user'
    const hasSocratic = !isUser && message.socratic_level !== undefined && message.socratic_level > 0

    return (
        <div className="fade-up" style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: isUser ? 'flex-end' : 'flex-start',
            maxWidth: '75%',
            alignSelf: isUser ? 'flex-end' : 'flex-start',
        }}>
            {/* Author label */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '6px',
            }}>
                {!isUser && (
                    <span style={{
                        width: '5px', height: '5px',
                        borderRadius: '50%',
                        background: 'var(--accent-bright)',
                        boxShadow: '0 0 6px var(--accent)',
                        display: 'inline-block',
                    }} />
                )}
                <span style={{
                    fontSize: '0.65rem',
                    fontFamily: 'var(--font-mono)',
                    color: isUser ? 'var(--text-muted)' : 'var(--accent-bright)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    fontWeight: 500,
                }}>
                    {isUser ? 'You' : mentorName}
                </span>
                {!isUser && message.socratic_level !== undefined && (
                    <SocraticBadge level={message.socratic_level as 0 | 1 | 2 | 3 | 4} />
                )}
            </div>

            {/* Message bubble */}
            <div style={{
                padding: '14px 18px',
                background: isUser
                    ? 'var(--bg-raised)'
                    : hasSocratic
                        ? 'linear-gradient(135deg, var(--bg-surface) 0%, rgba(108,63,201,0.06) 100%)'
                        : 'var(--bg-surface)',
                border: isUser
                    ? '1px solid var(--border-subtle)'
                    : hasSocratic
                        ? '1px solid var(--border-accent)'
                        : '1px solid var(--border-subtle)',
                borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                fontSize: '0.88rem',
                lineHeight: 1.7,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                boxShadow: hasSocratic ? 'var(--shadow-accent)' : 'none',
                transition: 'all var(--t-fast)',
            }}>
                {message.content}
            </div>

            {/* Vault citation */}
            {!isUser && message.vault_citation && (
                <div style={{
                    marginTop: '8px',
                    fontSize: '0.65rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '4px 10px',
                    background: 'var(--bg-raised)',
                    borderRadius: '6px',
                    border: '1px solid var(--border-subtle)',
                }}>
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                    </svg>
                    {message.vault_citation}
                </div>
            )}
        </div>
    )
}
