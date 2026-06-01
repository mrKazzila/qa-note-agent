from __future__ import annotations

from dataclasses import dataclass

from qa_note_agent.application.use_cases.analyze_branch_changes import (
    AnalyzeBranchChangesUseCase,
)
from qa_note_agent.application.use_cases.build_qa_note_context import (
    BuildQaNoteContextUseCase,
)
from qa_note_agent.config.settings.base import Settings


@dataclass(frozen=True, slots=True)
class CliContext:
    """Dependencies available to CLI commands."""

    settings: Settings
    analyze_branch_changes_use_case: AnalyzeBranchChangesUseCase
    build_qa_note_context_use_case: BuildQaNoteContextUseCase
