"""Utility functions for the PME backend."""
from typing import Any


def envelope(success: bool = True, data: Any = None, error: str | None = None) -> dict:
    """Standard API response envelope (ARCH-5).

    Every FastAPI endpoint returns:
    {"success": bool, "data": any, "error": str | null}
    """
    return {"success": success, "data": data, "error": error}
