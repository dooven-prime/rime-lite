"""Hostile controls for the repository-non-intervention guard."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

from verification_state import (
    changed_tracked_paths,
    copy_visible_worktree,
    snapshot_tracked_state,
    verification_exit_code,
)
from verify_zenodo_anchor import record_id


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_tracked_mutation_is_detected() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        _git(root, "init")
        _git(root, "config", "user.name", "Verification Test")
        _git(root, "config", "user.email", "verification@example.invalid")
        tracked = root / "historical-artifact.json"
        tracked.write_text('{"state":"frozen"}\n', encoding="utf-8")
        _git(root, "add", tracked.name)
        _git(root, "commit", "-m", "fixture")

        before = snapshot_tracked_state(root)
        assert before == snapshot_tracked_state(root)
        with tempfile.TemporaryDirectory() as scratch_directory:
            scratch = Path(scratch_directory) / "repository"
            copy_visible_worktree(root, scratch)
            (scratch / tracked.name).write_text(
                '{"state":"scratch-only"}\n', encoding="utf-8"
            )
            assert before == snapshot_tracked_state(root)
        tracked.write_text('{"state":"rewritten"}\n', encoding="utf-8")
        after = snapshot_tracked_state(root)

        assert before != after
        assert changed_tracked_paths(before, after) == [tracked.name]
        assert verification_exit_code(0, before, after) == 1


def test_zenodo_record_id_forms() -> None:
    assert record_id("21988041") == "21988041"
    assert record_id("10.5281/zenodo.21988041") == "21988041"
    assert record_id("https://doi.org/10.5281/zenodo.21988041") == "21988041"


if __name__ == "__main__":
    test_tracked_mutation_is_detected()
    test_zenodo_record_id_forms()
    print("test_verification_state.py: OK")
