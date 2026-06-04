"""Cert node — Proof of Mastery certificate generation (ARCH-2).

Runs as BackgroundTask after mastery_node. Checks if any concepts
have crossed the mastery threshold and generates certificates.
"""
import json
import uuid
import logging
from datetime import datetime, timezone
from graph.state import PMEState
from core.config import settings
from core.database import AsyncSessionLocal
from models.mastery import MasteryLedger, MasteryCertificate
from services.llm_service import llm_service
from sqlalchemy import select

logger = logging.getLogger(__name__)

CERT_SYSTEM_PROMPT = """You are a mentor writing a short certificate statement for a student who has demonstrated mastery of a concept. Write 2-3 sentences acknowledging their achievement. Be warm, specific, and encouraging. Reference the concept by name."""


async def cert_node(state: PMEState) -> dict:
    """Issue Proof of Mastery certificates for concepts at threshold.

    Called as a BackgroundTask, not as a graph node (ARCH-2).
    Checks mastery_event concepts against thresholds.
    """
    mastery_event = state.get("mastery_event")
    if not mastery_event:
        return {}

    persona_id = mastery_event.get("persona_id", "")
    concepts = mastery_event.get("concepts", [])

    if not concepts or not persona_id:
        return {}

    try:
        async with AsyncSessionLocal() as db:
            for concept in concepts:
                if concept.get("outcome") != "success":
                    continue

                concept_key = concept.get("key", "")
                if not concept_key:
                    continue

                # Check mastery score
                result = await db.execute(
                    select(MasteryLedger).where(
                        MasteryLedger.persona_id == persona_id,
                        MasteryLedger.concept_key == concept_key,
                    )
                )
                entry = result.scalar_one_or_none()
                if entry is None:
                    continue

                # Check thresholds
                if entry.mastery_score < settings.MASTERY_CERT_THRESHOLD:
                    continue
                if entry.success_count < settings.MASTERY_CERT_MIN_SUCCESSES:
                    continue

                # Parse sessions_tested
                try:
                    sessions = json.loads(entry.sessions_tested or "[]")
                except (json.JSONDecodeError, TypeError):
                    sessions = []
                if len(sessions) < settings.MASTERY_CERT_MIN_SESSIONS:
                    continue

                # Check for existing cert
                cert_result = await db.execute(
                    select(MasteryCertificate).where(
                        MasteryCertificate.persona_id == persona_id,
                        MasteryCertificate.concept_key == concept_key,
                    )
                )
                existing_cert = cert_result.scalar_one_or_none()
                if existing_cert:
                    continue

                # Generate mentor statement
                try:
                    statement = await llm_service.chat(
                        message=f"Write a certificate statement for mastering: {entry.concept_label}",
                        system=CERT_SYSTEM_PROMPT,
                    )
                except Exception:
                    statement = f"Congratulations on mastering {entry.concept_label}!"

                # Create certificate
                cert = MasteryCertificate(
                    cert_id=f"cert_{uuid.uuid4().hex[:12]}",
                    persona_id=persona_id,
                    concept_key=concept_key,
                    concept_label=entry.concept_label,
                    issued_at=datetime.now(timezone.utc).isoformat(),
                    mentor_statement=statement,
                    evidence_summary=json.dumps({
                        "sessions_tested": len(sessions),
                        "success_count": entry.success_count,
                        "failure_count": entry.failure_count,
                        "mastery_score": entry.mastery_score,
                    }),
                    delivered=0,
                )
                db.add(cert)
                await db.commit()
                logger.info(f"Cert issued for {persona_id}/{concept_key}")

    except Exception as e:
        logger.warning(f"Cert generation failed: {e}")

    return {}
