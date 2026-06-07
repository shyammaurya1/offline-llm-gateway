from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.config import Settings
from app.ollama_client import OllamaClient, OllamaClientError, OllamaGenerateResult


class OverloadedError(Exception):
    pass


class GenerationError(Exception):
    pass


@dataclass
class GenerationResult:
    output_text: str
    model_used: str
    fallback_used: bool
    prompt_tokens: int | None
    completion_tokens: int | None


class Txt2TxtService:
    def __init__(self, settings: Settings, client: OllamaClient) -> None:
        self._settings = settings
        self._client = client
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_requests)

    async def generate(
        self,
        *,
        input_text: str,
        model: str | None,
        max_tokens: int | None,
        temperature: float | None,
        system_prompt: str | None,
    ) -> GenerationResult:
        if len(input_text) > self._settings.max_input_chars:
            raise ValueError(
                f"input_text exceeds MAX_INPUT_CHARS ({self._settings.max_input_chars})"
            )

        selected_model = model or self._settings.primary_model
        capped_tokens = min(max_tokens or self._settings.default_max_tokens, self._settings.max_allowed_tokens)
        effective_temperature = (
            self._settings.default_temperature if temperature is None else temperature
        )

        try:
            await asyncio.wait_for(self._semaphore.acquire(), timeout=0.001)
        except TimeoutError as exc:
            raise OverloadedError("server is busy; try again shortly") from exc

        try:
            primary = await self._attempt_generate(
                model=selected_model,
                input_text=input_text,
                max_tokens=capped_tokens,
                temperature=effective_temperature,
                system_prompt=system_prompt,
            )
            return GenerationResult(
                output_text=primary.text,
                model_used=primary.model,
                fallback_used=False,
                prompt_tokens=primary.prompt_tokens,
                completion_tokens=primary.completion_tokens,
            )
        except OllamaClientError:
            if selected_model != self._settings.primary_model:
                raise

            fallback = await self._attempt_generate(
                model=self._settings.fallback_model,
                input_text=input_text,
                max_tokens=capped_tokens,
                temperature=effective_temperature,
                system_prompt=system_prompt,
            )
            return GenerationResult(
                output_text=fallback.text,
                model_used=fallback.model,
                fallback_used=True,
                prompt_tokens=fallback.prompt_tokens,
                completion_tokens=fallback.completion_tokens,
            )
        except Exception as exc:  # noqa: BLE001
            raise GenerationError(str(exc)) from exc
        finally:
            self._semaphore.release()

    async def list_models(self) -> list[dict[str, object]]:
        return await self._client.list_models()

    async def health(self) -> bool:
        try:
            await self._client.list_models()
            return True
        except OllamaClientError:
            return False

    async def _attempt_generate(
        self,
        *,
        model: str,
        input_text: str,
        max_tokens: int,
        temperature: float,
        system_prompt: str | None,
    ) -> OllamaGenerateResult:
        attempts = self._settings.retry_attempts + 1
        last_err: OllamaClientError | None = None

        for _ in range(attempts):
            try:
                return await self._client.generate(
                    model=model,
                    input_text=input_text,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt,
                )
            except OllamaClientError as exc:
                last_err = exc

        if last_err is not None:
            # Preserve Ollama error type so caller can apply fallback logic.
            raise last_err

        raise GenerationError("unknown generation error")
