from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import QaNoteContext
from qa_note_agent.domain.branch_changes import BranchChanges


def render_shared_context(
    *,
    changes: BranchChanges,
    max_changed_files: int,
    max_commits: int,
) -> QaNoteContext:
    sections = [
        _render_branch_section(changes=changes),
        _render_summary_section(changes=changes),
        _render_changed_files_section(
            changes=changes,
            max_changed_files=max_changed_files,
        ),
        _render_commits_section(
            changes=changes,
            max_commits=max_commits,
        ),
    ]

    return QaNoteContext(
        content="\n\n".join(sections),
        is_truncated=(
            len(changes.changed_files) > max_changed_files
            or len(changes.commits) > max_commits
        ),
    )


def render_patch_section(*, patch: str) -> str:
    if not patch.strip():
        return "## Patch\n\nNo patch."

    return f"## Patch\n\n```diff\n{patch.rstrip()}\n```"


def _render_branch_section(*, changes: BranchChanges) -> str:
    return "\n".join(
        (
            "## Branch",
            "",
            f"- Base ref: `{changes.base_ref}`",
            f"- Head ref: `{changes.head_ref}`",
            f"- Merge base: `{changes.merge_base}`",
        ),
    )


def _render_summary_section(*, changes: BranchChanges) -> str:
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
    lines = ["## Changed files", ""]

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
    lines = ["## Commits", ""]

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


def render_no_patch_chunk_content(*, shared_context: str) -> str:
    return "\n\n".join(
        (
            "# QA note context chunk 1/1",
            shared_context,
            render_patch_section(patch=""),
        ),
    )


def render_chunk_content(
    *,
    index: int,
    total: int,
    title: str,
    shared_context: str,
    patch: str,
    files: tuple[str, ...],
    split_reason: str,
) -> str:
    return "\n\n".join(
        (
            f"# QA note context chunk {index}/{total}",
            f"Chunk title: `{title}`",
            shared_context,
            _render_chunk_files_section(files=files),
            f"## Patch split mode\n\n`{split_reason}`",
            render_patch_section(patch=patch),
        ),
    )


def _render_chunk_files_section(*, files: tuple[str, ...]) -> str:
    lines = [
        "## This chunk files",
        "",
    ]

    if not files:
        lines.append("No files.")
        return "\n".join(lines)

    for file in files:
        lines.append(f"- `{file}`")

    return "\n".join(lines)


def build_chunk_title(*, files: tuple[str, ...]) -> str:
    if not files:
        return "No files"

    if len(files) == 1:
        return files[0]

    return f"{files[0]} and {len(files) - 1} more"
