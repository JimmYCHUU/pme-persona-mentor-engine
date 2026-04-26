"""Dual-source retrieval across vault and fingerprint collections."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    """Simple retrieval record for prompt grounding."""

    text: str
    source: str
    score: float
    authority: float


class PMERetriever:
    """Retriever combining vault and fingerprint results with weighted ranking."""

    async def query(self, text: str, persona_id: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return ranked retrieval results for a query."""

        # Placeholder in this scaffold; full Chroma query in ingestion phase.
        return []

    async def get_citation(self, text: str, persona_id: str) -> str:
        """Return best source citation string for mentor response."""

        results = await self.query(text, persona_id, top_k=1)
        if not results:
            return "No vault source found"
        return f"{results[0].source} — reference"


retriever = PMERetriever()
