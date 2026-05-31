from dataclasses import dataclass

import typer

from qa_note_agent.config.dependencies.cli import create_cli_app
from qa_note_agent.config.settings.base import Settings


@dataclass(frozen=True, slots=True)
class CliDependencies:
    app: typer.Typer


def create_cli_dependencies(settings: Settings) -> CliDependencies:
    """Create dependencies for CLI runtime."""
    return CliDependencies(
        app=create_cli_app(settings=settings),
    )
