from __future__ import annotations


class LlmClientError(RuntimeError):
    """Base LLM client error."""


class OllamaClientError(LlmClientError):
    """Raised when Ollama request fails."""
