"""Hostile controls for the repository-non-intervention guard."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from verification_state import (
    changed_tracked_paths,
    create_verification_checkout,
    snapshot_tracked_state,
    verification_exit_code,
)
from tools.release.verify_zenodo_anchor import record_id


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
            create_verification_checkout(root, scratch)
            assert (scratch / ".git").is_dir()
            assert subprocess.run(
                ["git", "show", f"HEAD:{tracked.name}"],
                cwd=scratch,
                check=True,
                capture_output=True,
                text=True,
            ).stdout == '{"state":"frozen"}\n'
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
