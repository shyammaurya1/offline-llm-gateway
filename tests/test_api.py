from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


class FakeService:
    async def health(self) -> bool:
        return True

    async def list_models(self) -> list[dict[str, object]]:
        return [
            {"name": "qwen2.5:7b-instruct", "size": 4100000000},
            {"name": "qwen2.5:3b-instruct", "size": 2100000000},
        ]

    async def generate(self, **kwargs):
        class Result:
            output_text = "ok"
            model_used = "qwen2.5:7b-instruct"
            fallback_used = False
            prompt_tokens = 10
            completion_tokens = 20

        return Result()


def test_health_endpoint() -> None:
    app = create_app()
    app.state.service = FakeService()
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ollama_reachable"] is True


def test_models_endpoint() -> None:
    app = create_app()
    app.state.service = FakeService()
    client = TestClient(app)

    response = client.get("/models")
    assert response.status_code == 200
    body = response.json()
    assert len(body["models"]) == 2
    assert body["models"][0]["name"] == "qwen2.5:7b-instruct"


def test_txt2txt_endpoint() -> None:
    app = create_app()
    app.state.service = FakeService()
    client = TestClient(app)

    payload = {
        "input_text": "Summarize local offline inference in 3 points",
        "max_tokens": 100,
        "temperature": 0.2,
    }

    response = client.post("/v1/txt2txt", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["output_text"] == "ok"
    assert body["model_used"] == "qwen2.5:7b-instruct"
