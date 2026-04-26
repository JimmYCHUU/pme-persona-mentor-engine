"""Pydantic schemas used by API request and response payloads."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat API request body."""

    persona_id: str
    message: str
    mode: Literal["deep_dive", "friend_mode"] = "deep_dive"
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Chat API response payload in data envelope."""

    response: str
    socratic_level: int
    vault_citation: str | None = None
    guardian_flagged: bool = False
    session_id: str


class PersonaCreate(BaseModel):
    """Create persona request body."""

    persona_id: str
    name: str
    description: str
    soul: dict[str, Any] = Field(default_factory=dict)
    sliders: dict[str, Any] = Field(default_factory=dict)


class PersonaProfile(BaseModel):
    """Persona profile response schema."""

    persona_id: str
    name: str
    description: str
    soul: dict[str, Any] = Field(default_factory=dict)
    sliders: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class SessionSaveRequest(BaseModel):
    """Session save payload containing full snapshot."""

    snapshot: dict[str, Any]


class SessionResumeResponse(BaseModel):
    """Session resume payload schema."""

    snapshot: dict[str, Any] | None
    greeting: str


class WorkspaceEvent(BaseModel):
    """Workspace monitor event payload schema."""

    type: str
    content: str | None = None
    file: str | None = None
    language: str | None = None
    duration_seconds: int | None = None
    session_id: str | None = None
    persona_id: str | None = None


class MasteryLedgerResponse(BaseModel):
    """Mastery ledger API response item."""

    concept_id: str
    concept_key: str
    concept_label: str
    status: str
    mastery_score: float
    encounter_count: int
    success_count: int
    failure_count: int


class CertResponse(BaseModel):
    """Mastery certificate API response item."""

    cert_id: str
    persona_id: str
    concept_key: str
    concept_label: str
    issued_at: str
    mentor_statement: str
    evidence_summary: dict[str, Any]
    delivered: int
