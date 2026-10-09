from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import QaNoteContext
from qa_note_agent.application.services.qa_note_context_renderer import (
    render_patch_section,
    render_shared_context,
)
from qa_note_agent.domain.branch_changes import BranchChanges


class BuildQaNoteContextUseCase:
    """Build LLM-ready context from Git branch changes."""

    def execute(
        self,
        *,
        changes: BranchChanges,
        max_patch_chars: int = 20_000,
        max_changed_files: int = 80,
        max_commits: int = 30,
    ) -> QaNoteContext:
        shared_context = render_shared_context(
            changes=changes,
            max_changed_files=max_changed_files,
            max_commits=max_commits,
        )
        patch, is_patch_truncated = _truncate_text(
            text=changes.patch,
            max_chars=max_patch_chars,
        )

        return QaNoteContext(
            content="\n\n".join(
                (
                    "# Git changes context for QA note",
                    shared_context.content,
                    render_patch_section(patch=patch),
                ),
            ),
            is_truncated=shared_context.is_truncated or is_patch_truncated,
        )


def _truncate_text(*, text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0:
        return "", bool(text)

    if len(text) <= max_chars:
        return text, False

    suffix = "\n\n# ... patch truncated ..."
    available_chars = max_chars - len(suffix)

    if available_chars <= 0:
        return suffix.strip(), True

    return text[:available_chars].rstrip() + suffix, True
