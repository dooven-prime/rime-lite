#!/usr/bin/env python3
"""Validate the acyclic Paper XXXII public release closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper32"
MANIFEST = PACKAGE / "release-manifest.json"
DEVELOPMENT_MANIFEST = PACKAGE / "development-manifest.json"
PUBLIC_RECEIPT = (
    PACKAGE / "results" / "paper32_public_package_v1.validation-receipt.json"
)

MANIFEST_SCHEMA = "rime.paper32.release-manifest.v1"
RECEIPT_SCHEMA = "rime.paper32.public-package-receipt.v1"
CANONICAL_RELEASE_REPLAY = {
    "development_closure_verified": True,
    "source_audit_replayed": True,
    "finite_bounded_replay": True,
}
CLOSURE_CLASSES = (
    "normative-manuscript-build",
    "theorem-facing-computational",
    "public-package-documentation",
)
RELEASE_IDENTITY_CLASSES = CLOSURE_CLASSES[:2]

DIRECT_ARTIFACTS = (
    ("manuscript", "normative-manuscript-build", "papers/paper32/Paper XXXII.md"),
    ("reader-pdf", "normative-manuscript-build", "papers/paper32/paper32_arxiv.pdf"),
    ("bibliography", "normative-manuscript-build", "papers/paper32/references-v1.bib"),
    (
        "development-manifest",
        "theorem-facing-computational",
        "experiments/paper32/development-manifest.json",
    ),
    (
        "release-environment",
        "theorem-facing-computational",
        "experiments/paper32/release-environment.json",
    ),
    (
        "public-package-validator",
        "theorem-facing-computational",
        "experiments/paper32/validation/validate_public_package.py",
    ),
    (
        "evidence-readme",
        "public-package-documentation",
        "experiments/paper32/README.md",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def resolve_relative(path_text: str) -> Path:
    if "\\" in path_text:
        raise ValueError(f"release path is not POSIX-normalized: {path_text}")
    path = Path(path_text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"non-canonical release path: {path_text}")
    if any(token in path_text for token in "*?[]"):
        raise ValueError(f"wildcard release path: {path_text}")
    resolved = (ROOT / path).resolve()
    resolved.relative_to(ROOT.resolve())
    return resolved


def artifact_rows() -> list[dict]:
    rows = []
    for role, closure_class, path_text in DIRECT_ARTIFACTS:
        path = resolve_relative(path_text)
        if not path.is_file():
            raise FileNotFoundError(path_text)
        rows.append(
            {
                "role": role,
                "closure_class": closure_class,
                "path": path_text,
                "sha256": sha256(path),
            }
        )
    return rows


def manifest_payload() -> dict:
    return {
        "schema": MANIFEST_SCHEMA,
        "paper_id": "PAPER32",
        "release_version": "1.0",
        "status": "RELEASE_CANDIDATE",
        "release_identity_claimed": False,
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "digest_policy": {
            "algorithm": "sha256",
            "scope": "exact_file_bytes",
            "path_resolution": "exact repository-relative path",
            "wildcards_allowed": False,
            "absolute_paths_allowed": False,
            "current_head_fallback_allowed": False,
        },
        "artifacts": artifact_rows(),
        "nested_closures": {
            "development_evidence": {
                "manifest": "experiments/paper32/development-manifest.json",
                "release_identity_claimed": False,
            }
        },
        "claim_boundary": [
            "finite replay is not an all-n proof",
            "arbitrary-permutation replay is a bounded one-lane control, not an all-n proof",
            "the lane-wise dihedral and single-lane permutation classifications are manuscript theorems",
            "the full multi-lane promotion classification remains open",
            "raw Safe-Hit does not imply survivor incidence or typed projectability",
            "local closure verification is not independent mathematical validation",
        ],
        "release_candidate_date": "2026-09-30",
        "excluded_from_package_inventory": [
            "experiments/paper32/results/paper32_public_package_v1.validation-receipt.json",
            "**/__pycache__/**",
            "**/*.pyc",
        ],
        "closure_policy": {
            "classes": list(CLOSURE_CLASSES),
            "release_identity_classes": list(RELEASE_IDENTITY_CLASSES),
            "package_inventory_classes": list(CLOSURE_CLASSES),
            "note": (
                "The paper-owned development manifest is a nested exact-byte "
                "evidence closure. Public documentation is integrity-checked "
                "but excluded from release identity."
            ),
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def development_rows(manifest: dict) -> list[dict]:
    return [
        {"path": item["path"], "sha256": item["sha256"]}
        for item in manifest["artifacts"]
    ]


def deduplicate_rows(rows: list[dict]) -> list[dict]:
    by_path: dict[str, str] = {}
    for row in rows:
        existing = by_path.setdefault(row["path"], row["sha256"])
        if existing != row["sha256"]:
            raise ValueError(f"conflicting digest for {row['path']}")
    return [
        {"path": path, "sha256": digest}
        for path, digest in sorted(by_path.items())
    ]


def closure_block(rows: list[dict]) -> dict:
    ordered = deduplicate_rows(rows)
    return {
        "artifact_count": len(ordered),
        "closure_digest": canonical_digest(ordered),
        "ordered_artifacts": ordered,
    }


def validate_rows(rows: list[dict], errors: list[str]) -> None:
    for row in rows:
        try:
            path = resolve_relative(row["path"])
        except (OSError, ValueError) as error:
            errors.append(str(error))
            continue
        if not path.is_file():
            errors.append(f"closure artifact missing: {row['path']}")
        elif sha256(path) != row["sha256"]:
            errors.append(f"closure artifact digest mismatch: {row['path']}")


def validate_content_digest(payload: dict, errors: list[str], label: str) -> None:
    candidate = dict(payload)
    observed = candidate.pop("content_sha256", None)
    if observed != canonical_digest(candidate):
        errors.append(f"{label} content digest mismatch")


def load_development(errors: list[str]) -> tuple[dict, list[dict]]:
    try:
        manifest = json.loads(DEVELOPMENT_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"development closure is unreadable: {error}")
        return {}, []
    if manifest.get("schema") != "rime.paper32.development-manifest.v1":
        errors.append("development manifest schema mismatch")
    if manifest.get("release_identity_claimed") is not False:
        errors.append("development manifest must not claim a release identity")
    rows = development_rows(manifest)
    validate_rows(rows, errors)
    return manifest, rows


def validate_manifest(manifest: dict, errors: list[str]) -> None:
    if manifest != manifest_payload():
        errors.append("release manifest is stale or not canonical")
        return
    if manifest.get("schema") != MANIFEST_SCHEMA:
        errors.append("release manifest schema mismatch")
    if manifest.get("receipt_self_exclusion") is not True:
        errors.append("release receipt self-exclusion is not declared")


def package_files() -> set[str]:
    files: set[str] = set()
    for directory, dirnames, filenames in os.walk(PACKAGE):
        dirnames[:] = [name for name in dirnames if name != "__pycache__"]
        for filename in filenames:
            path = Path(directory) / filename
            if path.suffix == ".pyc" or path.resolve() == PUBLIC_RECEIPT.resolve():
                continue
            files.add(path.relative_to(ROOT).as_posix())
    return files


def validate_package_inventory(
    manifest: dict, development: list[dict], errors: list[str]
) -> None:
    covered = {
        row["path"]
        for row in manifest["artifacts"]
        if row["path"].startswith("experiments/paper32/")
    }
    covered.update(
        row["path"]
        for row in development
        if row["path"].startswith("experiments/paper32/")
    )
    covered.add(MANIFEST.relative_to(ROOT).as_posix())
    actual = package_files()
    unmanifested = sorted(actual - covered)
    absent = sorted(covered - actual)
    if unmanifested:
        errors.append(f"unmanifested package files: {unmanifested}")
    if absent:
        errors.append(f"manifest package files absent from inventory: {absent}")


def run_development_validator(replay: bool, errors: list[str]) -> None:
    command = [
        sys.executable,
        "experiments/paper32/validation/validate_package.py",
    ]
    if replay:
        command.append("--replay")
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        errors.append(f"development validator failed:\n{detail}")
    elif completed.stdout.strip():
        print(completed.stdout.strip())


def direct_rows(manifest: dict, classes: tuple[str, ...] | None = None) -> list[dict]:
    return [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in manifest["artifacts"]
        if classes is None or row["closure_class"] in classes
    ]


def receipt_payload(manifest: dict, development: list[dict]) -> dict:
    release_rows = direct_rows(manifest, RELEASE_IDENTITY_CLASSES)
    package_rows = deduplicate_rows(
        [
            {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST)},
            *direct_rows(manifest),
            *development,
        ]
    )
    payload = {
        "schema": RECEIPT_SCHEMA,
        "artifact_id": "PAPER32-V1-PUBLIC-PACKAGE-VALIDATED",
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "replay": dict(CANONICAL_RELEASE_REPLAY),
        "manifest_binding": {
            "path": MANIFEST.relative_to(ROOT).as_posix(),
            "sha256": sha256(MANIFEST),
        },
        "nested_closures": {
            "development_evidence": closure_block(development),
        },
        "release_identity": closure_block(release_rows),
        "package_inventory": closure_block(package_rows),
        "nonclaims": [
            "local closure verification is not independent validation",
            "finite replay is not an all-n proof",
            "the package contains no Paper XXXII Lean formalization",
            "the receipt does not occur in its own closure",
        ],
    }
    payload["content_sha256"] = canonical_digest(payload)
    return payload


def validate_receipt(
    manifest: dict, development: list[dict], errors: list[str]
) -> None:
    if not PUBLIC_RECEIPT.is_file():
        errors.append("public package receipt is missing")
        return
    try:
        receipt = json.loads(PUBLIC_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"public package receipt is unreadable: {error}")
        return
    validate_content_digest(receipt, errors, "public package receipt")
    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append("public package receipt schema mismatch")
        return
    if receipt.get("replay") != CANONICAL_RELEASE_REPLAY:
        errors.append("public package receipt replay block is not canonical")
        return
    if receipt != receipt_payload(manifest, development):
        errors.append("public package receipt is stale or not bound to current closure")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.write_receipt and not args.replay:
        parser.error("--write-receipt requires --replay")

    if args.write_manifest:
        write_json(MANIFEST, manifest_payload())
        print(f"wrote {MANIFEST.relative_to(ROOT).as_posix()}")

    errors: list[str] = []
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL Paper XXXII public package: {error}")
        return 1

    validate_manifest(manifest, errors)
    _, development = load_development(errors)
    if development:
        validate_package_inventory(manifest, development, errors)
    run_development_validator(args.replay, errors)

    if args.write_receipt and not errors:
        write_json(PUBLIC_RECEIPT, receipt_payload(manifest, development))
        print(f"wrote {PUBLIC_RECEIPT.relative_to(ROOT).as_posix()}")

    validate_receipt(manifest, development, errors)
    if errors:
        print("FAIL Paper XXXII public package")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "PASS Paper XXXII public package: "
        f"{len(manifest['artifacts'])} direct artifacts, "
        f"{len(development)} nested artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
