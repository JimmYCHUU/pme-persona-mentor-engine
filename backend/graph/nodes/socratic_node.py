"""
Socratic node — full implementation.
Computes deviation, selects Socratic Ladder level with mastery awareness,
fetches vault citation, and emits mastery_event for background processing.
"""

from graph.state import PMEState
from rag.retriever import retriever
from services.mastery_service import MasteryService
from core.config import settings

SOCRATIC_PROMPTS = {
    0: None,  # silent
    1: ('Ask ONE probing question about the fundamental constraint. '
        'Do NOT name the error. Do NOT give the answer.'),
    2: ('Reference a SPECIFIC piece of vault content relevant to the problem. '
        'Point to it without explaining it. Ask if they remember it.'),
    3: ('Explain the CONSEQUENCE of what the user is doing. '
        'Still do NOT give the fix.'),
    4: ('Give the direct solution. Then immediately ask: '
        '"Now tell me WHY that works." Do not move on until they answer.'),
}


async def socratic_node(state: PMEState) -> PMEState:
    """
    Computes deviation score, selects Socratic Ladder level,
    fetches vault citation if needed, emits mastery_event.
    """
    # In Friend Mode: always silent, no Socratic intervention
    if state['mode'] == 'friend_mode':
        state['deviation_score'] = 0.0
        state['socratic_level'] = 0
        state['vault_citation'] = None
        state['mastery_event'] = None
        return state

    # 1. Embed user message and compute deviation
    score = await _compute_deviation(
        state['user_message'], state['persona_id']
    )
    state['deviation_score'] = score

    # 2. Determine base ladder level from deviation score
    threshold = settings.DEVIATION_THRESHOLD
    if score < threshold:
        base_level = 0
    elif score < threshold + 0.1:
        base_level = 1
    elif score < threshold + 0.2:
        base_level = 2
    elif score < threshold + 0.3:
        base_level = 3
    else:
        base_level = 4

    # 3. Mastery-aware adjustment (only if deviation triggered)
    if base_level > 0:
        concept_key = await _extract_concept_key(state['user_message'])
        if concept_key:
            ledger_entry = await MasteryService.get_concept(
                state['persona_id'], concept_key
            )
            if ledger_entry:
                if hasattr(ledger_entry, 'status') and ledger_entry.status == 'struggling':
                    base_level = max(base_level, 2)  # skip level 1
                if hasattr(ledger_entry, 'failure_count') and ledger_entry.failure_count >= 5:
                    base_level = max(base_level, 3)  # skip to critique

            # Check per-session failure count for level 4
            snapshot = state.get('session_snapshot') or {}
            session_failures = snapshot.get('failure_counts', {})
            if session_failures.get(concept_key, 0) >= 3:
                base_level = 4

    state['socratic_level'] = base_level

    # 4. Fetch vault citation for levels 2+
    if base_level >= 2:
        citation = await retriever.get_citation(
            state['user_message'], state['persona_id']
        )
        state['vault_citation'] = citation
    else:
        state['vault_citation'] = None

    # 5. Emit mastery_event for BackgroundTask
    outcome = 'correct' if base_level == 0 else 'incorrect'
    state['mastery_event'] = {
        'persona_id': state['persona_id'],
        'session_id': state['session_id'],
        'user_message': state['user_message'],
        'outcome': outcome,
        'socratic_level': base_level,
    }

    return state


async def _compute_deviation(message: str, persona_id: str) -> float:
    """
    Embeds the user message and computes cosine distance from vault gold standard.
    Returns a float 0.0 (no deviation) to 1.0 (maximum deviation).
    """
    results = await retriever.query(message, persona_id, top_k=1)
    if not results:
        return 0.0  # no vault data = no deviation judgment possible
    similarity = results[0].score  # cosine similarity 0-1
    return 1.0 - similarity  # deviation = inverse of similarity


async def _extract_concept_key(message: str) -> str | None:
    """
    Extracts a simple concept key from the user message via a short LLM call.
    Returns a snake_case key like 'tcp_handshake' or None if no concept found.
    """
    from services.ollama_service import ollama_service
    from core.config import settings

    prompt = (
        f"Extract the main technical concept from this message as a single "
        f"snake_case identifier (e.g. 'tcp_handshake', 'buffer_overflow'). "
        f"If no specific concept, respond with 'none'. Message: {message[:200]}"
    )

    try:
        result = await ollama_service.chat(
            model=settings.OLLAMA_MODEL,
            system='You extract concept keys. Respond with only the key, nothing else.',
            message=prompt
        )
        key = result.strip().lower().replace(' ', '_')
        return None if key == 'none' else key[:50]
    except Exception:
        return None
