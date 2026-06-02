from __future__ import annotations

from qa_note_agent.application.errors import QaNoteAgentError


class LlmClientError(QaNoteAgentError):
    """Base LLM client error."""


class OllamaClientError(LlmClientError):
    """Raised when Ollama request fails."""


class LlmModelNotFoundError(LlmClientError):
    """Raised when configured Ollama model is not available."""

    def __init__(self, model: str) -> None:
        super().__init__(
            f"LLM model `{model}` was not found in Ollama.",
            hint=f"Run `ollama pull {model}` or change the configured model name.",
        )