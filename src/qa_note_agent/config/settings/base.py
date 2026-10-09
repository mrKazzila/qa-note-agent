__all__ = ("Settings",)

from typing import Literal, final

from pydantic import Field

from qa_note_agent.config.settings._base_settings import BaseAppSettings
from qa_note_agent.config.settings.app import AppSettings
from qa_note_agent.config.settings.langfuse import LangfuseSettings
from qa_note_agent.config.settings.llm import LlmSettings


@final
class Settings(BaseAppSettings):
    environment: Literal["local", "test", "production"] = "production"

    app: AppSettings = Field(default_factory=AppSettings)
    langfuse: LangfuseSettings = Field(default_factory=LangfuseSettings)
    llm: LlmSettings = Field(default_factory=LlmSettings)

    @property
    def debug(self) -> bool:
        if self.environment in ("local", "test"):
            return True
        return False
