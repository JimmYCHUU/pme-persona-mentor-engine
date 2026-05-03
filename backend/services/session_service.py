"""Session snapshot save/load service."""

import json
import os
from typing import Optional
from core.config import settings
from core.utils import now_iso


class SessionService:
    """Manages session snapshot persistence (JSON files + SQLite)."""

    @staticmethod
    async def load(session_id: str) -> Optional[dict]:
        """Load session snapshot from JSON file."""
        path = os.path.join(settings.SESSION_DIR, f'session_{session_id}.json')
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return json.load(f)

    @staticmethod
    async def save(snapshot: dict) -> None:
        """Save session snapshot to JSON file and SQLite."""
        session_id = snapshot.get('session_id', '')
        if not session_id:
            return
        os.makedirs(settings.SESSION_DIR, exist_ok=True)
        path = os.path.join(settings.SESSION_DIR, f'session_{session_id}.json')
        snapshot['updated_at'] = now_iso()
        with open(path, 'w') as f:
            json.dump(snapshot, f, indent=2)

        # Also save to SQLite
        from core.database import AsyncSessionLocal
        from models.session import Session
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Session).where(Session.session_id == session_id)
            )
            row = result.scalar_one_or_none()
            if row:
                row.snapshot_json = json.dumps(snapshot)
                row.mode = snapshot.get('mode', 'deep_dive')
            else:
                row = Session(
                    session_id=session_id,
                    persona_id=snapshot.get('persona_id', ''),
                    mode=snapshot.get('mode', 'deep_dive'),
                    snapshot_json=json.dumps(snapshot),
                )
                db.add(row)
            await db.commit()

    @staticmethod
    async def get_latest_for_persona(persona_id: str) -> Optional[dict]:
        """Get the most recent session for a persona."""
        from core.database import AsyncSessionLocal
        from models.session import Session
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Session)
                .where(Session.persona_id == persona_id)
                .order_by(Session.updated_at.desc())
                .limit(1)
            )
            row = result.scalar_one_or_none()
            if row:
                return json.loads(row.snapshot_json)
            return None
