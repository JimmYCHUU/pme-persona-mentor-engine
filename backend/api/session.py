"""Session API — resume and save endpoints."""

from fastapi import APIRouter
from models.schemas import SessionSaveRequest
from services.session_service import SessionService
from services.llm_service import llm_service
from services.persona_service import PersonaService
from core.utils import generate_id

router = APIRouter()
_session_svc = SessionService()
_persona_svc = PersonaService()


@router.post('/resume', response_model=dict)
async def resume_session(body: dict):
    """Load last session snapshot and generate resume greeting."""
    persona_id = body.get('persona_id', '')

    # Find latest session for this persona
    sessions = await _session_svc.list_sessions(persona_id)
    snapshot = sessions[-1] if sessions else None

    if not snapshot:
        return {
            'success': True,
            'data': {'session_id': generate_id(), 'snapshot': None, 'resume_greeting': ''},
            'error': None,
        }

    # Generate resume greeting via LLM
    profile = await _persona_svc.get_persona(persona_id)
    mentor_name = profile['name'] if profile else 'Mentor'
    summary = snapshot.get('mentor_assessment', {}).get('summary', 'your last session')
    next_steps = snapshot.get('mentor_assessment', {}).get('next_steps', [])

    greeting_prompt = (
        f"You are {mentor_name}. The user is returning. "
        f"Last session summary: {summary}. "
        f"Next steps from last time: {', '.join(next_steps[:3])}. "
        f"Greet them in your authentic voice. Be authoritative. "
        f"Tell them what needs to be done. Do not ask 'How can I help?'"
    )

    try:
        greeting = await llm_service.chat(
            message=greeting_prompt,
            system=f'You are {mentor_name}.',
            use_reasoning=False,
        )
    except Exception:
        greeting = f"Welcome back. Let's continue where we left off."

    return {
        'success': True,
        'data': {
            'session_id': snapshot.get('session_id', generate_id()),
            'snapshot': snapshot,
            'resume_greeting': greeting,
        },
        'error': None,
    }


@router.post('/save', response_model=dict)
async def save_session(req: SessionSaveRequest):
    """Save current session snapshot."""
    snapshot = req.snapshot
    snapshot['session_id'] = req.session_id
    snapshot['persona_id'] = req.persona_id
    _session_svc._save(req.session_id, snapshot)
    return {'success': True, 'data': {'saved': True}, 'error': None}
