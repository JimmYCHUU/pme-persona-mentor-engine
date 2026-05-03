"""Ingest API — full implementation for vault file uploads and fingerprint URLs."""

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
import os
from core.config import settings
from rag.vault import ingest_vault_file
from rag.fingerprint import ingest_youtube, ingest_url, seed_evolution_db

router = APIRouter()


@router.post('/vault', response_model=dict)
async def upload_vault(
    file: UploadFile = File(...),
    persona_id: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Accept file upload and run vault ingestion."""
    upload_dir = os.path.join(settings.UPLOAD_DIR, persona_id)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)

    # Run ingestion as background task
    background_tasks.add_task(_ingest_vault_bg, persona_id, file_path)

    return {
        'success': True,
        'data': {'filename': file.filename, 'persona_id': persona_id, 'status': 'ingesting'},
        'error': None,
    }


async def _ingest_vault_bg(persona_id: str, file_path: str) -> None:
    """Background task wrapper for vault ingestion."""
    try:
        await ingest_vault_file(persona_id, file_path)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Vault ingest failed: {e}')


@router.post('/fingerprint', response_model=dict)
async def ingest_fingerprint(body: dict, background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Accept URL for fingerprint ingestion.
    Auto-detects YouTube vs. generic URL.
    """
    url = body.get('url', '')
    persona_id = body.get('persona_id', '')

    if not url or not persona_id:
        return {'success': False, 'data': None, 'error': 'url and persona_id required'}

    # Seed evolution_db if not exists
    await seed_evolution_db(persona_id)

    # Detect YouTube
    is_youtube = any(d in url for d in ['youtube.com', 'youtu.be'])

    if is_youtube:
        background_tasks.add_task(_ingest_youtube_bg, persona_id, url)
    else:
        background_tasks.add_task(_ingest_url_bg, persona_id, url)

    return {
        'success': True,
        'data': {'url': url, 'persona_id': persona_id, 'type': 'youtube' if is_youtube else 'web'},
        'error': None,
    }


async def _ingest_youtube_bg(persona_id: str, url: str) -> None:
    """Background task wrapper for YouTube ingestion."""
    try:
        await ingest_youtube(persona_id, url)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'YouTube ingest failed: {e}')


async def _ingest_url_bg(persona_id: str, url: str) -> None:
    """Background task wrapper for URL ingestion."""
    try:
        await ingest_url(persona_id, url)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'URL ingest failed: {e}')
