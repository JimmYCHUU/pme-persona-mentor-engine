"""Tests for cert_node and guardian_node (Phase 4).

cert_node: checks mastery thresholds, generates certificates via LLM, saves to DB.
guardian_node: keyword-based content safety filter with flagging.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# ── Cert Node Tests ──

@pytest.fixture
def cert_state(base_state):
    """State with mastery event containing a concept at cert threshold."""
    state = dict(base_state)
    state['mastery_event'] = {
        'persona_id': 'test-persona-001',
        'concepts': [
            {'key': 'recursion', 'label': 'Recursion', 'outcome': 'success'},
        ],
    }
    state['final_response'] = 'Great job understanding recursion!'
    return state


@pytest.fixture
def cert_state_no_event(base_state):
    """State with no mastery event."""
    state = dict(base_state)
    state['mastery_event'] = None
    return state


@pytest.mark.asyncio
async def test_cert_node_no_event_passthrough(cert_state_no_event):
    """No mastery event → no cert check, empty result."""
    from graph.nodes.cert_node import cert_node
    result = await cert_node(cert_state_no_event)
    assert result == {} or result.get('mastery_event') is None


@pytest.mark.asyncio
async def test_cert_node_checks_mastery_threshold(cert_state):
    """cert_node should check if concept meets cert threshold."""
    from graph.nodes.cert_node import cert_node

    # Mock MasteryService to return a concept below threshold
    mock_entry = MagicMock()
    mock_entry.mastery_score = 0.5  # Below 0.8 threshold
    mock_entry.success_count = 2
    mock_entry.failure_count = 1
    mock_entry.concept_key = 'recursion'
    mock_entry.concept_label = 'Recursion'
    mock_entry.status = 'attempted'

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('graph.nodes.cert_node.AsyncSessionLocal', return_value=mock_session):
        result = await cert_node(cert_state)

    # Below threshold → no cert issued
    assert result == {}


@pytest.mark.asyncio
async def test_cert_node_issues_cert_at_threshold(cert_state):
    """When mastery_score >= threshold + enough sessions/successes, issue cert."""
    from graph.nodes.cert_node import cert_node

    mock_entry = MagicMock()
    mock_entry.mastery_score = 0.85
    mock_entry.success_count = 6
    mock_entry.failure_count = 1
    mock_entry.concept_key = 'recursion'
    mock_entry.concept_label = 'Recursion'
    mock_entry.status = 'mastered'
    mock_entry.sessions_tested = '["s1","s2","s3","s4"]'

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Mock existing cert check (no existing cert)
    mock_cert_result = MagicMock()
    mock_cert_result.scalar_one_or_none.return_value = None

    # First call returns entry, second returns no existing cert
    mock_session.execute = AsyncMock(side_effect=[mock_result, mock_cert_result])

    mock_llm_response = 'You have demonstrated a solid understanding of recursion.'
    with patch('graph.nodes.cert_node.AsyncSessionLocal', return_value=mock_session):
        with patch('graph.nodes.cert_node.llm_service') as mock_llm:
            mock_llm.chat = AsyncMock(return_value=mock_llm_response)
            result = await cert_node(cert_state)

    # Should have added a cert to DB
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called()


@pytest.mark.asyncio
async def test_cert_node_graceful_on_failure(cert_state):
    """If cert generation fails, return empty dict gracefully."""
    from graph.nodes.cert_node import cert_node

    with patch('graph.nodes.cert_node.AsyncSessionLocal', side_effect=Exception("DB down")):
        result = await cert_node(cert_state)

    assert result == {}


# ── Guardian Node Tests ──

@pytest.mark.asyncio
async def test_guardian_passes_clean_content(base_state):
    """Clean content should pass through unflagged."""
    from graph.nodes.guardian_node import guardian_node

    state = dict(base_state)
    state['styled_response'] = 'Recursion is a programming concept where a function calls itself.'
    result = await guardian_node(state)

    assert result['guardian_flagged'] is False
    assert result['final_response'] == state['styled_response']


@pytest.mark.asyncio
async def test_guardian_flags_harmful_content(base_state):
    """Content with harmful keywords should be flagged."""
    from graph.nodes.guardian_node import guardian_node

    state = dict(base_state)
    state['styled_response'] = 'Here is how to hack into someone else\'s account and steal their passwords.'
    result = await guardian_node(state)

    assert result['guardian_flagged'] is True
    assert 'cannot provide' in result['final_response'].lower() or \
           'inappropriate' in result['final_response'].lower() or \
           result['final_response'] != state['styled_response']


@pytest.mark.asyncio
async def test_guardian_flags_explicit_content(base_state):
    """Explicit or dangerous content should be caught."""
    from graph.nodes.guardian_node import guardian_node

    state = dict(base_state)
    state['styled_response'] = 'To build a weapon, first you need to acquire explosives and then...'
    result = await guardian_node(state)

    assert result['guardian_flagged'] is True


@pytest.mark.asyncio
async def test_guardian_preserves_educational_security_content(base_state):
    """Educational security content (pentesting, CTF) should pass."""
    from graph.nodes.guardian_node import guardian_node

    state = dict(base_state)
    state['styled_response'] = 'In a penetration test, you scan for open ports using nmap. This is a standard security assessment technique.'
    result = await guardian_node(state)

    assert result['guardian_flagged'] is False
    assert result['final_response'] == state['styled_response']


@pytest.mark.asyncio
async def test_guardian_handles_empty_response(base_state):
    """Empty response should pass through without error."""
    from graph.nodes.guardian_node import guardian_node

    state = dict(base_state)
    state['styled_response'] = ''
    state['raw_llm_response'] = ''
    result = await guardian_node(state)

    assert result['guardian_flagged'] is False
