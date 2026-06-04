"""Tests for the full ETM node (Phase 2).

Tests Experience-Triggered Memory:
  - Workspace event matching to teaching concepts
  - No workspace event → pass-through
  - Error in workspace event → graceful degradation
  - Concept extraction from events
"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def etm_state_with_event(base_state):
    """State with a workspace event (e.g. terminal error)."""
    state = dict(base_state)
    state['workspace_event'] = {
        'type': 'terminal_error',
        'content': 'TypeError: cannot read property "map" of undefined',
        'file': 'components/UserList.tsx',
        'language': 'typescript',
    }
    state['user_message'] = 'I keep getting this error'
    return state


@pytest.fixture
def etm_state_file_save(base_state):
    """State with a file-save workspace event."""
    state = dict(base_state)
    state['workspace_event'] = {
        'type': 'file_save',
        'content': 'async function fetchUsers() { const res = await fetch("/api/users"); }',
        'file': 'api/users.ts',
        'language': 'typescript',
    }
    state['user_message'] = 'Is this the right way to do async calls?'
    return state


@pytest.fixture
def etm_state_no_event(base_state):
    """State with no workspace event."""
    state = dict(base_state)
    state['workspace_event'] = None
    state['user_message'] = 'Tell me about arrays'
    return state


@pytest.mark.asyncio
async def test_etm_returns_required_keys_with_event(etm_state_with_event):
    """ETM node must return etm_context and etm_matched when event present."""
    from graph.nodes.etm_node import etm_node

    mock_response = '{"concept": "null_safety", "context": "The error suggests accessing a property on undefined. This is a null safety issue — the data is not loaded yet when .map() is called.", "matched": true}'
    with patch('graph.nodes.etm_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        result = await etm_node(etm_state_with_event)

    assert 'etm_context' in result
    assert 'etm_matched' in result
    assert result['etm_matched'] is True
    assert result['etm_context'] is not None


@pytest.mark.asyncio
async def test_etm_no_event_passthrough(etm_state_no_event):
    """No workspace event → no LLM call, etm_matched=False."""
    from graph.nodes.etm_node import etm_node

    with patch('graph.nodes.etm_node.llm_service') as mock_llm:
        result = await etm_node(etm_state_no_event)

    mock_llm.chat.assert_not_called()
    assert result['etm_context'] is None
    assert result['etm_matched'] is False


@pytest.mark.asyncio
async def test_etm_extracts_concept_from_error(etm_state_with_event):
    """ETM should identify a teaching concept from an error event."""
    from graph.nodes.etm_node import etm_node

    mock_response = '{"concept": "null_safety", "context": "The variable is undefined when .map() is called. Check if data has loaded before rendering.", "matched": true}'
    with patch('graph.nodes.etm_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        result = await etm_node(etm_state_with_event)

    assert result['etm_matched'] is True
    assert 'null_safety' in result['etm_context'].lower() or 'undefined' in result['etm_context'].lower()


@pytest.mark.asyncio
async def test_etm_graceful_on_llm_failure(etm_state_with_event):
    """If LLM fails, ETM returns safe defaults."""
    from graph.nodes.etm_node import etm_node

    with patch('graph.nodes.etm_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))
        result = await etm_node(etm_state_with_event)

    assert result['etm_context'] is None
    assert result['etm_matched'] is False


@pytest.mark.asyncio
async def test_etm_uses_reasoning_model(etm_state_with_event):
    """ETM should use the reasoning model for concept extraction."""
    from graph.nodes.etm_node import etm_node

    mock_response = '{"concept": "async_await", "context": "Pattern detected", "matched": true}'
    with patch('graph.nodes.etm_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        result = await etm_node(etm_state_with_event)

    call_kwargs = mock_llm.chat.call_args
    assert call_kwargs.kwargs.get('use_reasoning') is True or \
           (len(call_kwargs.args) > 3 and call_kwargs.args[3] is True)
