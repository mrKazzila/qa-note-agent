from __future__ import annotations

from pathlib import Path

from qa_note_agent.application.ports.git import GitClient
from qa_note_agent.domain.branch_changes import BranchChanges


class AnalyzeBranchChangesUseCase:
    def __init__(self, git_client: GitClient) -> None:
        self._git_client = git_client

    def execute(
        self,
        repo_path: Path,
        base_ref: str,
        head_ref: str = "HEAD",
    ) -> BranchChanges:
        return self._git_client.analyze_branch(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
        )
