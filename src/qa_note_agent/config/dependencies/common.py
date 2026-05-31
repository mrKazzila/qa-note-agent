from functools import lru_cache

from qa_note_agent.config.settings.base import Settings
from qa_note_agent.config.settings.logger import setup_logging, LoggingConfig



@lru_cache(maxsize=1)
def create_settings() -> Settings:
    """Create application settings."""
    return Settings()


def create_logging_config(settings: Settings) -> LoggingConfig:
    """Create logging config from application settings."""
    return LoggingConfig(
        level=settings.log_level,
        renderer=settings.log_renderer,
        enable_diagnostics=settings.debug,
        use_utc_timestamps=settings.use_utc_timestamps,
    )


def setup_app_logging(settings: Settings) -> None:
    """Setup application logging."""
    setup_logging(config=create_logging_config(settings=settings))
