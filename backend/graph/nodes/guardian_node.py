"""Guardian node safety rewrite with lazy classifier loading."""

from __future__ import annotations

import logging

from core.config import settings
from graph.state import PMEState


logger = logging.getLogger(__name__)
FLAGGED_CATEGORIES = ["illegal_instruction", "dangerous_technical", "pii_leak"]
_classifier = None


def _get_classifier():
    """Lazy-load DistilBERT classifier on first use."""

    global _classifier
    if _classifier is None:
        from transformers import pipeline

        _classifier = pipeline("text-classification", model=settings.GUARDIAN_MODEL, device=-1)
    return _classifier


async def guardian_node(state: PMEState) -> PMEState:
    """Run classifier and rewrite flagged output in-character if needed."""

    try:
        clf = _get_classifier()
        result = clf(state["styled_response"][:512])
        label = result[0]["label"]
        is_flagged = label in FLAGGED_CATEGORIES
    except Exception as exc:
        logger.error("Guardian classifier failed: %s", exc)
        state["guardian_flagged"] = False
        state["final_response"] = state["styled_response"]
        return state

    state["guardian_flagged"] = is_flagged
    if is_flagged:
        from services.ollama_service import ollama_service
        from services.persona_service import PersonaService

        profile = await PersonaService.load(state["persona_id"])
        rewrite_prompt = (
            f"The following advice was flagged as potentially harmful. Rewrite it entirely in the voice of {profile.get('name', 'Mentor')} "
            "to redirect to a safe, legal alternative. Frame it as your own evolved thinking — "
            "'I used to do X, but I learned better.' Do NOT say 'I cannot help'. Do NOT mention AI safety.\n\n"
            f"Original: {state['styled_response']}"
        )
        state["styled_response"] = await ollama_service.chat(
            model=settings.OLLAMA_MODEL,
            system=f"You are {profile.get('name', 'Mentor')}. Respond only as that person.",
            message=rewrite_prompt,
        )

    state["final_response"] = state["styled_response"]
    return state
