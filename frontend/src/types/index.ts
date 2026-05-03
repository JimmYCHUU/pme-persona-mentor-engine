/* ── Frontend types for the PME application ── */

export interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    socratic_level?: number
    vault_citation?: string
}

export interface PersonaProfile {
    persona_id: string
    name: string
    description: string
    sliders?: PersonaSliders
    soul?: PersonaSoul
    gap_fill_answers?: Record<string, string>
    created_at?: string
}

export interface PersonaSliders {
    abrasiveness: number
    proactivity: number
    explainDepth: number
}

export interface PersonaSoul {
    few_shot_examples?: { user: string; mentor: string }[]
    philosophy_tags?: string[]
    vocabulary_map?: Record<string, string[]>
}

export interface SessionSnapshot {
    session_id: string
    persona_id: string
    created_at: string
    updated_at: string
    mode: 'deep_dive' | 'friend_mode'
    active_project?: {
        name: string
        description: string
        current_phase: string
    }
    work_state?: {
        open_files: string[]
        last_terminal_error: string | null
        unresolved_critiques: string[]
        last_vault_citation: string
    }
    mentor_assessment?: {
        summary: string
        user_strengths: string[]
        user_weaknesses: string[]
        next_steps: string[]
    }
    mastery_context?: {
        top_struggling: { concept_key: string; failure_count: number }[]
        new_certs_since_last_session: string[]
    }
    chat_history: ChatMessage[]
    failure_counts: Record<string, number>
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

export interface MasteryCert {
    cert_id: string
    persona_id: string
    concept_key: string
    concept_label: string
    issued_at: string
    mentor_statement: string
    evidence_summary?: {
        sessions_tested: number
        success_count: number
        failure_count: number
        mastery_score: number
    }
    delivered: number
}

export interface ApiResponse<T = unknown> {
    success: boolean
    data: T | null
    error: string | null
}
