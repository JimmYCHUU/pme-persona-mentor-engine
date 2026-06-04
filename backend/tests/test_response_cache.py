"""TDD tests for services.response_cache — file-based LLM response cache."""
import json
import time
import pytest
from pathlib import Path


@pytest.fixture
def cache_dir(tmp_path):
    """Use a temporary directory for cache tests."""
    return tmp_path / "response_cache"


@pytest.fixture(autouse=True)
def _patch_cache_dir(monkeypatch, cache_dir):
    """Redirect CACHE_DIR to tmp for every test."""
    import services.response_cache as mod
    monkeypatch.setattr(mod, "CACHE_DIR", cache_dir)


# ── key generation ────────────────────────────────────────────

def test_key_is_deterministic():
    """Same inputs always produce the same cache key."""
    from services.response_cache import _key
    k1 = _key("model-a", "system-text", "hello")
    k2 = _key("model-a", "system-text", "hello")
    assert k1 == k2


def test_key_differs_on_different_input():
    """Different messages produce different keys."""
    from services.response_cache import _key
    k1 = _key("model-a", "system-text", "hello")
    k2 = _key("model-a", "system-text", "goodbye")
    assert k1 != k2


# ── cache miss ────────────────────────────────────────────────

def test_get_cached_returns_none_on_miss():
    """Cache miss returns None."""
    from services.response_cache import get_cached
    result = get_cached("model-a", "system", "never-seen-before")
    assert result is None


# ── set + get roundtrip ───────────────────────────────────────

def test_set_then_get_roundtrip():
    """set_cached stores a value that get_cached retrieves."""
    from services.response_cache import set_cached, get_cached
    set_cached("model-a", "sys", "msg", "the-response")
    assert get_cached("model-a", "sys", "msg") == "the-response"


# ── TTL expiration ────────────────────────────────────────────

def test_expired_entry_returns_none(monkeypatch, cache_dir):
    """Entries older than CACHE_TTL are evicted on read."""
    import services.response_cache as mod

    # Write a cache entry with a timestamp far in the past
    mod.set_cached("model-a", "sys", "msg", "old-response")
    key = mod._key("model-a", "sys", "msg")
    path = cache_dir / f"{key}.json"

    data = json.loads(path.read_text())
    data["ts"] = time.time() - 100_000  # well past 24h
    path.write_text(json.dumps(data))

    assert mod.get_cached("model-a", "sys", "msg") is None
    # File should be deleted after expiration
    assert not path.exists()


# ── cache directory auto-creation ─────────────────────────────

def test_set_cached_creates_directory(cache_dir):
    """set_cached auto-creates the cache directory if missing."""
    assert not cache_dir.exists()
    from services.response_cache import set_cached
    set_cached("model-a", "sys", "msg", "resp")
    assert cache_dir.exists()
