from __future__ import annotations


def render_empty_changes_qa_note(*, base_ref: str, head_ref: str) -> str:
    return "\n".join(
        (
            "# For QA",
            "",
            "## Summary",
            (
                f"- No Git changes were detected between `{base_ref}` and "
                f"`{head_ref}`."
            ),
            "",
            "## What changed",
            "- No changed files were found.",
            "",
            "## What to test",
            "- No QA checks are required for this diff.",
            "",
            "## Regression risks",
            ("- No regression risks were detected because the diff is empty."),
            "",
            "## Edge cases",
            ("- Verify the selected base ref if changes were expected."),
            "",
            "## Notes",
            (
                "- Run with another `--base` value if this branch should "
                "contain changes."
            ),
        ),
    )
