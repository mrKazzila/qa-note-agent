from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import QaNoteContext
from qa_note_agent.domain.branch_changes import BranchChanges


class BuildQaNoteContextUseCase:
    """Build LLM-ready context from Git branch changes."""

    def execute(
        self,
        changes: BranchChanges,
        max_patch_chars: int = 20_000,
        max_changed_files: int = 80,
        max_commits: int = 30,
    ) -> QaNoteContext:
        patch, is_patch_truncated = _truncate_text(
            changes.patch,
            max_chars=max_patch_chars,
        )

        sections = [
            _render_branch_section(changes),
            _render_summary_section(changes),
            _render_changed_files_section(
                changes=changes,
                max_changed_files=max_changed_files,
            ),
            _render_commits_section(
                changes=changes,
                max_commits=max_commits,
            ),
            _render_patch_section(patch),
        ]

        is_changed_files_truncated = (
            len(changes.changed_files) > max_changed_files
        )
        is_commits_truncated = len(changes.commits) > max_commits

        return QaNoteContext(
            content="\n\n".join(sections),
            is_truncated=(
                is_patch_truncated
                or is_changed_files_truncated
                or is_commits_truncated
            ),
        )


def _render_branch_section(changes: BranchChanges) -> str:
    return "\n".join(
        (
            "# Git changes context for QA note",
            "",
            "## Branch",
            "",
            f"- Base ref: `{changes.base_ref}`",
            f"- Head ref: `{changes.head_ref}`",
            f"- Merge base: `{changes.merge_base}`",
        ),
    )


def _render_summary_section(changes: BranchChanges) -> str:
    lines = [
        "## Summary",
        "",
        f"- Files changed: `{changes.stats.files_changed}`",
        f"- Insertions: `{changes.stats.insertions}`",
        f"- Deletions: `{changes.stats.deletions}`",
    ]

    if changes.stats.binary_files:
        lines.append(f"- Binary files: `{changes.stats.binary_files}`")

    return "\n".join(lines)


def _render_changed_files_section(
    *,
    changes: BranchChanges,
    max_changed_files: int,
) -> str:
    lines = [
        "## Changed files",
        "",
    ]

    if not changes.changed_files:
        lines.append("No changed files.")
        return "\n".join(lines)

    visible_files = changes.changed_files[:max_changed_files]

    for changed_file in visible_files:
        if changed_file.old_path is not None:
            similarity = ""
            if changed_file.similarity is not None:
                similarity = f" ({changed_file.similarity}%)"

            lines.append(
                f"- `{changed_file.status}` `{changed_file.old_path}` "
                f"→ `{changed_file.path}`{similarity}",
            )
        else:
            lines.append(f"- `{changed_file.status}` `{changed_file.path}`")

    hidden_count = len(changes.changed_files) - len(visible_files)

    if hidden_count > 0:
        lines.append(f"- ... omitted `{hidden_count}` changed files")

    return "\n".join(lines)


def _render_commits_section(
    *,
    changes: BranchChanges,
    max_commits: int,
) -> str:
    lines = [
        "## Commits",
        "",
    ]

    if not changes.commits:
        lines.append("No commits.")
        return "\n".join(lines)

    visible_commits = changes.commits[:max_commits]

    for commit in visible_commits:
        lines.append(f"- `{commit.sha[:8]}` {commit.subject}")

        if commit.body:
            body = " ".join(commit.body.split())
            lines.append(f"  - Body: {body}")

    hidden_count = len(changes.commits) - len(visible_commits)

    if hidden_count > 0:
        lines.append(f"- ... omitted `{hidden_count}` commits")

    return "\n".join(lines)


def _render_patch_section(patch: str) -> str:
    if not patch.strip():
        return "\n".join(
            (
                "## Patch",
                "",
                "No patch.",
            ),
        )

    return "\n".join(
        (
            "## Patch",
            "",
            "```diff",
            patch.rstrip(),
            "```",
        ),
    )


def _truncate_text(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0:
        return "", bool(text)

    if len(text) <= max_chars:
        return text, False

    suffix = "\n\n# ... patch truncated ..."
    available_chars = max_chars - len(suffix)

    if available_chars <= 0:
        return suffix.strip(), True

    return text[:available_chars].rstrip() + suffix, True
