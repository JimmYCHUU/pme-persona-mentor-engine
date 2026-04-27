import axios from 'axios'
import type { ChatRequest, ChatResponse } from '../types'

const client = axios.create({ baseURL: 'http://localhost:8000' })

export const api = {
  async sendMessage(payload: ChatRequest): Promise<ChatResponse> {
    const res = await client.post('/chat/message', payload)
    return res.data.data
  },
  async health(): Promise<{ ollama_online: boolean }> {
    const res = await client.get('/health')
    return res.data.data
  },
  async createPersona(payload: Record<string, unknown>) {
    const res = await client.post('/persona/create', payload)
    return res.data.data
  },
  async listPersonas() {
    const res = await client.get('/persona/list')
    return res.data.data
  },
  async updateSliders(personaId: string, sliders: Record<string, unknown>) {
    const res = await client.patch(`/persona/${personaId}/sliders`, sliders)
    return res.data.data
  },
  async saveSession(snapshot: Record<string, unknown>) {
    const res = await client.post('/session/save', { snapshot })
    return res.data.data
  },
  async saveLessons(payload: { session_id: string; persona_name: string; notes: string }) {
    const res = await client.post('/session/lessons', payload)
    return res.data.data
  },
  async resumeSession(persona_id: string) {
    const res = await client.post('/session/resume', { persona_id })
    return res.data.data
  },
  async getLedger(personaId: string) {
    const res = await client.get(`/mastery/${personaId}/ledger`)
    return res.data.data
  },
  async getPendingCerts(personaId: string) {
    const res = await client.get(`/mastery/${personaId}/pending-certs`)
    return res.data.data
  },
  async markCertDelivered(personaId: string, certId: string) {
    const res = await client.patch(`/mastery/${personaId}/cert/${certId}/delivered`)
    return res.data.data
  },
  async uploadVault(file: File, persona_id: string) {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('persona_id', persona_id)
    const res = await client.post('/ingest/vault', fd)
    return res.data.data
  },
  async ingestFingerprint(url: string, persona_id: string) {
    const res = await client.post('/ingest/fingerprint', { url, persona_id })
    return res.data.data
  },
}
