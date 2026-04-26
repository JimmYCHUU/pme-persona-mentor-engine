"""Session lifecycle API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from core.config import settings
from models.schemas import SessionSaveRequest
from services.ollama_service import ollama_service
from services.session_service import SessionService


router = APIRouter()


@router.post("/resume", response_model=dict)
async def resume_session(payload: dict) -> dict:
    """Load latest snapshot for persona and return greeting summary."""

    persona_id = payload.get("persona_id", "")
    snapshot = await SessionService.get_latest_for_persona(persona_id)
    greeting = "Welcome back."
    if snapshot:
        mentor_name = snapshot.get("mentor_assessment", {}).get("mentor_name", "Mentor")
        greeting = f"Welcome back. {mentor_name} has your workspace ready."
    return {"success": True, "data": {"snapshot": snapshot, "greeting": greeting}, "error": None}


@router.post("/save", response_model=dict)
async def save_session(req: SessionSaveRequest) -> dict:
    """Persist session snapshot."""

    await SessionService.save(req.snapshot)
    return {"success": True, "data": {"saved": True}, "error": None}


@router.post("/lessons", response_model=dict)
async def save_lessons(payload: dict) -> dict:
    """Generate and save lessons-learned markdown summary for a session."""

    session_id = payload.get("session_id", "")
    persona_name = payload.get("persona_name", "Mentor")
    notes = payload.get("notes", "")
    prompt = f"In the voice of {persona_name}, summarize key lessons from this session:\n{notes}"
    summary = await ollama_service.chat(model=settings.OLLAMA_MODEL, system=f"You are {persona_name}", message=prompt)
    out = Path(settings.SESSION_DIR) / f"{session_id}_lessons.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(summary, encoding="utf-8")
    return {"success": True, "data": {"saved": True, "path": str(out)}, "error": None}
