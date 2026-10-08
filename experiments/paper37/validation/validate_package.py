#!/usr/bin/env python3
"""Verify a self-contained draft closure; default mode includes finite replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/paper37"
MANIFEST = PACKAGE / "development-manifest.json"
sys.path.insert(0, str(PACKAGE))

from audit_scope import ARTIFACTS  # noqa: E402


RELEASE_ONLY = {
    "experiments/paper37/release-environment.json",
    "experiments/paper37/release-manifest.json",
    "experiments/paper37/validation/validate_release.py",
    "experiments/paper37/results/paper37_public_package_v1.validation-receipt.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def child_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    return environment


def check_manifest() -> None:
    raw = MANIFEST.read_bytes()
    require(b"\r" not in raw, "manifest must have LF bytes")
    manifest = json.loads(raw.decode("utf-8"))
    require(manifest.get("schema") == "rime.paper37.development-manifest.v1",
            "manifest schema mismatch")
    require(manifest.get("paper_id") == "PAPER37"
            and manifest.get("status") == "DRAFT_PAPER_OWNED_CLOSURE"
            and manifest.get("release_identity_claimed") is False,
            "development/release boundary drift")
    require(manifest.get("validation_mode") == "LOCAL_CLOSURE_VERIFICATION",
            "validation status drift")
    require(manifest.get("digest_policy") == {
        "algorithm": "sha256", "scope": "exact_file_bytes",
        "path_resolution": "exact repository-relative path",
        "wildcards_allowed": False, "absolute_paths_allowed": False,
    }, "digest policy drift")
    require(manifest.get("evidence_boundary") ==
            "Bounded consistency controls and a partial Lean spine; manuscript owns the all-g proofs.",
            "evidence boundary drift")
    require(manifest.get("excluded_dependencies") == [
        "experiments/exploratory/", "experiments/synchronizing_automata/",
        "papers/unnumbered/", "published paper-owned experiment packages",
    ], "excluded dependency inventory drift")
    artifacts = manifest.get("artifacts")
    require(isinstance(artifacts, list), "missing artifact inventory")
    require([(row.get("role"), row.get("path")) for row in artifacts] == list(ARTIFACTS),
            "fixed closure inventory drift")
    for row in artifacts:
        relative = row["path"]
        path = Path(relative)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in relative,
                "nonportable artifact path")
        resolved = (ROOT / path).resolve()
        require(resolved.is_relative_to(ROOT), "artifact escapes repository")
        data = resolved.read_bytes()
        require(b"\r" not in data, f"non-LF artifact: {relative}")
        data.decode("utf-8")
        require(hashlib.sha256(data).hexdigest() == row.get("sha256"),
                f"digest drift: {relative}")

    # Prune caches at directory level rather than traversing .lake first.
    actual = set()
    for directory, subdirectories, filenames in os.walk(PACKAGE):
        subdirectories[:] = [
            name for name in subdirectories if name not in {"__pycache__", ".lake"}
        ]
        for name in filenames:
            path = Path(directory) / name
            if path != MANIFEST and path.suffix != ".pyc":
                actual.add(path.relative_to(ROOT).as_posix())
    expected = {path for _, path in ARTIFACTS if path.startswith("experiments/paper37/")}
    require(expected <= actual and actual - expected <= RELEASE_ONLY,
            f"package inventory drift: {sorted(actual ^ expected)}")


def run(name: str, *arguments: str) -> None:
    subprocess.run([sys.executable, "-B", str(PACKAGE / "validation" / name), *arguments],
                   cwd=ROOT, env=child_environment(), check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true",
                        help="verify closure/source/coverage only, explicitly skip finite replay")
    parser.add_argument("--lean", action="store_true",
                        help="also replay the pinned partial Lean project and axiom audit")
    args = parser.parse_args()
    if args.static and args.lean:
        parser.error("--static cannot be combined with --lean")
    check_manifest()
    run("validate_source.py")
    run("validate_lean_formalization.py")
    if args.static:
        run("validate_ordinary_lane_audit.py", "--static")
    else:
        run("test_contract.py")
        run("validate_ordinary_lane_audit.py")
    if args.lean:
        run("validate_lean_formalization.py", "--replay")
    detail = "finite replay skipped" if args.static else "finite replay included"
    print(f"PASS: Paper XXXVII LOCAL_CLOSURE_VERIFICATION ({detail}); no release identity")


if __name__ == "__main__":
    main()
