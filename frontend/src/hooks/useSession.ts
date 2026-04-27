import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useChatStore } from '../store/chatStore'
import { usePersonaStore } from '../store/personaStore'
import { useSessionStore } from '../store/sessionStore'

export function useSession() {
  const { snapshot, setSnapshot, mode } = useSessionStore()
  const { sessionId, messages } = useChatStore()
  const { activeId, personas } = usePersonaStore()
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null)
  const [showLessonsModal, setShowLessonsModal] = useState(false)
  const [lessonsPath, setLessonsPath] = useState<string | null>(null)
  const [isGeneratingLessons, setIsGeneratingLessons] = useState(false)

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
          .then(async () => {
            const personaName = personas.find((p) => p.persona_id === (activeId ?? snapshot?.persona_id))?.name ?? 'Mentor'
            await api.saveLessons({
              session_id: sessionId,
              persona_name: personaName,
              notes: messages.map((m) => m.content).join('\n'),
            })
          })
      }
    }
    window.addEventListener('beforeunload', onBeforeUnload)
    return () => window.removeEventListener('beforeunload', onBeforeUnload)
  }, [sessionId, messages, mode, snapshot, personas, activeId])

  const requestCloseSession = () => {
    setShowLessonsModal(true)
  }

  const closeLessonsModal = () => {
    setShowLessonsModal(false)
  }

  const generateLessons = async () => {
    if (!sessionId) return
    setIsGeneratingLessons(true)
    try {
      await saveSession()
      const personaName = personas.find((p) => p.persona_id === (activeId ?? snapshot?.persona_id))?.name ?? 'Mentor'
      const result = await api.saveLessons({
        session_id: sessionId,
        persona_name: personaName,
        notes: messages.map((m) => m.content).join('\n'),
      })
      setLessonsPath(result.path ?? null)
    } finally {
      setIsGeneratingLessons(false)
    }
  }

  const savedSecondsAgo = lastSavedAt ? Math.max(0, Math.floor((Date.now() - lastSavedAt) / 1000)) : null

  return {
    snapshot,
    setSnapshot,
    saveSession,
    lastSavedAt,
    savedSecondsAgo,
    showLessonsModal,
    requestCloseSession,
    closeLessonsModal,
    generateLessons,
    lessonsPath,
    isGeneratingLessons,
  }
}
