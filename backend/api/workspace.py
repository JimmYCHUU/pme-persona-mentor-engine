"""Workspace API — STUB for Phase 1. Full implementation in Phase 2."""

from fastapi import APIRouter
from models.schemas import WorkspaceEvent

router = APIRouter()


@router.post('/event', response_model=dict)
async def workspace_event(event: WorkspaceEvent):
    """Stub: accepts event body, returns success, does nothing else."""
    return {'success': True, 'data': {'received': True}, 'error': None}
