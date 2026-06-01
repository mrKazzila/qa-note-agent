from __future__ import annotations

from pathlib import Path
from typing import Protocol

from qa_note_agent.domain.branch_changes import BranchChanges


class GitClient(Protocol):
    def analyze_branch(
        self,
        repo_path: Path,
        base_ref: str,
        head_ref: str = "HEAD",
    ) -> BranchChanges:
        """Analyze changes between base ref and head ref."""
