from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer

from qa_note_agent.presentation.cli.dependencies import CliContext
from qa_note_agent.presentation.renderers.git_branch_changes import (
    render_git_branch_changes,
)

CLICommandFunc = Callable[..., Any]


def create_analyze_branch_command(context: CliContext) -> CLICommandFunc:
    """Create command for analyzing local Git branch changes."""

    def analyze_branch_command(
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
        show_patch: bool = typer.Option(
            False,
            "--patch",
            help="Print full unified diff patch.",
        ),
    ) -> None:
        """Analyze changes in a local Git branch."""
        changes = context.analyze_branch_changes_use_case.execute(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
        )

        output = render_git_branch_changes(
            changes=changes,
            repo_path=repo_path,
            show_patch=show_patch,
        )

        typer.echo(output)

    return analyze_branch_command
