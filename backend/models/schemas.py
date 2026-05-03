"""Pydantic schemas for all API request/response types."""

from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request body for POST /chat/message."""
    persona_id: str
    message: str
    session_id: Optional[str] = None
    mode: Optional[str] = 'deep_dive'


class ChatResponse(BaseModel):
    """Response data for chat endpoint."""
    response: str
    socratic_level: int = 0
    vault_citation: Optional[str] = None
    guardian_flagged: bool = False
    session_id: str = ''


class PersonaCreate(BaseModel):
    """Request body for POST /persona/create."""
    name: str
    description: str = ''
    sliders: Optional[dict] = None
    urls: Optional[List[str]] = None
    gap_fill_answers: Optional[dict] = None


class PersonaProfile(BaseModel):
    """Response data for persona endpoints."""
    persona_id: str
    name: str
    description: str = ''
    sliders: Optional[dict] = None
    created_at: Optional[str] = None


class SessionSaveRequest(BaseModel):
    """Request body for POST /session/save."""
    session_id: str
    persona_id: str
    snapshot: dict


class SessionResumeResponse(BaseModel):
    """Response data for POST /session/resume."""
    session_id: str
    snapshot: Optional[dict] = None
    resume_greeting: str = ''


class WorkspaceEvent(BaseModel):
    """Request body for POST /workspace/event."""
    type: str
    content: Optional[str] = None
    file: Optional[str] = None
    language: Optional[str] = None
    duration_seconds: Optional[int] = None


class ConceptEntry(BaseModel):
    """Mastery ledger entry for API responses."""
    concept_id: str
    concept_key: str
    concept_label: str
    status: str
    mastery_score: float
    encounter_count: int = 0
    success_count: int = 0
    failure_count: int = 0


class MasteryCertResponse(BaseModel):
    """Certificate data for API responses."""
    cert_id: str
    persona_id: str
    concept_key: str
    concept_label: str
    issued_at: str
    mentor_statement: str
    evidence_summary: Optional[dict] = None
    delivered: int = 0


class MasteryLedgerResponse(BaseModel):
    """Response for GET /mastery/{pid}/ledger."""
    concepts: List[ConceptEntry] = []


class CertResponse(BaseModel):
    """Response for cert endpoints."""
    certs: List[MasteryCertResponse] = []
