export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  socratic_level?: 0 | 1 | 2 | 3 | 4
  vault_citation?: string | null
}

export interface PersonaProfile {
  persona_id: string
  name: string
  description: string
  soul?: Record<string, unknown>
  sliders?: Record<string, unknown>
  created_at?: string
}

export interface SessionSnapshot {
  session_id: string
  persona_id: string
  created_at: string
  updated_at: string
  mode: 'deep_dive' | 'friend_mode'
  active_project?: Record<string, unknown>
  work_state?: Record<string, unknown>
  mentor_assessment?: Record<string, unknown>
  mastery_context?: Record<string, unknown>
  chat_history?: Message[]
  failure_counts?: Record<string, number>
}

export interface ChatRequest {
  persona_id: string
  message: string
  mode?: 'deep_dive' | 'friend_mode'
  session_id?: string
}

export interface ChatResponse {
  response: string
  socratic_level: 0 | 1 | 2 | 3 | 4
  vault_citation?: string | null
  guardian_flagged: boolean
  session_id: string
}

export interface ConceptEntry {
  concept_id: string
  concept_key: string
  concept_label: string
  status: 'encountered' | 'attempted' | 'struggling' | 'mastered'
  mastery_score: number
  encounter_count: number
  success_count: number
  failure_count: number
}

export interface MasteryCertificate {
  cert_id: string
  persona_id: string
  concept_key: string
  concept_label: string
  issued_at: string
  mentor_statement: string
  evidence_summary: Record<string, unknown>
  delivered: number
}
