__all__ = ("BaseAppSettings",)


from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_project_root(start: Path) -> Path:
    start = start.resolve()
    current = start.parent if start.is_file() else start

    for path in (current, *current.parents):
        if (path / "pyproject.toml").exists():
            return path

    raise RuntimeError("Project root not found")


_ENV_FILE_PATH = _find_project_root(start=Path(__file__)) / "env/.env"


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE_PATH,
        extra="allow",
    )
