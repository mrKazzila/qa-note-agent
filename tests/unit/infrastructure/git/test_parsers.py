from __future__ import annotations

import pytest

from qa_note_agent.domain.branch_changes import (
    ChangedFile,
    ChangeStats,
    CommitInfo,
)
from qa_note_agent.infrastructure.git.parsers import (
    parse_changed_files,
    parse_commits,
    parse_numstat_summary,
)


def test_parse_commits_parses_single_commit() -> None:
    # Arrange
    raw = (
        "1234567890abcdef\x1fAlice\x1falice@example.com\x1f2026-06-01T12:00:00+00:00"
        "\x1fAdd parser tests\x1fBody text\x1e"
    )

    # Act
    result = parse_commits(raw)

    # Assert
    assert result == (
        CommitInfo(
            sha="1234567890abcdef",
            author_name="Alice",
            author_email="alice@example.com",
            date="2026-06-01T12:00:00+00:00",
            subject="Add parser tests",
            body="Body text",
        ),
    )


def test_parse_commits_parses_multiple_commits() -> None:
    # Arrange
    raw = (
        "1234567890abcdef\x1fAlice\x1falice@example.com\x1f2026-06-01T12:00:00+00:00"
        "\x1fAdd parser tests\x1fBody text\x1e"
        "fedcba0987654321\x1fBob\x1fbob@example.com\x1f2026-06-02T08:30:00+00:00"
        "\x1fRender git changes\x1fFollow-up body\x1e"
    )

    # Act
    result = parse_commits(raw)

    # Assert
    assert result == (
        CommitInfo(
            sha="1234567890abcdef",
            author_name="Alice",
            author_email="alice@example.com",
            date="2026-06-01T12:00:00+00:00",
            subject="Add parser tests",
            body="Body text",
        ),
        CommitInfo(
            sha="fedcba0987654321",
            author_name="Bob",
            author_email="bob@example.com",
            date="2026-06-02T08:30:00+00:00",
            subject="Render git changes",
            body="Follow-up body",
        ),
    )


def test_parse_commits_strips_commit_body() -> None:
    # Arrange
    raw = (
        "1234567890abcdef\x1fAlice\x1falice@example.com\x1f2026-06-01T12:00:00+00:00"
        "\x1fAdd parser tests\x1f\n\nDetailed explanation.\nSecond line.\n\x1e"
    )

    # Act
    result = parse_commits(raw)

    # Assert
    assert result == (
        CommitInfo(
            sha="1234567890abcdef",
            author_name="Alice",
            author_email="alice@example.com",
            date="2026-06-01T12:00:00+00:00",
            subject="Add parser tests",
            body="Detailed explanation.\nSecond line.",
        ),
    )


def test_parse_commits_skips_malformed_record() -> None:
    # Arrange
    raw = (
        "broken record without separators\x1e"
        "1234567890abcdef\x1fAlice\x1falice@example.com\x1f2026-06-01T12:00:00+00:00"
        "\x1fAdd parser tests\x1fBody text\x1e"
    )

    # Act
    result = parse_commits(raw)

    # Assert
    assert result == (
        CommitInfo(
            sha="1234567890abcdef",
            author_name="Alice",
            author_email="alice@example.com",
            date="2026-06-01T12:00:00+00:00",
            subject="Add parser tests",
            body="Body text",
        ),
    )


@pytest.mark.parametrize(
    ("status_raw", "path", "expected_status"),
    [
        ("M", "src/module.py", "MODIFIED"),
        ("A", "src/module.py", "ADDED"),
        ("D", "src/module.py", "DELETED"),
    ],
)
def test_parse_changed_files_maps_simple_statuses(
    status_raw: str,
    path: str,
    expected_status: str,
) -> None:
    # Arrange
    raw = f"{status_raw}\t{path}"

    # Act
    result = parse_changed_files(raw)

    # Assert
    assert result == (
        ChangedFile(
            path=path,
            status=expected_status,
        ),
    )


@pytest.mark.parametrize(
    ("status_raw", "old_path", "new_path", "expected_status", "similarity"),
    [
        ("R100", "src/old.py", "src/new.py", "RENAMED", 100),
        ("R087", "src/legacy.py", "src/current.py", "RENAMED", 87),
        ("C100", "src/template.py", "src/template_copy.py", "COPIED", 100),
    ],
)
def test_parse_changed_files_parses_rename_and_copy_entries(
    status_raw: str,
    old_path: str,
    new_path: str,
    expected_status: str,
    similarity: int,
) -> None:
    # Arrange
    raw = f"{status_raw}\t{old_path}\t{new_path}"

    # Act
    result = parse_changed_files(raw)

    # Assert
    assert result == (
        ChangedFile(
            path=new_path,
            old_path=old_path,
            status=expected_status,
            similarity=similarity,
        ),
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "10\t2\tsrc/app.py\n3\t1\tsrc/domain.py",
            ChangeStats(
                files_changed=2,
                insertions=13,
                deletions=3,
                binary_files=0,
            ),
        ),
        (
            "10\t2\tsrc/app.py\n-\t-\tassets/logo.png",
            ChangeStats(
                files_changed=2,
                insertions=10,
                deletions=2,
                binary_files=1,
            ),
        ),
        (
            "",
            ChangeStats(
                files_changed=0,
                insertions=0,
                deletions=0,
                binary_files=0,
            ),
        ),
        (
            "10\t2\tsrc/app.py\nmalformed line\n7\t1\tsrc/valid.py",
            ChangeStats(
                files_changed=2,
                insertions=17,
                deletions=3,
                binary_files=0,
            ),
        ),
    ],
)
def test_parse_numstat_summary_aggregates_expected_stats(
    raw: str,
    expected: ChangeStats,
) -> None:
    # Arrange
    numstat_output = raw

    # Act
    result = parse_numstat_summary(numstat_output)

    # Assert
    assert result == expected
