"""
Retriever — dual-collection query with authority re-ranking.
Queries both vault_{persona_id} and fingerprint_{persona_id} collections.
"""

import logging
from typing import Optional
from core.config import settings
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_chroma_client = None


def _get_chroma():
    """Lazy-load ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _chroma_client


@dataclass
class RetrievalResult:
    """A single retrieval result with score and metadata."""
    content: str
    score: float
    source: str
    authority: int
    metadata: dict


class Retriever:
    """Dual-collection retriever with authority-aware re-ranking."""

    async def query(self, message: str, persona_id: str,
                    top_k: int = 3) -> list[RetrievalResult]:
        """
        Query both vault and fingerprint collections.
        Returns results sorted by authority-weighted score.
        """
        client = _get_chroma()
        results = []

        # Query vault collection (authority=100)
        try:
            vault_col = client.get_collection(f'vault_{persona_id}')
            vault_results = vault_col.query(
                query_texts=[message],
                n_results=min(top_k, vault_col.count() or 1),
            )
            if vault_results and vault_results['documents']:
                for i, doc in enumerate(vault_results['documents'][0]):
                    dist = vault_results['distances'][0][i] if vault_results.get('distances') else 0.5
                    meta = vault_results['metadatas'][0][i] if vault_results.get('metadatas') else {}
                    similarity = max(0.0, 1.0 - dist)
                    results.append(RetrievalResult(
                        content=doc,
                        score=similarity,
                        source=meta.get('source_file', 'vault'),
                        authority=meta.get('authority', 100),
                        metadata=meta,
                    ))
        except Exception as e:
            logger.debug(f'Vault collection not found for {persona_id}: {e}')

        # Query fingerprint collection (authority=50)
        try:
            fp_col = client.get_collection(f'fingerprint_{persona_id}')
            fp_results = fp_col.query(
                query_texts=[message],
                n_results=min(top_k, fp_col.count() or 1),
            )
            if fp_results and fp_results['documents']:
                for i, doc in enumerate(fp_results['documents'][0]):
                    dist = fp_results['distances'][0][i] if fp_results.get('distances') else 0.5
                    meta = fp_results['metadatas'][0][i] if fp_results.get('metadatas') else {}
                    similarity = max(0.0, 1.0 - dist)
                    results.append(RetrievalResult(
                        content=doc,
                        score=similarity,
                        source=meta.get('source_file', 'fingerprint'),
                        authority=meta.get('authority', 50),
                        metadata=meta,
                    ))
        except Exception as e:
            logger.debug(f'Fingerprint collection not found for {persona_id}: {e}')

        # Re-rank by authority-weighted score
        for r in results:
            r.score = r.score * (r.authority / 100.0)

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    async def get_citation(self, message: str, persona_id: str) -> Optional[str]:
        """
        Get a vault citation for the Socratic engine.
        Returns a formatted citation string or None.
        """
        results = await self.query(message, persona_id, top_k=1)
        if not results:
            return None

        r = results[0]
        source = r.source
        content_preview = r.content[:150].replace('\n', ' ')
        return f'{source}: "{content_preview}..."'


retriever = Retriever()
