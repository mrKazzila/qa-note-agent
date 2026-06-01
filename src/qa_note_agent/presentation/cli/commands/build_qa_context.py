from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer

from qa_note_agent.presentation.cli.dependencies import CliContext

CLICommandFunc = Callable[..., Any]


def create_build_qa_context_command(context: CliContext) -> CLICommandFunc:
    """Create command for building QA note LLM context."""

    def build_qa_context_command(
        repo_path: Path = typer.Option(
            Path(),
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
        max_patch_chars: int = typer.Option(
            20_000,
            "--max-patch-chars",
            min=0,
            help="Maximum number of patch characters included in context.",
        ),
    ) -> None:
        """Build LLM-ready context from local Git branch changes."""
        changes = context.analyze_branch_changes_use_case.execute(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
        )

        qa_context = context.build_qa_note_context_use_case.execute(
            changes=changes,
            max_patch_chars=max_patch_chars,
        )

        typer.echo(qa_context.content)

        if qa_context.is_truncated:
            typer.echo()
            typer.echo("> Context was truncated.")

    return build_qa_context_command
