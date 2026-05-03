"""ETM node — STUB for Phase 1. Full implementation in Phase 2."""

from graph.state import PMEState


async def etm_node(state: PMEState) -> PMEState:
    """Stub: returns state unchanged with no evolution context."""
    state['etm_context'] = None
    state['etm_matched'] = False
    return state
