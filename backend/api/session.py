"""Session API — resume and save endpoints."""

from fastapi import APIRouter
from models.schemas import SessionSaveRequest
from services.session_service import SessionService
from services.ollama_service import ollama_service
from services.persona_service import PersonaService
from core.config import settings
from core.utils import generate_id

router = APIRouter()


@router.post('/resume', response_model=dict)
async def resume_session(body: dict):
    """Load last session snapshot and generate resume greeting."""
    persona_id = body.get('persona_id', '')
    snapshot = await SessionService.get_latest_for_persona(persona_id)

    if not snapshot:
        return {
            'success': True,
            'data': {'session_id': generate_id(), 'snapshot': None, 'resume_greeting': ''},
            'error': None,
        }

    # Generate resume greeting via LLM
    profile = await PersonaService.load(persona_id)
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
        greeting = await ollama_service.chat(
            model=settings.OLLAMA_MODEL,
            system=f'You are {mentor_name}.',
            message=greeting_prompt,
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
    await SessionService.save(snapshot)
    return {'success': True, 'data': {'saved': True}, 'error': None}
