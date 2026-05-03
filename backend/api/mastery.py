"""Mastery API — STUB for Phase 1. Full implementation in Phase 3."""

from fastapi import APIRouter

router = APIRouter()


@router.get('/{persona_id}/ledger', response_model=dict)
async def get_ledger(persona_id: str):
    """Stub: returns empty concepts list."""
    return {'success': True, 'data': {'concepts': []}, 'error': None}


@router.get('/{persona_id}/struggling', response_model=dict)
async def get_struggling(persona_id: str):
    """Stub: returns empty list."""
    return {'success': True, 'data': {'concepts': []}, 'error': None}


@router.get('/{persona_id}/pending-certs', response_model=dict)
async def get_pending_certs(persona_id: str):
    """Stub: returns empty certs list."""
    return {'success': True, 'data': {'certs': []}, 'error': None}


@router.patch('/{persona_id}/cert/{cert_id}/delivered', response_model=dict)
async def mark_cert_delivered(persona_id: str, cert_id: str):
    """Stub: returns success."""
    return {'success': True, 'data': {'delivered': True}, 'error': None}
