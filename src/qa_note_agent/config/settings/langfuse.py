__all__ = ("LangfuseSettings",)

from pydantic import BaseModel, Field


class LangfuseSettings(BaseModel):
    """Langfuse tracing settings."""

    enabled: bool = True
    public_key: str | None = None
    secret_key: str | None = None
    base_url: str = "https://cloud.langfuse.com"
    environment: str = "local"
    sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    debug: bool = False

    def is_configured(self) -> bool:
        """Return whether tracing can be initialized."""
        return bool(self.public_key and self.secret_key)
