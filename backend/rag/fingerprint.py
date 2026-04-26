"""Fingerprint ingestion for public persona sources."""

from __future__ import annotations

import logging
from pathlib import Path

from core.config import settings
from core.utils import write_json


logger = logging.getLogger(__name__)


async def fingerprint_ingest(url: str, persona_id: str) -> None:
    """Ingest public source URL and seed persona evolution db."""

    logger.info("Fingerprint ingest requested: %s", url)
    evolution_path = Path(settings.PERSONA_DIR) / persona_id / "evolution_db.json"
    if not evolution_path.exists():
        write_json(evolution_path, [])
