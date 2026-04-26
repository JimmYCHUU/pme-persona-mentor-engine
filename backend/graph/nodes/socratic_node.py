"""Socratic node computes intervention level and mastery events."""

from __future__ import annotations

from core.config import settings
from graph.state import PMEState
from rag.retriever import retriever
from services.mastery_service import MasteryService


async def socratic_node(state: PMEState) -> PMEState:
    """Compute deviation, determine Socratic level, and emit mastery event."""

    if state["mode"] == "friend_mode":
        state["deviation_score"] = 0.0
        state["socratic_level"] = 0
        state["vault_citation"] = None
        state["mastery_event"] = None
        return state

    score = await _compute_deviation(state["user_message"], state["persona_id"])
    state["deviation_score"] = score

    t = settings.DEVIATION_THRESHOLD
    if score < t:
        level = 0
    elif score < t + 0.1:
        level = 1
    elif score < t + 0.2:
        level = 2
    elif score < t + 0.3:
        level = 3
    else:
        level = 4

    if level > 0:
        concept_key = await _extract_concept_key(state["user_message"])
        if concept_key:
            ledger = await MasteryService.get_concept(state["persona_id"], concept_key)
            if ledger:
                if ledger.status == "struggling":
                    level = max(level, 2)
                if ledger.failure_count >= 5:
                    level = max(level, 3)
                fails = (state.get("session_snapshot") or {}).get("failure_counts", {})
                if fails.get(concept_key, 0) >= 3:
                    level = 4

    state["socratic_level"] = level
    state["vault_citation"] = (
        await retriever.get_citation(state["user_message"], state["persona_id"])
        if level >= 2
        else None
    )
    state["mastery_event"] = {
        "persona_id": state["persona_id"],
        "session_id": state["session_id"],
        "user_message": state["user_message"],
        "outcome": "correct" if level == 0 else "incorrect",
        "socratic_level": level,
    }
    return state


async def _compute_deviation(message: str, persona_id: str) -> float:
    """Compute deviation as inverse similarity to top vault result."""

    results = await retriever.query(message, persona_id, top_k=1)
    if not results:
        return 0.0
    return 1.0 - float(getattr(results[0], "score", 0.0))


async def _extract_concept_key(message: str) -> str | None:
    """Extract rough concept key from message for mastery tracking."""

    from services.ollama_service import ollama_service

    prompt = (
        "Extract the main technical concept from this message as a single snake_case identifier. "
        f"If no specific concept exists, respond with 'none'. Message: {message[:200]}"
    )
    result = await ollama_service.chat(
        model=settings.OLLAMA_MODEL,
        system="You extract concept keys.",
        message=prompt,
    )
    key = result.strip().lower().replace(" ", "_")
    return None if key == "none" else key[:50]
