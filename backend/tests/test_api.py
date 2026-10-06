from app.api import entries as entries_api


def test_rejects_blank_text(client) -> None:
    response = client.post("/entries", json={"text": "   "})
    assert response.status_code == 422


def test_creates_and_fetches_entry_with_mocked_ai(client, monkeypatch) -> None:
    async def fake_generate_content(text: str) -> dict:
        return {"summary": "A short summary", "tags": ["one", "two", "three"]}

    monkeypatch.setattr(entries_api, "generate_content", fake_generate_content)
    response = client.post("/entries", json={"text": "Some useful content"})
    assert response.status_code == 201
    body = response.json()
    assert body["tags"] == ["one", "two", "three"]

    assert client.get(f"/entries/{body['id']}").json()["summary"] == "A short summary"
    assert len(client.get("/entries").json()) == 1


def test_get_missing_entry_returns_404(client) -> None:
    response = client.get("/entries/999")
    assert response.status_code == 404
    assert response.json()["message"] == "Entry 999 not found."


def test_created_at_is_returned_as_utc(client, monkeypatch) -> None:
    async def fake_generate_content(text: str) -> dict:
        return {"summary": "s", "tags": ["a", "b", "c"]}

    monkeypatch.setattr(entries_api, "generate_content", fake_generate_content)
    client.post("/entries", json={"text": "hello"})
    created_at = client.get("/entries").json()[0]["created_at"]
    assert created_at.endswith("Z") or created_at.endswith("+00:00")
