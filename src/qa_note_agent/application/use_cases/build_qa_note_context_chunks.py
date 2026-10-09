from __future__ import annotations

import structlog

from qa_note_agent.application.dtos.qa_note_context import (
    QaNoteContextChunk,
    QaNoteContextChunkSet,
)
from qa_note_agent.application.services.diff_chunker import DiffChunker
from qa_note_agent.application.services.qa_note_context_renderer import (
    build_chunk_title,
    render_chunk_content,
    render_no_patch_chunk_content,
    render_shared_context,
)
from qa_note_agent.domain.branch_changes import BranchChanges

logger = structlog.get_logger(__name__)


class BuildQaNoteContextChunksUseCase:
    """Build chunked LLM-ready context from Git branch changes."""

    def __init__(self, diff_chunker: DiffChunker) -> None:
        self._diff_chunker = diff_chunker

    def execute(
        self,
        *,
        changes: BranchChanges,
        max_chunk_chars: int = 12_000,
        max_changed_files: int = 80,
        max_commits: int = 30,
    ) -> QaNoteContextChunkSet:
        if max_chunk_chars < 2_000:
            msg = "max_chunk_chars must be at least 2000"
            raise ValueError(msg)

        context = render_shared_context(
            changes=changes,
            max_changed_files=max_changed_files,
            max_commits=max_commits,
        )
        shared_context = context.content
        is_shared_context_truncated = context.is_truncated

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
                content=render_no_patch_chunk_content(
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
            title = build_chunk_title(files=diff_chunk.files)

            chunks.append(
                QaNoteContextChunk(
                    index=index,
                    total=total,
                    title=title,
                    content=render_chunk_content(
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
