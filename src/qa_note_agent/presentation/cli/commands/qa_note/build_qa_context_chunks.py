from __future__ import annotations

import typer

from qa_note_agent.presentation.cli.commands.common.types import CLICommandFunc
from qa_note_agent.presentation.cli.commands.qa_note.options import (
    BuildQAContextChunkOptions as Options,
)
from qa_note_agent.presentation.cli.dependencies import CliContext


def create_build_qa_context_chunks_command(
    context: CliContext,
) -> CLICommandFunc:
    """Create command for building chunked QA note LLM context."""

    def build_qa_context_chunks_command(
        repo_path: Options.repo_path.annotation = Options.repo_path.default,
        base_ref: Options.base_ref.annotation = Options.base_ref.default,
        head_ref: Options.head_ref.annotation = Options.head_ref.default,
        max_chunk_chars: Options.max_chunk_chars.annotation = Options.max_chunk_chars.default,
        chunk_index: Options.chunk_index.annotation = Options.chunk_index.default,
        list_only: Options.list_only.annotation = Options.list_only.default,
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
                    f"({len(chunk.content)} chars, files: {files})",
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
