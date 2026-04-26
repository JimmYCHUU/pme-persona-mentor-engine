import pytest

from graph.nodes.memory_node import memory_node


@pytest.mark.asyncio
async def test_memory_node_no_snapshot_sets_false(monkeypatch, base_state: dict) -> None:
    async def fake_load(_: str):
        return None

    monkeypatch.setattr("services.session_service.SessionService.load", fake_load)
    out = await memory_node(base_state)
    assert out["is_returning_user"] is False
    assert out["session_snapshot"] is None


@pytest.mark.asyncio
async def test_memory_node_snapshot_sets_true(monkeypatch, base_state: dict) -> None:
    async def fake_load(_: str):
        return {"chat_history": []}

    async def fake_summary(_: str):
        return {"top_struggling": []}

    monkeypatch.setattr("services.session_service.SessionService.load", fake_load)
    monkeypatch.setattr("services.mastery_service.MasteryService.get_summary", fake_summary)
    out = await memory_node(base_state)
    assert out["is_returning_user"] is True
    assert out["session_snapshot"] is not None
