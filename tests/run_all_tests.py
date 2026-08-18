#!/usr/bin/env python
"""Run active regressions without allowing them to mutate the source tree."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from verification_state import (
    SCRATCH_ENV,
    changed_tracked_paths,
    copy_visible_worktree,
    snapshot_tracked_state,
    verification_exit_code,
)


TESTS = [
    "test_action_token.py",
    "test_cubie.py",
    "test_cubieoperator.py",
    "test_spectralstructure.py",
    "test_spectral_utils_api.py",
    "test_representation.py",
    "test_spectrum.py",
    "test_sectors.py",
    "test_commutant.py",
    "test_transport.py",
    "test_experiment_observation.py",
    "test_verification_state.py",
    "test_contract_api.py",
    "test_accessibility_engine.py",
    "test_wall_trajectory.py",
    "test_registry_v2.py",
    "test_registry_migration.py",
    "test_sofcompiler_contracts.py",
    "test_sofrs_v2.py",
    "test_sofaudit_v2.py",
    "test_sof_action.py",
    "test_sofaction_v2.py",
]

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
BASELINE_PATH = ROOT / "verification-baseline.json"


def load_baseline() -> set[str]:
    payload = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return set(payload["expected_failures"])


def run_suite() -> int:
    if os.environ.get(SCRATCH_ENV) != "1":
        raise SystemExit("internal suite execution is allowed only in verification scratch")

    env = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
    failed: list[str] = []
    for name in TESTS:
        path = ROOT / name
        print(f"\n{'=' * 60}", flush=True)
        print(f" {name} ".center(60, "="), flush=True)
        print(f"{'=' * 60}", flush=True)
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(PROJECT_ROOT),
            env=env,
        )
        if result.returncode != 0:
            failed.append(name)

    expected = load_baseline()
    observed = set(failed)
    new = sorted(observed - expected)
    existing = sorted(observed & expected)
    resolved = sorted(expected - observed)

    print(f"\n{'=' * 60}")
    print(f"  TEST RESULTS: {len(TESTS) - len(failed)}/{len(TESTS)} passed")
    print(f"  NEW_FAILURES: {new or 'none'}")
    print(f"  BASELINE_FAILURES: {existing or 'none'}")
    print(f"  RESOLVED_BASELINE_FAILURES: {resolved or 'none'}")
    if new:
        status, returncode = "FAIL", 1
    elif existing or resolved:
        status, returncode = "UNRESOLVED", 2
    else:
        status, returncode = "PASS", 0
    print(f"  VERIFICATION_STATUS: {status}")
    print(f"{'=' * 60}")
    return returncode


def verify(*, keep_scratch: bool, scratch_parent: Path | None) -> int:
    before = snapshot_tracked_state(PROJECT_ROOT)
    temporary = tempfile.mkdtemp(
        prefix="rime-verify-",
        dir=str(scratch_parent) if scratch_parent else None,
    )
    scratch = Path(temporary) / "repository"
    returncode = 1
    try:
        print("RELEASE_STAGE: VERIFY")
        print(f"VERIFY_SOURCE_HEAD: {before.head}")
        print(
            "VERIFY_SOURCE_TRACKED_STATUS: "
            f"{before.status.rstrip() or 'CLEAN'}"
        )
        print(f"VERIFY_SOURCE_TRACKED_DIFF: {before.diff_digest}")
        print(f"VERIFY_SOURCE_TRACKED_CONTENT: {before.content_digest}")
        print(f"VERIFY_SCRATCH: {scratch}", flush=True)
        copy_visible_worktree(PROJECT_ROOT, scratch)
        print("RELEASE_STAGE: BUILD_REPLAY_IN_ISOLATION", flush=True)
        env = {**os.environ, SCRATCH_ENV: "1"}
        result = subprocess.run(
            [
                sys.executable,
                str(scratch / "tests" / "run_all_tests.py"),
                "--scratch-suite",
            ],
            cwd=str(scratch),
            env=env,
        )
        returncode = result.returncode
    finally:
        after = snapshot_tracked_state(PROJECT_ROOT)
        changed = changed_tracked_paths(before, after)
        print(f"VERIFY_END_HEAD: {after.head}")
        print(
            "VERIFY_END_TRACKED_STATUS: "
            f"{after.status.rstrip() or 'CLEAN'}"
        )
        print(f"VERIFY_END_TRACKED_DIFF: {after.diff_digest}")
        print(f"VERIFY_END_TRACKED_CONTENT: {after.content_digest}")
        if before != after:
            print("VERIFICATION_SIDE_EFFECT")
            print(f"  HEAD_BEFORE: {before.head}")
            print(f"  HEAD_AFTER: {after.head}")
            print(f"  TRACKED_CONTENT_BEFORE: {before.content_digest}")
            print(f"  TRACKED_CONTENT_AFTER: {after.content_digest}")
            print(f"  CHANGED_TRACKED_PATHS: {changed or ['state metadata changed']}")
        else:
            print("VERIFY_TRACKED_TREE: UNCHANGED")
        returncode = verification_exit_code(returncode, before, after)
        if keep_scratch:
            print(f"VERIFY_SCRATCH_RETAINED: {scratch}")
        else:
            shutil.rmtree(temporary, ignore_errors=True)
    return returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run active tests in an isolated copy and reject source-tree mutation."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="verify",
        choices=("verify",),
        help="verification is isolated and read-only with respect to the source tree",
    )
    parser.add_argument("--keep-scratch", action="store_true")
    parser.add_argument("--scratch-parent", type=Path)
    parser.add_argument("--scratch-suite", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.scratch_suite:
        return run_suite()
    if args.scratch_parent:
        args.scratch_parent.mkdir(parents=True, exist_ok=True)
    return verify(
        keep_scratch=args.keep_scratch,
        scratch_parent=args.scratch_parent,
    )


if __name__ == "__main__":
    raise SystemExit(main())
