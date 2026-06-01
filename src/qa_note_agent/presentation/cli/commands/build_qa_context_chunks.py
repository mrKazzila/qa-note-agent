from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer

from qa_note_agent.presentation.cli.dependencies import CliContext


CLICommandFunc = Callable[..., Any]


def create_build_qa_context_chunks_command(context: CliContext) -> CLICommandFunc:
    """Create command for building chunked QA note LLM context."""

    def build_qa_context_chunks_command(
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
        chunk_index: int | None = typer.Option(
            None,
            "--chunk",
            min=1,
            help="Print only one chunk by 1-based index.",
        ),
        list_only: bool = typer.Option(
            False,
            "--list",
            help="Print chunk list without full content.",
        ),
    ) -> None:
        """Build chunked LLM-ready context from local Git branch changes."""
        changes = context.analyze_branch_changes_use_case.execute(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
        )

        chunk_set = context.build_qa_note_context_chunks_use_case.execute(
            changes=changes,
            max_chunk_chars=max_chunk_chars,
        )

        if list_only:
            typer.echo(f"Chunks: {len(chunk_set.chunks)}")
            typer.echo(f"Truncated: {chunk_set.is_truncated}")
            typer.echo()

            for chunk in chunk_set.chunks:
                files = ", ".join(chunk.files) if chunk.files else "no files"
                typer.echo(
                    f"{chunk.index}/{chunk.total}: {chunk.title} "
                    f"({len(chunk.content)} chars, files: {files})"
                )

            return

        if chunk_index is not None:
            selected_chunk = next(
                (
                    chunk
                    for chunk in chunk_set.chunks
                    if chunk.index == chunk_index
                ),
                None,
            )

            if selected_chunk is None:
                msg = (
                    f"Chunk {chunk_index} does not exist. "
                    f"Available chunks: 1..{len(chunk_set.chunks)}"
                )
                raise typer.BadParameter(msg)

            typer.echo(selected_chunk.content)
            return

        for chunk in chunk_set.chunks:
            typer.echo(chunk.content)

            if chunk.index != chunk.total:
                typer.echo()
                typer.echo("---")
                typer.echo()

        if chunk_set.is_truncated:
            typer.echo()
            typer.echo("> Context was truncated.")

    return build_qa_context_chunks_command
