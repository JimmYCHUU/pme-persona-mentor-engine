"""Ingest API — STUB for Phase 1. Full implementation in Phase 2."""

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
import os
from core.config import settings

router = APIRouter()


@router.post('/vault', response_model=dict)
async def upload_vault(
    file: UploadFile = File(...),
    persona_id: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Accept file upload for vault ingestion."""
    # Save file to uploads directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, persona_id)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)

    # In Phase 2, this will trigger vault_ingest as BackgroundTask
    return {
        'success': True,
        'data': {'filename': file.filename, 'persona_id': persona_id},
        'error': None,
    }


@router.post('/fingerprint', response_model=dict)
async def ingest_fingerprint(body: dict):
    """Accept URL for fingerprint ingestion."""
    url = body.get('url', '')
    persona_id = body.get('persona_id', '')
    # In Phase 2, this will trigger fingerprint_ingest as BackgroundTask
    return {
        'success': True,
        'data': {'url': url, 'persona_id': persona_id},
        'error': None,
    }
