/**
 * InputBar — premium chat input with glowing border and accent send button.
 */

import { useState, useRef, type KeyboardEvent } from 'react'

interface Props {
    onSend: (text: string) => void
    disabled?: boolean
}

export function InputBar({ onSend, disabled }: Props) {
    const [text, setText] = useState('')
    const [focused, setFocused] = useState(false)
    const inputRef = useRef<HTMLTextAreaElement>(null)

    const handleSend = () => {
        if (!text.trim() || disabled) return
        onSend(text.trim())
        setText('')
        inputRef.current?.focus()
    }

    const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div style={{
            padding: '12px 32px 20px',
            background: 'var(--bg-surface)',
            borderTop: '1px solid var(--border-subtle)',
        }}>
            <div style={{
                display: 'flex',
                gap: '10px',
                alignItems: 'flex-end',
                background: 'var(--bg-raised)',
                border: focused
                    ? '1px solid var(--border-accent)'
                    : '1px solid var(--border-default)',
                borderRadius: '14px',
                padding: '6px 6px 6px 16px',
                transition: 'border-color var(--t-fast), box-shadow var(--t-fast)',
                boxShadow: focused ? 'var(--shadow-accent)' : 'none',
            }}>
                <textarea
                    ref={inputRef}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                    placeholder="Ask your mentor anything…"
                    disabled={disabled}
                    rows={1}
                    style={{
                        flex: 1,
                        resize: 'none',
                        minHeight: '36px',
                        maxHeight: '120px',
                        background: 'transparent',
                        border: 'none',
                        outline: 'none',
                        color: 'var(--text-primary)',
                        fontFamily: 'var(--font-body)',
                        fontSize: '0.9rem',
                        lineHeight: 1.6,
                        padding: '6px 0',
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={disabled || !text.trim()}
                    style={{
                        padding: '8px 18px',
                        background: disabled || !text.trim()
                            ? 'var(--bg-overlay)'
                            : 'var(--accent)',
                        border: 'none',
                        borderRadius: '10px',
                        color: disabled || !text.trim()
                            ? 'var(--text-disabled)'
                            : '#fff',
                        fontFamily: 'var(--font-body)',
                        fontSize: '0.8rem',
                        fontWeight: 500,
                        letterSpacing: '0.04em',
                        cursor: disabled || !text.trim() ? 'not-allowed' : 'pointer',
                        transition: 'all var(--t-fast)',
                        flexShrink: 0,
                    }}
                >
                    Send
                </button>
            </div>
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                marginTop: '8px',
            }}>
                <span style={{
                    fontSize: '0.6rem',
                    color: 'var(--text-disabled)',
                    fontFamily: 'var(--font-mono)',
                }}>
                    Enter to send · Shift+Enter for newline
                </span>
            </div>
        </div>
    )
}
