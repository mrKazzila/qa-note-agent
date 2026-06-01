from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LlmGenerateRequest:
    """LLM text generation request."""

    prompt: str
    system_prompt: str | None = None


@dataclass(frozen=True, slots=True)
class LlmGenerateResponse:
    """LLM text generation response."""

    text: str
