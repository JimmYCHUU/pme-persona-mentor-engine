"""Ingestor graph node placeholder used for future ingestion workflows."""

from graph.state import PMEState


async def ingestor_node(state: PMEState) -> PMEState:
    """Pass state through unchanged."""

    return state
