from __future__ import annotations

from pathlib import Path

from qa_note_agent.domain.branch_changes import BranchChanges


def render_git_branch_changes(
    *,
    changes: BranchChanges,
    repo_path: Path,
    show_patch: bool = False,
) -> str:
    """Render local Git branch changes as a readable CLI report."""
    sections = [
        _render_header(repo_path=repo_path, changes=changes),
        _render_summary(changes=changes),
        _render_changed_files(changes=changes),
        _render_commits(changes=changes),
    ]

    if show_patch:
        sections.append(_render_patch(changes=changes))

    return "\n\n".join(section for section in sections if section.strip())


def _render_header(
    *,
    repo_path: Path,
    changes: BranchChanges,
) -> str:
    return "\n".join(
        (
            "# Git branch analysis",
            "",
            f"- Repository: `{repo_path}`",
            f"- Base ref: `{changes.base_ref}`",
            f"- Head ref: `{changes.head_ref}`",
            f"- Merge base: `{changes.merge_base}`",
        ),
    )


def _render_summary(*, changes: BranchChanges) -> str:
    lines = [
        "## Summary",
        "",
        f"- Files changed: `{changes.stats.files_changed}`",
        f"- Insertions: `{changes.stats.insertions}`",
        f"- Deletions: `{changes.stats.deletions}`",
    ]

    if changes.stats.binary_files:
        lines.append(f"- Binary files: `{changes.stats.binary_files}`")

    if changes.stat_raw.strip():
        lines.extend(
            (
                "",
                "```text",
                changes.stat_raw.rstrip(),
                "```",
            ),
        )

    return "\n".join(lines)


def _render_changed_files(*, changes: BranchChanges) -> str:
    if not changes.changed_files:
        return "\n".join(
            (
                "## Changed files",
                "",
                "No changed files.",
            ),
        )

    lines = [
        "## Changed files",
        "",
    ]

    for file in changes.changed_files:
        if file.old_path is not None:
            suffix = ""
            if file.similarity is not None:
                suffix = f" ({file.similarity}%)"

            lines.append(
                f"- `{file.status}` `{file.old_path}` → `{file.path}`{suffix}",
            )
        else:
            lines.append(f"- `{file.status}` `{file.path}`")

    return "\n".join(lines)


def _render_commits(*, changes: BranchChanges) -> str:
    if not changes.commits:
        return "\n".join(
            (
                "## Commits",
                "",
                "No commits.",
            ),
        )

    lines = [
        "## Commits",
        "",
    ]

    for commit in changes.commits:
        lines.append(f"- `{commit.sha[:8]}` {commit.subject}")
        lines.append(
            f"  - Author: {commit.author_name} <{commit.author_email}>",
        )
        lines.append(f"  - Date: {commit.date}")

        if commit.body:
            normalized_body = " ".join(commit.body.split())
            lines.append(f"  - Body: {normalized_body}")

    return "\n".join(lines)


def _render_patch(*, changes: BranchChanges) -> str:
    if not changes.patch.strip():
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
            changes.patch.rstrip(),
            "```",
        ),
    )
