"""Workspace event API routes used by VS Code extension."""

from __future__ import annotations

from fastapi import APIRouter

from graph.nodes.socratic_node import socratic_node
from services.session_service import SessionService


router = APIRouter()


@router.post("/event", response_model=dict)
async def workspace_event(event: dict) -> dict:
    """Accept workspace event and return optional Socratic level hint."""

    level = 0
    event_type = event.get("type")
    if event_type in {"terminal_error", "file_save", "idle"}:
        session_id = event.get("session_id", "workspace-event")
        persona_id = event.get("persona_id", "default")
        snapshot = await SessionService.load(session_id) or {
            "session_id": session_id,
            "persona_id": persona_id,
            "mode": "deep_dive",
            "work_state": {
                "open_files": [],
                "last_terminal_error": None,
                "unresolved_critiques": [],
                "last_vault_citation": "",
                "events": [],
            },
            "chat_history": [],
            "failure_counts": {},
        }
        work_state = snapshot.setdefault("work_state", {})
        events = list(work_state.get("events", []))
        events.append(event)
        work_state["events"] = events[-50:]
        if event_type == "terminal_error":
            work_state["last_terminal_error"] = event.get("content")
        if event_type == "file_save" and event.get("file"):
            opens = list(work_state.get("open_files", []))
            opens.append(event.get("file"))
            work_state["open_files"] = opens[-20:]
        await SessionService.save(snapshot)

        state = {
            "session_id": session_id,
            "persona_id": persona_id,
            "user_message": event.get("content", event_type),
            "workspace_event": event,
            "session_snapshot": snapshot,
            "is_returning_user": True,
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
