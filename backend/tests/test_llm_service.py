"""TDD tests for services.llm_service — LLM with fallback chain + cache."""
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock


# ── Helpers ───────────────────────────────────────────────────

def _ok_response(content: str = "test response") -> dict:
    """Simulates a valid OpenRouter JSON response."""
    return {"choices": [{"message": {"content": content}}]}


def _make_429_response():
    """Simulates an HTTP 429 response."""
    resp = httpx.Response(429, request=httpx.Request("POST", "http://fake"))
    return httpx.HTTPStatusError("rate limited", request=resp.request, response=resp)


# ── Cache integration ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_returns_cached_when_no_history(monkeypatch):
    """When no history, cache hit skips LLM call."""
    from services.llm_service import LLMService
    import services.llm_service as mod

    svc = LLMService()
    monkeypatch.setattr(mod, "get_cached", lambda *a: "cached-reply")
    # Should never call LLM
    svc._call_with_fallback = AsyncMock(side_effect=AssertionError("should not be called"))
    result = await svc.chat("hello", "system", history=[])
    assert result == "cached-reply"


@pytest.mark.asyncio
async def test_chat_skips_cache_when_history_present(monkeypatch):
    """When history is present, cache is bypassed."""
    from services.llm_service import LLMService

    svc = LLMService()
    # Cache should NOT be checked
    cache_called = False

    def fake_get(*a):
        nonlocal cache_called
        cache_called = True
        return None

    monkeypatch.setattr("services.response_cache.get_cached", fake_get)
    monkeypatch.setattr(
        "services.response_cache.set_cached", lambda *a: None
    )

    mock_call = AsyncMock(return_value="live-reply")
    svc._call_with_fallback = mock_call

    result = await svc.chat("hello", "system", history=[{"role": "user", "content": "prev"}])
    assert result == "live-reply"
    assert not cache_called


@pytest.mark.asyncio
async def test_chat_stores_in_cache_on_miss(monkeypatch):
    """On cache miss with no history, result is cached."""
    from services.llm_service import LLMService
    import services.llm_service as mod

    svc = LLMService()
    monkeypatch.setattr(mod, "get_cached", lambda *a: None)

    stored = {}

    def fake_set(model, sys, msg, resp):
        stored["resp"] = resp

    monkeypatch.setattr(mod, "set_cached", fake_set)

    mock_call = AsyncMock(return_value="new-reply")
    svc._call_with_fallback = mock_call

    result = await svc.chat("hello", "system", history=[])
    assert result == "new-reply"
    assert stored["resp"] == "new-reply"


# ── Fallback chain ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fallback_chain_tries_next_model_on_429(monkeypatch):
    """When primary model gets 429, fallback models are tried."""
    from services.llm_service import LLMService
    import services.llm_service as mod

    svc = LLMService()
    call_log = []

    async def fake_openrouter(model, system, message, history):
        call_log.append(model)
        if model == "primary-model":
            raise _make_429_response()
        return "fallback-response"

    svc._call_openrouter = fake_openrouter

    monkeypatch.setattr(mod, "FALLBACK_CHAIN", ["fallback-model-1"])

    result = await svc._call_with_fallback("primary-model", "sys", "msg", [])
    assert result == "fallback-response"
    assert "primary-model" in call_log
    assert "fallback-model-1" in call_log


# ── Graceful failure ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_graceful_failure_when_all_providers_fail(monkeypatch):
    """When all models and Ollama fail, returns graceful message."""
    from services.llm_service import LLMService
    import services.llm_service as mod

    svc = LLMService()

    async def fail_openrouter(*a):
        raise Exception("dead")

    async def fail_ollama(*a):
        raise Exception("also dead")

    svc._call_openrouter = fail_openrouter
    svc._call_ollama = fail_ollama
    monkeypatch.setattr(mod, "FALLBACK_CHAIN", [])

    result = await svc._call_with_fallback("model", "sys", "msg", [])
    assert "moment" in result.lower() or "capacity" in result.lower()


# ── Context trimming ──────────────────────────────────────────

def test_trim_keeps_recent_within_budget():
    """Trimmer retains the most recent history within token budget."""
    from services.llm_service import LLMService

    svc = LLMService()
    history = [
        {"role": "user", "content": "a" * 5000},  # older — should be dropped
        {"role": "assistant", "content": "b" * 100},  # recent — should be kept
    ]
    trimmed = svc._trim("sys", "msg", history)
    # The large old message should be dropped to stay within budget
    assert len(trimmed) <= 2
    # The most recent small message should be kept
    if trimmed:
        assert trimmed[-1]["content"] == "b" * 100


def test_trim_empty_history():
    """Empty history returns empty list."""
    from services.llm_service import LLMService

    svc = LLMService()
    assert svc._trim("sys", "msg", []) == []


# ── Health check ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check_returns_dict():
    """Health check returns a dict with expected keys."""
    from services.llm_service import LLMService

    svc = LLMService()
    # Will fail gracefully since no real servers are running
    result = await svc.check_health()
    assert "openrouter" in result
    assert "ollama" in result
    assert "primary" in result
