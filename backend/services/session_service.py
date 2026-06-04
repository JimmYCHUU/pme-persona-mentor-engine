"""Session service — manages session lifecycle and state persistence."""
import json
import uuid
from pathlib import Path
from core.config import settings


class SessionService:
    """Manages session creation, retrieval, and snapshot persistence."""

    def __init__(self):
        self.session_dir = Path(settings.SESSION_DIR)
        self.session_dir.mkdir(parents=True, exist_ok=True)

    async def create_session(self, persona_id: str) -> dict:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "persona_id": persona_id,
            "history": [],
            "status": "active",
        }
        self._save(session_id, session)
        return session

    async def get_session(self, session_id: str) -> dict | None:
        """Get a session by ID."""
        return self._load(session_id)

    async def get_snapshot(self, session_id: str) -> dict | None:
        """Get session snapshot for memory node."""
        return self._load(session_id)

    async def append_turn(self, session_id: str, role: str, content: str) -> None:
        """Append a conversation turn to the session."""
        session = self._load(session_id)
        if session:
            session["history"].append({"role": role, "content": content})
            self._save(session_id, session)

    async def list_sessions(self, persona_id: str | None = None) -> list:
        """List all sessions, optionally filtered by persona."""
        sessions = []
        for path in self.session_dir.glob("*.json"):
            session = json.loads(path.read_text())
            if persona_id and session.get("persona_id") != persona_id:
                continue
            sessions.append(session)
        return sessions

    def _save(self, session_id: str, data: dict) -> None:
        path = self.session_dir / f"{session_id}.json"
        path.write_text(json.dumps(data, indent=2))

    def _load(self, session_id: str) -> dict | None:
        path = self.session_dir / f"{session_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())
