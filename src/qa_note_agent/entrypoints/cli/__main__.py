from __future__ import annotations

from typing import TYPE_CHECKING

from qa_note_agent.config.dependencies.cli import create_cli_app
from qa_note_agent.config.dependencies.common import (
    create_settings,
    setup_app_logging,
)
from qa_note_agent.presentation.cli.error_handling import handle_errors

if TYPE_CHECKING:
    from typer import Typer


@handle_errors
def main() -> None:
    """Run CLI application."""
    app = _build_cli_app()
    app(standalone_mode=False)


def _build_cli_app() -> Typer:
    """Build configured CLI application."""
    settings = create_settings()
    setup_app_logging(settings=settings)

    return create_cli_app(settings=settings)


if __name__ == "__main__":
    main()
