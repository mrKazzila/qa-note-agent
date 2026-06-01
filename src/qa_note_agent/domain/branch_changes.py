from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommitInfo:
    """Git commit metadata."""

    sha: str
    author_name: str
    author_email: str
    date: str
    subject: str
    body: str


@dataclass(frozen=True, slots=True)
class ChangedFile:
    """Changed file metadata."""

    path: str
    status: str
    old_path: str | None = None
    similarity: int | None = None


@dataclass(frozen=True, slots=True)
class ChangeStats:
    """Aggregated Git diff stats."""

    files_changed: int
    insertions: int
    deletions: int
    binary_files: int


@dataclass(frozen=True, slots=True)
class BranchChanges:
    """Git branch analysis result."""

    base_ref: str
    head_ref: str
    merge_base: str
    commits: tuple[CommitInfo, ...]
    changed_files: tuple[ChangedFile, ...]
    stats: ChangeStats
    stat_raw: str
    patch: str
