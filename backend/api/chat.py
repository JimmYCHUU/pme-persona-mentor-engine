"""Chat API — main conversation endpoint."""

from fastapi import APIRouter, BackgroundTasks
from graph.orchestrator import pme_graph
from graph.nodes.mastery_node import process_mastery_event
from models.schemas import ChatRequest
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/message', response_model=dict)
async def send_message(req: ChatRequest,
                       background_tasks: BackgroundTasks):
    """
    Main chat endpoint. Runs the full LangGraph pipeline.
    Triggers mastery_event processing as a BackgroundTask AFTER response.
    Returns: {success, data: ChatResponse, error}
    """
    initial_state = {
        'session_id': req.session_id or str(uuid.uuid4()),
        'persona_id': req.persona_id,
        'user_message': req.message,
        'workspace_event': None,
        'is_returning_user': False,
        'session_snapshot': None,
        'mastery_summary': None,
        'etm_context': None,
        'etm_matched': False,
        'deviation_score': 0.0,
        'socratic_level': 0,
        'vault_citation': None,
        'mastery_event': None,
        'raw_llm_response': '',
        'styled_response': '',
        'guardian_flagged': False,
        'final_response': '',
        'mode': req.mode or 'deep_dive',
    }

    try:
        result = await pme_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f'Graph execution failed: {e}', exc_info=True)
        return {'success': False, 'data': None, 'error': str(e)}

    # Debug: log key state fields
    final = result.get('final_response') or ''
    styled = result.get('styled_response') or ''
    raw = result.get('raw_llm_response') or ''

    if not final:
        logger.warning(
            f'Empty final_response! '
            f'styled_response="{styled[:100]}", '
            f'raw_llm_response="{raw[:100]}", '
            f'guardian_flagged={result.get("guardian_flagged")}'
        )
        # Fallback: use styled_response or raw_llm_response
        final = styled or raw or (
            'The AI provider is currently rate-limited (free tier). '
            'Please wait 30-60 seconds and try again.'
        )

    # Schedule mastery update as BackgroundTask (non-blocking)
    if result.get('mastery_event'):
        background_tasks.add_task(
            process_mastery_event, result['mastery_event']
        )

    return {
        'success': True,
        'data': {
            'response': final,
            'socratic_level': result.get('socratic_level', 0),
            'vault_citation': result.get('vault_citation'),
            'guardian_flagged': result.get('guardian_flagged', False),
            'session_id': result.get('session_id', ''),
        },
        'error': None,
    }
