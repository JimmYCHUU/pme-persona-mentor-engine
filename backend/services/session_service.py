"""Session persistence to SQLite and JSON snapshot backups."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from core.config import settings
from core.database import AsyncSessionLocal
from core.utils import ensure_dir, read_json, utcnow_iso, write_json
from models.session import SessionSnapshot


class SessionService:
    """Service for session load/save operations."""

    @staticmethod
    async def load(session_id: str) -> dict | None:
        """Load a session snapshot by id from SQLite or JSON fallback."""

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SessionSnapshot).where(SessionSnapshot.session_id == session_id))
            row = result.scalar_one_or_none()
            if row:
                return json.loads(row.snapshot_json)
        p = Path(settings.SESSION_DIR) / f"{session_id}.json"
        return read_json(p, None)

    @staticmethod
    async def save(snapshot: dict) -> None:
        """Save session snapshot to both SQLite and JSON backup."""

        snapshot.setdefault("updated_at", utcnow_iso())
        snapshot.setdefault("created_at", snapshot["updated_at"])
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(SessionSnapshot).where(SessionSnapshot.session_id == snapshot["session_id"])
            )
            row = result.scalar_one_or_none()
            payload = json.dumps(snapshot)
            if row is None:
                row = SessionSnapshot(
                    session_id=snapshot["session_id"],
                    persona_id=snapshot.get("persona_id", ""),
                    created_at=snapshot["created_at"],
                    updated_at=snapshot["updated_at"],
                    mode=snapshot.get("mode", "deep_dive"),
                    snapshot_json=payload,
                )
                db.add(row)
            else:
                row.updated_at = snapshot["updated_at"]
                row.mode = snapshot.get("mode", "deep_dive")
                row.snapshot_json = payload
            await db.commit()
        ensure_dir(settings.SESSION_DIR)
        write_json(Path(settings.SESSION_DIR) / f"{snapshot['session_id']}.json", snapshot)

    @staticmethod
    async def get_latest_for_persona(persona_id: str) -> dict | None:
        """Return the latest saved snapshot for a persona if present."""

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SessionSnapshot).where(SessionSnapshot.persona_id == persona_id))
            rows = list(result.scalars().all())
        if not rows:
            return None
        rows.sort(key=lambda r: r.updated_at, reverse=True)
        return json.loads(rows[0].snapshot_json)
