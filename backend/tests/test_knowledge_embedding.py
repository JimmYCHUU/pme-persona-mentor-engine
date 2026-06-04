"""Tests for knowledge embedding and persona node vault integration (Phase 2)."""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
from pathlib import Path


# ── Knowledge Embedding Tests ──

@pytest.fixture
def knowledge_dir(tmp_path):
    """Create a temporary knowledge directory with test files."""
    kdir = tmp_path / "knowledge"
    kdir.mkdir()

    quotes = {
        "mentor_id": "testmentor",
        "quotes": [
            {
                "topic": "testing",
                "quote": "Tests are the first documentation of your code.",
                "why_they_said_it": "He believes tests communicate intent.",
            },
            {
                "topic": "tdd",
                "quote": "Red, green, refactor is the heartbeat of TDD.",
                "why_they_said_it": "He follows strict TDD methodology.",
            },
        ]
    }
    (kdir / "quotes.json").write_text(json.dumps(quotes))

    explanations = {
        "mentor_id": "testmentor",
        "explanations": [
            {
                "topic": "recursion",
                "explanation": "Think of recursion like Russian nesting dolls.",
                "when_to_use": "When introducing recursion to beginners",
            }
        ]
    }
    (kdir / "explanations.json").write_text(json.dumps(explanations))
    return kdir


@pytest.mark.asyncio
async def test_embed_knowledge_adds_documents(knowledge_dir):
    """Knowledge embedding should add documents to the collection."""
    from api.mentor_gallery import _embed_knowledge

    mock_collection = MagicMock()
    mock_collection.get.return_value = {"ids": []}  # No existing docs

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    with patch('chromadb.PersistentClient', return_value=mock_client):
        await _embed_knowledge("testmentor", knowledge_dir)

    # Should have called collection.add for each item
    assert mock_collection.add.call_count == 3  # 2 quotes + 1 explanation


@pytest.mark.asyncio
async def test_embed_knowledge_skips_existing(knowledge_dir):
    """Already-embedded documents should be skipped (dedup by id)."""
    from api.mentor_gallery import _embed_knowledge

    mock_collection = MagicMock()
    # Simulate first doc already exists, second and third are new
    def mock_get(ids):
        if ids[0] == "testmentor_quotes_0":
            return {"ids": ["testmentor_quotes_0"]}
        return {"ids": []}

    mock_collection.get.side_effect = mock_get

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    with patch('chromadb.PersistentClient', return_value=mock_client):
        await _embed_knowledge("testmentor", knowledge_dir)

    # Should have skipped the first quote, added 2 (second quote + explanation)
    assert mock_collection.add.call_count == 2


@pytest.mark.asyncio
async def test_embed_knowledge_sets_authority_100(knowledge_dir):
    """All mentor knowledge docs should have authority=100."""
    from api.mentor_gallery import _embed_knowledge

    mock_collection = MagicMock()
    mock_collection.get.return_value = {"ids": []}

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    with patch('chromadb.PersistentClient', return_value=mock_client):
        await _embed_knowledge("testmentor", knowledge_dir)

    # Check all add calls have authority=100 in metadata
    for c in mock_collection.add.call_args_list:
        metadata = c.kwargs.get("metadatas", c.args[0] if c.args else None)
        if metadata is None and "metadatas" in (c.kwargs or {}):
            metadata = c.kwargs["metadatas"]
        # Handle both positional and keyword args
        actual_call = c
        if actual_call.kwargs.get("metadatas"):
            for m in actual_call.kwargs["metadatas"]:
                assert m["authority"] == 100
                assert m["mentor_id"] == "testmentor"


@pytest.mark.asyncio
async def test_embed_knowledge_creates_collection_per_mentor(knowledge_dir):
    """Collection name should be vault_{mentor_id}."""
    from api.mentor_gallery import _embed_knowledge

    mock_collection = MagicMock()
    mock_collection.get.return_value = {"ids": []}

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    with patch('chromadb.PersistentClient', return_value=mock_client):
        await _embed_knowledge("networkchuck", knowledge_dir)

    mock_client.get_or_create_collection.assert_called_once_with("vault_networkchuck")


# ── Persona Node with Vault Citation Tests ──

@pytest.mark.asyncio
async def test_persona_node_includes_vault_citation(base_state):
    """When vault_citation is set, persona should include it in system prompt."""
    from graph.nodes.persona_node import persona_node

    state = dict(base_state)
    state['vault_citation'] = 'notes.pdf: "Recursion requires a base case..."'
    state['socratic_level'] = 1

    mock_persona = {
        "system_prompt": "You are a helpful mentor.",
        "name": "TestMentor",
    }

    with patch('graph.nodes.persona_node.PersonaService') as MockPS:
        instance = MockPS.return_value
        instance.get_persona = AsyncMock(return_value=mock_persona)
        with patch('graph.nodes.persona_node.llm_service') as mock_llm:
            mock_llm.chat = AsyncMock(return_value="Great question about recursion!")
            result = await persona_node(state)

    # Verify the system prompt sent to LLM contains the vault citation
    call_kwargs = mock_llm.chat.call_args
    system_sent = call_kwargs.kwargs.get('system', call_kwargs.args[1] if len(call_kwargs.args) > 1 else '')
    assert 'REFERENCE' in system_sent
    assert 'base case' in system_sent


@pytest.mark.asyncio
async def test_persona_node_includes_socratic_instruction(base_state):
    """Socratic level > 0 should add instruction to system prompt."""
    from graph.nodes.persona_node import persona_node

    state = dict(base_state)
    state['socratic_level'] = 3  # Challenge level

    mock_persona = {
        "system_prompt": "You are a helpful mentor.",
    }

    with patch('graph.nodes.persona_node.PersonaService') as MockPS:
        instance = MockPS.return_value
        instance.get_persona = AsyncMock(return_value=mock_persona)
        with patch('graph.nodes.persona_node.llm_service') as mock_llm:
            mock_llm.chat = AsyncMock(return_value="Let me challenge that assumption.")
            result = await persona_node(state)

    call_kwargs = mock_llm.chat.call_args
    system_sent = call_kwargs.kwargs.get('system', call_kwargs.args[1] if len(call_kwargs.args) > 1 else '')
    assert 'SOCRATIC L3' in system_sent
    assert 'Challenge' in system_sent


@pytest.mark.asyncio
async def test_persona_node_includes_etm_context(base_state):
    """When etm_context is set, persona should include workspace context."""
    from graph.nodes.persona_node import persona_node

    state = dict(base_state)
    state['etm_context'] = '[null_safety] The error shows accessing undefined.'

    mock_persona = {
        "system_prompt": "You are a helpful mentor.",
    }

    with patch('graph.nodes.persona_node.PersonaService') as MockPS:
        instance = MockPS.return_value
        instance.get_persona = AsyncMock(return_value=mock_persona)
        with patch('graph.nodes.persona_node.llm_service') as mock_llm:
            mock_llm.chat = AsyncMock(return_value="I see you're working on null safety.")
            result = await persona_node(state)

    call_kwargs = mock_llm.chat.call_args
    system_sent = call_kwargs.kwargs.get('system', call_kwargs.args[1] if len(call_kwargs.args) > 1 else '')
    assert 'WORKSPACE CONTEXT' in system_sent
    assert 'null_safety' in system_sent
