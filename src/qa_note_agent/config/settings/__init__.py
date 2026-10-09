from functools import lru_cache

from qa_note_agent.config.settings.base import Settings


@lru_cache(maxsize=1)
def create_settings() -> Settings:
    """Load and cache application settings."""
    return Settings()
