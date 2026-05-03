"""Socratic node — STUB for Phase 1. Full implementation in Phase 2."""

from graph.state import PMEState


async def socratic_node(state: PMEState) -> PMEState:
    """Stub: always returns silent level with no intervention."""
    state['deviation_score'] = 0.0
    state['socratic_level'] = 0
    state['vault_citation'] = None
    state['mastery_event'] = None
    return state
