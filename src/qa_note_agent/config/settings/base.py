__all__ = ("Settings",)

from typing import final, Literal

from pydantic import Field

from qa_note_agent.config.settings._base_settings import BaseAppSettings
from qa_note_agent.config.settings.app import AppSettings


@final
class Settings(BaseAppSettings):
    app: AppSettings = Field(default_factory=AppSettings)

    @property
    def name(self) -> str:
        return self.app.name

    @property
    def version(self) -> str:
        return self.app.version

    @property
    def log_level(self) -> str:
        return self.app.log_level

    @property
    def log_renderer(self) -> Literal["console", "json"]:
        return self.app.log_renderer

    @property
    def use_utc_timestamps(self) -> bool:
        return self.app.use_utc_timestamps

    @property
    def debug(self) -> bool:
        return self.app.debug
