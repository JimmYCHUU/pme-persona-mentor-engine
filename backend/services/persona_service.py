"""Persona profile CRUD service."""

import json
import os
from typing import Optional
from core.config import settings
from core.utils import generate_id, now_iso


class PersonaService:
    """Manages persona profile persistence."""

    @staticmethod
    async def load(persona_id: str) -> Optional[dict]:
        """Load persona profile from JSON file."""
        path = os.path.join(settings.PERSONA_DIR, persona_id, 'profile.json')
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return json.load(f)

    @staticmethod
    async def save(profile: dict) -> None:
        """Save persona profile to JSON file."""
        persona_id = profile.get('persona_id', generate_id())
        profile['persona_id'] = persona_id
        persona_dir = os.path.join(settings.PERSONA_DIR, persona_id)
        os.makedirs(persona_dir, exist_ok=True)
        path = os.path.join(persona_dir, 'profile.json')
        with open(path, 'w') as f:
            json.dump(profile, f, indent=2)

    @staticmethod
    async def list_all() -> list[dict]:
        """Return all saved persona profiles."""
        personas = []
        if not os.path.exists(settings.PERSONA_DIR):
            return personas
        for name in os.listdir(settings.PERSONA_DIR):
            profile_path = os.path.join(settings.PERSONA_DIR, name, 'profile.json')
            if os.path.exists(profile_path):
                with open(profile_path) as f:
                    personas.append(json.load(f))
        return personas

    @staticmethod
    async def update_sliders(persona_id: str, sliders: dict) -> None:
        """Update persona slider values."""
        profile = await PersonaService.load(persona_id)
        if profile:
            profile['sliders'] = sliders
            await PersonaService.save(profile)
