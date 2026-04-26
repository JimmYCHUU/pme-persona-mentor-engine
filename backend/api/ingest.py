"""Ingestion API routes for vault files and fingerprint URLs."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile

from core.config import settings
from rag.fingerprint import fingerprint_ingest
from rag.vault import vault_ingest


router = APIRouter()


@router.post("/vault", response_model=dict)
async def ingest_vault(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    persona_id: str = Form(...),
) -> dict:
    """Store uploaded file locally and trigger async vault ingestion."""

    target_dir = Path(settings.UPLOAD_DIR) / persona_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / file.filename
    target.write_bytes(await file.read())
    background_tasks.add_task(vault_ingest, str(target), persona_id)
    return {"success": True, "data": {"queued": True, "path": str(target)}, "error": None}


@router.post("/fingerprint", response_model=dict)
async def ingest_fingerprint(payload: dict, background_tasks: BackgroundTasks) -> dict:
    """Queue public URL fingerprint ingestion."""

    url = payload.get("url", "")
    persona_id = payload.get("persona_id", "")
    background_tasks.add_task(fingerprint_ingest, url, persona_id)
    return {"success": True, "data": {"queued": True}, "error": None}
