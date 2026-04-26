import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../../api/client'
import { useChatStore } from '../../store/chatStore'
import { Message } from './Message'
import { InputBar } from './InputBar'

export function ChatPane() {
  const { messages } = useChatStore()
  const endRef = useRef<HTMLDivElement>(null)
  const [offline, setOffline] = useState(false)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  useEffect(() => {
    const tick = async () => {
      const h = await api.health()
      setOffline(!h.ollama_online)
    }
    void tick()
    const id = setInterval(() => void tick(), 30000)
    return () => clearInterval(id)
  }, [])

  return (
    <section style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 10, padding: 12 }}>
        {messages.map((m) => (
          <Message key={m.id} message={m} />
        ))}
        <div ref={endRef} />
      </div>
      {offline && (
        <div style={{ background: 'var(--accent-dim)', color: 'var(--accent)', padding: '6px 10px', marginBottom: 8 }}>
          Mentor offline. Start Ollama: run 'ollama serve' in terminal.
        </div>
      )}
      <InputBar offline={offline} />
    </section>
  )
}
