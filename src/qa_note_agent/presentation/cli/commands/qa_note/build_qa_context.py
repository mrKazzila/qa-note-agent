from __future__ import annotations

import typer

from qa_note_agent.presentation.cli.commands.common.types import CLICommandFunc
from qa_note_agent.presentation.cli.commands.qa_note.options import (
    BuildQAContextOptions as Options,
)
from qa_note_agent.presentation.cli.dependencies import CliContext
from qa_note_agent.presentation.renderers.qa_note_context import (
    render_qa_note_context,
)


def create_build_qa_context_command(context: CliContext) -> CLICommandFunc:
    """Create command for building QA note LLM context."""

    def build_qa_context_command(
        repo_path: Options.repo_path.annotation = Options.repo_path.default,
        base_ref: Options.base_ref.annotation = Options.base_ref.default,
        head_ref: Options.head_ref.annotation = Options.head_ref.default,
        max_patch_chars: Options.max_chunk_chars.annotation = Options.max_chunk_chars.default,
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

        typer.echo(render_qa_note_context(context=qa_context))

    return build_qa_context_command
