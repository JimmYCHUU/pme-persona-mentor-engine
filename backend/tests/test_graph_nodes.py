"""TDD tests for graph nodes — memory, etm, socratic, persona, guardian, mastery, cert."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def base_state() -> dict:
    """A minimal valid PMEState for testing nodes."""
    return {
        "session_id": "test-session-001",
        "persona_id": "test-persona-001",
        "user_message": "How do I fix this loop?",
        "workspace_event": None,
        "is_returning_user": False,
        "session_snapshot": None,
        "mastery_summary": None,
        "etm_context": None,
        "etm_matched": False,
        "deviation_score": 0.0,
        "socratic_level": 0,
        "vault_citation": None,
        "mastery_event": None,
        "raw_llm_response": "",
        "styled_response": "",
        "guardian_flagged": False,
        "final_response": "",
        "mode": "deep_dive",
    }


# ── Memory Node ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_memory_node_new_user(base_state, monkeypatch):
    """New user (no snapshot) sets is_returning_user to False."""
    from graph.nodes.memory_node import memory_node

    mock_svc = AsyncMock()
    mock_svc.get_snapshot.return_value = None
    monkeypatch.setattr("graph.nodes.memory_node.SessionService", lambda: mock_svc)

    result = await memory_node(base_state)
    assert result["session_snapshot"] is None
    assert result["is_returning_user"] is False


@pytest.mark.asyncio
async def test_memory_node_returning_user(base_state, monkeypatch):
    """Returning user with history sets is_returning_user to True."""
    from graph.nodes.memory_node import memory_node

    mock_svc = AsyncMock()
    mock_svc.get_snapshot.return_value = {
        "history": [{"role": "user", "content": "previous message"}]
    }
    monkeypatch.setattr("graph.nodes.memory_node.SessionService", lambda: mock_svc)

    result = await memory_node(base_state)
    assert result["is_returning_user"] is True
    assert result["session_snapshot"]["history"][0]["role"] == "user"


# ── ETM Node (stub) ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_etm_node_stub(base_state):
    """ETM stub returns no context and no match."""
    from graph.nodes.etm_node import etm_node

    result = await etm_node(base_state)
    assert result["etm_context"] is None
    assert result["etm_matched"] is False


# ── Socratic Node (stub) ─────────────────────────────────────

@pytest.mark.asyncio
async def test_socratic_node_stub(base_state, monkeypatch):
    """Socratic node in friend_mode returns level 0 and no deviation."""
    from graph.nodes.socratic_node import socratic_node

    # Mock retriever to avoid real ChromaDB calls
    mock_retriever = AsyncMock()
    mock_retriever.get_citation.return_value = None
    monkeypatch.setattr("graph.nodes.socratic_node.retriever", mock_retriever)

    # Friend mode always returns level 0 without calling LLM
    base_state["mode"] = "friend_mode"
    result = await socratic_node(base_state)
    assert result["socratic_level"] == 0
    assert result["deviation_score"] == 0.0


@pytest.mark.asyncio
async def test_socratic_node_with_assessment(base_state, monkeypatch):
    """Socratic node parses LLM assessment correctly."""
    from graph.nodes.socratic_node import socratic_node

    mock_retriever = AsyncMock()
    mock_retriever.get_citation.return_value = "test citation"
    monkeypatch.setattr("graph.nodes.socratic_node.retriever", mock_retriever)

    mock_llm = AsyncMock()
    mock_llm.chat.return_value = '{"level": 2, "deviation_score": 0.35, "reasoning": "partial understanding"}'
    monkeypatch.setattr("graph.nodes.socratic_node.llm_service", mock_llm)

    result = await socratic_node(base_state)
    assert result["socratic_level"] == 2
    assert result["deviation_score"] == 0.35
    assert result["vault_citation"] == "test citation"


# ── Persona Node ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_persona_node_generates_response(base_state, monkeypatch):
    """Persona node calls LLM and returns styled response."""
    from graph.nodes.persona_node import persona_node

    mock_persona_svc = AsyncMock()
    mock_persona_svc.get_persona.return_value = {
        "id": "test-persona-001",
        "system_prompt": "You are a test mentor.",
    }
    monkeypatch.setattr("graph.nodes.persona_node.PersonaService", lambda: mock_persona_svc)

    mock_llm = AsyncMock()
    mock_llm.chat.return_value = "Here is how you fix the loop."
    monkeypatch.setattr("graph.nodes.persona_node.llm_service", mock_llm)

    result = await persona_node(base_state)
    assert result["raw_llm_response"] == "Here is how you fix the loop."
    assert result["final_response"] == "Here is how you fix the loop."


@pytest.mark.asyncio
async def test_persona_node_missing_persona(base_state, monkeypatch):
    """Missing persona returns error message."""
    from graph.nodes.persona_node import persona_node

    mock_persona_svc = AsyncMock()
    mock_persona_svc.get_persona.return_value = None
    monkeypatch.setattr("graph.nodes.persona_node.PersonaService", lambda: mock_persona_svc)

    result = await persona_node(base_state)
    assert "not found" in result["final_response"].lower()


# ── Guardian Node (stub) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_guardian_node_passes_through(base_state):
    """Guardian stub passes response through unchanged."""
    from graph.nodes.guardian_node import guardian_node

    base_state["styled_response"] = "Test response content."
    result = await guardian_node(base_state)
    assert result["guardian_flagged"] is False
    assert result["final_response"] == "Test response content."


# ── Mastery Node (stub) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_mastery_node_stub(base_state):
    """Mastery stub returns no event."""
    from graph.nodes.mastery_node import mastery_node

    result = await mastery_node(base_state)
    assert result["mastery_event"] is None


# ── Cert Node (stub) ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_cert_node_stub(base_state):
    """Cert stub returns empty dict."""
    from graph.nodes.cert_node import cert_node

    result = await cert_node(base_state)
    assert isinstance(result, dict)
