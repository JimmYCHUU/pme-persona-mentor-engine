"""Persona service — manages mentor persona profiles."""
import json
import uuid
from pathlib import Path
from core.config import settings


class PersonaService:
    """Manages persona creation, retrieval, and activation."""

    def __init__(self):
        self.persona_dir = Path(settings.PERSONA_DIR)
        self.persona_dir.mkdir(parents=True, exist_ok=True)

    async def get_persona(self, persona_id: str) -> dict | None:
        """Get persona by ID."""
        path = self.persona_dir / f"{persona_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    async def create_persona(self, name: str, system_prompt: str, **kwargs) -> dict:
        """Create a custom persona."""
        persona_id = str(uuid.uuid4())
        persona = {
            "id": persona_id,
            "name": name,
            "system_prompt": system_prompt,
            **kwargs,
        }
        self._save(persona_id, persona)
        return persona

    @staticmethod
    async def create_prebuilt(mentor_id: str, profile: dict, system_prompt: str) -> dict:
        """Activate a pre-built mentor as a persona."""
        svc = PersonaService()
        persona = {
            "id": mentor_id,
            "name": profile.get("display_name", mentor_id),
            "system_prompt": system_prompt,
            "profile": profile,
            "is_prebuilt": True,
        }
        svc._save(mentor_id, persona)
        return persona

    async def list_personas(self) -> list:
        """List all available personas."""
        personas = []
        for path in self.persona_dir.glob("*.json"):
            personas.append(json.loads(path.read_text()))
        return personas

    async def delete_persona(self, persona_id: str) -> bool:
        """Delete a persona."""
        path = self.persona_dir / f"{persona_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def _save(self, persona_id: str, data: dict) -> None:
        path = self.persona_dir / f"{persona_id}.json"
        path.write_text(json.dumps(data, indent=2))
