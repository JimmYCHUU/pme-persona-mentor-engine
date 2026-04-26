import { useState } from 'react'
import { useChat } from '../../hooks/useChat'
import { usePersonaStore } from '../../store/personaStore'
import { Button } from '../shared/Button'
import { Spinner } from '../shared/Spinner'

export function InputBar({ offline = false }: { offline?: boolean }) {
  const [text, setText] = useState('')
  const { send, isStreaming } = useChat()
  const { activeId } = usePersonaStore()

  const onSend = async () => {
    if (!activeId || !text.trim()) return
    const content = text
    setText('')
    await send(activeId, content)
  }

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      <input
        value={text}
        disabled={isStreaming || offline}
        onChange={(e) => setText(e.target.value)}
        placeholder='Ask your mentor...'
        style={{ flex: 1, padding: 10, borderRadius: 8, border: '1px solid var(--bg-overlay)', background: 'var(--bg-surface)', color: 'var(--text-primary)' }}
      />
      <Button onClick={() => void onSend()} disabled={isStreaming || offline}>
        {isStreaming ? <Spinner /> : 'Send'}
      </Button>
    </div>
  )
}
