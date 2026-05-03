"""Full MasteryService — manages mastery ledger and scoring."""

import json
from typing import Optional
from core.config import settings
from core.database import AsyncSessionLocal
from core.utils import generate_id, now_iso
from models.mastery import MasteryLedger, MasteryCertificate
from sqlalchemy import select


class MasteryService:
    """
    Manages mastery tracking: ledger CRUD, scoring, status computation,
    and certification eligibility checks.
    """

    @staticmethod
    async def get_or_create(persona_id: str, concept_key: str,
                            concept_label: str = '') -> MasteryLedger:
        """Get existing ledger entry or create a new one."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            entry = result.scalar_one_or_none()

            if not entry:
                entry = MasteryLedger(
                    concept_id=generate_id(),
                    persona_id=persona_id,
                    concept_key=concept_key,
                    concept_label=concept_label or concept_key.replace('_', ' ').title(),
                    status='encountered',
                    mastery_score=0.0,
                    encounter_count=0,
                    success_count=0,
                    failure_count=0,
                    sessions_tested='[]',
                    first_seen=now_iso(),
                    last_tested=now_iso(),
                    vault_sources='[]',
                )
                db.add(entry)
                await db.commit()
                await db.refresh(entry)

            return entry

    @staticmethod
    def compute_new_score(current: float, outcome: str) -> float:
        """
        Compute new mastery score.
        correct: +MASTERY_SCORE_INCREMENT
        incorrect: -MASTERY_SCORE_DECREMENT
        Clamped to [0.0, 1.0]
        """
        if outcome == 'correct':
            new_score = current + settings.MASTERY_SCORE_INCREMENT
        else:
            new_score = current - settings.MASTERY_SCORE_DECREMENT
        return max(0.0, min(1.0, new_score))

    @staticmethod
    def compute_status(score: float, failure_count: int) -> str:
        """
        Determine mastery status from score and failures.
        mastered: score >= 0.8
        struggling: failure_count >= 3 and score < 0.5
        attempted: score > 0 but not mastered/struggling
        encountered: score == 0
        """
        if score >= settings.MASTERY_CERT_THRESHOLD:
            return 'mastered'
        if failure_count >= 3 and score < 0.5:
            return 'struggling'
        if score > 0.0:
            return 'attempted'
        return 'encountered'

    @staticmethod
    async def update_concept(persona_id: str, concept_key: str,
                             outcome: str, session_id: str) -> MasteryLedger:
        """
        Update a concept entry based on the outcome of an interaction.
        Called by mastery_node as a BackgroundTask.
        """
        entry = await MasteryService.get_or_create(persona_id, concept_key)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.concept_id == entry.concept_id,
                )
            )
            entry = result.scalar_one()

            entry.encounter_count += 1
            if outcome == 'correct':
                entry.success_count += 1
            else:
                entry.failure_count += 1

            entry.mastery_score = MasteryService.compute_new_score(
                entry.mastery_score, outcome
            )
            entry.status = MasteryService.compute_status(
                entry.mastery_score, entry.failure_count
            )
            entry.last_tested = now_iso()

            # Update sessions_tested list
            sessions = json.loads(entry.sessions_tested or '[]')
            if session_id not in sessions:
                sessions.append(session_id)
            entry.sessions_tested = json.dumps(sessions)

            await db.commit()
            await db.refresh(entry)
            return entry

    @staticmethod
    async def should_certify(persona_id: str, concept_key: str) -> bool:
        """
        Check if a concept is eligible for certification.
        Requires: score >= threshold, min sessions, min successes, no existing cert.
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            entry = result.scalar_one_or_none()

            if not entry:
                return False

            if entry.mastery_score < settings.MASTERY_CERT_THRESHOLD:
                return False

            sessions = json.loads(entry.sessions_tested or '[]')
            if len(sessions) < settings.MASTERY_CERT_MIN_SESSIONS:
                return False

            if entry.success_count < settings.MASTERY_CERT_MIN_SUCCESSES:
                return False

            # Check no existing cert
            cert_result = await db.execute(
                select(MasteryCertificate).where(
                    MasteryCertificate.persona_id == persona_id,
                    MasteryCertificate.concept_key == concept_key,
                )
            )
            existing = cert_result.scalar_one_or_none()
            return existing is None

    @staticmethod
    async def get_summary(persona_id: str) -> dict:
        """
        Get a summary of all mastery concepts for a persona.
        Used by memory_node to inject mastery context.
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                )
            )
            entries = result.scalars().all()

            struggling = [
                {'concept_key': e.concept_key, 'failure_count': e.failure_count}
                for e in entries if e.status == 'struggling'
            ]
            mastered = [e.concept_key for e in entries if e.status == 'mastered']

            return {
                'total_concepts': len(entries),
                'struggling': struggling,
                'mastered': mastered,
            }

    @staticmethod
    async def get_concept(persona_id: str, concept_key: str) -> Optional[MasteryLedger]:
        """Get a single concept entry."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.concept_key == concept_key,
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_all_concepts(persona_id: str) -> list[MasteryLedger]:
        """Get all concept entries for a persona."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                ).order_by(MasteryLedger.last_tested.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_struggling(persona_id: str) -> list[MasteryLedger]:
        """Get all struggling concepts for a persona."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MasteryLedger).where(
                    MasteryLedger.persona_id == persona_id,
                    MasteryLedger.status == 'struggling',
                ).order_by(MasteryLedger.failure_count.desc())
            )
            return list(result.scalars().all())
