from __future__ import annotations

import typer

from qa_note_agent.application.use_cases.analyze_branch_changes import (
    AnalyzeBranchChangesUseCase,
)
from qa_note_agent.application.use_cases.build_qa_note_context import (
    BuildQaNoteContextUseCase,
)
from qa_note_agent.config.settings.base import Settings
from qa_note_agent.infrastructure.git.cli_git_client import CliGitClient
from qa_note_agent.presentation.cli.app import create_app
from qa_note_agent.presentation.cli.dependencies import CliContext
from qa_note_agent.application.services.diff_chunker import DiffChunker
from qa_note_agent.application.use_cases.build_qa_note_context_chunks import (
    BuildQaNoteContextChunksUseCase,
)


def create_analyze_branch_changes_use_case() -> AnalyzeBranchChangesUseCase:
    """Create analyze branch changes use case."""
    git_client = CliGitClient()

    return AnalyzeBranchChangesUseCase(
        git_client=git_client,
    )


def create_build_qa_note_context_use_case() -> BuildQaNoteContextUseCase:
    """Create build QA note context use case."""
    return BuildQaNoteContextUseCase()


def create_build_qa_note_context_chunks_use_case() -> BuildQaNoteContextChunksUseCase:
    """Create build QA note context chunks use case."""
    return BuildQaNoteContextChunksUseCase(
        diff_chunker=DiffChunker(),
    )


def create_cli_context(settings: Settings) -> CliContext:
    """Create CLI context."""
    return CliContext(
        settings=settings,
        analyze_branch_changes_use_case=create_analyze_branch_changes_use_case(),
        build_qa_note_context_use_case=create_build_qa_note_context_use_case(),
        build_qa_note_context_chunks_use_case=create_build_qa_note_context_chunks_use_case(),
    )


def create_cli_app(settings: Settings) -> typer.Typer:
    """Create CLI application."""
    context = create_cli_context(settings=settings)

    return create_app(context=context)


