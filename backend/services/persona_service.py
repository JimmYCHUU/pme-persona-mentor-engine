"""Persona profile persistence and gap-fill helper logic."""

from __future__ import annotations

import json
from pathlib import Path

from core.config import settings
from core.utils import ensure_dir, read_json, utcnow_iso, write_json


class PersonaService:
    """Service for persona CRUD operations on local JSON files."""

    @staticmethod
    async def load(persona_id: str) -> dict:
        """Load a persona profile by id from local storage."""

        persona_path = Path(settings.PERSONA_DIR) / f"{persona_id}.json"
        data = read_json(persona_path, {})
        if data:
            return data
        # fallback folder-style path used by ingestion metadata
        nested = Path(settings.PERSONA_DIR) / persona_id / "profile.json"
        return read_json(nested, {})

    @staticmethod
    async def save(profile: dict) -> None:
        """Save a persona profile to local storage."""

        ensure_dir(settings.PERSONA_DIR)
        profile.setdefault("created_at", utcnow_iso())
        persona_id = profile["persona_id"]
        write_json(Path(settings.PERSONA_DIR) / f"{persona_id}.json", profile)
        write_json(Path(settings.PERSONA_DIR) / persona_id / "profile.json", profile)

    @staticmethod
    async def list_all() -> list[dict]:
        """Return all stored persona profiles."""

        base = ensure_dir(settings.PERSONA_DIR)
        profiles: list[dict] = []
        for f in sorted(base.glob("*.json")):
            if f.name == "evolution_db.json":
                continue
            data = read_json(f, {})
            if data.get("persona_id"):
                profiles.append(data)
        return profiles

    @staticmethod
    async def update_sliders(persona_id: str, sliders: dict) -> None:
        """Update slider values in an existing persona profile."""

        profile = await PersonaService.load(persona_id)
        profile.setdefault("sliders", {})
        profile["sliders"].update(sliders)
        await PersonaService.save(profile)

    @staticmethod
    async def detect_gaps(persona_id: str) -> list[str]:
        """Detect missing soul attributes for a persona profile."""

        profile = await PersonaService.load(persona_id)
        soul = profile.get("soul", {})
        required = ["philosophy_tags", "few_shot_examples", "catchphrases", "reaction_patterns"]
        return [k for k in required if not soul.get(k)]

    @staticmethod
    async def generate_gap_questions(gaps: list[str]) -> list[str]:
        """Generate targeted interview questions for missing soul attributes."""

        mapping = {
            "philosophy_tags": "What core principles should always guide your teaching style?",
            "few_shot_examples": "Provide a short mentor-style exchange example for a struggling student.",
            "catchphrases": "What phrases do you repeat when emphasizing important concepts?",
            "reaction_patterns": "How do you respond to repeated mistakes or confusion?",
        }
        questions = [mapping[g] for g in gaps if g in mapping]
        return questions[:5]

    @staticmethod
    async def save_gap_fill_answers(persona_id: str, answers: dict) -> None:
        """Persist answers from the gap-fill interview for the persona."""

        profile = await PersonaService.load(persona_id)
        profile.setdefault("gap_fill", {})
        profile["gap_fill"].update(answers)
        await PersonaService.save(profile)
