"""
Vault ingestion pipeline — handles PDF, DOCX, MP4/MP3 ingestion.
Chunks content semantically and stores in ChromaDB.
"""

import os
import json
import uuid
import logging
from typing import Optional
from core.config import settings

logger = logging.getLogger(__name__)

# Lazy imports for heavy libraries
_chroma_client = None


def _get_chroma():
    """Lazy-load ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _chroma_client


async def ingest_vault_file(persona_id: str, file_path: str) -> dict:
    """
    Ingest a file into the persona's vault ChromaDB collection.
    Supports: PDF, DOCX, TXT, MP4, MP3, M4A

    Returns: {chunks_added: int, source_file: str}
    """
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    # Extract text based on file type
    if ext == '.pdf':
        text = _extract_pdf(file_path)
    elif ext == '.docx':
        text = _extract_docx(file_path)
    elif ext == '.txt':
        with open(file_path, 'r', errors='ignore') as f:
            text = f.read()
    elif ext in ('.mp4', '.mp3', '.m4a'):
        text = await _transcribe_audio(file_path)
    else:
        logger.warning(f'Unsupported file type: {ext}')
        return {'chunks_added': 0, 'source_file': filename}

    if not text or len(text.strip()) < 50:
        logger.warning(f'Extracted text too short from {filename}')
        return {'chunks_added': 0, 'source_file': filename}

    # Chunk the text semantically
    chunks = _semantic_chunk(text, max_chunk_size=1000)

    # Store in ChromaDB
    collection_name = f'vault_{persona_id}'
    client = _get_chroma()
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={'persona_id': persona_id, 'type': 'vault'},
    )

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f'{persona_id}_{filename}_{i}_{uuid.uuid4().hex[:8]}'
        ids.append(chunk_id)
        documents.append(chunk)
        metadatas.append({
            'source_file': filename,
            'chunk_index': i,
            'authority': 100,  # Private vault = Truth_100
            'persona_id': persona_id,
        })

    if ids:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    logger.info(f'Ingested {len(ids)} chunks from {filename} into {collection_name}')
    return {'chunks_added': len(ids), 'source_file': filename}


def _extract_pdf(file_path: str) -> str:
    """Extract text from PDF using pypdf."""
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return '\n\n'.join(pages)


def _extract_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    from docx import Document
    doc = Document(file_path)
    return '\n\n'.join([p.text for p in doc.paragraphs if p.text.strip()])


async def _transcribe_audio(file_path: str) -> str:
    """Transcribe audio/video using Whisper (base model only)."""
    try:
        import whisper
        model = whisper.load_model('base')
        result = model.transcribe(file_path)
        return result.get('text', '')
    except Exception as e:
        logger.error(f'Whisper transcription failed: {e}')
        return ''


def _semantic_chunk(text: str, max_chunk_size: int = 1000) -> list[str]:
    """
    Simple semantic chunking by paragraph boundaries.
    Merges short paragraphs, splits long ones.
    """
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ''

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            current_chunk += ('\n\n' + para) if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If single paragraph exceeds max, split by sentences
            if len(para) > max_chunk_size:
                sentences = para.replace('. ', '.\n').split('\n')
                sub_chunk = ''
                for sent in sentences:
                    if len(sub_chunk) + len(sent) + 1 <= max_chunk_size:
                        sub_chunk += (' ' + sent) if sub_chunk else sent
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = sent
                current_chunk = sub_chunk
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
