__all__ = (
    "CLIOptionSpec",
    "CommonOptionSpecs",
)

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Generic, TypeVar

import typer

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class CLIOptionSpec(Generic[T]):
    annotation: Any
    default: T


class CommonOptionSpecs:
    repo_path = CLIOptionSpec[Path](
        annotation=Annotated[
            Path,
            typer.Option(
                "--repo",
                "-r",
                exists=True,
                file_okay=False,
                dir_okay=True,
                readable=True,
                resolve_path=True,
                help="Path to local Git repository.",
            ),
        ],
        default=Path(),
    )

    base_ref = CLIOptionSpec[str](
        annotation=Annotated[
            str,
            typer.Option(
                "--base",
                "-b",
                help="Base Git ref to compare against.",
            ),
        ],
        default="origin/main",
    )

    head_ref = CLIOptionSpec[str](
        annotation=Annotated[
            str,
            typer.Option(
                "--head",
                help="Head Git ref to analyze.",
            ),
        ],
        default="HEAD",
    )
