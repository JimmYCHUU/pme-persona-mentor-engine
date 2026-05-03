"""Guardian node — STUB for Phase 1. Full implementation in Phase 4."""

from graph.state import PMEState


async def guardian_node(state: PMEState) -> PMEState:
    """Stub: passes styled_response through as final_response."""
    state['guardian_flagged'] = False
    state['final_response'] = state['styled_response']
    return state
