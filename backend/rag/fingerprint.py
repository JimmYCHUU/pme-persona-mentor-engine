"""
Fingerprint ingestion — public persona data extraction.
Handles YouTube transcription, social media, and linguistic profile building.
Seeds evolution_db.json for the Ethical Time Machine.
"""

import os
import json
import uuid
import logging
from typing import Optional
from core.config import settings

logger = logging.getLogger(__name__)

_chroma_client = None


def _get_chroma():
    """Lazy-load ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _chroma_client


async def ingest_youtube(persona_id: str, url: str) -> dict:
    """
    Download and transcribe a YouTube video.
    Store transcript in fingerprint collection.
    """
    try:
        import yt_dlp

        # Download audio
        upload_dir = os.path.join(settings.UPLOAD_DIR, persona_id, 'youtube')
        os.makedirs(upload_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(upload_dir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get('id', 'unknown')
            title = info.get('title', 'Unknown Video')

        # Transcribe
        audio_path = os.path.join(upload_dir, f'{video_id}.mp3')
        if os.path.exists(audio_path):
            import whisper
            model = whisper.load_model('base')
            result = model.transcribe(audio_path)
            transcript = result.get('text', '')
        else:
            transcript = ''

        if not transcript:
            return {'success': False, 'error': 'No transcript extracted'}

        # Store in fingerprint collection
        _store_fingerprint_chunks(persona_id, transcript, title, authority=50)

        return {'success': True, 'title': title, 'chunks_added': len(transcript) // 1000 + 1}

    except Exception as e:
        logger.error(f'YouTube ingestion failed: {e}')
        return {'success': False, 'error': str(e)}


async def ingest_url(persona_id: str, url: str) -> dict:
    """
    Scrape a web page and store content in fingerprint collection.
    """
    try:
        import httpx
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Extract text content
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        text = soup.get_text(separator='\n', strip=True)

        if len(text) < 100:
            return {'success': False, 'error': 'Too little text extracted'}

        title = soup.title.string if soup.title else url
        _store_fingerprint_chunks(persona_id, text, title, authority=50)

        return {'success': True, 'title': title}

    except Exception as e:
        logger.error(f'URL ingestion failed: {e}')
        return {'success': False, 'error': str(e)}


def _store_fingerprint_chunks(persona_id: str, text: str,
                               source_name: str, authority: int = 50):
    """Store text chunks in the fingerprint ChromaDB collection."""
    from rag.vault import _semantic_chunk

    chunks = _semantic_chunk(text, max_chunk_size=800)
    collection_name = f'fingerprint_{persona_id}'
    client = _get_chroma()
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={'persona_id': persona_id, 'type': 'fingerprint'},
    )

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f'{persona_id}_fp_{uuid.uuid4().hex[:8]}'
        ids.append(chunk_id)
        documents.append(chunk)
        metadatas.append({
            'source_file': source_name,
            'chunk_index': i,
            'authority': authority,
            'persona_id': persona_id,
        })

    if ids:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f'Stored {len(ids)} fingerprint chunks for {persona_id}')


async def seed_evolution_db(persona_id: str) -> None:
    """
    Seed evolution_db.json with empty structure.
    Full evolution extraction happens during fingerprint analysis.
    """
    persona_dir = os.path.join(settings.PERSONA_DIR, persona_id)
    os.makedirs(persona_dir, exist_ok=True)
    db_path = os.path.join(persona_dir, 'evolution_db.json')
    if not os.path.exists(db_path):
        with open(db_path, 'w') as f:
            json.dump([], f, indent=2)
        logger.info(f'Seeded evolution_db.json for {persona_id}')
