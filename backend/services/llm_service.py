"""
LLM Service — wraps OpenRouter API with Ollama fallback.

Primary: OpenRouter (deepseek-v3 for persona, deepseek-r1 for reasoning)
Fallback: Local Ollama (llama3.2:3b) if OpenRouter is unavailable

TWO MODELS, TWO JOBS:
  PERSONA_MODEL   — deepseek-v3-0324:free  — persona voice, style transfer
  REASONING_MODEL — deepseek-r1-0528:free  — Socratic scoring, concept extract
"""

import json
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

CTX_LIMIT = 8192       # conservative limit for DeepSeek V3 free
CHARS_PER_TOKEN = 4    # rough approximation


class LLMService:
    """
    Unified LLM service. Routes to OpenRouter by default,
    falls back to local Ollama if OpenRouter is unreachable.
    """

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=8))
    async def chat(
        self,
        message: str,
        system: str,
        history: list = [],
        use_reasoning: bool = False,
    ) -> str:
        """
        Send a chat request.

        Args:
            message: The user message.
            system: The system prompt (persona instructions).
            history: Previous conversation turns.
            use_reasoning: If True, uses REASONING_MODEL (DeepSeek R1).
                           If False, uses PERSONA_MODEL (DeepSeek V3).
        """
        model = settings.REASONING_MODEL if use_reasoning else settings.PERSONA_MODEL
        trimmed = self._trim_history(history, system, message)

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                *trimmed,
                {"role": "user", "content": message},
            ],
            "stream": False,
        }

        # Try OpenRouter first
        if settings.OPENROUTER_API_KEY:
            try:
                return await self._call_openrouter(payload)
            except Exception as e:
                logger.warning(
                    f"OpenRouter failed ({e}), falling back to Ollama"
                )

        # Fallback to local Ollama
        return await self._call_ollama(system, message, trimmed)

    async def stream(
        self,
        message: str,
        system: str,
        history: list = [],
        use_reasoning: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Streaming version — yields token strings."""
        model = settings.REASONING_MODEL if use_reasoning else settings.PERSONA_MODEL
        trimmed = self._trim_history(history, system, message)

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                *trimmed,
                {"role": "user", "content": message},
            ],
            "stream": True,
        }

        if settings.OPENROUTER_API_KEY:
            try:
                async for token in self._stream_openrouter(payload):
                    yield token
                return
            except Exception as e:
                logger.warning(f"OpenRouter stream failed ({e}), falling back")

        # Fallback
        result = await self._call_ollama(system, message, trimmed)
        yield result

    async def check_health(self) -> dict:
        """
        Returns status of both OpenRouter and local Ollama.
        Used by the /health endpoint.
        """
        status = {
            "openrouter": False,
            "ollama": False,
            "primary": "none"
        }

        # Check OpenRouter
        if settings.OPENROUTER_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    r = await client.get(
                        "https://openrouter.ai/api/v1/models",
                        headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                    )
                    status["openrouter"] = r.status_code == 200
            except Exception:
                pass

        # Check Ollama
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                status["ollama"] = r.status_code == 200
        except Exception:
            pass

        if status["openrouter"]:
            status["primary"] = "openrouter"
        elif status["ollama"]:
            status["primary"] = "ollama"

        return status

    # ── Private helpers ────────────────────────────────────────

    async def _call_openrouter(self, payload: dict) -> str:
        """POST to OpenRouter API (OpenAI-compatible)."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5173",
                    "X-Title": "Persona Mentor Engine",
                },
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    async def _stream_openrouter(
        self, payload: dict
    ) -> AsyncGenerator[str, None]:
        """Streaming POST to OpenRouter API."""
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5173",
                    "X-Title": "Persona Mentor Engine",
                },
                json=payload,
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            pass

    async def _call_ollama(
        self, system: str, message: str, history: list
    ) -> str:
        """Fallback to local Ollama."""
        payload = {
            "model": settings.OLLAMA_FALLBACK_MODEL,
            "messages": [
                {"role": "system", "content": system},
                *history,
                {"role": "user", "content": message},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload
            )
            r.raise_for_status()
            return r.json()["message"]["content"]

    def _trim_history(
        self, history: list, system: str, message: str
    ) -> list:
        """Keep most recent turns within context budget."""
        budget = (
            CTX_LIMIT * CHARS_PER_TOKEN
            - len(system)
            - len(message)
            - 400  # safety margin
        )
        result = []
        used = 0
        for turn in reversed(history):
            chars = len(turn.get("content", ""))
            if used + chars > budget:
                break
            result.insert(0, turn)
            used += chars
        return result


# Module-level singleton — import this everywhere
llm_service = LLMService()
