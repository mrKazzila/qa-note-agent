__all__ = ("AppSettings",)

from typing import Literal

from pydantic import BaseModel


class AppSettings(BaseModel):
    """Application settings."""

    name: str = "qa_note_agent"
    version: str = "0.0.1"

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = False
    log_renderer: Literal["console", "json"] = "console"
    use_utc_timestamps: bool = True
