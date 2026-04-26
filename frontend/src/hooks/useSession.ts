import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useChatStore } from '../store/chatStore'
import { useSessionStore } from '../store/sessionStore'

export function useSession() {
  const { snapshot, setSnapshot, mode } = useSessionStore()
  const { sessionId, messages } = useChatStore()
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null)

  const saveSession = async () => {
    if (!sessionId) return
    await api.saveSession({
      session_id: sessionId,
      persona_id: snapshot?.persona_id ?? 'default',
      created_at: snapshot?.created_at ?? new Date().toISOString(),
      updated_at: new Date().toISOString(),
      mode,
      chat_history: messages,
    })
    setLastSavedAt(Date.now())
  }

  useEffect(() => {
    const id = setInterval(() => {
      void saveSession()
    }, 60000)
    return () => clearInterval(id)
  }, [sessionId, mode, messages.length])

  useEffect(() => {
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = 'Save a Lessons Learned summary for your journal?'
      if (sessionId) {
        void api
          .saveSession({
            session_id: sessionId,
            persona_id: snapshot?.persona_id ?? 'default',
            created_at: snapshot?.created_at ?? new Date().toISOString(),
            updated_at: new Date().toISOString(),
            mode,
            chat_history: messages,
          })
          .then(() =>
            fetch('http://localhost:8000/session/lessons', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: sessionId, notes: messages.map((m) => m.content).join('\n') }),
            })
          )
      }
    }
    window.addEventListener('beforeunload', onBeforeUnload)
    return () => window.removeEventListener('beforeunload', onBeforeUnload)
  }, [sessionId, messages, mode, snapshot])

  const savedSecondsAgo = lastSavedAt ? Math.max(0, Math.floor((Date.now() - lastSavedAt) / 1000)) : null

  return { snapshot, setSnapshot, saveSession, lastSavedAt, savedSecondsAgo }
}
