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
