#!/usr/bin/env python3
"""Verify the acyclic Paper XXXIX public package and bounded replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper39"
MANIFEST = PACKAGE / "release-manifest.json"
DEVELOPMENT = PACKAGE / "development-manifest.json"
RECEIPT = PACKAGE / "results" / "paper39_public_package_v1.validation-receipt.json"

CLASSES = (
    "normative-manuscript-build",
    "theorem-facing-computational",
    "public-package-documentation",
)
IDENTITY_CLASSES = CLASSES[:2]
DIRECT_ARTIFACTS = (
    ("manuscript", CLASSES[0], "papers/paper39/Paper XXXIX.md"),
    ("reader-pdf", CLASSES[0], "papers/paper39/paper39_arxiv.pdf"),
    ("consumer-specification", CLASSES[0], "experiments/paper39/notes/ABSORPTION_CONSUMER_SPEC.md"),
    ("supplementary-proof", CLASSES[0], "experiments/paper39/notes/ABSORPTION_CONSUMER_ADEQUACY.md"),
    ("supplementary-correspondence", CLASSES[0], "experiments/paper39/notes/UFE_CORRESPONDENCE.md"),
    ("bibliography", CLASSES[0], "papers/paper39/references-v1.bib"),
    ("reader-build-entrypoint", CLASSES[0], "papers/tex/build.py"),
    ("reader-build-driver", CLASSES[0], "papers/tex/_build.py"),
    ("reader-build-postprocessor", CLASSES[0], "papers/tex/_postprocess.py"),
    ("reader-build-hrule-cleaner", CLASSES[0], "papers/tex/_clean_hrule.py"),
    ("development-manifest", CLASSES[1], "experiments/paper39/development-manifest.json"),
    ("release-environment", CLASSES[1], "experiments/paper39/release-environment.json"),
    ("release-validator", CLASSES[1], "experiments/paper39/validation/validate_release.py"),
    ("evidence-readme", CLASSES[2], "experiments/paper39/README.md"),
)
REPLAY = {
    "development_closure_verified": True,
    "manuscript_source_audited": True,
    "bounded_three_model_catalogue_replayed": True,
    "hostile_contract_tests_replayed": True,
    "lean_static_closure_checked": True,
    "lean_compiler_replayed": True,
    "external_zenodo_anchor_checked": False,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def resolve_relative(value: str) -> Path:
    if not value or "\\" in value or any(char in value for char in "*?[]"):
        raise ValueError(f"invalid release path: {value}")
    relative = Path(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError(f"noncanonical release path: {value}")
    resolved = (ROOT / relative).resolve()
    resolved.relative_to(ROOT.resolve())
    return resolved


def direct_rows() -> list[dict[str, str]]:
    rows = []
    for role, closure_class, relative in DIRECT_ARTIFACTS:
        path = resolve_relative(relative)
        if not path.is_file():
            raise ValueError(f"missing release artifact: {relative}")
        rows.append({
            "role": role,
            "closure_class": closure_class,
            "path": relative,
            "sha256": sha256(path),
        })
    return rows


def manifest_payload() -> dict:
    return {
        "schema": "rime.paper39.release-manifest.v1",
        "paper_id": "PAPER39",
        "release_version": "1.0",
        "intended_release_tag": "paper39-v1.0",
        "status": "RELEASE_CONTENT",
        "release_identity_claimed": True,
        "external_anchor_claimed": False,
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
        "artifacts": direct_rows(),
        "nested_closures": {
            "development_evidence": {
                "manifest": "experiments/paper39/development-manifest.json",
                "release_identity_claimed": False,
            },
        },
        "closure_policy": {
            "classes": list(CLASSES),
            "release_identity_classes": list(IDENTITY_CLASSES),
            "package_inventory_classes": list(CLASSES),
        },
        "claim_boundary": [
            "complete consumer adequacy and the UFE correspondence are manuscript proofs",
            "the 464-case three-model replay is a bounded consistency control, not an all-N proof",
            "the partial Lean spine does not prove Theorem 4.1 or Proposition 5.1",
            "no minimality, efficiency, external UFE implementation, or arbitrary ambient-state claim is established",
            "local closure verification is not independent mathematical validation",
        ],
    }


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def development_rows() -> list[dict[str, str]]:
    manifest = read_json(DEVELOPMENT)
    if manifest.get("schema") != "rime.paper39.development-manifest.v1":
        raise ValueError("development manifest schema mismatch")
    if manifest.get("release_identity_claimed") is not False:
        raise ValueError("development inventory claims release identity")
    rows = manifest.get("artifacts")
    if not isinstance(rows, list):
        raise ValueError("development artifact list missing")
    result = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise ValueError("invalid development artifact row")
        relative = row["path"]
        path = resolve_relative(relative)
        if not path.is_file() or row.get("sha256") != sha256(path):
            raise ValueError(f"development artifact drift: {relative}")
        result.append({"path": relative, "sha256": row["sha256"]})
    return result


def run_development_validator() -> None:
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    completed = subprocess.run(
        [sys.executable, "-B", "experiments/paper39/validation/validate_package.py", "--lean"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise ValueError(f"development replay failed:\n{completed.stdout}{completed.stderr}")
    print(completed.stdout.strip())


def ordered_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_path: dict[str, str] = {}
    for row in rows:
        relative, digest = row["path"], row["sha256"]
        previous = by_path.setdefault(relative, digest)
        if previous != digest:
            raise ValueError(f"conflicting digest for {relative}")
    return [{"path": path, "sha256": digest} for path, digest in sorted(by_path.items())]


def closure(rows: list[dict[str, str]]) -> dict:
    ordered = ordered_rows(rows)
    return {
        "artifact_count": len(ordered),
        "closure_digest": canonical_digest(ordered),
        "ordered_artifacts": ordered,
    }


def package_files() -> set[str]:
    files = set()
    for directory, dirnames, filenames in os.walk(PACKAGE):
        dirnames[:] = [name for name in dirnames if name not in {"__pycache__", ".lake"}]
        for filename in filenames:
            path = Path(directory) / filename
            if path.suffix == ".pyc" or path.resolve() == RECEIPT.resolve():
                continue
            files.add(path.relative_to(ROOT).as_posix())
    return files


def receipt_payload(manifest: dict, development: list[dict[str, str]]) -> dict:
    direct = [{"path": row["path"], "sha256": row["sha256"]}
              for row in manifest["artifacts"]]
    identity = [{"path": row["path"], "sha256": row["sha256"]}
                for row in manifest["artifacts"]
                if row["closure_class"] in IDENTITY_CLASSES]
    manifest_row = {"path": MANIFEST.relative_to(ROOT).as_posix(),
                    "sha256": sha256(MANIFEST)}
    payload = {
        "schema": "rime.paper39.public-package-receipt.v1",
        "artifact_id": "PAPER39-V1-PUBLIC-PACKAGE-VALIDATED",
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "replay": dict(REPLAY),
        "manifest_binding": manifest_row,
        "nested_closures": {"development_evidence": closure(development)},
        "release_identity": closure(identity),
        "package_inventory": closure([manifest_row, *direct, *development]),
        "nonclaims": [
            "receipt validation is local closure verification, not independent validation",
            "bounded replay and the partial Lean spine do not prove the all-N theorems",
            "the receipt does not depend on itself",
            "Zenodo deposit integrity is checked separately from this local receipt",
        ],
    }
    payload["content_sha256"] = canonical_digest(payload)
    return payload


def validate_inventory(manifest: dict, development: list[dict[str, str]]) -> None:
    expected = {
        row["path"] for row in manifest["artifacts"]
        if row["path"].startswith("experiments/paper39/")
    }
    expected.update(row["path"] for row in development
                    if row["path"].startswith("experiments/paper39/"))
    expected.add(MANIFEST.relative_to(ROOT).as_posix())
    actual = package_files()
    if actual != expected:
        raise ValueError(f"package inventory drift: {sorted(actual ^ expected)}")
    if RECEIPT.relative_to(ROOT).as_posix() in expected:
        raise ValueError("receipt appears in its own closure")
    expected_paper = {
        row["path"] for row in manifest["artifacts"]
        if row["path"].startswith("papers/paper39/")
    }
    actual_paper = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "papers" / "paper39").iterdir()
        if path.is_file()
    }
    if actual_paper != expected_paper:
        raise ValueError(f"paper directory inventory drift: {sorted(actual_paper ^ expected_paper)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    try:
        run_development_validator()
        development = development_rows()
        if args.write_manifest:
            write_json(MANIFEST, manifest_payload())
        manifest = read_json(MANIFEST)
        if manifest != manifest_payload():
            raise ValueError("release manifest is stale or noncanonical")
        validate_inventory(manifest, development)
        if args.write_manifest and not args.write_receipt:
            print("WROTE Paper XXXIX manifest; release receipt still required")
            return 0
        if args.write_receipt:
            write_json(RECEIPT, receipt_payload(manifest, development))
        receipt = read_json(RECEIPT)
        if receipt.get("replay") != REPLAY or receipt != receipt_payload(manifest, development):
            raise ValueError("release receipt is stale or noncanonical")
        print(f"PASS Paper XXXIX public package: {len(manifest['artifacts'])} direct, "
              f"{len(development)} nested artifacts")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL Paper XXXIX public package: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
