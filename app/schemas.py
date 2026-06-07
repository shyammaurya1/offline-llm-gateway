from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Txt2TxtRequest(BaseModel):
    input_text: str = Field(..., min_length=1, description="Input prompt text")
    model: Optional[str] = Field(default=None, description="Optional model override")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Max generated tokens")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    system_prompt: Optional[str] = Field(default=None, description="Optional system instruction")


class TokenUsage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class Txt2TxtResponse(BaseModel):
    request_id: str
    status: str
    output_text: str
    model_used: str
    fallback_used: bool
    latency_ms: int
    token_usage: TokenUsage


class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    configured_primary_model: str
    configured_fallback_model: str


class ModelInfo(BaseModel):
    name: str
    size: Optional[int] = None


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
