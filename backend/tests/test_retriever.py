import pytest

from rag.retriever import PMERetriever


@pytest.mark.asyncio
async def test_get_citation_returns_default_when_empty() -> None:
    r = PMERetriever()
    assert await r.get_citation("x", "p") == "No vault source found"
