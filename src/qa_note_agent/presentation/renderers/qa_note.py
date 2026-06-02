from __future__ import annotations

from pathlib import Path

from qa_note_agent.application.dtos.qa_note import QaNote


def render_qa_note_stdout(note: QaNote) -> str:
    """Render generated QA note for stdout."""
    lines: list[str] = [
        note.content,
        "",
        "---",
        f"Chunks analyzed: {note.chunks_count}",
    ]

    if note.was_context_truncated:
        lines.append("Context was truncated.")

    return "\n".join(lines)


def render_qa_note_write_summary(note: QaNote, output_path: Path) -> str:
    """Render summary after QA note was written to file."""
    lines: list[str] = [
        f"QA note written to: {output_path}",
        f"Chunks analyzed: {note.chunks_count}",
    ]

    if note.was_context_truncated:
        lines.append("Context was truncated.")

    return "\n".join(lines)
