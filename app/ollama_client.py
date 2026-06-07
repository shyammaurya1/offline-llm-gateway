from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import httpx


class OllamaClientError(Exception):
    pass


@dataclass
class OllamaGenerateResult:
    text: str
    model: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]


class OllamaClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    async def generate(
        self,
        *,
        model: str,
        input_text: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str],
    ) -> OllamaGenerateResult:
        payload: dict[str, Any] = {
            "model": model,
            "messages": self._build_messages(input_text=input_text, system_prompt=system_prompt),
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds, trust_env=False) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaClientError(f"Ollama request failed: {exc}") from exc

        data = response.json()
        message = data.get("message", {})
        text = message.get("content", "")
        if not isinstance(text, str):
            text = str(text)

        return OllamaGenerateResult(
            text=text,
            model=data.get("model", model),
            prompt_tokens=_as_int(data.get("prompt_eval_count")),
            completion_tokens=_as_int(data.get("eval_count")),
        )

    async def list_models(self) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds, trust_env=False) as client:
                response = await client.get(f"{self._base_url}/api/tags")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaClientError(f"Could not fetch model list: {exc}") from exc

        data = response.json()
        raw = data.get("models", [])
        if isinstance(raw, list):
            return raw
        return []

    @staticmethod
    def _build_messages(input_text: str, system_prompt: Optional[str]) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": input_text})
        return messages


def _as_int(value: Any) -> Optional[int]:
    if isinstance(value, int):
        return value
    return None
