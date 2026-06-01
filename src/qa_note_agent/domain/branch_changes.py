from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BranchChanges:
    """Raw Git branch analysis result."""

    base_ref: str
    head_ref: str
    merge_base: str
    commits_raw: str
    name_status_raw: str
    numstat_raw: str
    stat_raw: str
    patch: str
