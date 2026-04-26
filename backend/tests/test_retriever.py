import pytest

from rag.retriever import PMERetriever, RetrievedChunk


@pytest.mark.asyncio
async def test_vault_results_rank_higher_than_fingerprint(monkeypatch) -> None:
    r = PMERetriever()

    async def fake_vault(*_args, **_kwargs):
        return [RetrievedChunk(text="vault", source="vault.pdf", score=0.4, authority=100)]

    async def fake_fingerprint(*_args, **_kwargs):
        return [RetrievedChunk(text="finger", source="tweet", score=0.7, authority=50)]

    monkeypatch.setattr(r, "_query_vault", fake_vault)
    monkeypatch.setattr(r, "_query_fingerprint", fake_fingerprint)

    out = await r.query("x", "p")
    assert out[0].source == "vault.pdf"


@pytest.mark.asyncio
async def test_query_returns_only_vault_when_no_fingerprint(monkeypatch) -> None:
    r = PMERetriever()

    async def fake_vault(*_args, **_kwargs):
        return [RetrievedChunk(text="vault", source="chapter1", score=0.6, authority=100)]

    async def fake_fingerprint(*_args, **_kwargs):
        return []

    monkeypatch.setattr(r, "_query_vault", fake_vault)
    monkeypatch.setattr(r, "_query_fingerprint", fake_fingerprint)

    out = await r.query("x", "p")
    assert len(out) == 1
    assert out[0].source == "chapter1"


@pytest.mark.asyncio
async def test_query_returns_empty_when_no_results(monkeypatch) -> None:
    r = PMERetriever()

    async def empty(*_args, **_kwargs):
        return []

    monkeypatch.setattr(r, "_query_vault", empty)
    monkeypatch.setattr(r, "_query_fingerprint", empty)

    out = await r.query("x", "p")
    assert out == []


@pytest.mark.asyncio
async def test_get_citation_returns_default_when_empty() -> None:
    r = PMERetriever()
    assert await r.get_citation("x", "p") == "No vault source found"
