#!/usr/bin/env python3
"""Read-only paper-owned closure verification; raw bounded replay by default."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/paper38"
MANIFEST = PACKAGE / "development-manifest.json"
sys.path.insert(0, str(PACKAGE))
from audit_scope import ARTIFACTS  # noqa: E402

RELEASE_ONLY = {
    "experiments/paper38/release-environment.json",
    "experiments/paper38/release-manifest.json",
    "experiments/paper38/validation/validate_release.py",
    "experiments/paper38/results/paper38_public_package_v1.validation-receipt.json",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def child_environment():
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def snapshot():
    return {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in [*(path for _, path in ARTIFACTS),
                             "experiments/paper38/development-manifest.json"]}


def check_manifest():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(set(manifest) == {
        "schema", "paper_id", "status", "release_identity_claimed", "validation_mode",
        "formalization_claimed", "digest_policy", "proof_ownership", "excluded_dependencies", "artifacts",
    }, "manifest fields drift")
    require(manifest["schema"] == "rime.paper38.development-manifest.v1"
            and manifest["paper_id"] == "PAPER38"
            and manifest["status"] == "DRAFT_PAPER_OWNED_CLOSURE"
            and manifest["release_identity_claimed"] is False
            and manifest["formalization_claimed"] == "PARTIAL_ALGEBRAIC_SPINE"
            and manifest["validation_mode"] == "LOCAL_CLOSURE_VERIFICATION", "development boundary drift")
    require(manifest["digest_policy"] == {
        "algorithm": "sha256", "scope": "exact_file_bytes", "text_eol": "LF",
    }, "digest policy drift")
    require(manifest["proof_ownership"] ==
            "The manuscript owns the data-independent theorems; finite controls are supplementary.",
            "proof ownership drift")
    require(manifest["excluded_dependencies"] == [
        "experiments/exploratory/", "experiments/synchronizing_automata/",
        "papers/unnumbered/", "upstream experiment workspaces",
    ], "dependency exclusions drift")
    rows = manifest["artifacts"]
    require(isinstance(rows, list)
            and [(row.get("role"), row.get("path")) for row in rows] == list(ARTIFACTS),
            "closure inventory drift")
    for row in rows:
        require(set(row) == {"path", "role", "size", "sha256"}, "artifact fields drift")
        relative = row["path"]
        path = PurePosixPath(relative)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in relative
                and not any(token in relative for token in "*?[]"), "unsafe artifact path")
        resolved = (ROOT / relative).resolve()
        require(resolved.is_relative_to(ROOT), "artifact escapes workspace")
        data = resolved.read_bytes()
        require(b"\r" not in data and len(data) == row["size"], f"byte/EOL drift: {relative}")
        data.decode("utf-8")
        require(hashlib.sha256(data).hexdigest() == row["sha256"], f"digest drift: {relative}")
    expected = {path for _, path in ARTIFACTS if path.startswith("experiments/paper38/")}
    actual = set()
    for directory, subdirectories, filenames in os.walk(PACKAGE):
        subdirectories[:] = [name for name in subdirectories if name not in {"__pycache__", ".lake"}]
        for name in filenames:
            path = Path(directory) / name
            if path != MANIFEST and path.suffix != ".pyc":
                actual.add(path.relative_to(ROOT).as_posix())
    require(expected <= actual and actual - expected <= RELEASE_ONLY,
            f"package inventory drift: {sorted(actual ^ expected)}")
    require(b"\r" not in MANIFEST.read_bytes(), "non-LF manifest")


def check_upstream(compare_tag=False):
    record = json.loads((PACKAGE / "upstream-provenance.json").read_text(encoding="utf-8"))
    require(record == {
        "schema": "rime.paper38.upstream-provenance.v1", "consumer": "PAPER38",
        "status": "PUBLISHED_THEOREM_INPUT_BINDING", "owner": "PAPER37", "version": "1.0",
        "release_tag": "paper37-v1.0", "release_content_commit": "71723bdd67d92013ad285bc27994d18fe019fa6e",
        "doi": "10.5281/zenodo.23227579",
        "source": {"path": "papers/paper37/Paper XXXVII.md",
                   "sha256_at_tag": "5ef584777bb0453b6b76b0bd320fcf038eb98a07a77b66ff41a794d446bbc9af"},
        "imported_results": [
            "Lemma 3.1 and equation (3.2): uniform full ordinary-lane edge law",
            "Theorem 4.1: complete unbudgeted reachable injections",
            "Theorem 5.1: actual pre-collapse terminal placements",
            "Theorem 5.2: same-permutation survivor restriction",
        ], "finite_artifacts_imported": [], "head_fallback_allowed": False,
        "default_requires_upstream_workspace": False,
        "boundary": "The manuscript owns the inherited theorem; this record binds its published bytes. No Paper37 finite evidence is reused as Paper38 budget evidence.",
    }, "published theorem binding drift")
    if compare_tag:
        ref = "refs/tags/" + record["release_tag"]
        subprocess.run(["git", "show-ref", "--verify", ref], cwd=ROOT, check=True, capture_output=True)
        commit = subprocess.check_output(["git", "rev-parse", ref + "^{commit}"], cwd=ROOT).decode().strip()
        require(commit == record["release_content_commit"], "upstream tag target mismatch")
        raw = subprocess.check_output(["git", "show", ref + ":" + record["source"]["path"]], cwd=ROOT)
        require(hashlib.sha256(raw).hexdigest() == record["source"]["sha256_at_tag"],
                "published upstream source bytes mismatch")
        print("PASS: exact published XXXVII tag bytes compared; no HEAD fallback")


def run(script, *arguments):
    subprocess.run([sys.executable, "-B", str(PACKAGE / "validation" / script), *arguments],
                   cwd=ROOT, env=child_environment(), check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="explicitly skip mathematical finite replay")
    parser.add_argument("--lean", action="store_true", help="also compile and audit the pinned partial Lean spine")
    parser.add_argument("--compare-upstream-tag", action="store_true", help="also compare exact historical Git tag bytes")
    args = parser.parse_args()
    if args.static and args.lean:
        parser.error("--static cannot be combined with --lean")
    check_manifest()
    before = snapshot()
    check_upstream(args.compare_upstream_tag)
    run("validate_source.py")
    run("validate_lean_formalization.py")
    if args.static:
        run("validate_return_budget.py", "--static")
    else:
        run("test_contract.py")
        run("validate_return_budget.py")
    if args.lean:
        run("validate_lean_formalization.py", "--replay")
    check_manifest()
    require(snapshot() == before, "read-only verification mutated its closure")
    detail = "finite replay skipped" if args.static else "finite replay included"
    print(f"PASS: Paper XXXVIII LOCAL_CLOSURE_VERIFICATION ({detail}); no release identity")


if __name__ == "__main__":
    main()
