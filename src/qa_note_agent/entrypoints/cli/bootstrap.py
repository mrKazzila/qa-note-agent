from __future__ import annotations

from typing import TYPE_CHECKING

from qa_note_agent.config.settings.base import Settings
from qa_note_agent.entrypoints.cli.dependencies import create_cli_context
from qa_note_agent.infrastructure.observability.logger_setup import (
    setup_logging,
)
from qa_note_agent.presentation.cli.app import create_app

if TYPE_CHECKING:
    from typer import Typer


def create_application(*, settings: Settings) -> Typer:
    """Build configured CLI application."""
    setup_logging(config=settings.app.logging.to_config())

    context = create_cli_context(settings=settings)

    return create_app(context=context)
