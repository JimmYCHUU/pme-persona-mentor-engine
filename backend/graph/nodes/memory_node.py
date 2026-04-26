"""Memory node loads previous session snapshots and mastery summary."""

from graph.state import PMEState
from services.mastery_service import MasteryService
from services.session_service import SessionService


async def memory_node(state: PMEState) -> PMEState:
    """Load latest snapshot and set returning-user flags."""

    snapshot = await SessionService.load(state["session_id"])
    state["session_snapshot"] = snapshot
    state["is_returning_user"] = snapshot is not None
    state["mastery_summary"] = (
        await MasteryService.get_summary(state["persona_id"]) if snapshot else None
    )
    return state
