#!/usr/bin/env python3
"""Verify Paper XVIII release bytes and immutable source bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/paper18"
MANIFEST = PACKAGE / "release-manifest.json"
RECEIPT = PACKAGE / "results/paper18_local_release.validation-receipt.json"
TAG = "paper18-v1.0"
HISTORICAL_COMMIT = "4d7595936e9fb2271a870ec560e77c021a64fdb9"
HISTORICAL_PREFIX = "papers/unnumbered/from_support_to_state/"
WITNESS_PATH = HISTORICAL_PREFIX + "witness/malecns_two_source_witness_v1.0.zip"
WITNESS_SHA256 = "6ff8175d62b893f2f71c357ae51419727edc58aed160365fe8fb86a52feea2c9"
DATASET_SHA256 = "6bf11532ed405ab5bc0a74b78ed1360931454124da954c35e74cc72c8e016f3d"
DATASET_DOI = "10.5281/zenodo.23555888"
CLASSES = ("normative-manuscript-build", "theorem-facing-evidence", "public-package-documentation")
DIRECT_ARTIFACTS = (
    ("manuscript", CLASSES[0], "papers/paper18/Paper XVIII.md"),
    ("technical-notes", CLASSES[0], "papers/paper18/TECHNICAL_NOTES.md"),
    ("bibliography", CLASSES[0], "papers/paper18/references-v1.bib"),
    ("reader-pdf", CLASSES[0], "papers/paper18/paper18_arxiv.pdf"),
    ("technical-notes-pdf", CLASSES[0], "papers/paper18/paper18_technical_notes.pdf"),
    ("report-readme", CLASSES[2], "papers/paper18/README.md"),
    ("evidence-index", CLASSES[2], "experiments/paper18/README.md"),
    ("release-validator", CLASSES[1], "experiments/paper18/validation/validate_release.py"),
    ("release-tests", CLASSES[1], "experiments/paper18/validation/test_release.py"),
    ("reader-build-entrypoint", CLASSES[0], "papers/tex/build.py"),
    ("reader-build-driver", CLASSES[0], "papers/tex/_build.py"),
    ("reader-build-postprocessor", CLASSES[0], "papers/tex/_postprocess.py"),
    ("reader-build-hrule-cleaner", CLASSES[0], "papers/tex/_clean_hrule.py"),
    ("figure-1-png", CLASSES[0], "figures/paper18/profile_multiplicity.png"),
    ("figure-1-svg", CLASSES[0], "figures/paper18/profile_multiplicity.svg"),
    ("figure-1-pdf", CLASSES[0], "figures/paper18/profile_multiplicity.pdf"),
    ("figure-2-png", CLASSES[0], "figures/paper18/coordinate_profile_splits.png"),
    ("figure-2-svg", CLASSES[0], "figures/paper18/coordinate_profile_splits.svg"),
    ("figure-2-pdf", CLASSES[0], "figures/paper18/coordinate_profile_splits.pdf"),
)
REQUIRED_HISTORICAL = frozenset({
    HISTORICAL_PREFIX + "evidence/profile_heterogeneity_census.v1.json",
    HISTORICAL_PREFIX + "evidence/profile_heterogeneity_census.py",
    HISTORICAL_PREFIX + "evidence/test_profile_heterogeneity.py",
    HISTORICAL_PREFIX + "evidence/somaside_exact_witness.v1.json",
    HISTORICAL_PREFIX + "evidence/somaside_exact_witness.py",
    HISTORICAL_PREFIX + "evidence/test_somaside_exact_witness.py",
    HISTORICAL_PREFIX + "dataset/manifest.json",
    HISTORICAL_PREFIX + "dataset/verify_dataset.py",
    HISTORICAL_PREFIX + "dataset/SHA256SUMS.txt",
    HISTORICAL_PREFIX + "witness/manifest.json",
    HISTORICAL_PREFIX + "witness/verify_witness.py",
    HISTORICAL_PREFIX + "witness/SHA256SUMS_witness.txt",
    WITNESS_PATH,
})
REPLAY = {
    "historical_git_objects_and_checkout_bytes_verified": True,
    "focused_census_and_witness_controls_replayed": True,
    "compact_witness_zip_replayed": True,
    "dataset_carrier_replayed": False,
    "reader_pdfs_rebuilt": False,
    "external_zenodo_bytes_checked": False,
    "paper18_publication_identity_claimed": False,
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_row(path: str) -> dict[str, object]:
    content = checked_path(path).read_bytes()
    return {"path": path, "sha256": digest(content), "size": len(content)}


def checked_path(value: str) -> Path:
    if not value or "\\" in value or any(char in value for char in "*?[]:"):
        raise ValueError(f"invalid path: {value}")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"noncanonical path: {value}")
    resolved = (ROOT / value).resolve()
    resolved.relative_to(ROOT.resolve())
    return resolved


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace')}")
    return result.stdout


def historical_rows() -> list[dict[str, object]]:
    if git_bytes("rev-parse", HISTORICAL_COMMIT).strip().decode() != HISTORICAL_COMMIT:
        raise ValueError("historical commit is unavailable")
    if git_bytes("cat-file", "-t", HISTORICAL_COMMIT).strip() != b"commit":
        raise ValueError("historical anchor is not a commit")
    paths = git_bytes("ls-tree", "-r", "--name-only", HISTORICAL_COMMIT, HISTORICAL_PREFIX).decode().splitlines()
    if len(paths) != 33 or len(set(paths)) != 33 or not REQUIRED_HISTORICAL.issubset(paths):
        raise ValueError("historical JCN source inventory drift")
    tracked = set(git_bytes("ls-files", "--", HISTORICAL_PREFIX).decode().splitlines())
    if tracked != set(paths):
        raise ValueError("historical JCN checkout inventory drift")
    rows = []
    for path in paths:
        original = git_bytes("show", f"{HISTORICAL_COMMIT}:{path}")
        if checked_path(path).read_bytes() != original:
            raise ValueError(f"historical checkout byte drift: {path}")
        rows.append({"path": path, "sha256": digest(original), "size": len(original)})
    if next(row for row in rows if row["path"] == WITNESS_PATH)["sha256"] != WITNESS_SHA256:
        raise ValueError("compact witness archive digest drift")
    sums = checked_path(HISTORICAL_PREFIX + "dataset/SHA256SUMS.txt").read_text(encoding="utf-8")
    if f"{DATASET_SHA256}  malecns_predictive_refinement_v1.0.zip" not in sums.splitlines():
        raise ValueError("deposited Dataset digest binding drift")
    return rows


def validate_claim_values() -> None:
    census = read_json(checked_path(HISTORICAL_PREFIX + "evidence/profile_heterogeneity_census.v1.json"))
    soma = census["partitions"]["somaSide"]
    sectors = {row["source_sector"]: row for row in soma["by_source_sector"]}
    if (soma["eligible_sources"], soma["profile_classes_with_source_sector_retained"]) != (163439, 90148):
        raise ValueError("Paper XVIII headline census mismatch")
    if set(sectors) != {"<missing>", "L", "M", "R"}:
        raise ValueError("somaSide sector set mismatch")
    if (sectors["R"]["eligible_sources"], sectors["R"]["exact_profile_classes"]) != (72750, 36896):
        raise ValueError("largest somaSide fiber claim mismatch")
    separation = soma["coordinate_separation"]
    if (separation["status"], separation["minimum_coordinate_count"],
            separation["minimum_coordinate_sets"]) != (
                "EXACT_BY_EXHAUSTIVE_SUBSETS", 3, [["<missing>", "L", "R"]]):
        raise ValueError("somaSide coordinate separation mismatch")
    witness = read_json(checked_path(HISTORICAL_PREFIX + "evidence/somaside_exact_witness.v1.json"))
    if (witness["selection"]["body_ids"], witness["selection"]["coordinate"],
            witness["derived"]["cross_product"], witness["derived"]["exact_difference"]) != (
                [10002, 10006], "M", -36355, [-661, 84521472]):
        raise ValueError("two-source exact witness claim mismatch")


def direct_rows() -> list[dict[str, object]]:
    rows = []
    for role, closure_class, path in DIRECT_ARTIFACTS:
        rows.append({"role": role, "closure_class": closure_class, **file_row(path)})
    return rows


def manifest_payload() -> dict:
    return {
        "schema": "rime.paper18.release-manifest.v1",
        "paper_id": "PAPER18",
        "release_version": "1.0",
        "intended_release_tag": TAG,
        "status": "RELEASE_CONTENT",
        "release_identity_claimed": True,
        "external_anchor_claimed": False,
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "digest_policy": {
            "algorithm": "sha256", "scope": "exact_file_bytes",
            "historical_commit": HISTORICAL_COMMIT,
            "current_head_fallback_allowed": False,
        },
        "artifacts": direct_rows(),
        "historical_evidence": {
            "commit": HISTORICAL_COMMIT,
            "source_path": HISTORICAL_PREFIX.rstrip("/"),
            "artifacts": historical_rows(),
        },
        "external_packages": {
            "census_dataset": {
                "doi": DATASET_DOI,
                "archive": "malecns_predictive_refinement_v1.0.zip",
                "sha256": DATASET_SHA256,
                "remote_bytes_checked": False,
            },
            "compact_witness": {
                "path": WITNESS_PATH,
                "sha256": WITNESS_SHA256,
                "separate_doi_claimed": False,
            },
        },
        "claim_boundary": [
            "the unit-source criterion specializes classical block-row-sum reasoning",
            "the exact census uses a derived carrier; this local gate does not regenerate original connectome inputs",
            "the Dataset DOI does not identify the compact witness ZIP",
            "historical byte replay and local controls do not establish independent scientific validation",
        ],
    }


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def validate_manifest(manifest: dict) -> None:
    if manifest != manifest_payload():
        raise ValueError("release manifest is stale or noncanonical")


def validate_tag(manifest: dict) -> None:
    ref = f"refs/tags/{TAG}"
    git_bytes("show-ref", "--verify", ref)
    if git_bytes("cat-file", "-t", ref).strip() != b"tag":
        raise ValueError("release tag is not annotated")
    commit = git_bytes("rev-parse", f"{ref}^{{commit}}").strip().decode()
    git_bytes("merge-base", "--is-ancestor", commit, "HEAD")
    for row in [
        file_row(MANIFEST.relative_to(ROOT).as_posix()),
        file_row(RECEIPT.relative_to(ROOT).as_posix()),
        *manifest["artifacts"],
        *manifest["historical_evidence"]["artifacts"],
    ]:
        content = git_bytes("show", f"{commit}:{row['path']}")
        if digest(content) != row["sha256"] or len(content) != row["size"]:
            raise ValueError(f"tagged release byte drift: {row['path']}")


def inventory() -> None:
    direct = {path for _, _, path in DIRECT_ARTIFACTS}
    for prefix in ("papers/paper18/", "figures/paper18/", "experiments/paper18/"):
        actual = set()
        for parent, dirs, files in os.walk(ROOT / prefix):
            dirs[:] = [name for name in dirs if name != "__pycache__"]
            for name in files:
                path = Path(parent) / name
                if path.suffix != ".pyc" and path.resolve() != RECEIPT.resolve():
                    actual.add(path.relative_to(ROOT).as_posix())
        expected = {path for path in direct if path.startswith(prefix)}
        if prefix == "experiments/paper18/":
            expected.add(MANIFEST.relative_to(ROOT).as_posix())
        if actual != expected:
            raise ValueError(f"Paper XVIII package inventory drift: {sorted(actual ^ expected)}")


def run_controls() -> None:
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    for pattern in ("test_profile_heterogeneity.py", "test_somaside_exact_witness.py"):
        result = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s",
             HISTORICAL_PREFIX + "evidence", "-p", pattern],
            cwd=ROOT, env=env, capture_output=True, text=True, check=False, timeout=180,
        )
        if result.returncode:
            raise ValueError(f"focused control failed ({pattern}):\n{result.stdout}{result.stderr}")
    result = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s",
         "experiments/paper18/validation", "-p", "test_release.py"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False, timeout=180,
    )
    if result.returncode:
        raise ValueError(f"release boundary control failed:\n{result.stdout}{result.stderr}")
    with tempfile.TemporaryDirectory(prefix="paper18-witness-") as temporary:
        with zipfile.ZipFile(checked_path(WITNESS_PATH)) as archive:
            for item in archive.infolist():
                path = PurePosixPath(item.filename)
                if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
                    raise ValueError("unsafe compact witness archive path")
            archive.extractall(temporary)
        witness = Path(temporary) / "malecns_two_source_witness_v1.0"
        result = subprocess.run(
            [sys.executable, "-B", "verify_witness.py"], cwd=witness, env=env,
            capture_output=True, text=True, check=False, timeout=180,
        )
        if result.returncode or "COMPACT_WITNESS_PASS" not in result.stdout:
            raise ValueError(f"compact witness replay failed:\n{result.stdout}{result.stderr}")


def closure(rows: list[dict]) -> dict:
    ordered = sorted(({key: row[key] for key in ("path", "sha256", "size")} for row in rows),
                     key=lambda row: row["path"])
    if len({row["path"] for row in ordered}) != len(ordered):
        raise ValueError("duplicate closure path")
    serialized = json.dumps(ordered, sort_keys=True, separators=(",", ":")).encode()
    return {"artifact_count": len(ordered), "closure_sha256": digest(serialized)}


def receipt_payload(manifest: dict) -> dict:
    manifest_row = file_row(MANIFEST.relative_to(ROOT).as_posix())
    direct = manifest["artifacts"]
    history = manifest["historical_evidence"]["artifacts"]
    payload = {
        "schema": "rime.paper18.local-release-receipt.v1",
        "status": "PASS_LOCAL_RELEASE_CONTENT",
        "release_identity_claimed": True,
        "receipt_self_exclusion": True,
        "replay": dict(REPLAY),
        "manifest_binding": manifest_row,
        "historical_evidence": closure(history),
        "release_content": closure([manifest_row, *direct, *history]),
        "nonclaims": [
            "this receipt does not validate a Paper XVIII DOI; the tag is checked separately",
            "the Dataset archive is digest-declared but not downloaded or source-replayed by this gate",
            "the compact witness has no independent DOI",
        ],
    }
    payload["content_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write-manifest", action="store_true")
    group.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--check-tag", action="store_true")
    args = parser.parse_args()
    if args.check_tag and (args.write_manifest or args.write_receipt):
        parser.error("--check-tag is read-only")
    try:
        if args.write_manifest:
            write_json(MANIFEST, manifest_payload())
        manifest = read_json(MANIFEST)
        validate_manifest(manifest)
        validate_claim_values()
        inventory()
        run_controls()
        if args.write_manifest:
            print("WROTE Paper XVIII release manifest; receipt still required")
            return 0
        if args.write_receipt:
            write_json(RECEIPT, receipt_payload(manifest))
        if read_json(RECEIPT) != receipt_payload(manifest):
            raise ValueError("local release receipt is stale or noncanonical")
        if args.check_tag:
            validate_tag(manifest)
        print(f"PASS Paper XVIII release content: {len(manifest['artifacts'])} direct, "
              f"{len(manifest['historical_evidence']['artifacts'])} historical files; "
              f"focused and compact-witness replay PASS; tag checked: {args.check_tag}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, zipfile.BadZipFile) as error:
        print(f"FAIL Paper XVIII release content: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
