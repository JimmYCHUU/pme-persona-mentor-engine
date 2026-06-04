"""Mastery service — tracks concept mastery across sessions.

Provides CRUD operations for the MasteryLedger and score management.
Uses configurable thresholds from settings for score increments.
"""
import uuid
import logging
from datetime import datetime, timezone
from core.config import settings
from core.database import AsyncSessionLocal
from models.mastery import MasteryLedger
from sqlalchemy import select

logger = logging.getLogger(__name__)


class MasteryService:
    """Tracks concept mastery across sessions."""

    async def record_encounter(
        self,
        persona_id: str,
        concept_key: str,
        concept_label: str,
    ) -> dict:
        """Record an encounter with a concept. Creates entry if first time."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            entry = result.scalar_one_or_none()

            if entry is None:
                # First encounter
                entry = MasteryLedger(
                    concept_id=f"{persona_id}_{concept_key}_{uuid.uuid4().hex[:8]}",
                    persona_id=persona_id,
                    concept_key=concept_key,
                    concept_label=concept_label,
                    status="encountered",
                    mastery_score=0.0,
                    encounter_count=1,
                    success_count=0,
                    failure_count=0,
                    first_seen=datetime.now(timezone.utc).isoformat(),
                    last_tested=datetime.now(timezone.utc).isoformat(),
                )
                db.add(entry)
                await db.commit()
                return {"status": "encountered", "concept_key": concept_key}
            else:
                entry.encounter_count += 1
                entry.last_tested = datetime.now(timezone.utc).isoformat()
                await db.commit()
                return {"status": entry.status, "concept_key": concept_key}

    async def record_success(
        self,
        persona_id: str,
        concept_key: str,
    ) -> dict:
        """Record a successful demonstration of a concept."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            entry = result.scalar_one_or_none()
            if entry is None:
                return {"status": "not_found", "concept_key": concept_key}

            entry.success_count += 1
            entry.mastery_score = min(
                1.0,
                entry.mastery_score + settings.MASTERY_SCORE_INCREMENT,
            )
            entry.last_tested = datetime.now(timezone.utc).isoformat()

            # Status transitions
            if entry.status == "encountered":
                entry.status = "attempted"
            if entry.mastery_score >= settings.MASTERY_CERT_THRESHOLD:
                entry.status = "mastered"

            await db.commit()
            return {"status": entry.status, "concept_key": concept_key}

    async def record_failure(
        self,
        persona_id: str,
        concept_key: str,
    ) -> dict:
        """Record a failure/misconception for a concept."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            entry = result.scalar_one_or_none()
            if entry is None:
                return {"status": "not_found", "concept_key": concept_key}

            entry.failure_count += 1
            entry.mastery_score = max(
                0.0,
                entry.mastery_score - settings.MASTERY_SCORE_DECREMENT,
            )
            entry.last_tested = datetime.now(timezone.utc).isoformat()

            # Status transitions
            if entry.status == "encountered":
                entry.status = "attempted"
            if entry.failure_count >= 3 and entry.mastery_score < 0.4:
                entry.status = "struggling"

            await db.commit()
            return {"status": entry.status, "concept_key": concept_key}

    async def get_summary(self, persona_id: str) -> dict | None:
        """Get mastery summary: top struggling, total counts, etc."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                )
            )
            entries = result.scalars().all()

        if not entries:
            return None

        struggling = [
            {"concept_key": e.concept_key, "failure_count": e.failure_count}
            for e in entries
            if e.status == "struggling"
        ]
        struggling.sort(key=lambda x: x["failure_count"], reverse=True)

        mastered = [e for e in entries if e.status == "mastered"]

        return {
            "total_concepts": len(entries),
            "mastered_count": len(mastered),
            "struggling_count": len(struggling),
            "top_struggling": struggling[:5],
            "new_certs_since_last_session": [],
        }

    @staticmethod
    async def get_all_concepts(persona_id: str) -> list:
        """Get all mastery entries for a persona."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                )
            )
            return result.scalars().all()

    @staticmethod
    async def get_struggling(persona_id: str) -> list:
        """Get struggling concepts for a persona."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.status == "struggling",
                )
            )
            return result.scalars().all()

    async def record_event(self, event: dict) -> None:
        """Record a mastery event (legacy interface)."""
        if not event:
            return
        persona_id = event.get("persona_id", "")
        for concept in event.get("concepts", []):
            key = concept.get("key", "")
            label = concept.get("label", key)
            outcome = concept.get("outcome", "encounter")

            await self.record_encounter(persona_id, key, label)
            if outcome == "success":
                await self.record_success(persona_id, key)
            elif outcome == "failure":
                await self.record_failure(persona_id, key)
