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


@router.get('/status/{persona_id}', response_model=dict)
async def ingest_status(persona_id: str):
    """
    Returns per-source ingestion status for the progress screen.
    Checks what data exists for this persona in the vector store.
    """
    import os
    upload_dir = os.path.join(settings.UPLOAD_DIR, persona_id)
    files_uploaded = []
    if os.path.isdir(upload_dir):
        files_uploaded = os.listdir(upload_dir)

    persona_dir = os.path.join(settings.PERSONA_DIR, persona_id)
    has_evolution_db = os.path.exists(os.path.join(persona_dir, 'evolution_db.json')) if os.path.isdir(persona_dir) else False

    return {
        'success': True,
        'data': {
            'files_uploaded': files_uploaded,
            'file_count': len(files_uploaded),
            'has_evolution_db': has_evolution_db,
            'status': 'done' if files_uploaded or has_evolution_db else 'pending',
        },
        'error': None,
    }


@router.post('/scan-folder', response_model=dict)
async def scan_folder(request: dict):
    """
    Scans a folder path for mentor materials.
    Uses the reasoning model to infer which person the materials belong to.
    """
    from pathlib import Path
    from services.llm_service import llm_service

    folder_path = Path(request.get('folder_path', ''))

    if not folder_path.exists() or not folder_path.is_dir():
        return {'success': False, 'data': None, 'error': 'Folder not found'}

    # Collect all supported files
    supported = {'.pdf', '.mp4', '.mp3', '.docx', '.txt', '.m4a'}
    files = [f for f in folder_path.rglob('*') if f.suffix.lower() in supported]

    if not files:
        return {
            'success': True,
            'data': {
                'status': 'empty',
                'files': [],
                'detected_person': None,
                'confidence': 0.0,
            },
            'error': None,
        }

    # Check for MENTOR.txt config file first
    mentor_config = folder_path / 'MENTOR.txt'
    if mentor_config.exists():
        name = mentor_config.read_text().strip().split('\n')[0]
        return {
            'success': True,
            'data': {
                'status': 'config_found',
                'files': [str(f) for f in files],
                'detected_person': name,
                'confidence': 1.0,
            },
            'error': None,
        }

    # Use reasoning model to infer the person from filenames + content samples
    file_samples = []
    for f in files[:5]:
        if f.suffix == '.txt':
            try:
                sample = f.read_text(errors='ignore')[:500]
                file_samples.append(f"File: {f.name}\nSample: {sample[:200]}")
            except Exception:
                file_samples.append(f"File: {f.name}")
        else:
            file_samples.append(f"File: {f.name}")

    prompt = (
        "Based on these filenames and content samples, answer two questions:\n"
        "1. Who is the real-world person these materials are primarily about?\n"
        "2. Do the materials seem to be about multiple DIFFERENT people?\n"
        "Reply ONLY in this format:\n"
        "NAME: [name or 'unknown']\n"
        "CONFIDENCE: [0.0-1.0]\n"
        "MULTIPLE_PEOPLE: [yes or no]\n\n"
        f"Files:\n" + "\n".join(file_samples)
    )

    inference = await llm_service.chat(
        message=prompt,
        system="You identify people from document filenames and content samples. Be concise.",
        use_reasoning=True,
    )

    # Parse the response
    detected_name = None
    confidence = 0.0
    multiple_people = False
    for line in inference.split('\n'):
        if line.startswith('NAME:'):
            detected_name = line.split(':', 1)[1].strip()
            if detected_name.lower() == 'unknown':
                detected_name = None
        elif line.startswith('CONFIDENCE:'):
            try:
                confidence = float(line.split(':', 1)[1].strip())
            except Exception:
                confidence = 0.5
        elif line.startswith('MULTIPLE_PEOPLE:'):
            multiple_people = 'yes' in line.lower()

    if multiple_people:
        status = 'multiple_people'
    elif confidence >= 0.6 and detected_name:
        status = 'detected'
    else:
        status = 'ambiguous'

    return {
        'success': True,
        'data': {
            'status': status,
            'files': [str(f) for f in files],
            'file_count': len(files),
            'detected_person': detected_name,
            'confidence': confidence,
        },
        'error': None,
    }


@router.post('/confirm-folder', response_model=dict)
async def confirm_folder(request: dict, background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    After user confirms the scan result, begins ingestion of all files.
    """
    file_paths = request.get('file_paths', [])
    persona_id = request.get('persona_id', '')

    for file_path in file_paths:
        background_tasks.add_task(_ingest_vault_bg, persona_id, file_path)

    return {
        'success': True,
        'data': {'queued': len(file_paths)},
        'error': None,
    }
