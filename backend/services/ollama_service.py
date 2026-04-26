"""Ollama API service wrapper used for all model calls."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings


CTX_LIMIT = 4096
CHARS_PER_TOKEN = 4


class OllamaService:
    """Singleton wrapper for Ollama chat and streaming calls."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def chat(
        self,
        model: str,
        system: str,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Send a non-streaming chat request and return model response text."""

        trimmed = self._trim_history(history or [], system, message)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                *trimmed,
                {"role": "user", "content": message},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    async def stream(
        self,
        model: str,
        system: str,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Send a streaming chat request and yield token chunks."""

        trimmed = self._trim_history(history or [], system, message)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                *trimmed,
                {"role": "user", "content": message},
            ],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if not data.get("done"):
                            yield data["message"]["content"]

    def _trim_history(self, history: list[dict[str, str]], system: str, message: str) -> list[dict[str, str]]:
        """Keep only the most recent turns that fit into the context budget."""

        budget = (CTX_LIMIT * CHARS_PER_TOKEN) - len(system) - len(message) - 200
        result: list[dict[str, str]] = []
        used = 0
        for turn in reversed(history):
            turn_chars = len(turn.get("content", ""))
            if used + turn_chars > budget:
                break
            result.insert(0, turn)
            used += turn_chars
        return result

    async def check_health(self) -> bool:
        """Return True if Ollama API is reachable."""

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def embed(self, model: str, text: str) -> list[float]:
        """Generate a vector embedding using Ollama embedding model."""

        payload = {"model": model, "input": text}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{settings.OLLAMA_BASE_URL}/api/embed", json=payload)
            resp.raise_for_status()
            data = resp.json()
            if "embeddings" in data and data["embeddings"]:
                return data["embeddings"][0]
        payload = {"model": model, "prompt": text}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{settings.OLLAMA_BASE_URL}/api/embeddings", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [])


ollama_service = OllamaService()
