from __future__ import annotations

import structlog

from qa_note_agent.application.dtos.qa_note_context import (
    QaNoteContextChunk,
    QaNoteContextChunkSet,
)
from qa_note_agent.application.services.diff_chunker import DiffChunker
from qa_note_agent.domain.branch_changes import BranchChanges

logger = structlog.get_logger(__name__)


class BuildQaNoteContextChunksUseCase:
    """Build chunked LLM-ready context from Git branch changes."""

    def __init__(self, diff_chunker: DiffChunker) -> None:
        self._diff_chunker = diff_chunker

    def execute(
        self,
        changes: BranchChanges,
        max_chunk_chars: int = 12_000,
        max_changed_files: int = 80,
        max_commits: int = 30,
    ) -> QaNoteContextChunkSet:
        if max_chunk_chars < 2_000:
            msg = "max_chunk_chars must be at least 2000"
            raise ValueError(msg)

        shared_context, is_shared_context_truncated = _render_shared_context(
            changes=changes,
            max_changed_files=max_changed_files,
            max_commits=max_commits,
        )

        patch_budget = max(1_000, max_chunk_chars - len(shared_context) - 800)

        diff_chunks = self._diff_chunker.split(
            patch=changes.patch,
            max_chunk_chars=patch_budget,
        )

        if not diff_chunks:
            logger.info(
                "qa_note_context_chunked",
                chunk_count=1,
                max_chunk_chars=max_chunk_chars,
                patch_budget=patch_budget,
                changed_files_count=changes.stats.files_changed,
                commit_count=len(changes.commits),
                shared_context_truncated=is_shared_context_truncated,
                patch_present=False,
            )
            chunk = QaNoteContextChunk(
                index=1,
                total=1,
                title="No patch",
                content=_render_no_patch_chunk_content(
                    shared_context=shared_context,
                ),
                files=(),
                is_truncated=is_shared_context_truncated,
            )

            return QaNoteContextChunkSet(
                chunks=(chunk,),
                is_truncated=is_shared_context_truncated,
            )

        total = len(diff_chunks)
        chunks: list[QaNoteContextChunk] = []

        for index, diff_chunk in enumerate(diff_chunks, start=1):
            title = _build_chunk_title(diff_chunk.files)

            chunks.append(
                QaNoteContextChunk(
                    index=index,
                    total=total,
                    title=title,
                    content=_render_chunk_content(
                        index=index,
                        total=total,
                        title=title,
                        shared_context=shared_context,
                        patch=diff_chunk.content,
                        files=diff_chunk.files,
                        split_reason=diff_chunk.split_reason,
                    ),
                    files=diff_chunk.files,
                    is_truncated=is_shared_context_truncated,
                ),
            )

        logger.info(
            "qa_note_context_chunked",
            chunk_count=total,
            max_chunk_chars=max_chunk_chars,
            patch_budget=patch_budget,
            changed_files_count=changes.stats.files_changed,
            commit_count=len(changes.commits),
            shared_context_truncated=is_shared_context_truncated,
            patch_present=True,
        )

        return QaNoteContextChunkSet(
            chunks=tuple(chunks),
            is_truncated=is_shared_context_truncated,
        )


def _render_shared_context(
    *,
    changes: BranchChanges,
    max_changed_files: int,
    max_commits: int,
) -> tuple[str, bool]:
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
    ]

    is_truncated = (
        len(changes.changed_files) > max_changed_files
        or len(changes.commits) > max_commits
    )

    return "\n\n".join(sections), is_truncated


def _render_branch_section(changes: BranchChanges) -> str:
    return "\n".join(
        (
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


def _render_no_patch_chunk_content(*, shared_context: str) -> str:
    return "\n\n".join(
        (
            "# QA note context chunk 1/1",
            shared_context,
            "## Patch",
            "No patch.",
        ),
    )


def _render_chunk_content(
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
            _render_chunk_files_section(files),
            f"## Patch split mode\n\n`{split_reason}`",
            _render_patch_section(patch),
        ),
    )


def _render_chunk_files_section(files: tuple[str, ...]) -> str:
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


def _build_chunk_title(files: tuple[str, ...]) -> str:
    if not files:
        return "No files"

    if len(files) == 1:
        return files[0]

    return f"{files[0]} and {len(files) - 1} more"
