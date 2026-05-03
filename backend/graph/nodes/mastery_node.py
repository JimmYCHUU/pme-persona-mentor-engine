"""Mastery node — STUB for Phase 1. Full implementation in Phase 3."""

import logging

logger = logging.getLogger(__name__)


async def process_mastery_event(event: dict) -> None:
    """Stub: logs event and does nothing in Phase 1."""
    logger.debug(f'mastery_node stub: received event {event}')
    pass
