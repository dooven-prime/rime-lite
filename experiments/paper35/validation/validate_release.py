#!/usr/bin/env python3
"""Verify the acyclic Paper XXXV content package and its declared replays."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper35"
MANIFEST = PACKAGE / "release-manifest.json"
DEVELOPMENT = PACKAGE / "development-manifest.json"
RECEIPT = PACKAGE / "results" / "paper35_public_package_v1.validation-receipt.json"
GATE = "tools/release/paper35-inheritance-gate.v1.json"

CLASSES = (
    "normative-manuscript-build",
    "theorem-facing-computational",
    "public-package-documentation",
)
IDENTITY_CLASSES = CLASSES[:2]
DIRECT_ARTIFACTS = (
    ("manuscript", CLASSES[0], "papers/paper35/Paper XXXV.md"),
    ("reader-pdf", CLASSES[0], "papers/paper35/paper35_arxiv.pdf"),
    ("bibliography", CLASSES[0], "papers/paper35/references-v1.bib"),
    ("development-manifest", CLASSES[1], "experiments/paper35/development-manifest.json"),
    ("release-environment", CLASSES[1], "experiments/paper35/release-environment.json"),
    ("release-validator", CLASSES[1], "experiments/paper35/validation/validate_release.py"),
    ("inheritance-gate", CLASSES[1], GATE),
    ("inheritance-validator", CLASSES[1], "tools/release/verify_inheritance_gate.py"),
    ("evidence-readme", CLASSES[2], "experiments/paper35/README.md"),
)
REPLAY = {
    "development_closure_verified": True,
    "manuscript_source_audited": True,
    "finite_order_phase_control_replayed": True,
    "lean_spine_compiled": True,
    "paper32_paper34_inheritance_replayed": True,
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
        "schema": "rime.paper35.release-manifest.v1",
        "paper_id": "PAPER35",
        "release_version": "1.0",
        "intended_release_tag": "paper35-v1.0",
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
                "manifest": "experiments/paper35/development-manifest.json",
                "release_identity_claimed": False,
            },
        },
        "closure_policy": {
            "classes": list(CLASSES),
            "release_identity_classes": list(IDENTITY_CLASSES),
            "package_inventory_classes": list(CLASSES),
        },
        "claim_boundary": [
            "the all-n one-lane theorem is proved in the manuscript",
            "the six-point replay is a bounded consistency control, not an all-n proof",
            "Lean formalizes a partial theorem spine, not the full guarded geometry",
            "the theorem note is supplementary provenance, not a second theorem authority",
            "upstream inheritance replay does not enlarge owner theorem scopes",
            "raw incidence gives no typed transfer or recursive-return authority",
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
    if manifest.get("schema") != "rime.paper35.development-manifest.v1":
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


def run_command(arguments: list[str], label: str, markers: tuple[str, ...]) -> None:
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-B", *arguments],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    if completed.returncode or any(marker not in output for marker in markers):
        raise ValueError(f"{label} failed or omitted a required result:\n{output}")
    print(output.strip())


def run_replays() -> None:
    run_command(
        ["experiments/paper35/validation/validate_package.py", "--replay", "--replay-lean"],
        "paper-owned replay",
        ("PASS: Paper XXXV paper-owned package",),
    )
    run_command(
        ["tools/release/verify_inheritance_gate.py", GATE, "--timeout", "2400"],
        "inheritance replay",
        ("PASS PAPER32 inheritance replay", "PASS PAPER34 inheritance replay",
         "PASS PAPER35 pre-inheritance gate"),
    )


def closure(rows: list[dict[str, str]]) -> dict:
    by_path: dict[str, str] = {}
    for row in rows:
        relative, digest = row["path"], row["sha256"]
        previous = by_path.setdefault(relative, digest)
        if previous != digest:
            raise ValueError(f"conflicting digest for {relative}")
    ordered = [{"path": path, "sha256": digest} for path, digest in sorted(by_path.items())]
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


def validate_inventory(manifest: dict, development: list[dict[str, str]]) -> None:
    expected = {row["path"] for row in manifest["artifacts"]
                if row["path"].startswith("experiments/paper35/")}
    expected.update(row["path"] for row in development
                    if row["path"].startswith("experiments/paper35/"))
    expected.add(MANIFEST.relative_to(ROOT).as_posix())
    actual = package_files()
    if actual != expected:
        raise ValueError(f"package inventory drift: {sorted(actual ^ expected)}")
    if RECEIPT.relative_to(ROOT).as_posix() in expected:
        raise ValueError("receipt appears in its own closure")
    expected_paper = {row["path"] for row in manifest["artifacts"]
                      if row["path"].startswith("papers/paper35/")}
    actual_paper = {path.relative_to(ROOT).as_posix()
                    for path in (ROOT / "papers" / "paper35").iterdir() if path.is_file()}
    if actual_paper != expected_paper:
        raise ValueError(f"paper directory inventory drift: {sorted(actual_paper ^ expected_paper)}")


def receipt_payload(manifest: dict, development: list[dict[str, str]]) -> dict:
    direct = [{"path": row["path"], "sha256": row["sha256"]}
              for row in manifest["artifacts"]]
    identity = [{"path": row["path"], "sha256": row["sha256"]}
                for row in manifest["artifacts"]
                if row["closure_class"] in IDENTITY_CLASSES]
    manifest_row = {"path": MANIFEST.relative_to(ROOT).as_posix(),
                    "sha256": sha256(MANIFEST)}
    payload = {
        "schema": "rime.paper35.public-package-receipt.v1",
        "artifact_id": "PAPER35-V1-PUBLIC-PACKAGE-VALIDATED",
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
            "bounded replay and partial Lean formalization do not prove the all-n theorem",
            "the receipt does not depend on itself",
            "Zenodo deposit integrity is checked separately from this local receipt",
        ],
    }
    payload["content_sha256"] = canonical_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    try:
        run_replays()
        development = development_rows()
        if args.write_manifest:
            write_json(MANIFEST, manifest_payload())
        manifest = read_json(MANIFEST)
        if manifest != manifest_payload():
            raise ValueError("release manifest is stale or noncanonical")
        validate_inventory(manifest, development)
        if args.write_manifest and not args.write_receipt:
            print("WROTE Paper XXXV manifest; release receipt still required")
            return 0
        if args.write_receipt:
            write_json(RECEIPT, receipt_payload(manifest, development))
        receipt = read_json(RECEIPT)
        if receipt.get("replay") != REPLAY or receipt != receipt_payload(manifest, development):
            raise ValueError("release receipt is stale or noncanonical")
        print(f"PASS Paper XXXV public package: {len(manifest['artifacts'])} direct, "
              f"{len(development)} nested artifacts")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL Paper XXXV public package: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
