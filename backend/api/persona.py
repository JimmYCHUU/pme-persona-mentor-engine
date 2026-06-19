"""Persona API — CRUD endpoints for persona profiles."""

from fastapi import APIRouter
from models.schemas import PersonaCreate
from services.persona_service import PersonaService
from core.utils import generate_id, now_iso

router = APIRouter()
_svc = PersonaService()


@router.post('/create', response_model=dict)
async def create_persona(req: PersonaCreate):
    """Create a new persona profile with auto-generated system prompt."""
    persona_id = generate_id()

    # Auto-generate a system prompt from user-provided fields
    system_prompt = f"""You are {req.name} — a mentor specializing in {req.field}.

━━ YOUR IDENTITY ━━
{req.description if req.description else f'You are an expert in {req.field} who helps students learn through practical, hands-on teaching.'}

━━ YOUR TEACHING STYLE ━━
Your tone is: {req.tone}
You teach through clear explanations, practical examples, and guiding questions.
When the student is confused, you break concepts down into simpler parts.
When the student shows understanding, you challenge them to go deeper.

━━ YOUR APPROACH ━━
1. Always stay in character as {req.name}.
2. Use your authentic voice and personality in every response.
3. Reference real-world examples and practical applications.
4. Be {req.tone} in all interactions.
"""

    profile = {
        'id': persona_id,
        'persona_id': persona_id,
        'name': req.name,
        'description': req.description,
        'system_prompt': system_prompt,
        'profile': {
            'field': req.field,
            'sub_speciality': req.description[:100] if req.description else req.field,
            'best_for': [req.field],
            'personality_tags': [t.strip() for t in req.tone.split(',') if t.strip()],
        },
        'sliders': req.sliders or {'abrasiveness': 50, 'proactivity': 50, 'explainDepth': 50},
        'soul': {},
        'gap_fill_answers': req.gap_fill_answers or {},
        'created_at': now_iso(),
    }
    _svc._save(persona_id, profile)
    return {'success': True, 'data': profile, 'error': None}


@router.get('/list', response_model=dict)
async def list_personas():
    """Return all saved persona profiles."""
    personas = await _svc.list_personas()
    # Normalize: ensure each has persona_id field for frontend
    for p in personas:
        if 'persona_id' not in p:
            p['persona_id'] = p.get('id', '')
    return {'success': True, 'data': personas, 'error': None}


@router.get('/{persona_id}', response_model=dict)
async def get_persona(persona_id: str):
    """Get a specific persona profile."""
    profile = await _svc.get_persona(persona_id)
    if not profile:
        return {'success': False, 'data': None, 'error': 'Persona not found'}
    return {'success': True, 'data': profile, 'error': None}


@router.patch('/{persona_id}/sliders', response_model=dict)
async def update_sliders(persona_id: str, sliders: dict):
    """Update persona slider values."""
    profile = await _svc.get_persona(persona_id)
    if not profile:
        return {'success': False, 'data': None, 'error': 'Persona not found'}
    profile['sliders'] = sliders
    _svc._save(persona_id, profile)
    return {'success': True, 'data': {'updated': True}, 'error': None}


@router.delete('/{persona_id}', response_model=dict)
async def delete_persona(persona_id: str):
    """Delete a persona and all its data."""
    deleted = await _svc.delete_persona(persona_id)
    if not deleted:
        return {'success': False, 'data': None, 'error': 'Persona not found'}
    return {'success': True, 'data': {'deleted': True}, 'error': None}


@router.post('/create-pending', response_model=dict)
async def create_pending(req: dict):
    """
    Create a persona with status='pending' — returns an ID before ingestion.
    Used by PersonaBuilder step 1 so we have an ID to attach sources/files to.
    """
    persona_id = generate_id()
    profile = {
        'id': persona_id,
        'persona_id': persona_id,
        'name': req.get('name', 'Unknown'),
        'domain': req.get('domain', ''),
        'description': '',
        'sliders': {'abrasiveness': 50, 'proactivity': 50, 'explainDepth': 50},
        'soul': {},
        'gap_fill_answers': {},
        'status': 'pending',
        'created_at': now_iso(),
    }
    _svc._save(persona_id, profile)
    return {'success': True, 'data': profile, 'error': None}


@router.post('/{persona_id}/activate', response_model=dict)
async def activate_persona(persona_id: str, req: dict):
    """
    Finalise a pending persona — sets status='active',
    saves sliders and gap_fill_answers, links ingestion jobs.
    """
    profile = await _svc.get_persona(persona_id)
    if not profile:
        return {'success': False, 'data': None, 'error': 'Persona not found'}

    profile['status'] = 'active'
    profile['sliders'] = req.get('sliders', profile.get('sliders', {}))
    profile['gap_fill_answers'] = req.get('gap_fill_answers', profile.get('gap_fill_answers', {}))

    _svc._save(persona_id, profile)
    return {'success': True, 'data': profile, 'error': None}
