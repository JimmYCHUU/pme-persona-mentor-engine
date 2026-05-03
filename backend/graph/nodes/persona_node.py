"""Persona node — loads persona profile, builds system prompt, calls LLM."""

from graph.state import PMEState
from services.persona_service import PersonaService
from services.ollama_service import ollama_service
from core.config import settings


async def persona_node(state: PMEState) -> PMEState:
    """
    Loads the persona profile, builds the style-transfer system prompt,
    calls OllamaService, and stores the styled response.
    The persona changes HOW the answer is expressed, not WHAT it says.
    """
    profile = await PersonaService.load(state['persona_id'])

    if not profile:
        profile = {
            'name': 'Mentor',
            'description': 'A knowledgeable mentor.',
            'soul': {},
            'sliders': {},
        }

    system_prompt = _build_system_prompt(
        profile=profile,
        socratic_level=state['socratic_level'],
        vault_citation=state.get('vault_citation'),
        etm_context=state.get('etm_context'),
        mode=state['mode'],
    )

    history = []
    if state.get('session_snapshot'):
        history = state['session_snapshot'].get('chat_history', [])
        history = [{'role': m['role'], 'content': m['content']}
                   for m in history[-20:]]  # last 20 turns max

    response = await ollama_service.chat(
        model=settings.OLLAMA_MODEL,
        system=system_prompt,
        message=state['user_message'],
        history=history,
    )

    state['raw_llm_response'] = response
    state['styled_response'] = response

    return state


def _build_system_prompt(profile: dict, socratic_level: int,
                         vault_citation: str | None,
                         etm_context: str | None,
                         mode: str) -> str:
    """
    Constructs the full system prompt for this interaction.
    ORDERING: persona identity → style rules → ETM context → socratic instruction.
    """
    soul = profile.get('soul', {})
    sliders = profile.get('sliders', {})
    abrasiveness = sliders.get('abrasiveness', 50)
    explain_depth = sliders.get('explainDepth', 50)

    few_shots = '\n'.join([
        f"User: {ex['user']}\n{profile['name']}: {ex['mentor']}"
        for ex in soul.get('few_shot_examples', [])[:12]
    ])

    socratic_instruction = ''
    if socratic_level == 0 or mode == 'friend_mode':
        socratic_instruction = 'Respond naturally.'
    elif socratic_level == 1:
        socratic_instruction = ('Ask ONE probing question about the fundamental constraint. '
                                'Do NOT name the error. Do NOT give the answer.')
    elif socratic_level == 2:
        citation_ref = vault_citation or 'a relevant concept from your knowledge'
        socratic_instruction = f'Reference this source: {citation_ref}. Point to it. Do not explain it.'
    elif socratic_level == 3:
        socratic_instruction = ('Explain the consequence of the current approach. '
                                f"Be {'very blunt' if abrasiveness > 70 else 'direct'}. "
                                'Still do NOT give the fix.')
    elif socratic_level == 4:
        socratic_instruction = ('Give the direct solution. Then immediately ask: '
                                '"Now tell me WHY that works."')

    etm_section = f'\n\nEVOLUTION CONTEXT:\n{etm_context}' if etm_context else ''

    return f"""You are {profile['name']}.

PERSONALITY:
{profile.get('description', '')}

YOUR COMMUNICATION RULES:
- Abrasiveness level: {abrasiveness}/100 (0=gentle professor, 100=drill sergeant)
- Explain depth: {explain_depth}/100 (0=just do it, 100=explain everything)
- You are NEVER polite for politeness sake.
- You speak from your own worldview and biases.
- You do NOT identify as an AI.
- {'This is a casual conversation. Relax. Be yourself.' if mode == 'friend_mode' else 'The user is in a focused learning session.'}

YOUR VOCABULARY AND STYLE (examples of how YOU speak):
{few_shots}

YOUR PHILOSOPHY (rules you live by):
{chr(10).join(soul.get('philosophy_tags', []))}
{etm_section}

CURRENT INSTRUCTION FOR THIS RESPONSE:
{socratic_instruction}"""
