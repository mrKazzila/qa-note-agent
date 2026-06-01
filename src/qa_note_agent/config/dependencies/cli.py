from __future__ import annotations

import typer

from qa_note_agent.application.use_cases.analyze_branch_changes import (
    AnalyzeBranchChangesUseCase,
)
from qa_note_agent.config.settings.base import Settings
from qa_note_agent.infrastructure.git.cli_git_client import CliGitClient
from qa_note_agent.presentation.cli.app import create_app
from qa_note_agent.presentation.cli.dependencies import CliContext


def create_analyze_branch_changes_use_case() -> AnalyzeBranchChangesUseCase:
    """Create analyze branch changes use case."""
    git_client = CliGitClient()

    return AnalyzeBranchChangesUseCase(
        git_client=git_client,
    )


def create_cli_context(settings: Settings) -> CliContext:
    """Create CLI context."""
    return CliContext(
        settings=settings,
        analyze_branch_changes_use_case=create_analyze_branch_changes_use_case(),
    )


def create_cli_app(settings: Settings) -> typer.Typer:
    """Create CLI application."""
    context = create_cli_context(settings=settings)

    return create_app(context=context)
