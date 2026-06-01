from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QaNoteContext:
    """Prepared context for QA note generation."""

    content: str
    is_truncated: bool
    