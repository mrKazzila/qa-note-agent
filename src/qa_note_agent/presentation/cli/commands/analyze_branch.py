from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import typer

from qa_note_agent.presentation.cli.dependencies import CliContext


CLICommandFunc = Callable[..., Any]


def create_analyze_branch_command(context: CliContext) -> CLICommandFunc:
    """Create command for analyzing local Git branch changes."""

    def analyze_branch_command(
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

        typer.echo(f"Repository: {repo_path}")
        typer.echo(f"Base ref:   {changes.base_ref}")
        typer.echo(f"Head ref:   {changes.head_ref}")
        typer.echo(f"Merge base: {changes.merge_base}")
        typer.echo()

        typer.echo("Changed files:")
        if changes.name_status_raw.strip():
            typer.echo(changes.name_status_raw.rstrip())
        else:
            typer.echo("No changed files.")
        typer.echo()

        typer.echo("Stat:")
        if changes.stat_raw.strip():
            typer.echo(changes.stat_raw.rstrip())
        else:
            typer.echo("No diff stat.")
        typer.echo()

        typer.echo("Commits:")
        if changes.commits_raw.strip():
            typer.echo(changes.commits_raw.rstrip())
        else:
            typer.echo("No commits.")
        typer.echo()

        if show_patch:
            typer.echo("Patch:")
            if changes.patch.strip():
                typer.echo(changes.patch.rstrip())
            else:
                typer.echo("No patch.")

    return analyze_branch_command
