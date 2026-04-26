"""Persona management API routes."""

from __future__ import annotations

from fastapi import APIRouter

from models.schemas import PersonaCreate
from services.persona_service import PersonaService


router = APIRouter()


@router.post("/create", response_model=dict)
async def create_persona(req: PersonaCreate) -> dict:
    """Create or overwrite a persona profile."""

    profile = req.model_dump()
    await PersonaService.save(profile)
    return {"success": True, "data": profile, "error": None}


@router.get("/list", response_model=dict)
async def list_personas() -> dict:
    """Return all personas."""

    return {"success": True, "data": await PersonaService.list_all(), "error": None}


@router.get("/{persona_id}", response_model=dict)
async def get_persona(persona_id: str) -> dict:
    """Return one persona by id."""

    profile = await PersonaService.load(persona_id)
    if not profile:
        return {"success": False, "data": None, "error": "NOT_FOUND"}
    return {"success": True, "data": profile, "error": None}


@router.patch("/{persona_id}/sliders", response_model=dict)
async def patch_sliders(persona_id: str, sliders: dict) -> dict:
    """Patch slider values for a persona profile."""

    await PersonaService.update_sliders(persona_id, sliders)
    return {"success": True, "data": {"persona_id": persona_id, "sliders": sliders}, "error": None}


@router.get("/{persona_id}/gap-questions", response_model=dict)
async def gap_questions(persona_id: str) -> dict:
    """Return generated interview questions for missing persona soul fields."""

    gaps = await PersonaService.detect_gaps(persona_id)
    questions = await PersonaService.generate_gap_questions(gaps)
    return {"success": True, "data": {"gaps": gaps, "questions": questions}, "error": None}


@router.post("/{persona_id}/gap-fill-answers", response_model=dict)
async def save_gap_answers(persona_id: str, answers: dict) -> dict:
    """Save gap-fill interview answers."""

    await PersonaService.save_gap_fill_answers(persona_id, answers)
    return {"success": True, "data": {"saved": True}, "error": None}
