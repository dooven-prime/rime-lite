#!/usr/bin/env python3
"""Validate the acyclic Paper XXVIII public release closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper28"
MANIFEST = PACKAGE / "release-manifest.json"
PUBLIC_RECEIPT = (
    PACKAGE / "results" / "paper28_public_package_v1.validation-receipt.json"
)
DEPENDENCY_MANIFEST = PACKAGE / "dependency-manifest.json"
FINITE_RECEIPT = (
    PACKAGE / "validation" / "paper28_release_validation_v1.receipt.json"
)
LEAN_RECEIPT = (
    PACKAGE / "results" / "paper28_lean_formalization_v1.receipt.json"
)

MANIFEST_SCHEMA = "rime.paper28.release-manifest.v1"
RECEIPT_SCHEMA = "rime.paper28.public-package-receipt.v1"
CLOSURE_CLASSES = (
    "normative-manuscript-build",
    "theorem-facing-computational",
    "public-package-documentation",
)
RELEASE_IDENTITY_CLASSES = CLOSURE_CLASSES[:2]

DIRECT_ARTIFACTS = (
    ("manuscript", "normative-manuscript-build", "papers/paper28/Paper XXVIII.md"),
    ("reader-pdf", "normative-manuscript-build", "papers/paper28/paper28_arxiv.pdf"),
    ("bibliography", "normative-manuscript-build", "papers/paper28/references-v1.bib"),
    ("reader-figure", "normative-manuscript-build", "figures/paper28/fig1_finite_mechanism_structure.png"),
    ("figure-source", "normative-manuscript-build", "figures/paper28/fig1_finite_mechanism_structure.dot"),
    ("figure-renderer", "normative-manuscript-build", "figures/paper28/render.py"),
    ("finite-mirror-manifest", "theorem-facing-computational", "experiments/paper28/dependency-manifest.json"),
    ("finite-validation-receipt", "theorem-facing-computational", "experiments/paper28/validation/paper28_release_validation_v1.receipt.json"),
    ("lean-validation-receipt", "theorem-facing-computational", "experiments/paper28/results/paper28_lean_formalization_v1.receipt.json"),
    ("finite-mirror-validator", "theorem-facing-computational", "experiments/paper28/validation/validate_mirror.py"),
    ("finite-replay-validator", "theorem-facing-computational", "experiments/paper28/validation/validate_release.py"),
    ("public-package-validator", "theorem-facing-computational", "experiments/paper28/validation/validate_public_package.py"),
    ("evidence-readme", "public-package-documentation", "experiments/paper28/README.md"),
    ("mirror-staging-tool", "public-package-documentation", "experiments/paper28/validation/stage_mirror.py"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def direct_artifact_rows() -> list[dict]:
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
        "paper_id": "PAPER28",
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
        "artifacts": direct_artifact_rows(),
        "nested_closures": {
            "finite_mirror": {
                "manifest": "experiments/paper28/dependency-manifest.json",
                "validation_receipt": "experiments/paper28/validation/paper28_release_validation_v1.receipt.json",
            },
            "lean_formalization": {
                "validation_receipt": "experiments/paper28/results/paper28_lean_formalization_v1.receipt.json",
            },
        },
        "claim_boundary": [
            "fixed finite n=6 and n=7 carriers only",
            "no all-rank projectable-origin theorem",
            "no uniform mechanism selector",
            "no universal reset bound",
            "local closure verification is not independent mathematical validation",
        ],
        "release_candidate_date": "2026-09-27",
        "excluded_from_package_inventory": [
            "experiments/paper28/results/paper28_public_package_v1.validation-receipt.json",
            "experiments/paper28/lean/.lake/**",
            "**/__pycache__/**",
            "**/*.pyc",
        ],
        "closure_policy": {
            "classes": list(CLOSURE_CLASSES),
            "release_identity_classes": list(RELEASE_IDENTITY_CLASSES),
            "package_inventory_classes": list(CLOSURE_CLASSES),
            "note": (
                "The finite mirror and Lean receipt are nested source-addressed "
                "closures. Public documentation is integrity-checked but excluded "
                "from release identity."
            ),
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def dependency_rows(dependency_manifest: dict) -> list[dict]:
    rows = [
        {"path": item["mirror"], "sha256": item["sha256"]}
        for item in dependency_manifest["files"]
    ]
    rows.extend(
        {"path": item["mirror"], "sha256": item["sha256"]}
        for item in dependency_manifest["upstream_inputs"]
    )
    return deduplicate_rows(rows)


def lean_rows(lean_receipt: dict) -> list[dict]:
    return [
        {
            "path": item["artifact"]["uri"],
            "sha256": item["artifact"]["sha256"],
        }
        for item in lean_receipt["artifact_closure"]["ordered_artifacts"]
    ]


def deduplicate_rows(rows: list[dict]) -> list[dict]:
    by_path: dict[str, str] = {}
    for row in rows:
        existing = by_path.setdefault(row["path"], row["sha256"])
        if existing != row["sha256"]:
            raise ValueError(f"conflicting digest for {row['path']}")
    return [{"path": path, "sha256": digest} for path, digest in sorted(by_path.items())]


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


def load_nested(errors: list[str]) -> tuple[dict, dict, list[dict], list[dict]]:
    try:
        dependency_manifest = json.loads(DEPENDENCY_MANIFEST.read_text(encoding="utf-8"))
        lean_receipt = json.loads(LEAN_RECEIPT.read_text(encoding="utf-8"))
        finite_receipt = json.loads(FINITE_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"nested closure is unreadable: {error}")
        return {}, {}, [], []

    if dependency_manifest.get("schema") != "paper28-frozen-finite-mirror-v2":
        errors.append("finite mirror manifest schema mismatch")
    if lean_receipt.get("schema") != "rime.paper28.lean-formalization-receipt.v1":
        errors.append("Lean receipt schema mismatch")
    if lean_receipt.get("receipt_self_exclusion") is not True:
        errors.append("Lean receipt self-exclusion is not declared")
    validate_content_digest(lean_receipt, errors, "Lean receipt")
    if finite_receipt.get("manifest_sha256") != sha256(DEPENDENCY_MANIFEST):
        errors.append("finite receipt is not bound to the current dependency manifest")

    finite_rows = dependency_rows(dependency_manifest)
    formal_rows = lean_rows(lean_receipt)
    validate_rows(finite_rows, errors)
    validate_rows(formal_rows, errors)
    return dependency_manifest, lean_receipt, finite_rows, formal_rows


def validate_manifest(manifest: dict, errors: list[str]) -> None:
    if manifest != manifest_payload():
        errors.append("release manifest is stale or not canonical")
        return
    if manifest.get("schema") != MANIFEST_SCHEMA:
        errors.append("release manifest schema mismatch")
    if manifest.get("receipt_self_exclusion") is not True:
        errors.append("release receipt self-exclusion is not declared")


def package_files() -> set[str]:
    files = set()
    for path in PACKAGE.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(PACKAGE).parts
        if "__pycache__" in relative_parts or ".lake" in relative_parts:
            continue
        if path.suffix == ".pyc" or path.resolve() == PUBLIC_RECEIPT.resolve():
            continue
        files.add(path.relative_to(ROOT).as_posix())
    return files


def validate_package_inventory(
    manifest: dict,
    finite_rows: list[dict],
    formal_rows: list[dict],
    errors: list[str],
) -> None:
    covered = {
        row["path"] for row in manifest["artifacts"]
        if row["path"].startswith("experiments/paper28/")
    }
    covered.update(row["path"] for row in finite_rows)
    covered.update(row["path"] for row in formal_rows)
    covered.add(MANIFEST.relative_to(ROOT).as_posix())
    actual = package_files()
    missing = sorted(actual - covered)
    extra = sorted(covered - actual)
    if missing:
        errors.append(f"unmanifested package files: {missing}")
    if extra:
        errors.append(f"manifest package files absent from inventory: {extra}")


def run_validator(arguments: list[str], errors: list[str]) -> None:
    completed = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        errors.append(f"validator failed: {' '.join(arguments)}\n{detail}")
    elif completed.stdout.strip():
        print(completed.stdout.strip())


def direct_rows(manifest: dict, classes: tuple[str, ...] | None = None) -> list[dict]:
    return [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in manifest["artifacts"]
        if classes is None or row["closure_class"] in classes
    ]


def receipt_payload(
    manifest: dict,
    finite_rows: list[dict],
    formal_rows: list[dict],
    replay: dict,
) -> dict:
    theorem_direct = direct_rows(manifest, RELEASE_IDENTITY_CLASSES)
    release_rows = deduplicate_rows([*theorem_direct, *finite_rows, *formal_rows])
    package_rows = deduplicate_rows(
        [
            {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST)},
            *direct_rows(manifest),
            *finite_rows,
            *formal_rows,
        ]
    )
    payload = {
        "schema": RECEIPT_SCHEMA,
        "artifact_id": "PAPER28-V1-PUBLIC-PACKAGE-VALIDATED",
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "replay": replay,
        "manifest_binding": {
            "path": MANIFEST.relative_to(ROOT).as_posix(),
            "sha256": sha256(MANIFEST),
        },
        "nested_closures": {
            "finite_mirror": closure_block(finite_rows),
            "lean_formalization": closure_block(formal_rows),
        },
        "release_identity": closure_block(release_rows),
        "package_inventory": closure_block(package_rows),
        "nonclaims": [
            "local closure verification is not independent validation",
            "the release receipt does not certify an all-rank theorem",
            "the receipt does not occur in its own closure",
        ],
    }
    payload["content_sha256"] = canonical_digest(payload)
    return payload


def validate_receipt(
    manifest: dict,
    finite_rows: list[dict],
    formal_rows: list[dict],
    errors: list[str],
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
    replay = receipt.get("replay")
    if not isinstance(replay, dict):
        errors.append("public package receipt replay block is missing")
        return
    if receipt != receipt_payload(manifest, finite_rows, formal_rows, replay):
        errors.append("public package receipt is stale or not bound to current closure")


def main() -> None:
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
        print(f"ERROR: release manifest is unreadable: {error}", file=sys.stderr)
        raise SystemExit(1)

    validate_manifest(manifest, errors)
    _, _, finite_rows, formal_rows = load_nested(errors)
    if finite_rows and formal_rows:
        validate_package_inventory(manifest, finite_rows, formal_rows, errors)

    run_validator(
        ["experiments/paper28/validation/validate_mirror.py"], errors
    )
    if args.replay:
        run_validator(
            ["experiments/paper28/validation/validate_release.py"], errors
        )
        run_validator(
            [
                "experiments/paper28/validation/validate_lean_formalization.py",
                "--replay",
            ],
            errors,
        )
    else:
        run_validator(
            ["experiments/paper28/validation/validate_lean_formalization.py"],
            errors,
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

    replay = {
        "finite_mirror_verified": True,
        "finite_root_validators_replayed": args.replay,
        "lean_elaboration_replayed": args.replay,
    }
    if args.write_receipt:
        write_json(
            PUBLIC_RECEIPT,
            receipt_payload(manifest, finite_rows, formal_rows, replay),
        )
        print(f"wrote {PUBLIC_RECEIPT.relative_to(ROOT).as_posix()}")
    else:
        validate_receipt(manifest, finite_rows, formal_rows, errors)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            raise SystemExit(1)

    print("PASS Paper XXVIII public release closure")


if __name__ == "__main__":
    main()
