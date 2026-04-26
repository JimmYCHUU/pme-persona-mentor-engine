import json
import uuid

import pytest
from sqlalchemy import delete

from core.config import settings
from core.database import AsyncSessionLocal
from models.mastery import MasteryCertificate, MasteryLedger
from services.mastery_service import MasteryService


def _ledger(
    *,
    persona_id: str,
    concept_key: str,
    score: float,
    sessions: int,
    successes: int,
) -> MasteryLedger:
    return MasteryLedger(
        concept_id=str(uuid.uuid4()),
        persona_id=persona_id,
        concept_key=concept_key,
        concept_label="Test Concept",
        status="attempted",
        mastery_score=score,
        encounter_count=max(successes, sessions),
        success_count=successes,
        failure_count=0,
        sessions_tested=json.dumps([f"s{i}" for i in range(sessions)]),
        vault_sources="[]",
    )


@pytest.mark.asyncio
async def test_cert_not_issued_when_score_below_threshold() -> None:
    persona_id = "p-cert-low-score"
    concept_key = "tcp_handshake"
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MasteryCertificate).where(MasteryCertificate.persona_id == persona_id))
        await db.execute(delete(MasteryLedger).where(MasteryLedger.persona_id == persona_id))
        db.add(_ledger(persona_id=persona_id, concept_key=concept_key, score=settings.MASTERY_CERT_THRESHOLD - 0.01, sessions=3, successes=5))
        await db.commit()

    assert await MasteryService.should_certify(persona_id, concept_key) is False


@pytest.mark.asyncio
async def test_cert_not_issued_when_sessions_below_minimum() -> None:
    persona_id = "p-cert-low-sessions"
    concept_key = "recursion"
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MasteryCertificate).where(MasteryCertificate.persona_id == persona_id))
        await db.execute(delete(MasteryLedger).where(MasteryLedger.persona_id == persona_id))
        db.add(_ledger(persona_id=persona_id, concept_key=concept_key, score=settings.MASTERY_CERT_THRESHOLD, sessions=settings.MASTERY_CERT_MIN_SESSIONS - 1, successes=10))
        await db.commit()

    assert await MasteryService.should_certify(persona_id, concept_key) is False


@pytest.mark.asyncio
async def test_cert_not_issued_when_successes_below_minimum() -> None:
    persona_id = "p-cert-low-success"
    concept_key = "asyncio"
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MasteryCertificate).where(MasteryCertificate.persona_id == persona_id))
        await db.execute(delete(MasteryLedger).where(MasteryLedger.persona_id == persona_id))
        db.add(_ledger(persona_id=persona_id, concept_key=concept_key, score=settings.MASTERY_CERT_THRESHOLD, sessions=settings.MASTERY_CERT_MIN_SESSIONS + 1, successes=settings.MASTERY_CERT_MIN_SUCCESSES - 1))
        await db.commit()

    assert await MasteryService.should_certify(persona_id, concept_key) is False


@pytest.mark.asyncio
async def test_cert_issued_when_all_conditions_met() -> None:
    persona_id = "p-cert-ready"
    concept_key = "sql_transactions"
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MasteryCertificate).where(MasteryCertificate.persona_id == persona_id))
        await db.execute(delete(MasteryLedger).where(MasteryLedger.persona_id == persona_id))
        db.add(_ledger(persona_id=persona_id, concept_key=concept_key, score=settings.MASTERY_CERT_THRESHOLD, sessions=settings.MASTERY_CERT_MIN_SESSIONS + 1, successes=settings.MASTERY_CERT_MIN_SUCCESSES))
        await db.commit()

    assert await MasteryService.should_certify(persona_id, concept_key) is True


@pytest.mark.asyncio
async def test_cert_not_issued_if_already_exists() -> None:
    persona_id = "p-cert-existing"
    concept_key = "threading"
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MasteryCertificate).where(MasteryCertificate.persona_id == persona_id))
        await db.execute(delete(MasteryLedger).where(MasteryLedger.persona_id == persona_id))
        db.add(_ledger(persona_id=persona_id, concept_key=concept_key, score=settings.MASTERY_CERT_THRESHOLD + 0.05, sessions=settings.MASTERY_CERT_MIN_SESSIONS + 1, successes=settings.MASTERY_CERT_MIN_SUCCESSES + 1))
        db.add(
            MasteryCertificate(
                cert_id=str(uuid.uuid4()),
                persona_id=persona_id,
                concept_key=concept_key,
                concept_label="Threading",
                issued_at="2026-01-01T00:00:00",
                mentor_statement="Already certified.",
                evidence_summary="{}",
                cert_json_path="/tmp/threading.json",
                delivered=0,
            )
        )
        await db.commit()

    assert await MasteryService.should_certify(persona_id, concept_key) is False
