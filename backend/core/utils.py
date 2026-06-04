"""Utility functions for the PME backend."""
import uuid
from datetime import datetime, timezone
from typing import Any


def envelope(success: bool = True, data: Any = None, error: str | None = None) -> dict:
    """Standard API response envelope (ARCH-5).

    Every FastAPI endpoint returns:
    {"success": bool, "data": any, "error": str | null}
    """
    return {"success": success, "data": data, "error": error}


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    uid = uuid.uuid4().hex[:12]
    return f"{prefix}{uid}" if prefix else uid


def now_iso() -> str:
    """Return current UTC time as ISO format string."""
    return datetime.now(timezone.utc).isoformat()

