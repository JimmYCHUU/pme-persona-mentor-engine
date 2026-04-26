import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_ollama():
    """Mock OllamaService that returns a controlled string."""

    svc = AsyncMock()
    svc.chat.return_value = "Mock mentor response."
    svc.check_health.return_value = True
    return svc


@pytest.fixture
def mock_chroma():
    """Ephemeral in-memory ChromaDB — never writes to disk."""

    import chromadb

    return chromadb.Client()


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
