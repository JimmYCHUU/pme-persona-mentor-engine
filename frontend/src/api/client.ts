/**
 * API client — centralised HTTP client for all backend calls.
 */

import axios from 'axios'
import type { ApiResponse } from '../types'

const API_BASE = 'http://localhost:8000'

const api = axios.create({
    baseURL: API_BASE,
    timeout: 120_000,
    headers: { 'Content-Type': 'application/json' },
})

export async function sendMessage(
    personaId: string,
    message: string,
    sessionId?: string,
    mode: string = 'deep_dive'
): Promise<ApiResponse> {
    const res = await api.post('/chat/message', {
        persona_id: personaId,
        message,
        session_id: sessionId,
        mode,
    })
    return res.data
}

export async function createPersona(data: {
    name: string
    description?: string
    sliders?: Record<string, number>
}): Promise<ApiResponse> {
    const res = await api.post('/persona/create', data)
    return res.data
}

export async function listPersonas(): Promise<ApiResponse> {
    const res = await api.get('/persona/list')
    return res.data
}

export async function getPersona(personaId: string): Promise<ApiResponse> {
    const res = await api.get(`/persona/${personaId}`)
    return res.data
}

export async function updateSliders(
    personaId: string,
    sliders: Record<string, number>
): Promise<ApiResponse> {
    const res = await api.patch(`/persona/${personaId}/sliders`, sliders)
    return res.data
}

export async function resumeSession(personaId: string): Promise<ApiResponse> {
    const res = await api.post('/session/resume', { persona_id: personaId })
    return res.data
}

export async function saveSession(
    sessionId: string,
    personaId: string,
    snapshot: Record<string, unknown>
): Promise<ApiResponse> {
    const res = await api.post('/session/save', {
        session_id: sessionId,
        persona_id: personaId,
        snapshot,
    })
    return res.data
}

export async function uploadVaultFile(
    personaId: string,
    file: File,
): Promise<ApiResponse> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('persona_id', personaId)
    const res = await api.post('/ingest/vault', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
}

export async function ingestFingerprint(
    personaId: string,
    url: string,
): Promise<ApiResponse> {
    const res = await api.post('/ingest/fingerprint', {
        persona_id: personaId,
        url,
    })
    return res.data
}

export async function getMasteryLedger(personaId: string): Promise<ApiResponse> {
    const res = await api.get(`/mastery/${personaId}/ledger`)
    return res.data
}

export async function getPendingCerts(personaId: string): Promise<ApiResponse> {
    const res = await api.get(`/mastery/${personaId}/pending-certs`)
    return res.data
}

export async function markCertDelivered(
    personaId: string,
    certId: string,
): Promise<ApiResponse> {
    const res = await api.patch(`/mastery/${personaId}/cert/${certId}/delivered`)
    return res.data
}

export async function checkHealth(): Promise<ApiResponse> {
    const res = await api.get('/health')
    return res.data
}

export default api
