from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

from qa_note_agent.presentation.cli.commands.common.options import (
    CLIOptionSpec,
    CommonOptionSpecs,
)


@dataclass
class BuildQAContextOptions(CommonOptionSpecs):
    max_chunk_chars = CLIOptionSpec[int](
        annotation=Annotated[
            int,
            typer.Option(
                "--max-chunk-chars",
                min=2_000,
                help="Maximum number of characters per context chunk.",
            ),
        ],
        default=12_000,
    )

    chunk_index = CLIOptionSpec[int | None](
        annotation=Annotated[
            int | None,
            typer.Option(
                "--chunk",
                min=1,
                help="Print only one chunk by 1-based index.",
            ),
        ],
        default=None,
    )

    list_only = CLIOptionSpec[bool](
        annotation=Annotated[
            bool,
            typer.Option(
                "--list",
                help="Print chunk list without full content.",
            ),
        ],
        default=False,
    )


@dataclass
class BuildQAContextChunkOptions(BuildQAContextOptions):
    pass


@dataclass
class GenerateQANoteOptions(BuildQAContextOptions):
    session_id = CLIOptionSpec[str | None](
        annotation=Annotated[
            str | None,
            typer.Option(
                "--session-id",
                help=(
                    "Optional Langfuse session ID. Defaults to a stable ID "
                    "derived from repo path and refs."
                ),
            ),
        ],
        default=None,
    )

    map_temperature = CLIOptionSpec[float](
        annotation=Annotated[
            float,
            typer.Option(
                "--map-temperature",
                min=0.0,
                max=2.0,
                help="Temperature for per-chunk analysis generation.",
            ),
        ],
        default=0.1,
    )

    reduce_temperature = CLIOptionSpec[float](
        annotation=Annotated[
            float,
            typer.Option(
                "--reduce-temperature",
                min=0.0,
                max=2.0,
                help="Temperature for final QA note generation.",
            ),
        ],
        default=0.2,
    )

    map_num_predict = CLIOptionSpec[int](
        annotation=Annotated[
            int,
            typer.Option(
                "--map-num-predict",
                min=128,
                help="Maximum generated tokens for each chunk analysis.",
            ),
        ],
        default=800,
    )

    reduce_num_predict = CLIOptionSpec[int](
        annotation=Annotated[
            int,
            typer.Option(
                "--reduce-num-predict",
                min=256,
                help="Maximum generated tokens for the final QA note.",
            ),
        ],
        default=1_400,
    )

    output_path = CLIOptionSpec[Path | None](
        annotation=Annotated[
            Path | None,
            typer.Option(
                "--output",
                "-o",
                dir_okay=False,
                writable=True,
                resolve_path=True,
                help="Write generated QA note to file instead of stdout.",
            ),
        ],
        default=None,
    )
