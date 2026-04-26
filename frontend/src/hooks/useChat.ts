import { api } from '../api/client'
import { useChatStore } from '../store/chatStore'
import { useSessionStore } from '../store/sessionStore'

export function useChat() {
  const { messages, addMessage, isStreaming, setStreaming, setSessionId, sessionId } = useChatStore()
  const { mode } = useSessionStore()

  const send = async (personaId: string, content: string) => {
    setStreaming(true)
    const userMsg = { id: crypto.randomUUID(), role: 'user' as const, content, socratic_level: 0 as const }
    addMessage(userMsg)
    try {
      const resp = await api.sendMessage({ persona_id: personaId, message: content, session_id: sessionId ?? undefined, mode })
      setSessionId(resp.session_id)
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: resp.response,
        socratic_level: resp.socratic_level,
        vault_citation: resp.vault_citation,
      })
    } finally {
      setStreaming(false)
    }
  }

  return { messages, isStreaming, send }
}
