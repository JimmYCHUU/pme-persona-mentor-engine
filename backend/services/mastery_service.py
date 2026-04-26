"""Mastery ledger business logic and certification checks."""

from __future__ import annotations

import json
import uuid

from sqlalchemy import select

from core.config import settings
from core.database import AsyncSessionLocal
from models.mastery import MasteryCertificate, MasteryLedger


SCORE_INCREMENT = settings.MASTERY_SCORE_INCREMENT
SCORE_DECREMENT = settings.MASTERY_SCORE_DECREMENT


class MasteryService:
    """Service methods for mastery updates and summarization."""

    @staticmethod
    async def get_or_create(persona_id: str, concept_key: str, concept_label: str) -> MasteryLedger:
        """Return existing concept ledger row or create defaults."""

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = MasteryLedger(
                    concept_id=str(uuid.uuid4()),
                    persona_id=persona_id,
                    concept_key=concept_key,
                    concept_label=concept_label,
                    status="encountered",
                    mastery_score=0.0,
                    sessions_tested="[]",
                    vault_sources="[]",
                )
                db.add(row)
                await db.commit()
                await db.refresh(row)
            return row

    @staticmethod
    def compute_new_score(current: float, outcome: str) -> float:
        """Compute deterministic updated score for correct/incorrect/partial outcomes."""

        if outcome == "correct":
            delta = SCORE_INCREMENT
        elif outcome == "incorrect":
            delta = -SCORE_DECREMENT
        else:
            delta = SCORE_INCREMENT * 0.5
        return max(0.0, min(1.0, current + delta))

    @staticmethod
    def compute_status(score: float, failure_count: int) -> str:
        """Compute status label from score and repeated failures."""

        if score >= settings.MASTERY_CERT_THRESHOLD:
            return "mastered"
        if score < 0.4 and failure_count >= 3:
            return "struggling"
        if score >= 0.2:
            return "attempted"
        return "encountered"

    @staticmethod
    async def should_certify(persona_id: str, concept_key: str) -> bool:
        """Return True when all certification thresholds are met."""

        async with AsyncSessionLocal() as db:
            res = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            ledger = res.scalar_one_or_none()
            if ledger is None:
                return False
            cert_res = await db.execute(
                select(MasteryCertificate).where(
                    MasteryCertificate.persona_id == persona_id,
                    MasteryCertificate.concept_key == concept_key,
                )
            )
            if cert_res.scalar_one_or_none() is not None:
                return False
            sessions = json.loads(ledger.sessions_tested or "[]")
            return (
                ledger.mastery_score >= settings.MASTERY_CERT_THRESHOLD
                and len(sessions) >= settings.MASTERY_CERT_MIN_SESSIONS
                and ledger.success_count >= settings.MASTERY_CERT_MIN_SUCCESSES
            )

    @staticmethod
    async def get_concept(persona_id: str, concept_key: str) -> MasteryLedger | None:
        """Fetch one ledger concept by persona and concept key."""

        async with AsyncSessionLocal() as db:
            res = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            return res.scalar_one_or_none()

    @staticmethod
    async def get_summary(persona_id: str) -> dict:
        """Return summary payload used by memory node and resume UI."""

        async with AsyncSessionLocal() as db:
            ledgers = list(
                (
                    await db.execute(select(MasteryLedger).where(MasteryLedger.persona_id == persona_id))
                ).scalars()
            )
            pending = list(
                (
                    await db.execute(
                        select(MasteryCertificate).where(
                            MasteryCertificate.persona_id == persona_id,
                            MasteryCertificate.delivered == 0,
                        )
                    )
                ).scalars()
            )
        struggling = [l.concept_label for l in ledgers if l.status == "struggling"]
        return {
            "top_struggling": struggling[:5],
            "new_certs": [c.concept_label for c in pending],
        }
