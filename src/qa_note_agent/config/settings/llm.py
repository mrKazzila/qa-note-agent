__all__ = ("LlmSettings", "OllamaSettings")

from typing import Literal

from pydantic import BaseModel, Field


class OllamaSettings(BaseModel):
    """Ollama client settings."""

    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:7b"
    timeout_seconds: float = Field(default=120.0, gt=0)

    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    num_predict: int = Field(default=1_200, gt=0)

    def default_options(self) -> dict[str, object]:
        """Build default Ollama generation options."""
        return {
            "temperature": self.temperature,
            "num_predict": self.num_predict,
        }


class LlmSettings(BaseModel):
    """LLM provider settings."""

    provider: Literal["ollama"] = "ollama"
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
