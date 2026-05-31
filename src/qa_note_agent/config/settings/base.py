__all__ = ("Settings",)

from typing import final

from pydantic import Field

from qa_note_agent.config.settings._base_settings import BaseAppSettings
from qa_note_agent.config.settings.app import AppSettings


@final
class Settings(BaseAppSettings):
    app: AppSettings = Field(default_factory=AppSettings)

    @property
    def log_level(self) -> str:
        return self.app.log_level

    @property
    def debug(self) -> bool:
        return self.app.debug
