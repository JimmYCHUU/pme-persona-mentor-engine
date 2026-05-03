"""Memory node — loads session snapshot and mastery summary."""

from graph.state import PMEState
from services.session_service import SessionService
from services.mastery_service import MasteryService


async def memory_node(state: PMEState) -> PMEState:
    """
    Loads session snapshot and mastery summary for the active session.
    Sets is_returning_user=True if a previous snapshot exists.
    """
    snapshot = await SessionService.load(state['session_id'])
    state['session_snapshot'] = snapshot
    state['is_returning_user'] = snapshot is not None

    if snapshot:
        mastery = await MasteryService.get_summary(state['persona_id'])
        state['mastery_summary'] = mastery
    else:
        state['mastery_summary'] = None

    return state
