from graph.nodes.persona_node import _build_system_prompt


def test_build_system_prompt_includes_name() -> None:
    prompt = _build_system_prompt(
        profile={"name": "Ada", "description": "desc", "soul": {}, "sliders": {}},
        socratic_level=1,
        vault_citation=None,
        etm_context=None,
        mode="deep_dive",
    )
    assert "Ada" in prompt


def test_build_system_prompt_level_1_instruction() -> None:
    prompt = _build_system_prompt(
        profile={"name": "Ada", "description": "desc", "soul": {}, "sliders": {}},
        socratic_level=1,
        vault_citation=None,
        etm_context=None,
        mode="deep_dive",
    )
    assert "probing question" in prompt


def test_build_system_prompt_level_4_instruction() -> None:
    prompt = _build_system_prompt(
        profile={"name": "Ada", "description": "desc", "soul": {}, "sliders": {}},
        socratic_level=4,
        vault_citation=None,
        etm_context=None,
        mode="deep_dive",
    )
    assert "WHY that works" in prompt


def test_build_system_prompt_friend_mode_instruction() -> None:
    prompt = _build_system_prompt(
        profile={"name": "Ada", "description": "desc", "soul": {}, "sliders": {}},
        socratic_level=4,
        vault_citation=None,
        etm_context=None,
        mode="friend_mode",
    )
    assert "Respond naturally" in prompt
