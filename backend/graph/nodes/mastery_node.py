"""Background mastery processing node (not in LangGraph pipeline)."""

from __future__ import annotations

import json
import logging

from sqlalchemy import select

from core.database import AsyncSessionLocal
from graph.nodes.cert_node import cert_node
from models.mastery import MasteryLedger
from services.mastery_service import MasteryService


logger = logging.getLogger(__name__)


async def process_mastery_event(event: dict) -> None:
    """Update mastery ledger from socratic event in background."""

    try:
        persona_id = event["persona_id"]
        session_id = event["session_id"]
        user_message = event["user_message"]
        outcome = event["outcome"]

        from graph.nodes.socratic_node import _extract_concept_key

        concept_key = await _extract_concept_key(user_message)
        if not concept_key:
            return

        concept_label = concept_key.replace("_", " ").title()
        entry = await MasteryService.get_or_create(persona_id, concept_key, concept_label)
        new_score = MasteryService.compute_new_score(entry.mastery_score, outcome)
        sessions = json.loads(entry.sessions_tested or "[]")
        if session_id not in sessions:
            sessions.append(session_id)

        async with AsyncSessionLocal() as db:
            row = (
                await db.execute(select(MasteryLedger).where(MasteryLedger.concept_id == entry.concept_id))
            ).scalar_one()
            row.mastery_score = new_score
            row.status = MasteryService.compute_status(new_score, row.failure_count)
            row.encounter_count += 1
            if outcome == "correct":
                row.success_count += 1
            elif outcome == "incorrect":
                row.failure_count += 1
            row.sessions_tested = json.dumps(sessions)
            from core.utils import utcnow_iso

            row.last_tested = utcnow_iso()
            await db.commit()

        if await MasteryService.should_certify(persona_id, concept_key):
            await cert_node(persona_id, concept_key, concept_label, entry)
    except Exception as exc:
        logger.error("mastery_node background task failed: %s", exc, exc_info=True)
