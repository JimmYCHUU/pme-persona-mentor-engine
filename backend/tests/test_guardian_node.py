import pytest

from graph.nodes.guardian_node import guardian_node


@pytest.mark.asyncio
async def test_guardian_pass_through_when_clean(monkeypatch, base_state: dict) -> None:
    base_state["styled_response"] = "clean"
    monkeypatch.setattr("graph.nodes.guardian_node._get_classifier", lambda: lambda _: [{"label": "clean"}])
    out = await guardian_node(base_state)
    assert out["guardian_flagged"] is False
    assert out["final_response"] == "clean"


@pytest.mark.asyncio
async def test_guardian_pass_through_when_classifier_fails(monkeypatch, base_state: dict) -> None:
    base_state["styled_response"] = "x"

    def boom():
        raise RuntimeError("fail")

    monkeypatch.setattr("graph.nodes.guardian_node._get_classifier", boom)
    out = await guardian_node(base_state)
    assert out["final_response"] == "x"
