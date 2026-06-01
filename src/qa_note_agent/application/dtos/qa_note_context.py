from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QaNoteContext:
    """Prepared context for QA note generation."""

    content: str
    is_truncated: bool


@dataclass(frozen=True, slots=True)
class QaNoteContextChunk:
    """Single LLM-ready context chunk."""

    index: int
    total: int
    title: str
    content: str
    files: tuple[str, ...]
    is_truncated: bool = False


@dataclass(frozen=True, slots=True)
class QaNoteContextChunkSet:
    """Chunked context for multi-step QA note generation."""

    chunks: tuple[QaNoteContextChunk, ...]
    is_truncated: bool