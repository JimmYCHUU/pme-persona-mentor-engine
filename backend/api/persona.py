"""Persona API — CRUD endpoints for persona profiles."""

from fastapi import APIRouter
from models.schemas import PersonaCreate
from services.persona_service import PersonaService
from core.utils import generate_id, now_iso

router = APIRouter()


@router.post('/create', response_model=dict)
async def create_persona(req: PersonaCreate):
    """Create a new persona profile."""
    profile = {
        'persona_id': generate_id(),
        'name': req.name,
        'description': req.description,
        'sliders': req.sliders or {'abrasiveness': 50, 'proactivity': 50, 'explainDepth': 50},
        'soul': {},
        'gap_fill_answers': req.gap_fill_answers or {},
        'created_at': now_iso(),
    }
    await PersonaService.save(profile)
    return {'success': True, 'data': profile, 'error': None}


@router.get('/list', response_model=dict)
async def list_personas():
    """Return all saved persona profiles."""
    personas = await PersonaService.list_all()
    return {'success': True, 'data': personas, 'error': None}


@router.get('/{persona_id}', response_model=dict)
async def get_persona(persona_id: str):
    """Get a specific persona profile."""
    profile = await PersonaService.load(persona_id)
    if not profile:
        return {'success': False, 'data': None, 'error': 'Persona not found'}
    return {'success': True, 'data': profile, 'error': None}


@router.patch('/{persona_id}/sliders', response_model=dict)
async def update_sliders(persona_id: str, sliders: dict):
    """Update persona slider values."""
    await PersonaService.update_sliders(persona_id, sliders)
    return {'success': True, 'data': {'updated': True}, 'error': None}


@router.delete('/{persona_id}', response_model=dict)
async def delete_persona(persona_id: str):
    """Delete a persona and all its data."""
    deleted = await PersonaService.delete(persona_id)
    if not deleted:
        return {'success': False, 'data': None, 'error': 'Persona not found'}
    return {'success': True, 'data': {'deleted': True}, 'error': None}


@router.post('/create-pending', response_model=dict)
async def create_pending(req: dict):
    """
    Create a persona with status='pending' — returns an ID before ingestion.
    Used by PersonaBuilder step 1 so we have an ID to attach sources/files to.
    """
    profile = {
        'persona_id': generate_id(),
        'name': req.get('name', 'Unknown'),
        'domain': req.get('domain', ''),
        'description': '',
        'sliders': {'abrasiveness': 50, 'proactivity': 50, 'explainDepth': 50},
        'soul': {},
        'gap_fill_answers': {},
        'status': 'pending',
        'created_at': now_iso(),
    }
    await PersonaService.save(profile)
    return {'success': True, 'data': profile, 'error': None}


@router.post('/{persona_id}/activate', response_model=dict)
async def activate_persona(persona_id: str, req: dict):
    """
    Finalise a pending persona — sets status='active',
    saves sliders and gap_fill_answers, links ingestion jobs.
    """
    profile = await PersonaService.load(persona_id)
    if not profile:
        return {'success': False, 'data': None, 'error': 'Persona not found'}

    profile['status'] = 'active'
    profile['sliders'] = req.get('sliders', profile.get('sliders', {}))
    profile['gap_fill_answers'] = req.get('gap_fill_answers', profile.get('gap_fill_answers', {}))

    await PersonaService.save(profile)
    return {'success': True, 'data': profile, 'error': None}
