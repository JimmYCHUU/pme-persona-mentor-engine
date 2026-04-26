"""Shared backend utility helpers."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


def utcnow_iso() -> str:
    """Return UTC timestamp in ISO-8601 format."""

    return dt.datetime.utcnow().isoformat()


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if needed and return a Path object."""

    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_json(path: str | Path, default: Any) -> Any:
    """Read JSON from path and return default if file is missing or invalid."""

    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: str | Path, payload: Any) -> None:
    """Write JSON payload to disk with UTF-8 encoding and indentation."""

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
