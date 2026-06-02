from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import click
import typer

from qa_note_agent.application.errors import QaNoteAgentError
from qa_note_agent.config.dependencies.common import create_settings

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def handle_errors(func: Callable[P, R]) -> Callable[P, R]:
    """Handle top-level CLI errors."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)

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
            if _is_debug_enabled():
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
            if _is_debug_enabled():
                raise

            typer.secho("Unexpected error.", err=True, fg=typer.colors.RED, bold=True)
            typer.echo(
                "Run with `QA_NOTE_AGENT_APP__DEBUG=true` to see the full traceback.",
                err=True,
            )

            raise SystemExit(1) from error

    return wrapper


def _render_expected_error(error: QaNoteAgentError) -> None:
    typer.secho("Error:", err=True, fg=typer.colors.RED, bold=True)
    typer.echo(f"  {error.message}", err=True)

    if error.hint:
        typer.secho("Hint:", err=True, fg=typer.colors.BLUE, bold=True)
        typer.echo(f"  {error.hint}", err=True)


def _is_debug_enabled() -> bool:
    try:
        settings = create_settings()
    except Exception:
        return False

    return settings.app.debug
