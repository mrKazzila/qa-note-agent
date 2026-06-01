from __future__ import annotations

from typing import Protocol

from qa_note_agent.application.dtos.llm import (
    LlmGenerateRequest,
    LlmGenerateResponse,
)


class LlmClient(Protocol):
    """Port for LLM text generation."""

    def generate(self, request: LlmGenerateRequest) -> LlmGenerateResponse:
        """Generate text from prompt."""
