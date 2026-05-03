"""Shared utilities for the PME backend (DRY target)."""

import uuid
import datetime
from typing import Any


def generate_id() -> str:
    """Generate a UUID v4 string."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """Return current UTC time as ISO-8601 string."""
    return datetime.datetime.utcnow().isoformat()


def success_response(data: Any = None) -> dict:
    """Build a standard success envelope."""
    return {"success": True, "data": data, "error": None}


def error_response(error: str) -> dict:
    """Build a standard error envelope."""
    return {"success": False, "data": None, "error": error}
