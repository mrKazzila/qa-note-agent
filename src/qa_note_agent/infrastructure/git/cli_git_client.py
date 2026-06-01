from __future__ import annotations

import subprocess
from pathlib import Path

from qa_note_agent.application.ports.git import GitClient
from qa_note_agent.domain.branch_changes import BranchChanges
from qa_note_agent.infrastructure.git.errors import GitCommandError


class CliGitClient(GitClient):
    """Git client implementation based on local git CLI."""

    def analyze_branch(
        self,
        repo_path: Path,
        base_ref: str,
        head_ref: str = "HEAD",
    ) -> BranchChanges:
        merge_base = self._merge_base(
            repo_path=repo_path,
            base_ref=base_ref,
            head_ref=head_ref,
        )

        commits_raw = self._run_git(
            repo_path,
            "log",
            "--no-color",
            "--date=iso-strict",
            "--format=%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b%x1e",
            f"{merge_base}..{head_ref}",
        )

        name_status_raw = self._run_git(
            repo_path,
            "diff",
            "--no-color",
            "--no-ext-diff",
            "--name-status",
            "-M",
            f"{merge_base}...{head_ref}",
        )

        numstat_raw = self._run_git(
            repo_path,
            "diff",
            "--no-color",
            "--no-ext-diff",
            "--numstat",
            f"{merge_base}...{head_ref}",
        )

        stat_raw = self._run_git(
            repo_path,
            "diff",
            "--no-color",
            "--no-ext-diff",
            "--stat",
            f"{merge_base}...{head_ref}",
        )

        patch = self._run_git(
            repo_path,
            "diff",
            "--no-color",
            "--no-ext-diff",
            "--find-renames",
            f"{merge_base}...{head_ref}",
        )

        return BranchChanges(
            base_ref=base_ref,
            head_ref=head_ref,
            merge_base=merge_base,
            commits_raw=commits_raw,
            name_status_raw=name_status_raw,
            numstat_raw=numstat_raw,
            stat_raw=stat_raw,
            patch=patch,
        )

    def _merge_base(
        self,
        repo_path: Path,
        base_ref: str,
        head_ref: str,
    ) -> str:
        return self._run_git(repo_path, "merge-base", base_ref, head_ref).strip()

    def _run_git(self, repo_path: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        if result.returncode != 0:
            raise GitCommandError(
                command=("git", *args),
                stderr=result.stderr.strip(),
                returncode=result.returncode,
            )

        return result.stdout
