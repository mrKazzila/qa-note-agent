from __future__ import annotations

from pathlib import Path

import pytest

from qa_note_agent.domain.branch_changes import (
    BranchChanges,
    ChangedFile,
    ChangeStats,
    CommitInfo,
)
from qa_note_agent.presentation.renderers.git_branch_changes import (
    render_git_branch_changes,
)


@pytest.fixture
def branch_changes_factory():
    def factory(
        *,
        commits: tuple[CommitInfo, ...] | None = None,
        changed_files: tuple[ChangedFile, ...] | None = None,
        stats: ChangeStats | None = None,
        stat_raw: str = "",
        patch: str = "",
    ) -> BranchChanges:
        return BranchChanges(
            base_ref="origin/main",
            head_ref="HEAD",
            merge_base="abc123def456",
            commits=commits or (),
            changed_files=changed_files or (),
            stats=stats
            or ChangeStats(
                files_changed=0,
                insertions=0,
                deletions=0,
                binary_files=0,
            ),
            stat_raw=stat_raw,
            patch=patch,
        )

    return factory


def test_render_git_branch_changes_renders_main_sections(
    branch_changes_factory,
) -> None:
    # Arrange
    changes = branch_changes_factory(
        commits=(
            CommitInfo(
                sha="1234567890abcdef",
                author_name="Alice",
                author_email="alice@example.com",
                date="2026-06-01T12:00:00+00:00",
                subject="Add parser tests",
                body="Detailed body",
            ),
        ),
        changed_files=(
            ChangedFile(
                path="src/module.py",
                status="MODIFIED",
            ),
        ),
        stats=ChangeStats(
            files_changed=1,
            insertions=10,
            deletions=2,
            binary_files=0,
        ),
    )

    # Act
    result = render_git_branch_changes(
        changes=changes,
        repo_path=Path("/repo/project"),
    )

    # Assert
    assert "# Git branch analysis" in result
    assert "## Summary" in result
    assert "## Changed files" in result
    assert "## Commits" in result


def test_render_git_branch_changes_renders_rename_with_similarity(
    branch_changes_factory,
) -> None:
    # Arrange
    changes = branch_changes_factory(
        changed_files=(
            ChangedFile(
                path="src/new.py",
                old_path="src/old.py",
                status="RENAMED",
                similarity=87,
            ),
        ),
    )

    # Act
    result = render_git_branch_changes(
        changes=changes,
        repo_path=Path("/repo/project"),
    )

    # Assert
    assert "`RENAMED` `src/old.py` → `src/new.py` (87%)" in result


def test_render_git_branch_changes_shows_empty_changed_files_section(
    branch_changes_factory,
) -> None:
    # Arrange
    changes = branch_changes_factory()

    # Act
    result = render_git_branch_changes(
        changes=changes,
        repo_path=Path("/repo/project"),
    )

    # Assert
    assert "## Changed files" in result
    assert "No changed files." in result


def test_render_git_branch_changes_shows_empty_commits_section(
    branch_changes_factory,
) -> None:
    # Arrange
    changes = branch_changes_factory()

    # Act
    result = render_git_branch_changes(
        changes=changes,
        repo_path=Path("/repo/project"),
    )

    # Assert
    assert "## Commits" in result
    assert "No commits." in result


def test_render_git_branch_changes_includes_stat_block_only_when_present(
    branch_changes_factory,
) -> None:
    # Arrange
    changes_with_stat = branch_changes_factory(
        stats=ChangeStats(
            files_changed=1,
            insertions=3,
            deletions=1,
            binary_files=0,
        ),
        stat_raw=" src/module.py | 4 ++--",
    )
    changes_without_stat = branch_changes_factory(
        stats=ChangeStats(
            files_changed=1,
            insertions=3,
            deletions=1,
            binary_files=0,
        ),
        stat_raw="",
    )

    # Act
    rendered_with_stat = render_git_branch_changes(
        changes=changes_with_stat,
        repo_path=Path("/repo/project"),
    )
    rendered_without_stat = render_git_branch_changes(
        changes=changes_without_stat,
        repo_path=Path("/repo/project"),
    )

    # Assert
    assert "```text" in rendered_with_stat
    assert "src/module.py | 4 ++--" in rendered_with_stat
    assert "```text" not in rendered_without_stat


def test_render_git_branch_changes_includes_binary_files_line_only_when_needed(
    branch_changes_factory,
) -> None:
    # Arrange
    changes_with_binary = branch_changes_factory(
        stats=ChangeStats(
            files_changed=2,
            insertions=10,
            deletions=2,
            binary_files=1,
        ),
    )
    changes_without_binary = branch_changes_factory(
        stats=ChangeStats(
            files_changed=2,
            insertions=10,
            deletions=2,
            binary_files=0,
        ),
    )

    # Act
    rendered_with_binary = render_git_branch_changes(
        changes=changes_with_binary,
        repo_path=Path("/repo/project"),
    )
    rendered_without_binary = render_git_branch_changes(
        changes=changes_without_binary,
        repo_path=Path("/repo/project"),
    )

    # Assert
    assert "- Binary files: `1`" in rendered_with_binary
    assert "- Binary files:" not in rendered_without_binary
