"""Mastery API — full implementation with ledger, struggling, and cert endpoints."""

from fastapi import APIRouter
from services.mastery_service import MasteryService

router = APIRouter()


@router.get('/{persona_id}/ledger', response_model=dict)
async def get_ledger(persona_id: str):
    """Return all mastery concepts for a persona."""
    entries = await MasteryService.get_all_concepts(persona_id)
    concepts = [
        {
            'concept_id': e.concept_id,
            'concept_key': e.concept_key,
            'concept_label': e.concept_label,
            'status': e.status,
            'mastery_score': e.mastery_score,
            'encounter_count': e.encounter_count,
            'success_count': e.success_count,
            'failure_count': e.failure_count,
        }
        for e in entries
    ]
    return {'success': True, 'data': {'concepts': concepts}, 'error': None}


@router.get('/{persona_id}/struggling', response_model=dict)
async def get_struggling(persona_id: str):
    """Return all struggling concepts for a persona."""
    entries = await MasteryService.get_struggling(persona_id)
    concepts = [
        {
            'concept_id': e.concept_id,
            'concept_key': e.concept_key,
            'concept_label': e.concept_label,
            'mastery_score': e.mastery_score,
            'failure_count': e.failure_count,
        }
        for e in entries
    ]
    return {'success': True, 'data': {'concepts': concepts}, 'error': None}


@router.get('/{persona_id}/pending-certs', response_model=dict)
async def get_pending_certs(persona_id: str):
    """Return all undelivered certificates for a persona."""
    from core.database import AsyncSessionLocal
    from models.mastery import MasteryCertificate
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MasteryCertificate).where(
                MasteryCertificate.persona_id == persona_id,
                MasteryCertificate.delivered == 0,
            )
        )
        certs = result.scalars().all()

    cert_data = [
        {
            'cert_id': c.cert_id,
            'persona_id': c.persona_id,
            'concept_key': c.concept_key,
            'concept_label': c.concept_label,
            'issued_at': c.issued_at,
            'mentor_statement': c.mentor_statement,
            'evidence_summary': c.evidence_summary,
            'delivered': c.delivered,
        }
        for c in certs
    ]
    return {'success': True, 'data': {'certs': cert_data}, 'error': None}


@router.patch('/{persona_id}/cert/{cert_id}/delivered', response_model=dict)
async def mark_cert_delivered(persona_id: str, cert_id: str):
    """Mark a certificate as delivered (shown to user)."""
    from core.database import AsyncSessionLocal
    from models.mastery import MasteryCertificate
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MasteryCertificate).where(
                MasteryCertificate.cert_id == cert_id,
            )
        )
        cert = result.scalar_one_or_none()
        if cert:
            cert.delivered = 1
            await db.commit()
            return {'success': True, 'data': {'delivered': True}, 'error': None}
        return {'success': False, 'data': None, 'error': 'Cert not found'}
