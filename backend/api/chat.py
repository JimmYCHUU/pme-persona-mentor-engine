"""Main chat API routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect

from graph.nodes.mastery_node import process_mastery_event
from graph.orchestrator import pme_graph
from services.ollama_service import ollama_service
from core.config import settings
from models.schemas import ChatRequest


router = APIRouter()


@router.post("/message", response_model=dict)
async def send_message(req: ChatRequest, background_tasks: BackgroundTasks) -> dict:
    """Run full graph pipeline and return chat payload envelope."""

    initial_state = {
        "session_id": req.session_id or str(uuid.uuid4()),
        "persona_id": req.persona_id,
        "user_message": req.message,
        "workspace_event": None,
        "is_returning_user": False,
        "session_snapshot": None,
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
        "mode": req.mode or "deep_dive",
    }
    try:
        result = await pme_graph.ainvoke(initial_state)
    except Exception as exc:
        text = str(exc)
        if "Connection" in text or "ollama" in text.lower():
            return {"success": False, "data": None, "error": "OLLAMA_OFFLINE"}
        return {"success": False, "data": None, "error": text}

    if result.get("mastery_event"):
        background_tasks.add_task(process_mastery_event, result["mastery_event"])

    return {
        "success": True,
        "data": {
            "response": result["final_response"],
            "socratic_level": result["socratic_level"],
            "vault_citation": result.get("vault_citation"),
            "guardian_flagged": result["guardian_flagged"],
            "session_id": result["session_id"],
        },
        "error": None,
    }


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str) -> None:
    """Stream response token chunks over websocket for live chat updates."""

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            system = data.get("system", "You are a mentor.")
            message = data.get("message", "")
            history = data.get("history", [])
            async for token in ollama_service.stream(
                model=settings.OLLAMA_MODEL,
                system=system,
                message=message,
                history=history,
            ):
                await websocket.send_json({"type": "token", "content": token, "session_id": session_id})
            await websocket.send_json({"type": "done", "session_id": session_id})
    except WebSocketDisconnect:
        return
