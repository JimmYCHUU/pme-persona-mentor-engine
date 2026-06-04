"""TDD tests for api.mentor_gallery — pre-built mentor gallery endpoints."""
import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mentor_base(tmp_path):
    """Create a temporary mentor directory structure for testing."""
    # Create cybersecurity/testmentor
    mentor_dir = tmp_path / "cybersecurity" / "testmentor"
    mentor_dir.mkdir(parents=True)

    (mentor_dir / "profile.json").write_text(json.dumps({
        "id": "testmentor",
        "display_name": "Test Mentor",
        "real_name": "Test Person",
        "field": "cybersecurity",
        "sub_speciality": "Testing",
        "description": "A test mentor.",
        "avatar_emoji": "🧪",
        "teaching_level": "Beginner",
        "best_for": ["testing", "debugging", "TDD"],
        "personality_tags": ["calm", "patient"],
        "subscriber_count": "1M",
    }))

    (mentor_dir / "system_prompt.txt").write_text(
        "You are Test Mentor. You teach testing."
    )

    knowledge_dir = mentor_dir / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "quotes.json").write_text(json.dumps({
        "mentor_id": "testmentor",
        "quotes": [{"topic": "testing", "quote": "Always test first."}],
    }))

    # Create business category with no mentors (empty)
    (tmp_path / "business").mkdir()

    return tmp_path


def test_get_categories(mentor_base, monkeypatch):
    """GET /categories returns all 8 categories with counts."""
    import api.mentor_gallery as mod
    monkeypatch.setattr(mod, "MENTOR_BASE", mentor_base)

    import asyncio
    result = asyncio.get_event_loop().run_until_complete(mod.get_categories())
    assert result["success"] is True
    cats = result["data"]
    assert isinstance(cats, list)
    # Should find cybersecurity with 1 mentor
    cyber = next((c for c in cats if c["id"] == "cybersecurity"), None)
    assert cyber is not None
    assert cyber["mentor_count"] == 1


def test_get_category_mentors(mentor_base, monkeypatch):
    """GET /{category} returns mentor profiles."""
    import api.mentor_gallery as mod
    monkeypatch.setattr(mod, "MENTOR_BASE", mentor_base)

    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        mod.get_category_mentors("cybersecurity")
    )
    assert result["success"] is True
    mentors = result["data"]
    assert len(mentors) == 1
    assert mentors[0]["display_name"] == "Test Mentor"


def test_get_category_not_found(mentor_base, monkeypatch):
    """GET /{category} returns error for non-existent category."""
    import api.mentor_gallery as mod
    monkeypatch.setattr(mod, "MENTOR_BASE", mentor_base)

    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        mod.get_category_mentors("nonexistent")
    )
    assert result["success"] is False
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_activate_mentor(mentor_base, monkeypatch):
    """POST /{category}/{mentor_id}/activate creates persona."""
    import api.mentor_gallery as mod
    from fastapi import BackgroundTasks
    monkeypatch.setattr(mod, "MENTOR_BASE", mentor_base)

    # Mock PersonaService.create_prebuilt by patching the import inside activate_mentor
    mock_create = AsyncMock(return_value={"id": "testmentor"})
    monkeypatch.setattr("services.persona_service.PersonaService.create_prebuilt", mock_create)

    bg = BackgroundTasks()
    result = await mod.activate_mentor("cybersecurity", "testmentor", bg)
    assert result["success"] is True
    assert result["data"]["persona_id"] == "testmentor"
    assert result["data"]["status"] == "activated"


@pytest.mark.asyncio
async def test_activate_nonexistent_mentor(mentor_base, monkeypatch):
    """POST /{category}/{mentor_id}/activate returns error for missing mentor."""
    import api.mentor_gallery as mod
    from fastapi import BackgroundTasks
    monkeypatch.setattr(mod, "MENTOR_BASE", mentor_base)

    bg = BackgroundTasks()
    result = await mod.activate_mentor("cybersecurity", "nobody", bg)
    assert result["success"] is False
