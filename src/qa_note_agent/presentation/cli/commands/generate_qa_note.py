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
    ) -> None:
        """Generate QA note from local Git branch changes."""
        qa_note = context.generate_qa_note_use_case.execute(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
            max_chunk_chars=max_chunk_chars,
        )

        typer.echo(qa_note.content)

        typer.echo()
        typer.echo("---")
        typer.echo(f"Chunks analyzed: {qa_note.chunks_count}")

        if qa_note.was_context_truncated:
            typer.echo("Context was truncated.")

    return generate_qa_note_command
