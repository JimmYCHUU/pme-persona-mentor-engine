"""
Full mastery_node — processes mastery events as FastAPI BackgroundTask.
Updates mastery ledger based on Socratic outcomes.
"""

import logging
from services.mastery_service import MasteryService

logger = logging.getLogger(__name__)


async def process_mastery_event(event: dict) -> None:
    """
    Process a mastery event emitted by socratic_node.
    Called as a FastAPI BackgroundTask (never in the LangGraph pipeline).

    Event schema:
    {
        persona_id: str,
        session_id: str,
        user_message: str,
        outcome: 'correct' | 'incorrect',
        socratic_level: int,
    }
    """
    persona_id = event.get('persona_id', '')
    session_id = event.get('session_id', '')
    outcome = event.get('outcome', 'correct')

    if not persona_id or not session_id:
        logger.warning('mastery_node: missing persona_id or session_id')
        return

    # Extract concept key from the user message
    concept_key = await _extract_concept(event.get('user_message', ''))
    if not concept_key:
        logger.debug('mastery_node: no concept extracted, skipping')
        return

    try:
        # Update the ledger
        entry = await MasteryService.update_concept(
            persona_id=persona_id,
            concept_key=concept_key,
            outcome=outcome,
            session_id=session_id,
        )

        logger.info(
            f'mastery_node: updated {concept_key} for {persona_id} → '
            f'score={entry.mastery_score:.2f}, status={entry.status}'
        )

        # Check if certification is now eligible
        if await MasteryService.should_certify(persona_id, concept_key):
            logger.info(f'mastery_node: {concept_key} eligible for certification!')
            # cert_node will handle actual cert creation in Phase 4

    except Exception as e:
        logger.error(f'mastery_node: failed to update {concept_key}: {e}')


async def _extract_concept(user_message: str) -> str | None:
    """
    Extract concept key from user message.
    Reuses the socratic_node's extraction logic.
    """
    from graph.nodes.socratic_node import _extract_concept_key
    return await _extract_concept_key(user_message)
