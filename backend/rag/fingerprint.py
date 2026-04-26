"""Fingerprint ingestion for public persona sources."""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path
from statistics import mean

import chromadb
import httpx
from bs4 import BeautifulSoup

from core.config import settings
from core.utils import read_json
from core.utils import write_json
from services.ollama_service import ollama_service


logger = logging.getLogger(__name__)


async def fingerprint_ingest(url: str, persona_id: str) -> None:
    """Ingest public source URL and seed persona evolution db."""

    logger.info("Fingerprint ingest requested: %s", url)
    text = await _fetch_public_text(url)
    profile = _build_profile(text)
    await _store_profile(persona_id, profile, source=url)
    _seed_evolution_db(persona_id, text)


async def _fetch_public_text(url: str) -> str:
    """Fetch source text from YouTube/Twitter/LinkedIn/public pages."""

    lower = url.lower()
    if "youtube.com" in lower or "youtu.be" in lower:
        return await _youtube_transcript(url)
    if "twitter.com" in lower or "x.com" in lower:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            return " ".join([t.get_text(" ", strip=True) for t in soup.find_all("p")])
    if "linkedin.com" in lower:
        # Lightweight fallback: static fetch. Playwright-rich extraction can replace this.
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.get_text(" ", strip=True)
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser").get_text(" ", strip=True)


async def _youtube_transcript(url: str) -> str:
    """Download audio via yt-dlp and transcribe with Whisper base model."""

    import whisper

    tmp_dir = Path(settings.UPLOAD_DIR) / "_tmp_youtube"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_tpl = str(tmp_dir / "%(id)s.%(ext)s")
    cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "-o", out_tpl, url]
    subprocess.run(cmd, check=False, capture_output=True)
    audio_files = sorted(tmp_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not audio_files:
        return ""
    model = whisper.load_model("base")
    result = model.transcribe(str(audio_files[0]))
    return str(result.get("text", ""))


def _build_profile(text: str) -> dict:
    """Create linguistic fingerprint profile from source corpus text."""

    tokens = re.findall(r"[A-Za-z][A-Za-z\-']{2,}", text.lower())
    freq: dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    vocab = [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:50]]

    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    catchphrases = [s for s in sentences if len(s.split()) <= 8][:20]
    if len(catchphrases) > 10:
        catchphrases = catchphrases[:10]

    pos_words = {"great", "excellent", "good", "improve", "solid", "best"}
    neg_words = {"bad", "wrong", "avoid", "terrible", "never", "fail"}
    score_parts = []
    for s in sentences[:200]:
        words = set(re.findall(r"[a-z]+", s.lower()))
        score_parts.append((len(words & pos_words) - len(words & neg_words)) / max(len(words), 1))
    sentiment = float(max(-1.0, min(1.0, mean(score_parts) if score_parts else 0.0)))

    sarcasm_markers = ["yeah right", "sure", "obviously", "as if", "lol"]
    sarcasm_hits = sum(1 for s in sentences if any(m in s.lower() for m in sarcasm_markers))
    sarcasm_level = float(min(1.0, sarcasm_hits / max(len(sentences), 1) * 10))

    few_shot_examples = []
    for s in sentences[:15]:
        few_shot_examples.append({"user": "How should I approach this?", "mentor": s})

    philosophy_tags = [w for w in vocab if w in {"discipline", "clarity", "practice", "fundamentals", "consistency"}]
    reaction_patterns = [s for s in sentences if any(k in s.lower() for k in ["mistake", "again", "retry", "fix"])][:10]

    return {
        "catchphrases": catchphrases,
        "vocabulary": vocab,
        "philosophy_tags": philosophy_tags,
        "sentiment_score": sentiment,
        "sarcasm_level": sarcasm_level,
        "few_shot_examples": few_shot_examples[:10],
        "reaction_patterns": reaction_patterns,
    }


async def _store_profile(persona_id: str, profile: dict, source: str) -> None:
    """Store profile in persona fingerprint collection."""

    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(name=f"fingerprint_{persona_id}")
    body = str(profile)
    embedding = await ollama_service.embed(settings.OLLAMA_EMBED_MODEL, body)
    collection.add(
        ids=[f"fingerprint-{persona_id}"],
        documents=[body],
        metadatas=[{"source": source, "authority": 60}],
        embeddings=[embedding],
    )


def _seed_evolution_db(persona_id: str, text: str) -> None:
    """Seed evolution DB with extracted change-in-thinking entries."""

    evolution_path = Path(settings.PERSONA_DIR) / persona_id / "evolution_db.json"
    if not evolution_path.exists():
        write_json(evolution_path, [])
    existing = read_json(evolution_path, [])
    for sentence in re.split(r"[.!?]+", text):
        s = sentence.strip()
        if not s:
            continue
        if "used to" in s.lower() or "now" in s.lower() or "no longer" in s.lower():
            existing.append(
                {
                    "concept_key": "practice_evolution",
                    "old_advice": s,
                    "new_advice": s,
                    "evolution_year": "2024",
                    "keywords": ["used to", "now", "no longer"],
                }
            )
            if len(existing) >= 25:
                break
    write_json(evolution_path, existing)
