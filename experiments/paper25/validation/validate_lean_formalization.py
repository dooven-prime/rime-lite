"""Validate and optionally replay the Paper XXV partial Lean formalization."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN = HERE.parent / "lean"
MANIFEST = LEAN / "formalization-manifest.json"
RECEIPT = HERE.parent / "results" / "paper25_lean_formalization_v1.receipt.json"
MATHLIB_REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def closure_rows(manifest: dict) -> list[dict]:
    paths = [
        ("formalization-manifest", MANIFEST),
        ("formalization-readme", LEAN / "README.md"),
        ("lean-toolchain", LEAN / "lean-toolchain"),
        ("lake-project", LEAN / "lakefile.toml"),
        ("lake-lock", LEAN / "lake-manifest.json"),
        *[("lean-source", ROOT / path) for path in manifest["source_files"]],
        ("formalization-validator", Path(__file__)),
    ]
    return [
        {
            "role": role,
            "artifact": {
                "uri": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
            },
        }
        for role, path in paths
    ]


def build_receipt(manifest: dict) -> dict:
    rows = closure_rows(manifest)
    receipt = {
        "schema": "rime.paper25.lean-formalization-receipt.v1",
        "artifact_id": "PAPER25-TYPED-TRANSPORT-SCALAR-MARGIN-V1-ELABORATED",
        "formalization_id": manifest["formalization_id"],
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "elaboration_commands": [
            "lake build",
            "lake env lean Formalization.lean"
        ],
        "artifact_closure": {
            "artifact_count": len(rows),
            "closure_digest": canonical_digest(rows),
            "ordered_artifacts": rows,
        },
    }
    receipt["content_sha256"] = canonical_digest(receipt)
    return receipt


def validate_static() -> tuple[dict, list[str]]:
    errors: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rime.paper25.lean-formalization-manifest.v1":
        errors.append("formalization manifest schema mismatch")
    if manifest.get("formalization_id") != "PAPER25-TYPED-TRANSPORT-SCALAR-MARGIN-V1":
        errors.append("formalization identity mismatch")
    if manifest.get("status") != "PARTIAL_FORMALIZATION":
        errors.append("formalization status drift")
    if manifest.get("validation_mode") != "LOCAL_CLOSURE_VERIFICATION":
        errors.append("formalization validation mode mismatch")
    if manifest.get("entry_point") != "experiments/paper25/lean/Formalization.lean":
        errors.append("formalization entry point mismatch")
    if manifest.get("lean_toolchain") != "leanprover/lean4:v4.33.0":
        errors.append("Lean toolchain declaration mismatch")
    if manifest.get("mathlib_revision") != MATHLIB_REVISION:
        errors.append("Mathlib declaration mismatch")

    expected_sources = [
        "experiments/paper25/lean/Formalization.lean",
        "experiments/paper25/lean/Formalization/Transport.lean",
        "experiments/paper25/lean/Formalization/Margin.lean",
    ]
    if manifest.get("source_files") != expected_sources:
        errors.append("formalization source inventory mismatch")

    toolchain = (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip()
    if toolchain != manifest.get("lean_toolchain"):
        errors.append("lean-toolchain bytes differ from manifest")
    lakefile = (LEAN / "lakefile.toml").read_text(encoding="utf-8")
    for marker in (
        'name = "rime_paper25"',
        'defaultTargets = ["Formalization"]',
        'name = "Formalization"',
        f'rev = "{MATHLIB_REVISION}"',
    ):
        if marker not in lakefile:
            errors.append(f"lakefile missing {marker!r}")

    lake_manifest = json.loads((LEAN / "lake-manifest.json").read_text(encoding="utf-8"))
    mathlib = next(
        (package for package in lake_manifest.get("packages", []) if package.get("name") == "mathlib"),
        None,
    )
    if mathlib is None or mathlib.get("rev") != MATHLIB_REVISION:
        errors.append("lake lock does not bind the declared Mathlib revision")

    placeholder = re.compile(r"\b(?:sorry|admit)\b|^\s*axiom\b", re.MULTILINE)
    for source in expected_sources:
        path = ROOT / source
        if not path.is_file():
            errors.append(f"missing Lean source: {source}")
            continue
        if placeholder.search(path.read_text(encoding="utf-8")):
            errors.append(f"placeholder or custom axiom in {source}")

    return manifest, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    if args.write_receipt and not args.replay:
        parser.error("--write-receipt requires --replay")

    manifest, errors = validate_static()
    if not errors and args.replay:
        for command in (["lake", "build"], ["lake", "env", "lean", "Formalization.lean"]):
            result = subprocess.run(command, cwd=LEAN)
            if result.returncode:
                errors.append(f"Lean replay failed: {' '.join(command)}")
                break

    expected_receipt = build_receipt(manifest)
    if not errors and args.write_receipt:
        RECEIPT.write_text(
            json.dumps(expected_receipt, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"WROTE {RECEIPT.relative_to(ROOT).as_posix()}")
    elif not errors:
        if not RECEIPT.is_file():
            errors.append("formalization receipt is missing")
        else:
            retained = json.loads(RECEIPT.read_text(encoding="utf-8"))
            if retained != expected_receipt:
                errors.append("formalization receipt differs from current source closure")

    if errors:
        print("FAIL Paper XXV Lean formalization")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        "PASS Paper XXV Lean formalization: "
        f"{expected_receipt['artifact_closure']['artifact_count']} bound artifacts, "
        f"closure {expected_receipt['artifact_closure']['closure_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
