from __future__ import annotations

import typer

from qa_note_agent.presentation.cli.commands.registry import CLI_COMMANDS
from qa_note_agent.presentation.cli.dependencies import CliContext


def register_commands(
    app: typer.Typer,
    context: CliContext,
) -> None:
    """Register CLI commands."""
    for command in CLI_COMMANDS:
        command_func = command.command_factory(context)

        app.command(
            name=command.name,
            help=command.help,
            rich_help_panel=command.group.value,
        )(command_func)
