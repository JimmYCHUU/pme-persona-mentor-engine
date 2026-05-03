"""Mastery tracking service — STUB for Phase 1."""

from typing import Optional


class MasteryService:
    """Stub mastery service. Full implementation in Phase 3."""

    @staticmethod
    async def get_or_create(persona_id: str, concept_key: str,
                            concept_label: str = '') -> None:
        """Stub: does nothing in Phase 1."""
        pass

    @staticmethod
    def compute_new_score(current: float, outcome: str) -> float:
        """Stub: returns current score unchanged."""
        return current

    @staticmethod
    def compute_status(score: float, failure_count: int) -> str:
        """Stub: returns 'encountered'."""
        return 'encountered'

    @staticmethod
    async def should_certify(persona_id: str, concept_key: str) -> bool:
        """Stub: never certifies in Phase 1."""
        return False

    @staticmethod
    async def get_summary(persona_id: str) -> dict:
        """Stub: returns empty summary."""
        return {}

    @staticmethod
    async def get_concept(persona_id: str, concept_key: str) -> Optional[object]:
        """Stub: returns None."""
        return None
