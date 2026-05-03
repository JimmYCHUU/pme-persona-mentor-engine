"""Singleton wrapper for all Ollama API calls."""

import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings
from typing import List, AsyncGenerator

CTX_LIMIT = 4096  # llama3.2:3b context window (tokens)
CHARS_PER_TOKEN = 4  # rough approximation


class OllamaService:
    """Singleton wrapper for all Ollama API calls."""

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=8))
    async def chat(self, model: str, system: str, message: str,
                   history: list = []) -> str:
        """Send a chat request to Ollama. Returns the response string."""
        trimmed = self._trim_history(history, system, message)
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system},
                *trimmed,
                {'role': 'user', 'content': message},
            ],
            'stream': False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f'{settings.OLLAMA_BASE_URL}/api/chat', json=payload
            )
            r.raise_for_status()
            return r.json()['message']['content']

    async def stream(self, model: str, system: str, message: str,
                     history: list = []) -> AsyncGenerator[str, None]:
        """Streaming version. Yields token strings for WebSocket delivery."""
        trimmed = self._trim_history(history, system, message)
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system},
                *trimmed,
                {'role': 'user', 'content': message},
            ],
            'stream': True,
        }
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream('POST',
                                     f'{settings.OLLAMA_BASE_URL}/api/chat',
                                     json=payload) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if not data.get('done'):
                            yield data['message']['content']

    def _trim_history(self, history: list, system: str,
                      message: str) -> list:
        """
        Trim history to fit within CTX_LIMIT.
        Always keeps the MOST RECENT turns (not oldest).
        """
        budget = (CTX_LIMIT * CHARS_PER_TOKEN
                  - len(system) - len(message) - 200)  # 200 char safety margin
        result = []
        used = 0
        for turn in reversed(history):
            turn_chars = len(turn.get('content', ''))
            if used + turn_chars > budget:
                break
            result.insert(0, turn)
            used += turn_chars
        return result

    async def check_health(self) -> bool:
        """Returns True if Ollama is reachable. Used by StatusBar."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f'{settings.OLLAMA_BASE_URL}/api/tags')
                return r.status_code == 200
        except Exception:
            return False


ollama_service = OllamaService()  # module-level singleton
