from __future__ import annotations

import pytest

from qa_note_agent.application.services.diff_chunker import DiffChunker


def test_split_returns_empty_tuple_for_empty_patch() -> None:
    chunker = DiffChunker()

    chunks = chunker.split("", max_chunk_chars=100)

    assert chunks == ()


def test_split_rejects_non_positive_max_chunk_chars() -> None:
    chunker = DiffChunker()

    with pytest.raises(ValueError, match="max_chunk_chars"):
        chunker.split("diff", max_chunk_chars=0)


def test_split_keeps_small_file_patch_as_single_chunk() -> None:
    chunker = DiffChunker()
    patch = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-old
+new
"""

    chunks = chunker.split(patch, max_chunk_chars=1_000)

    assert len(chunks) == 1
    assert chunks[0].files == ("src/app.py",)
    assert chunks[0].split_reason == "file"
    assert "diff --git a/src/app.py b/src/app.py" in chunks[0].content


def test_split_splits_patch_by_file_boundaries() -> None:
    chunker = DiffChunker()
    patch = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-old
+new
diff --git a/tests/test_app.py b/tests/test_app.py
index 3333333..4444444 100644
--- a/tests/test_app.py
+++ b/tests/test_app.py
@@ -1 +1 @@
-old_test
+new_test
"""

    chunks = chunker.split(patch, max_chunk_chars=180)

    assert len(chunks) == 2
    assert chunks[0].files == ("src/app.py",)
    assert chunks[1].files == ("tests/test_app.py",)


def test_split_splits_large_file_patch_by_hunks() -> None:
    chunker = DiffChunker()
    patch = """diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-old_1
+new_1
@@ -20 +20 @@
-old_2
+new_2
@@ -40 +40 @@
-old_3
+new_3
"""

    chunks = chunker.split(patch, max_chunk_chars=170)

    assert len(chunks) > 1
    assert {chunk.files for chunk in chunks} == {("src/app.py",)}
    assert all(chunk.split_reason in {"hunk", "hard"} for chunk in chunks)


def test_split_hard_splits_single_large_hunk() -> None:
    chunker = DiffChunker()
    large_line = "x" * 500
    patch = f"""diff --git a/src/app.py b/src/app.py
index 1111111..2222222 100644
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-{large_line}
+{large_line}
"""

    chunks = chunker.split(patch, max_chunk_chars=200)

    assert len(chunks) > 1
    assert all(chunk.files == ("src/app.py",) for chunk in chunks)
    assert all(chunk.split_reason == "hard" for chunk in chunks)
    assert all(
        "split inside a large hunk" in chunk.content for chunk in chunks
    )


def test_split_uses_unknown_file_for_non_git_diff_text() -> None:
    chunker = DiffChunker()

    chunks = chunker.split("plain patch text", max_chunk_chars=100)

    assert len(chunks) == 1
    assert chunks[0].files == ("unknown",)
