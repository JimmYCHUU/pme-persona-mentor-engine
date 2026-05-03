"""
ETM node (Ethical Time Machine) — full implementation.
Checks evolution_db.json for concepts that have evolved.
Injects evolution context before socratic_node.
"""

import json
import os
from graph.state import PMEState
from core.config import settings


async def etm_node(state: PMEState) -> PMEState:
    """
    Checks evolution_db.json for concepts that have evolved.
    If the user's message mentions an evolved concept, injects
    evolution context so the persona_node can reference it.
    Runs BEFORE socratic_node. Sets etm_context and etm_matched.
    """
    state['etm_context'] = None
    state['etm_matched'] = False

    db_path = os.path.join(settings.PERSONA_DIR,
                           state['persona_id'], 'evolution_db.json')

    if not os.path.exists(db_path):
        return state

    try:
        with open(db_path) as f:
            evolution_db: list = json.load(f)
    except (json.JSONDecodeError, IOError):
        return state

    user_msg_lower = state['user_message'].lower()

    for entry in evolution_db:
        # Simple keyword match on concept_key and related terms
        keywords = [entry['concept_key']] + entry.get('keywords', [])
        if any(kw.lower() in user_msg_lower for kw in keywords):
            state['etm_context'] = (
                f"EVOLUTION NOTE for persona: Regarding '{entry['concept_key']}': "
                f"Old advice (pre-{entry['evolution_year']}): {entry['old_advice']}. "
                f"Current evolved stance: {entry['new_advice']}. "
                f"Frame this as your own growth - do not mention an AI filter."
            )
            state['etm_matched'] = True
            break  # only inject first matching evolution

    return state
