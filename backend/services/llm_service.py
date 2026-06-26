"""
LLM Service — OpenRouter with fallback chain + Ollama + response cache.

Primary: OpenRouter (configurable models)
Fallback chain: tried in order on rate limit
Last resort: local Ollama
Graceful degradation: user-friendly message when all providers fail

ALL LLM calls in the system go through this service (ARCH-4).
"""

import httpx
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings
from services.response_cache import get_cached, set_cached
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

CTX_LIMIT = 8192
CHARS_PER_TOKEN = 4

FALLBACK_CHAIN = [
    settings.FALLBACK_MODEL_1,  # meta-llama/llama-3.3-70b-instruct:free
    settings.FALLBACK_MODEL_2,  # mistralai/mistral-7b-instruct:free
]


class LLMService:

    async def chat(self, message: str, system: str,
                   history: list = [], use_reasoning: bool = False) -> str:
        model = settings.REASONING_MODEL if use_reasoning else settings.PERSONA_MODEL

        # Cache check for history-free calls
        if not history:
            cached = get_cached(model, system, message)
            if cached:
                return cached

        response = await self._call_with_fallback(model, system, message, history)

        if not history:
            set_cached(model, system, message, response)

        return response

    async def _call_with_fallback(self, model, system, message, history) -> str:
        models = [model] + FALLBACK_CHAIN

        for m in models:
            for attempt in range(3):
                try:
                    return await self._call_openrouter(m, system, message, history)
                except httpx.HTTPStatusError as e:
                    code = e.response.status_code
                    if code == 429 and attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    # Any non-429 error (404, 403, 500) → skip to next model
                    logger.warning(f"Model {m} returned HTTP {code}, trying next")
                    break
                except Exception as e:
                    logger.warning(f"Model {m} failed: {e}, trying next")
                    break

        # All failed — try local Ollama
        try:
            return await self._call_ollama(system, message, history)
        except Exception:
            return (
                "I need a moment. The thinking pipeline is at capacity. "
                "Give it 60 seconds and ask me again."
            )

    async def _call_openrouter(self, model, system, message, history) -> str:
        trimmed = self._trim(system, message, history)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                *trimmed,
                {"role": "user", "content": message},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as c:
            r = await c.post(
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
            return r.json()["choices"][0]["message"]["content"]

    async def _call_ollama(self, system, message, history) -> str:
        trimmed = self._trim(system, message, history)
        payload = {
            "model": settings.OLLAMA_FALLBACK_MODEL,
            "messages": [
                {"role": "system", "content": system},
                *trimmed,
                {"role": "user", "content": message},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as c:
            r = await c.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload)
            r.raise_for_status()
            return r.json()["message"]["content"]

    async def check_health(self) -> dict:
        status = {"openrouter": False, "ollama": False, "primary": "none"}
        if settings.OPENROUTER_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=5.0) as c:
                    r = await c.get(
                        "https://openrouter.ai/api/v1/models",
                        headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                    )
                    status["openrouter"] = r.status_code == 200
            except Exception:
                pass
        try:
            async with httpx.AsyncClient(timeout=3.0) as c:
                r = await c.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                status["ollama"] = r.status_code == 200
        except Exception:
            pass
        if status["openrouter"]:
            status["primary"] = "openrouter"
        elif status["ollama"]:
            status["primary"] = "ollama"
        return status

    def _trim(self, system, message, history) -> list:
        budget = CTX_LIMIT * CHARS_PER_TOKEN - len(system) - len(message) - 400
        result, used = [], 0
        for turn in reversed(history):
            chars = len(turn.get("content", ""))
            if used + chars > budget:
                break
            result.insert(0, turn)
            used += chars
        return result

    async def chat_stream(
        self, message: str, system: str, history: list = []
    ) -> AsyncGenerator[str, None]:
        """Stream tokens from the LLM. Yields individual text chunks.

        Tries OpenRouter streaming first, falls back to non-streaming chat().
        """
        model = settings.PERSONA_MODEL
        try:
            async for chunk in self._stream_openrouter(model, system, message, history):
                yield chunk
        except Exception as e:
            logger.warning(f"Streaming failed ({e}), falling back to non-stream")
            # Fallback: get full response and yield it at once
            full = await self.chat(message=message, system=system, history=history)
            yield full

    async def _stream_openrouter(
        self, model, system, message, history
    ) -> AsyncGenerator[str, None]:
        """Stream from OpenRouter SSE endpoint, yielding content deltas."""
        trimmed = self._trim(system, message, history)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                *trimmed,
                {"role": "user", "content": message},
            ],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=120.0) as c:
            async with c.stream(
                "POST",
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5173",
                    "X-Title": "Persona Mentor Engine",
                },
                json=payload,
            ) as resp:
                resp.raise_for_status()
                import json as _json
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = _json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (KeyError, _json.JSONDecodeError):
                        continue


llm_service = LLMService()
