from typing import Literal

import typer

from qa_note_agent.presentation.cli.commands.register import register_commands
from qa_note_agent.presentation.cli.dependencies import CliContext


def create_app(context: CliContext) -> typer.Typer:
    """Create CLI application."""
    app = _create_typer_app(context=context)
    _setup_app(app=app, context=context)

    return app


def _create_typer_app(context: CliContext) -> typer.Typer:
    """Create base Typer application."""
    rich_markup_mode: Literal["markdown", "rich"] = "rich"

    return typer.Typer(
        name=context.settings.name,
        help=f"{context.settings.name} {context.settings.version}",
        rich_markup_mode=rich_markup_mode,
        add_completion=True,
        no_args_is_help=True,
    )


def _setup_app(app: typer.Typer, context: CliContext) -> None:
    """Setup CLI application."""
    register_commands(app=app, context=context)
