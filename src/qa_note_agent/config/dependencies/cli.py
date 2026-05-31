import typer

from qa_note_agent.config.settings.base import Settings
from qa_note_agent.presentation.cli.app import create_app
from qa_note_agent.presentation.cli.dependencies import CliContext


def create_cli_context(settings: Settings) -> CliContext:
    """Create CLI context."""
    return CliContext(settings=settings)


def create_cli_app(settings: Settings) -> typer.Typer:
    """Create CLI application."""
    context = create_cli_context(settings=settings)
    return create_app(context=context)
