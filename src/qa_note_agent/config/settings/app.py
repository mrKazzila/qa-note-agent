__all__ = ("AppSettings",)

from typing import Literal
from pydantic import Field

from qa_note_agent.config.settings._base_settings import BaseAppSettings


class AppSettings(BaseAppSettings):

    name: str = Field("qa_note_agent", validation_alias="APP_NAME")
    version: str = Field("0.0.1", validation_alias="APP_VERSION")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = Field(False, validation_alias="DEBUG")
    log_renderer: Literal["console", "json"] = "console"
    use_utc_timestamps: bool = True
