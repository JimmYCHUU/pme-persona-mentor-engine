"""Workspace event API routes used by VS Code extension."""

from __future__ import annotations

from fastapi import APIRouter

from graph.nodes.socratic_node import socratic_node


router = APIRouter()


@router.post("/event", response_model=dict)
async def workspace_event(event: dict) -> dict:
    """Accept workspace event and return optional Socratic level hint."""

    level = 0
    event_type = event.get("type")
    if event_type in {"terminal_error", "file_save", "idle"}:
        state = {
            "session_id": event.get("session_id", "workspace-event"),
            "persona_id": event.get("persona_id", "default"),
            "user_message": event.get("content", event_type),
            "workspace_event": event,
            "session_snapshot": None,
            "is_returning_user": False,
            "mastery_summary": None,
            "etm_context": None,
            "etm_matched": False,
            "deviation_score": 0.0,
            "socratic_level": 0,
            "vault_citation": None,
            "mastery_event": None,
            "raw_llm_response": "",
            "styled_response": "",
            "guardian_flagged": False,
            "final_response": "",
            "mode": "deep_dive",
        }
        result = await socratic_node(state)
        level = int(result.get("socratic_level", 0))
    return {"success": True, "data": {"received": True, "socratic_level": level}, "error": None}
