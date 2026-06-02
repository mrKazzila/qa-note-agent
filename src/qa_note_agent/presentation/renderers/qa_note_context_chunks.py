from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import (
    QaNoteContextChunk,
    QaNoteContextChunkSet,
)


def render_qa_note_context_chunk_list(chunk_set: QaNoteContextChunkSet) -> str:
    """Render short chunk list for CLI output."""
    lines: list[str] = [
        f"Chunks: {len(chunk_set.chunks)}",
        f"Truncated: {chunk_set.is_truncated}",
        "",
    ]

    for chunk in chunk_set.chunks:
        files = ", ".join(chunk.files) if chunk.files else "no files"
        lines.append(
            f"{chunk.index}/{chunk.total}: {chunk.title} "
            f"({len(chunk.content)} chars, files: {files})",
        )

    return "\n".join(lines)


def render_qa_note_context_chunk(chunk: QaNoteContextChunk) -> str:
    """Render a single QA note context chunk."""
    return chunk.content


def render_qa_note_context_chunks(chunk_set: QaNoteContextChunkSet) -> str:
    """Render all QA note context chunks."""
    parts: list[str] = []

    for chunk in chunk_set.chunks:
        parts.append(chunk.content)

    output = "\n\n---\n\n".join(parts)

    if chunk_set.is_truncated:
        output = f"{output}\n\n> Context was truncated."

    return output
