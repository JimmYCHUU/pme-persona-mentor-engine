"""Chat API — main conversation endpoint."""

from fastapi import APIRouter, BackgroundTasks
from graph.orchestrator import pme_graph
from graph.nodes.mastery_node import process_mastery_event
from models.schemas import ChatRequest
import uuid

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
        return {'success': False, 'data': None, 'error': str(e)}

    # Schedule mastery update as BackgroundTask (non-blocking)
    if result.get('mastery_event'):
        background_tasks.add_task(
            process_mastery_event, result['mastery_event']
        )

    return {
        'success': True,
        'data': {
            'response': result['final_response'],
            'socratic_level': result['socratic_level'],
            'vault_citation': result.get('vault_citation'),
            'guardian_flagged': result['guardian_flagged'],
            'session_id': result['session_id'],
        },
        'error': None,
    }
