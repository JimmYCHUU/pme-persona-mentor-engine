"""File-based LLM response cache with SHA256 keys and 24h TTL."""
import hashlib
import json
import os
import time
from pathlib import Path

CACHE_DIR = Path("./data/response_cache")
CACHE_TTL = 86400  # 24 hours


def _key(model: str, system: str, message: str) -> str:
    """Deterministic SHA256 key from model + system prefix + message."""
    raw = f"{model}::{system[:300]}::{message}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached(model: str, system: str, message: str) -> str | None:
    """Return cached response or None on miss / expiry."""
    path = CACHE_DIR / f"{_key(model, system, message)}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    if time.time() - data["ts"] > CACHE_TTL:
        path.unlink(missing_ok=True)
        return None
    return data["response"]


def set_cached(model: str, system: str, message: str, response: str) -> None:
    """Store a response in the file cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_key(model, system, message)}.json"
    path.write_text(json.dumps({"ts": time.time(), "response": response}))
