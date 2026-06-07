from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, HTTPException

from app.config import Settings, load_settings
from app.ollama_client import OllamaClient
from app.schemas import (
    HealthResponse,
    ModelInfo,
    ModelsResponse,
    TokenUsage,
    Txt2TxtRequest,
    Txt2TxtResponse,
)
from app.service import GenerationError, OverloadedError, Txt2TxtService


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or load_settings()

    app = FastAPI(title="Local Offline Txt2Txt API", version="1.0.0")
    client = OllamaClient(
        base_url=app_settings.ollama_base_url,
        timeout_seconds=app_settings.request_timeout_seconds,
    )
    service = Txt2TxtService(settings=app_settings, client=client)
    app.state.settings = app_settings
    app.state.service = service

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        healthy = await app.state.service.health()
        return HealthResponse(
            status="ok" if healthy else "degraded",
            ollama_reachable=healthy,
            configured_primary_model=app.state.settings.primary_model,
            configured_fallback_model=app.state.settings.fallback_model,
        )

    @app.get("/models", response_model=ModelsResponse)
    async def models() -> ModelsResponse:
        try:
            raw_models = await app.state.service.list_models()
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=503, detail=f"model listing failed: {exc}") from exc

        output = [
            ModelInfo(name=str(item.get("name", "unknown")), size=item.get("size"))
            for item in raw_models
        ]
        return ModelsResponse(models=output)

    @app.post("/v1/txt2txt", response_model=Txt2TxtResponse)
    async def txt2txt(payload: Txt2TxtRequest) -> Txt2TxtResponse:
        request_id = str(uuid.uuid4())
        started = time.perf_counter()

        try:
            result = await app.state.service.generate(
                input_text=payload.input_text,
                model=payload.model,
                max_tokens=payload.max_tokens,
                temperature=payload.temperature,
                system_prompt=payload.system_prompt,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except OverloadedError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        except GenerationError as exc:
            raise HTTPException(status_code=503, detail=f"generation failed: {exc}") from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        usage = TokenUsage(
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=(
                (result.prompt_tokens or 0) + (result.completion_tokens or 0)
                if (result.prompt_tokens is not None or result.completion_tokens is not None)
                else None
            ),
        )

        return Txt2TxtResponse(
            request_id=request_id,
            status="ok",
            output_text=result.output_text,
            model_used=result.model_used,
            fallback_used=result.fallback_used,
            latency_ms=latency_ms,
            token_usage=usage,
        )

    return app


app = create_app()
