from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer

from qa_note_agent.presentation.cli.dependencies import CliContext


CLICommandFunc = Callable[..., Any]


def create_generate_qa_note_command(context: CliContext) -> CLICommandFunc:
    """Create command for generating QA note."""

    def generate_qa_note_command(
        repo_path: Path = typer.Option(
            Path("."),
            "--repo",
            "-r",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="Path to local Git repository.",
        ),
        base_ref: str = typer.Option(
            "origin/main",
            "--base",
            "-b",
            help="Base Git ref to compare against.",
        ),
        head_ref: str = typer.Option(
            "HEAD",
            "--head",
            help="Head Git ref to analyze.",
        ),
        max_chunk_chars: int = typer.Option(
            12_000,
            "--max-chunk-chars",
            min=2_000,
            help="Maximum number of characters per context chunk.",
        ),
        map_temperature: float = typer.Option(
            0.1,
            "--map-temperature",
            min=0.0,
            max=2.0,
            help="Temperature for per-chunk analysis generation.",
        ),
        reduce_temperature: float = typer.Option(
            0.2,
            "--reduce-temperature",
            min=0.0,
            max=2.0,
            help="Temperature for final QA note generation.",
        ),
        map_num_predict: int = typer.Option(
            800,
            "--map-num-predict",
            min=128,
            help="Maximum generated tokens for each chunk analysis.",
        ),
        reduce_num_predict: int = typer.Option(
            1_400,
            "--reduce-num-predict",
            min=256,
            help="Maximum generated tokens for the final QA note.",
        ),
        output_path: Path | None = typer.Option(
            None,
            "--output",
            "-o",
            dir_okay=False,
            writable=True,
            resolve_path=True,
            help="Write generated QA note to file instead of stdout.",
        ),
    ) -> None:
        """Generate QA note from local Git branch changes."""
        qa_note = context.generate_qa_note_use_case.execute(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
            max_chunk_chars=max_chunk_chars,
            map_temperature=map_temperature,
            reduce_temperature=reduce_temperature,
            map_num_predict=map_num_predict,
            reduce_num_predict=reduce_num_predict,
        )

        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(qa_note.content + "\n", encoding="utf-8")

            typer.echo(f"QA note written to: {output_path}")
            typer.echo(f"Chunks analyzed: {qa_note.chunks_count}")

            if qa_note.was_context_truncated:
                typer.echo("Context was truncated.")

            return

        typer.echo(qa_note.content)
        typer.echo()
        typer.echo("---")
        typer.echo(f"Chunks analyzed: {qa_note.chunks_count}")

        if qa_note.was_context_truncated:
            typer.echo("Context was truncated.")

    return generate_qa_note_command
