from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.ollama_service import OllamaService


@pytest.mark.asyncio
async def test_chat_returns_string_from_mock_response() -> None:
    svc = OllamaService()
    resp = Mock()
    resp.json.return_value = {"message": {"content": "hello"}}
    resp.raise_for_status.return_value = None

    client = AsyncMock()
    client.post.return_value = resp
    cm = AsyncMock()
    cm.__aenter__.return_value = client
    cm.__aexit__.return_value = None

    with patch("services.ollama_service.httpx.AsyncClient", return_value=cm):
        out = await svc.chat(model="llama", system="sys", message="msg")
    assert out == "hello"


def test_trim_history_keeps_recent_turns() -> None:
    svc = OllamaService()
    history = [{"role": "user", "content": "a" * 10000}, {"role": "assistant", "content": "recent"}]
    trimmed = svc._trim_history(history, "sys", "msg")
    assert trimmed[-1]["content"] == "recent"


@pytest.mark.asyncio
async def test_check_health_true_on_200() -> None:
    svc = OllamaService()
    resp = Mock()
    resp.status_code = 200

    client = AsyncMock()
    client.get.return_value = resp
    cm = AsyncMock()
    cm.__aenter__.return_value = client
    cm.__aexit__.return_value = None

    with patch("services.ollama_service.httpx.AsyncClient", return_value=cm):
        assert await svc.check_health() is True


@pytest.mark.asyncio
async def test_check_health_false_on_exception() -> None:
    svc = OllamaService()
    with patch("services.ollama_service.httpx.AsyncClient", side_effect=RuntimeError("boom")):
        assert await svc.check_health() is False
