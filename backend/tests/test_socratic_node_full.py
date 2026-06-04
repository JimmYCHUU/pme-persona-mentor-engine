"""Tests for the full Socratic node (Phase 2).

Tests the 5-level Socratic ladder:
  Level 0 — Neutral / informational
  Level 1 — Gentle probing ("What do you think happens here?")
  Level 2 — Guided discovery ("What if we changed X?")
  Level 3 — Challenge ("Can you explain WHY that works?")
  Level 4 — Corrective ("Let's reconsider this part…")

Tests cover:
  - Level determination via LLM reasoning
  - Vault citation retrieval for grounding
  - Deviation scoring
  - Friend mode always maps to level 0
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.fixture
def socratic_state(base_state):
    """State with session history for Socratic assessment."""
    state = dict(base_state)
    state['user_message'] = 'I think recursion uses a stack frame, right?'
    state['session_snapshot'] = {
        'history': [
            {'role': 'user', 'content': 'What is recursion?'},
            {'role': 'assistant', 'content': 'Recursion is when a function calls itself...'},
        ]
    }
    return state


@pytest.fixture
def socratic_state_wrong(base_state):
    """State where user shows a misconception."""
    state = dict(base_state)
    state['user_message'] = 'Recursion is the same as a for loop, they are identical'
    state['session_snapshot'] = {
        'history': [
            {'role': 'user', 'content': 'What is recursion?'},
            {'role': 'assistant', 'content': 'Recursion is when a function calls itself.'},
        ]
    }
    return state


@pytest.fixture
def friend_mode_state(base_state):
    """State in friend_mode."""
    state = dict(base_state)
    state['mode'] = 'friend_mode'
    state['user_message'] = 'Hey, can you tell me about recursion?'
    return state


@pytest.mark.asyncio
async def test_socratic_returns_required_keys(socratic_state):
    """Socratic node must return socratic_level, deviation_score, vault_citation."""
    from graph.nodes.socratic_node import socratic_node

    # Mock LLM to return a structured assessment
    mock_response = '{"level": 1, "deviation_score": 0.2, "reasoning": "User shows partial understanding"}'
    with patch('graph.nodes.socratic_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        with patch('graph.nodes.socratic_node.retriever') as mock_ret:
            mock_ret.get_citation = AsyncMock(return_value=None)
            result = await socratic_node(socratic_state)

    assert 'socratic_level' in result
    assert 'deviation_score' in result
    assert 'vault_citation' in result


@pytest.mark.asyncio
async def test_socratic_level_in_valid_range(socratic_state):
    """Socratic level must be between 0 and 4."""
    from graph.nodes.socratic_node import socratic_node

    mock_response = '{"level": 2, "deviation_score": 0.3, "reasoning": "Needs guidance"}'
    with patch('graph.nodes.socratic_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        with patch('graph.nodes.socratic_node.retriever') as mock_ret:
            mock_ret.get_citation = AsyncMock(return_value=None)
            result = await socratic_node(socratic_state)

    assert 0 <= result['socratic_level'] <= 4


@pytest.mark.asyncio
async def test_socratic_high_deviation_on_misconception(socratic_state_wrong):
    """Misconception should produce higher deviation and level >= 3."""
    from graph.nodes.socratic_node import socratic_node

    mock_response = '{"level": 4, "deviation_score": 0.85, "reasoning": "Major misconception detected"}'
    with patch('graph.nodes.socratic_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        with patch('graph.nodes.socratic_node.retriever') as mock_ret:
            mock_ret.get_citation = AsyncMock(return_value=None)
            result = await socratic_node(socratic_state_wrong)

    assert result['socratic_level'] >= 3
    assert result['deviation_score'] > 0.5


@pytest.mark.asyncio
async def test_socratic_friend_mode_always_level_zero(friend_mode_state):
    """In friend_mode, Socratic level is always 0 (no probing)."""
    from graph.nodes.socratic_node import socratic_node

    with patch('graph.nodes.socratic_node.llm_service') as mock_llm:
        with patch('graph.nodes.socratic_node.retriever') as mock_ret:
            mock_ret.get_citation = AsyncMock(return_value=None)
            result = await socratic_node(friend_mode_state)

    # LLM should NOT even be called in friend mode
    mock_llm.chat.assert_not_called()
    assert result['socratic_level'] == 0
    assert result['deviation_score'] == 0.0


@pytest.mark.asyncio
async def test_socratic_vault_citation_integrated(socratic_state):
    """When retriever finds a citation, it is included in the result."""
    from graph.nodes.socratic_node import socratic_node

    mock_response = '{"level": 1, "deviation_score": 0.15, "reasoning": "Fine"}'
    citation = 'notes.pdf: "Recursion requires a base case to prevent infinite calls..."'

    with patch('graph.nodes.socratic_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        with patch('graph.nodes.socratic_node.retriever') as mock_ret:
            mock_ret.get_citation = AsyncMock(return_value=citation)
            result = await socratic_node(socratic_state)

    assert result['vault_citation'] == citation


@pytest.mark.asyncio
async def test_socratic_graceful_on_llm_failure(socratic_state):
    """If LLM fails, fall back to safe defaults (level 0, deviation 0)."""
    from graph.nodes.socratic_node import socratic_node

    with patch('graph.nodes.socratic_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))
        with patch('graph.nodes.socratic_node.retriever') as mock_ret:
            mock_ret.get_citation = AsyncMock(return_value=None)
            result = await socratic_node(socratic_state)

    assert result['socratic_level'] == 0
    assert result['deviation_score'] == 0.0


@pytest.mark.asyncio
async def test_socratic_uses_reasoning_model(socratic_state):
    """Socratic node must call LLM with use_reasoning=True."""
    from graph.nodes.socratic_node import socratic_node

    mock_response = '{"level": 1, "deviation_score": 0.1, "reasoning": "ok"}'
    with patch('graph.nodes.socratic_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        with patch('graph.nodes.socratic_node.retriever') as mock_ret:
            mock_ret.get_citation = AsyncMock(return_value=None)
            result = await socratic_node(socratic_state)

    # Verify use_reasoning=True was passed
    call_kwargs = mock_llm.chat.call_args
    assert call_kwargs.kwargs.get('use_reasoning') is True or \
           (len(call_kwargs.args) > 3 and call_kwargs.args[3] is True)
