from __future__ import annotations

from pathlib import Path

from qa_note_agent.application.services.qa_note_sessions import (
    build_session_id,
    normalize_session_id,
)


def test_build_session_id_is_stable_for_same_repo_and_refs() -> None:
    repo_path = Path("/tmp/example-repo")

    first = build_session_id(
        repo_path=repo_path,
        base_ref="origin/main",
        head_ref="HEAD",
        session_id=None,
    )
    second = build_session_id(
        repo_path=repo_path,
        base_ref="origin/main",
        head_ref="HEAD",
        session_id=None,
    )

    assert first == second
    assert first.startswith("qa-note:example-repo:origin/main:HEAD:")


def test_build_session_id_normalizes_manual_override() -> None:
    session_id = build_session_id(
        repo_path=Path("/tmp/example-repo"),
        base_ref="origin/main",
        head_ref="HEAD",
        session_id=" Feature QA / Sprint 1 ",
    )

    assert session_id == "Feature-QA-/-Sprint-1"


def test_normalize_session_id_replaces_non_ascii_and_limits_length() -> None:
    session_id = normalize_session_id(value="тест " + ("a" * 300))

    assert session_id.startswith("a")
    assert len(session_id) == 200
