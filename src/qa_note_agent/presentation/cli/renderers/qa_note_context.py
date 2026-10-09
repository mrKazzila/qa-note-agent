from __future__ import annotations

from qa_note_agent.application.dtos.qa_note_context import QaNoteContext


def render_qa_note_context(context: QaNoteContext) -> str:
    """Render QA note context for CLI output."""
    lines = [context.content]

    if context.is_truncated:
        lines.extend(("", "> Context was truncated."))

    return "\n".join(lines)
