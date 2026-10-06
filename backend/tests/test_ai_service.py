import pytest

from app.api import entries as entries_api
from app.core.exceptions import AIServiceError
from app.services.ai_service import _parse_result


def test_parse_result_accepts_valid_output() -> None:
    result = _parse_result('{"summary": " Short. ", "tags": ["a", "b", " c "]}')
    assert result == {"summary": "Short.", "tags": ["a", "b", "c"]}


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        '{"summary": "x"}',
        '{"summary": "", "tags": ["a", "b", "c"]}',
        '{"summary": "x", "tags": ["a", "b"]}',
        '{"summary": "x", "tags": ["a", "b", "c", "d"]}',
        '{"summary": "x", "tags": ["a", "b", 3]}',
        "[1, 2, 3]",
    ],
)
def test_parse_result_rejects_malformed_output(raw: str) -> None:
    with pytest.raises(AIServiceError):
        _parse_result(raw)


def test_ai_failure_returns_502_and_stores_nothing(client, monkeypatch) -> None:
    async def failing_generate_content(text: str) -> dict:
        raise AIServiceError("The AI returned invalid JSON")

    monkeypatch.setattr(entries_api, "generate_content", failing_generate_content)
    response = client.post("/entries", json={"text": "Some content"})
    assert response.status_code == 502
    assert response.json()["message"] == "The AI returned invalid JSON"
    assert client.get("/entries").json() == []


def test_generate_content_retries_once_then_succeeds(monkeypatch) -> None:
    import asyncio
    from types import SimpleNamespace

    from app.services import ai_service

    calls = {"n": 0}

    class FakeCompletions:
        async def create(self, **kwargs):
            calls["n"] += 1
            content = "not json" if calls["n"] == 1 else '{"summary": "ok", "tags": ["a", "b", "c"]}'
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

        async def close(self):
            pass

    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setattr(ai_service, "AsyncOpenAI", FakeClient)
    result = asyncio.run(ai_service.generate_content("hello"))
    assert result["summary"] == "ok"
    assert calls["n"] == 2
