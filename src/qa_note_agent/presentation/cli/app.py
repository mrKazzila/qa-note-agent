from typing import Literal

import typer

from qa_note_agent.presentation.cli.commands.register import register_commands

APP_NAME = "qa-note"
APP_VERSION = "0.0.1"


def create_app() -> typer.Typer:
    """Create CLI application."""
    rich_markup_mode: Literal["markdown", "rich"] = "rich"

    app = typer.Typer(
        name=APP_NAME,
        help=f"{APP_NAME} {APP_VERSION}",
        rich_markup_mode=rich_markup_mode,
        add_completion=True,
        no_args_is_help=True,
    )

    register_commands(app)

    return app
