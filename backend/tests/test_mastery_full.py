"""Tests for the full MasteryService (Phase 3).

Tests cover:
  - Recording a concept encounter
  - Updating mastery score (success/failure)
  - Status transitions (encountered → attempted → struggling → mastered)
  - Retrieving all concepts for a persona
  - Retrieving struggling concepts
  - Getting mastery summary
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json


@pytest.fixture
def mock_db_session():
    """Mock async database session."""
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    return session


# ── MasteryService Tests ──

@pytest.mark.asyncio
async def test_record_encounter_creates_new_concept():
    """First encounter of a concept creates a new MasteryLedger entry."""
    from services.mastery_service import MasteryService

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    # Simulate no existing entry (first encounter)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('services.mastery_service.AsyncSessionLocal', return_value=mock_session):
        svc = MasteryService()
        result = await svc.record_encounter(
            persona_id='test-persona',
            concept_key='recursion',
            concept_label='Recursion',
        )

    # Should have added a new entry
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert result['status'] == 'encountered'


@pytest.mark.asyncio
async def test_record_encounter_increments_existing():
    """Subsequent encounter increments encounter_count."""
    from services.mastery_service import MasteryService

    mock_entry = MagicMock()
    mock_entry.encounter_count = 2
    mock_entry.status = 'encountered'
    mock_entry.mastery_score = 0.1
    mock_entry.concept_key = 'recursion'

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('services.mastery_service.AsyncSessionLocal', return_value=mock_session):
        svc = MasteryService()
        result = await svc.record_encounter(
            persona_id='test-persona',
            concept_key='recursion',
            concept_label='Recursion',
        )

    assert mock_entry.encounter_count == 3
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_record_success_increments_score():
    """Recording a success should increment mastery_score."""
    from services.mastery_service import MasteryService

    mock_entry = MagicMock()
    mock_entry.mastery_score = 0.3
    mock_entry.success_count = 2
    mock_entry.failure_count = 1
    mock_entry.encounter_count = 5
    mock_entry.status = 'attempted'

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('services.mastery_service.AsyncSessionLocal', return_value=mock_session):
        svc = MasteryService()
        result = await svc.record_success(
            persona_id='test-persona',
            concept_key='recursion',
        )

    assert mock_entry.success_count == 3
    assert mock_entry.mastery_score > 0.3  # Score should increase
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_record_failure_decrements_score():
    """Recording a failure should decrement mastery_score."""
    from services.mastery_service import MasteryService

    mock_entry = MagicMock()
    mock_entry.mastery_score = 0.5
    mock_entry.success_count = 3
    mock_entry.failure_count = 1
    mock_entry.encounter_count = 6
    mock_entry.status = 'attempted'

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('services.mastery_service.AsyncSessionLocal', return_value=mock_session):
        svc = MasteryService()
        result = await svc.record_failure(
            persona_id='test-persona',
            concept_key='recursion',
        )

    assert mock_entry.failure_count == 2
    assert mock_entry.mastery_score < 0.5  # Score should decrease
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_status_transitions_to_struggling():
    """High failure count transitions status to 'struggling'."""
    from services.mastery_service import MasteryService

    mock_entry = MagicMock()
    mock_entry.mastery_score = 0.2
    mock_entry.success_count = 1
    mock_entry.failure_count = 4  # Will become 5 after this failure
    mock_entry.encounter_count = 8
    mock_entry.status = 'attempted'

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_entry
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('services.mastery_service.AsyncSessionLocal', return_value=mock_session):
        svc = MasteryService()
        await svc.record_failure(
            persona_id='test-persona',
            concept_key='recursion',
        )

    assert mock_entry.status == 'struggling'


@pytest.mark.asyncio
async def test_get_summary_returns_correct_format():
    """get_summary should return top struggling + overall stats."""
    from services.mastery_service import MasteryService

    mock_entries = [
        MagicMock(concept_key='recursion', status='struggling', failure_count=5, mastery_score=0.2),
        MagicMock(concept_key='async_await', status='mastered', failure_count=0, mastery_score=0.9),
        MagicMock(concept_key='closures', status='attempted', failure_count=2, mastery_score=0.4),
    ]

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_entries
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch('services.mastery_service.AsyncSessionLocal', return_value=mock_session):
        svc = MasteryService()
        summary = await svc.get_summary('test-persona')

    assert summary is not None
    assert 'top_struggling' in summary
    assert 'total_concepts' in summary
    assert summary['total_concepts'] == 3


# ── Mastery Node Tests ──

@pytest.mark.asyncio
async def test_mastery_node_extracts_concepts(base_state):
    """Mastery node should extract concepts from the conversation."""
    from graph.nodes.mastery_node import mastery_node

    state = dict(base_state)
    state['final_response'] = 'Recursion uses a call stack to track function calls...'
    state['socratic_level'] = 1
    state['deviation_score'] = 0.3

    mock_response = '{"concepts": [{"key": "recursion", "label": "Recursion", "outcome": "success"}]}'
    with patch('graph.nodes.mastery_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        with patch('graph.nodes.mastery_node.MasteryService') as MockMS:
            instance = MockMS.return_value
            instance.record_encounter = AsyncMock(return_value={'status': 'encountered'})
            instance.record_success = AsyncMock(return_value={'status': 'attempted'})
            result = await mastery_node(state)

    assert result['mastery_event'] is not None
    assert len(result['mastery_event']['concepts']) > 0


@pytest.mark.asyncio
async def test_mastery_node_graceful_on_failure(base_state):
    """If concept extraction fails, return safe defaults."""
    from graph.nodes.mastery_node import mastery_node

    state = dict(base_state)
    state['final_response'] = 'Hello!'

    with patch('graph.nodes.mastery_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(side_effect=Exception("fail"))
        result = await mastery_node(state)

    assert result['mastery_event'] is None


@pytest.mark.asyncio
async def test_mastery_node_records_failure_on_high_deviation(base_state):
    """High deviation score should record failures for concepts."""
    from graph.nodes.mastery_node import mastery_node

    state = dict(base_state)
    state['final_response'] = 'Let me correct your understanding of closures...'
    state['deviation_score'] = 0.8  # High deviation

    mock_response = '{"concepts": [{"key": "closures", "label": "Closures", "outcome": "failure"}]}'
    with patch('graph.nodes.mastery_node.llm_service') as mock_llm:
        mock_llm.chat = AsyncMock(return_value=mock_response)
        with patch('graph.nodes.mastery_node.MasteryService') as MockMS:
            instance = MockMS.return_value
            instance.record_encounter = AsyncMock(return_value={'status': 'encountered'})
            instance.record_failure = AsyncMock(return_value={'status': 'struggling'})
            result = await mastery_node(state)

    instance.record_failure.assert_called()
