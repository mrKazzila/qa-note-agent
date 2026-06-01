from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QaNote:
    """Generated QA note."""

    content: str
    chunks_count: int
    was_context_truncated: bool
