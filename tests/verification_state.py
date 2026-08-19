"""Tracked-tree snapshots and isolated verification workspace support."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SCRATCH_ENV = "RIME_VERIFICATION_SCRATCH"


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout


def _paths(root: Path, *args: str) -> list[str]:
    output = _git(root, "ls-files", "-z", *args)
    return [item.decode("utf-8") for item in output.split(b"\0") if item]


@dataclass(frozen=True)
class TrackedState:
    head: str
    status: str
    diff_digest: str
    content_digest: str
    file_digests: tuple[tuple[str, str], ...]


def snapshot_tracked_state(root: Path) -> TrackedState:
    root = root.resolve()
    head = _git(root, "rev-parse", "HEAD").decode("ascii").strip()
    status = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=no",
    ).decode("utf-8")
    diff = _git(root, "diff", "--binary", "--no-ext-diff", "HEAD", "--")
    records: list[tuple[str, str]] = []
    aggregate = hashlib.sha256()
    for relative in sorted(_paths(root, "--cached")):
        path = root / relative
        if path.is_symlink():
            payload = path.readlink().as_posix().encode("utf-8")
            marker = "symlink"
        elif path.is_file():
            payload = path.read_bytes()
            marker = "file"
        else:
            payload = b""
            marker = "missing"
        digest = hashlib.sha256(payload).hexdigest()
        records.append((relative, f"{marker}:{digest}"))
        aggregate.update(relative.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(marker.encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(payload)
        aggregate.update(b"\0")
    return TrackedState(
        head=head,
        status=status,
        diff_digest=hashlib.sha256(diff).hexdigest(),
        content_digest=aggregate.hexdigest(),
        file_digests=tuple(records),
    )


def changed_tracked_paths(before: TrackedState, after: TrackedState) -> list[str]:
    old = dict(before.file_digests)
    new = dict(after.file_digests)
    return sorted(
        path for path in old.keys() | new.keys() if old.get(path) != new.get(path)
    )


def verification_exit_code(
    test_returncode: int,
    before: TrackedState,
    after: TrackedState,
) -> int:
    """A tracked-tree delta always overrides a successful test result."""
    return 1 if before != after else test_returncode


def copy_visible_worktree(source: Path, destination: Path) -> None:
    """Copy tracked and non-ignored untracked files, excluding Git metadata."""
    source = source.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    relative_paths = sorted(
        set(_paths(source, "--cached", "--others", "--exclude-standard"))
    )
    for relative in relative_paths:
        src = source / relative
        dst = destination / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_symlink():
            dst.symlink_to(src.readlink())
        elif src.is_file():
            shutil.copy2(src, dst)


def create_verification_checkout(source: Path, destination: Path) -> None:
    """Create a history-capable scratch checkout of the visible worktree."""
    source = source.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "--shared",
            "--no-checkout",
            str(source),
            str(destination),
        ],
        check=True,
    )
    subprocess.run(["git", "read-tree", "HEAD"], cwd=destination, check=True)
    copy_visible_worktree(source, destination)


def run_script_in_isolation(source_root: Path, script: Path) -> int:
    """Run one generative regression in scratch and guard its source checkout."""
    source_root = source_root.resolve()
    relative_script = script.resolve().relative_to(source_root)
    before = snapshot_tracked_state(source_root)
    with tempfile.TemporaryDirectory(prefix="rime-verify-one-") as directory:
        scratch = Path(directory) / "repository"
        create_verification_checkout(source_root, scratch)
        result = subprocess.run(
            [sys.executable, str(scratch / relative_script)],
            cwd=scratch,
            env={**os.environ, SCRATCH_ENV: "1"},
        )
    after = snapshot_tracked_state(source_root)
    if before != after:
        print("VERIFICATION_SIDE_EFFECT")
        print(f"  CHANGED_TRACKED_PATHS: {changed_tracked_paths(before, after)}")
    else:
        print("VERIFY_TRACKED_TREE: UNCHANGED")
    return verification_exit_code(result.returncode, before, after)
