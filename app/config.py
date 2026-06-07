from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str
    primary_model: str
    fallback_model: str
    request_timeout_seconds: float
    retry_attempts: int
    max_input_chars: int
    default_max_tokens: int
    max_allowed_tokens: int
    default_temperature: float
    max_concurrent_requests: int


def _validate_local_base_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("OLLAMA_BASE_URL must start with http:// or https://")
    host = parsed.hostname
    if host not in {"localhost", "127.0.0.1"}:
        raise ValueError("OLLAMA_BASE_URL must be localhost or 127.0.0.1 for local-only safety")
    return url.rstrip("/")


def load_settings() -> Settings:
    base_url = _validate_local_base_url(os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))

    return Settings(
        ollama_base_url=base_url,
        primary_model=os.getenv("PRIMARY_MODEL", "qwen2.5:7b-instruct"),
        fallback_model=os.getenv("FALLBACK_MODEL", "qwen2.5:3b-instruct"),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "45")),
        retry_attempts=max(0, int(os.getenv("RETRY_ATTEMPTS", "1"))),
        max_input_chars=max(1, int(os.getenv("MAX_INPUT_CHARS", "12000"))),
        default_max_tokens=max(1, int(os.getenv("DEFAULT_MAX_TOKENS", "512"))),
        max_allowed_tokens=max(1, int(os.getenv("MAX_ALLOWED_TOKENS", "2048"))),
        default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.2")),
        max_concurrent_requests=max(1, int(os.getenv("MAX_CONCURRENT_REQUESTS", "4"))),
    )
