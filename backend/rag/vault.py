"""Vault ingestion pipeline for private user files."""

from __future__ import annotations

import logging
from pathlib import Path

from core.config import settings


logger = logging.getLogger(__name__)


async def vault_ingest(file_path: str, persona_id: str) -> None:
    """Ingest supported vault files and index semantic chunks into ChromaDB."""

    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix not in {".pdf", ".docx", ".mp4", ".mp3"}:
        logger.warning("Unsupported vault file type: %s", suffix)
        return
    # Minimal phase-safe implementation placeholder.
    # Full extraction/embedding is handled in later hardening.
    persona_dir = Path(settings.PERSONA_DIR) / persona_id
    persona_dir.mkdir(parents=True, exist_ok=True)
