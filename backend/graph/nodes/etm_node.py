"""Ethical Time Machine node for evolution context injection."""

from __future__ import annotations

from pathlib import Path

from core.config import settings
from core.utils import read_json
from graph.state import PMEState


async def etm_node(state: PMEState) -> PMEState:
    """Inject evolution note when user message matches evolved concepts."""

    state["etm_context"] = None
    state["etm_matched"] = False
    db_path = Path(settings.PERSONA_DIR) / state["persona_id"] / "evolution_db.json"
    entries = read_json(db_path, [])
    user_msg = state["user_message"].lower()
    for entry in entries:
        keywords = [entry.get("concept_key", ""), *entry.get("keywords", [])]
        if any(k and k.lower() in user_msg for k in keywords):
            state["etm_context"] = (
                f"EVOLUTION NOTE for persona: Regarding '{entry['concept_key']}': "
                f"Old advice (pre-{entry['evolution_year']}): {entry['old_advice']}. "
                f"Current evolved stance: {entry['new_advice']}. "
                "Frame this as your own growth — do not mention an AI filter."
            )
            state["etm_matched"] = True
            break
    return state
