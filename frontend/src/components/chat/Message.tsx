/**
 * Message — premium chat message with markdown rendering, gradient accents,
 * and refined typography. Renders **bold**, *italic*, lists, code etc.
 */

import React from 'react'
import { SocraticBadge } from './SocraticBadge'
import type { ChatMessage } from '../../types'

interface Props {
    message: ChatMessage
    mentorName: string
}

/**
 * Simple markdown → JSX renderer for chat messages.
 * Handles: **bold**, *italic*, `code`, headers, lists, blockquotes.
 * No external dependencies needed.
 */
function renderMarkdown(text: string): React.ReactElement {
    // Split into lines for block-level parsing
    const lines = text.split('\n')
    const elements: React.ReactElement[] = []
    let listItems: string[] = []
    let listType: 'ul' | 'ol' | null = null

    const flushList = () => {
        if (listItems.length > 0 && listType) {
            const Tag = listType
            elements.push(
                <Tag key={elements.length} style={{ margin: '8px 0', paddingLeft: '20px' }}>
                    {listItems.map((item, i) => (
                        <li key={i} style={{ marginBottom: '4px' }}>{renderInline(item)}</li>
                    ))}
                </Tag>
            )
            listItems = []
            listType = null
        }
    }

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i]

        // Headers
        const headerMatch = line.match(/^(#{1,4})\s+(.+)$/)
        if (headerMatch) {
            flushList()
            const level = headerMatch[1].length
            const fontSize = level === 1 ? '1.1em' : level === 2 ? '1.0em' : '0.95em'
            elements.push(
                <div key={i} style={{
                    fontSize,
                    fontWeight: 600,
                    marginTop: '12px',
                    marginBottom: '6px',
                    color: 'var(--text-primary)',
                }}>
                    {renderInline(headerMatch[2])}
                </div>
            )
            continue
        }

        // Unordered list items
        const ulMatch = line.match(/^\s*[-*•]\s+(.+)$/)
        if (ulMatch) {
            if (listType === 'ol') flushList()
            listType = 'ul'
            listItems.push(ulMatch[1])
            continue
        }

        // Ordered list items
        const olMatch = line.match(/^\s*\d+[.)]\s+(.+)$/)
        if (olMatch) {
            if (listType === 'ul') flushList()
            listType = 'ol'
            listItems.push(olMatch[1])
            continue
        }

        // Blockquote
        if (line.startsWith('>')) {
            flushList()
            elements.push(
                <div key={i} style={{
                    borderLeft: '3px solid var(--accent)',
                    paddingLeft: '12px',
                    margin: '8px 0',
                    color: 'var(--text-secondary)',
                    fontStyle: 'italic',
                }}>
                    {renderInline(line.replace(/^>\s*/, ''))}
                </div>
            )
            continue
        }

        // Horizontal rule (━━ or ---)
        if (/^(━{3,}|---{1,}|\*\*\*{1,})$/.test(line.trim())) {
            flushList()
            elements.push(
                <hr key={i} style={{
                    border: 'none',
                    borderTop: '1px solid var(--border-subtle)',
                    margin: '12px 0',
                }} />
            )
            continue
        }

        flushList()

        // Empty lines → spacing
        if (line.trim() === '') {
            elements.push(<div key={i} style={{ height: '8px' }} />)
            continue
        }

        // Regular paragraph
        elements.push(
            <div key={i} style={{ marginBottom: '4px' }}>
                {renderInline(line)}
            </div>
        )
    }

    flushList()

    return <>{elements}</>
}

/** Render inline markdown: **bold**, *italic*, `code`, ~~strike~~ */
function renderInline(text: string): (string | React.ReactElement)[] {
    const parts: (string | React.ReactElement)[] = []
    // Pattern matches: `code`, **bold**, *italic*, ~~strike~~, em-dashes
    const pattern = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|~~[^~]+~~|—|━)/g
    let lastIndex = 0
    let match: RegExpExecArray | null
    let key = 0

    while ((match = pattern.exec(text)) !== null) {
        // Add text before match
        if (match.index > lastIndex) {
            parts.push(text.slice(lastIndex, match.index))
        }

        const m = match[0]
        if (m.startsWith('`') && m.endsWith('`')) {
            // Inline code
            parts.push(
                <code key={key++} style={{
                    background: 'var(--bg-raised)',
                    padding: '1px 6px',
                    borderRadius: '4px',
                    fontSize: '0.85em',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--accent-bright)',
                }}>
                    {m.slice(1, -1)}
                </code>
            )
        } else if (m.startsWith('**') && m.endsWith('**')) {
            // Bold
            parts.push(<strong key={key++} style={{ fontWeight: 600 }}>{m.slice(2, -2)}</strong>)
        } else if (m.startsWith('*') && m.endsWith('*')) {
            // Italic
            parts.push(<em key={key++}>{m.slice(1, -1)}</em>)
        } else if (m.startsWith('~~') && m.endsWith('~~')) {
            // Strikethrough
            parts.push(<del key={key++}>{m.slice(2, -2)}</del>)
        } else if (m === '—' || m === '━') {
            // Em-dash → just a dash
            parts.push('–')
        }

        lastIndex = match.index + m.length
    }

    // Add remaining text
    if (lastIndex < text.length) {
        parts.push(text.slice(lastIndex))
    }

    return parts.length > 0 ? parts : [text]
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
                wordBreak: 'break-word',
                boxShadow: hasSocratic ? 'var(--shadow-accent)' : 'none',
                transition: 'all var(--t-fast)',
            }}>
                {isUser ? message.content : renderMarkdown(message.content)}
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
