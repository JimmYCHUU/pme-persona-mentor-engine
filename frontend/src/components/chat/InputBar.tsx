/**
 * InputBar — chat input with send button.
 */

import { useState, useRef, type KeyboardEvent } from 'react'

interface Props {
    onSend: (text: string) => void
    disabled?: boolean
}

export function InputBar({ onSend, disabled }: Props) {
    const [text, setText] = useState('')
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
            padding: '12px 24px 16px',
            borderTop: '1px solid var(--glass-border)',
            background: 'var(--bg-surface)',
        }}>
            <div style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'flex-end',
            }}>
                <textarea
                    ref={inputRef}
                    className="input"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    disabled={disabled}
                    rows={1}
                    style={{
                        flex: 1,
                        resize: 'none',
                        minHeight: '40px',
                        maxHeight: '120px',
                    }}
                />
                <button
                    className="btn btn-primary"
                    onClick={handleSend}
                    disabled={disabled || !text.trim()}
                    style={{
                        padding: '10px 16px',
                        opacity: disabled || !text.trim() ? 0.5 : 1,
                    }}
                >
                    Send
                </button>
            </div>
        </div>
    )
}
