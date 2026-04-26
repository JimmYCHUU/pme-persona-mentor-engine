import pytest

from graph.nodes.socratic_node import socratic_node


@pytest.mark.asyncio
async def test_friend_mode_level_zero(base_state: dict) -> None:
    base_state["mode"] = "friend_mode"
    out = await socratic_node(base_state)
    assert out["socratic_level"] == 0
