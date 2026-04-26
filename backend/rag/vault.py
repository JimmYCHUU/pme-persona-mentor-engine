"""Vault ingestion pipeline for private user files."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable

import chromadb

from core.config import settings
from services.ollama_service import ollama_service


logger = logging.getLogger(__name__)


async def vault_ingest(file_path: str, persona_id: str) -> None:
    """Ingest supported vault files and index semantic chunks into ChromaDB."""

    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix not in {".pdf", ".docx", ".mp4", ".mp3"}:
        logger.warning("Unsupported vault file type: %s", suffix)
        return

    text = await _extract_text(path)
    if not text.strip():
        logger.warning("No extractable text found in %s", path.name)
        return

    chunks = list(_chunk_text(text, 512))
    if not chunks:
        return

    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(name=f"vault_{persona_id}")
    ids: list[str] = []
    documents: list[str] = []
    embeddings: list[list[float]] = []
    metadatas: list[dict] = []
    timestamp = datetime.utcnow().isoformat()
    for idx, chunk in enumerate(chunks):
        try:
            emb = await ollama_service.embed(settings.OLLAMA_EMBED_MODEL, chunk)
            if not emb:
                continue
            ids.append(f"{path.stem}-{idx}")
            documents.append(chunk)
            embeddings.append(emb)
            metadatas.append({"source": path.name, "authority": 100, "timestamp": timestamp})
        except Exception as exc:
            logger.error("Embedding failed for %s chunk %s: %s", path.name, idx, exc)
            continue
    if ids:
        collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)


async def _extract_text(path: Path) -> str:
    """Extract text from supported file types."""

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join([(p.extract_text() or "") for p in reader.pages])
    if suffix == ".docx":
        from docx import Document

        doc = Document(str(path))
        return "\n".join([p.text for p in doc.paragraphs])
    if suffix in {".mp4", ".mp3"}:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(str(path))
        return str(result.get("text", ""))
    return ""


def _chunk_text(text: str, chunk_size: int) -> Iterable[str]:
    """Split text into fixed-size semantic chunks."""

    clean = " ".join(text.split())
    if not clean:
        return []
    return [clean[i : i + chunk_size] for i in range(0, len(clean), chunk_size)]
