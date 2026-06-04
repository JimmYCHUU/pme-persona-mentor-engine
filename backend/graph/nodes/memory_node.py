"""Memory node — loads session history and returning-user context."""
from graph.state import PMEState
from services.session_service import SessionService


async def memory_node(state: PMEState) -> dict:
    """Load session snapshot and set is_returning_user flag.

    Returns partial state update dict (never mutates state directly).
    """
    session_svc = SessionService()
    snapshot = await session_svc.get_snapshot(state["session_id"])

    return {
        "session_snapshot": snapshot,
        "is_returning_user": snapshot is not None and len(snapshot.get("history", [])) > 0,
    }
