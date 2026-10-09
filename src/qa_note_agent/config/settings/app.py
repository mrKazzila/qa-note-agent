__all__ = ("AppSettings",)

from pydantic import BaseModel, Field

from qa_note_agent.config.settings.logger import LoggingSettings


class AppSettings(BaseModel):
    """Application settings."""

    name: str = "qa_note_agent"
    version: str = "0.0.1"

    logging: LoggingSettings = Field(
        default_factory=lambda: LoggingSettings(renderer="console"),
    )
