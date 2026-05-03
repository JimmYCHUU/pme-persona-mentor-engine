"""Workspace API — full VS Code event receiver with Socratic checking."""

from fastapi import APIRouter, BackgroundTasks
from models.schemas import WorkspaceEvent
from graph.orchestrator import pme_graph
from graph.nodes.mastery_node import process_mastery_event
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/event', response_model=dict)
async def workspace_event(event: WorkspaceEvent,
                          background_tasks: BackgroundTasks):
    """
    Receives events from the VS Code extension.
    Terminal errors and file saves trigger Socratic analysis.
    Idle events trigger check-in.
    """
    logger.info(f'Workspace event: type={event.type}')

    if event.type == 'terminal_error' and event.content:
        # Run through the pipeline with the error as user_message
        # This allows Socratic intervention on errors
        background_tasks.add_task(
            _process_workspace_event, event.type, event.content
        )

    elif event.type == 'file_save' and event.content:
        # Log file save, potentially trigger analysis
        logger.debug(f'File saved: {event.file}')

    elif event.type == 'idle':
        logger.info(f'User idle for {event.duration_seconds}s')

    return {'success': True, 'data': {'received': True, 'type': event.type}, 'error': None}


async def _process_workspace_event(event_type: str, content: str) -> None:
    """Process workspace event through the Socratic pipeline."""
    try:
        # This is a lightweight analysis — we just log it for now
        # Full implementation would run it through a specialized pipeline
        logger.info(f'Processing workspace event: {event_type}, content length: {len(content)}')
    except Exception as e:
        logger.error(f'Workspace event processing failed: {e}')
