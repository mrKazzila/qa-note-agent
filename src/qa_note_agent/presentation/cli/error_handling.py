from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import click
import typer

from qa_note_agent.application.errors import QaNoteAgentError

logger = logging.getLogger(__name__)


@contextmanager
def handle_errors(*, debug: bool) -> Iterator[None]:
    """Render CLI command errors unless debug mode requires a traceback."""
    try:
        yield

    except click.ClickException as error:
        error.show()
        raise SystemExit(error.exit_code) from error

    except click.Abort as error:
        typer.secho("Aborted.", err=True, fg=typer.colors.YELLOW)
        raise SystemExit(130) from error

    except KeyboardInterrupt as error:
        typer.secho("Interrupted.", err=True, fg=typer.colors.YELLOW)
        raise SystemExit(130) from error

    except QaNoteAgentError as error:
        if debug:
            raise

        _render_expected_error(error)

        logger.debug(
            "cli_expected_error",
            extra={
                "error_type": type(error).__name__,
                "error_message": error.message,
            },
        )

        raise SystemExit(error.exit_code) from error

    except Exception as error:
        if debug:
            raise

        typer.secho(
            "Unexpected error.",
            err=True,
            fg=typer.colors.RED,
            bold=True,
        )
        typer.echo(
            "Run with `QA_NOTE_AGENT_APP__DEBUG=true` "
            "to see the full traceback.",
            err=True,
        )

        raise SystemExit(1) from error


def _render_expected_error(error: QaNoteAgentError) -> None:
    typer.secho("Error:", err=True, fg=typer.colors.RED, bold=True)
    typer.echo(f"  {error.message}", err=True)

    if error.hint:
        typer.secho("Hint:", err=True, fg=typer.colors.BLUE, bold=True)
        typer.echo(f"  {error.hint}", err=True)
