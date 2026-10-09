from __future__ import annotations

__all__ = (
    "HasLoggingSettings",
    "LoggingConfig",
    "LogLevel",
    "LogRenderer",
)

import logging
from dataclasses import dataclass
from typing import Literal, Protocol, Self, final

LogLevel = Literal[
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]
LogRenderer = Literal["console", "json"]


class HasLoggingSettings(Protocol):
    """Object containing settings required for logging."""

    @property
    def log_level(self) -> LogLevel: ...

    @property
    def log_renderer(self) -> LogRenderer: ...

    @property
    def enable_log_diagnostics(self) -> bool: ...

    @property
    def use_utc_timestamps(self) -> bool: ...


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class LoggingConfig:
    level: LogLevel = "INFO"
    renderer: LogRenderer = "console"
    enable_diagnostics: bool = False
    use_utc_timestamps: bool = False

    @classmethod
    def from_settings(cls, settings: HasLoggingSettings) -> Self:
        return cls(
            level=settings.log_level,
            renderer=settings.log_renderer,
            enable_diagnostics=settings.enable_log_diagnostics,
            use_utc_timestamps=settings.use_utc_timestamps,
        )

    def resolved_level(self) -> int:
        return self._get_log_level(self.level)

    @staticmethod
    def _get_log_level(level: str) -> int:
        normalized = logging.getLevelName(level.upper())
        return normalized if isinstance(normalized, int) else logging.INFO
