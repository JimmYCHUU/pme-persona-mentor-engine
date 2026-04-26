"""Mastery and certificate API routes."""

from __future__ import annotations

import json

from fastapi import APIRouter
from sqlalchemy import select

from core.database import AsyncSessionLocal
from models.mastery import MasteryCertificate, MasteryLedger


router = APIRouter()


@router.get("/{persona_id}/ledger", response_model=dict)
async def ledger(persona_id: str) -> dict:
    """Return all mastery ledger entries for persona."""

    async with AsyncSessionLocal() as db:
        rows = list((await db.execute(select(MasteryLedger).where(MasteryLedger.persona_id == persona_id))).scalars())
    data = [
        {
            "concept_id": r.concept_id,
            "concept_key": r.concept_key,
            "concept_label": r.concept_label,
            "status": r.status,
            "mastery_score": r.mastery_score,
            "encounter_count": r.encounter_count,
            "success_count": r.success_count,
            "failure_count": r.failure_count,
        }
        for r in rows
    ]
    return {"success": True, "data": data, "error": None}


@router.get("/{persona_id}/struggling", response_model=dict)
async def struggling(persona_id: str) -> dict:
    """Return struggling mastery ledger entries."""

    async with AsyncSessionLocal() as db:
        rows = list(
            (
                await db.execute(
                    select(MasteryLedger).where(
                        MasteryLedger.persona_id == persona_id,
                        MasteryLedger.status == "struggling",
                    )
                )
            ).scalars()
        )
    return {"success": True, "data": [r.concept_key for r in rows], "error": None}


@router.get("/{persona_id}/pending-certs", response_model=dict)
async def pending_certs(persona_id: str) -> dict:
    """Return undelivered certificates."""

    async with AsyncSessionLocal() as db:
        rows = list(
            (
                await db.execute(
                    select(MasteryCertificate).where(
                        MasteryCertificate.persona_id == persona_id,
                        MasteryCertificate.delivered == 0,
                    )
                )
            ).scalars()
        )
    data = [
        {
            "cert_id": r.cert_id,
            "persona_id": r.persona_id,
            "concept_key": r.concept_key,
            "concept_label": r.concept_label,
            "issued_at": r.issued_at,
            "mentor_statement": r.mentor_statement,
            "evidence_summary": json.loads(r.evidence_summary or "{}"),
            "delivered": r.delivered,
        }
        for r in rows
    ]
    return {"success": True, "data": data, "error": None}


@router.patch("/{persona_id}/cert/{cert_id}/delivered", response_model=dict)
async def mark_cert_delivered(persona_id: str, cert_id: str) -> dict:
    """Mark certificate as delivered."""

    async with AsyncSessionLocal() as db:
        row = (
            await db.execute(
                select(MasteryCertificate).where(
                    MasteryCertificate.persona_id == persona_id,
                    MasteryCertificate.cert_id == cert_id,
                )
            )
        ).scalar_one_or_none()
        if row is None:
            return {"success": False, "data": None, "error": "NOT_FOUND"}
        row.delivered = 1
        await db.commit()
    return {"success": True, "data": {"updated": True}, "error": None}
