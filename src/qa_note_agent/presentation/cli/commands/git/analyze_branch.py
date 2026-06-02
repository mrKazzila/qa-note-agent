from __future__ import annotations

import typer

from qa_note_agent.presentation.cli.commands.common.types import CLICommandFunc
from qa_note_agent.presentation.cli.commands.git.options import (
    AnalyzeBranchOptions as Options,
)
from qa_note_agent.presentation.cli.dependencies import CliContext
from qa_note_agent.presentation.renderers.git_branch_changes import (
    render_git_branch_changes,
)


def create_analyze_branch_command(context: CliContext) -> CLICommandFunc:
    """Create command for analyzing local Git branch changes."""

    def analyze_branch_command(
        repo_path: Options.repo_path.annotation = Options.repo_path.default,
        base_ref: Options.base_ref.annotation = Options.base_ref.default,
        head_ref: Options.head_ref.annotation = Options.head_ref.default,
        show_patch: Options.show_patch.annotation = Options.show_patch.default,
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
