#!/usr/bin/env python3
"""Validate the source-addressed Paper XXVII public evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper27"
MANIFEST = PACKAGE / "release-manifest.json"
RECEIPT = PACKAGE / "results" / "paper27_public_package_v1.validation-receipt.json"
THEOREM_INPUT = (
    PACKAGE / "results" / "single_defect_n7_extremal_carrier_input_v1.json"
)
THEOREM_INPUT_SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_CHANNEL_COVER_V1"
THEOREM_INPUT_PROJECTION = (
    "e3f991a551cdd977b468d3e0f36f5f236945ca62fbe3cd44fc7444cbb0ce2d43"
)
DISCOVERY_SOURCE_SHA256 = (
    "e5932ce94944ef050a49177d66e173df84c23eb060d5d7ac1f5b9645f5a2a975"
)
MANIFEST_SCHEMA = "rime.paper27.release-manifest.v3"
RECEIPT_SCHEMA = "rime.paper27.public-package-receipt.v3"
CLOSURE_CLASSES = (
    "normative-manuscript-build",
    "theorem-facing-computational",
    "public-package-documentation",
)
RELEASE_IDENTITY_CLASSES = CLOSURE_CLASSES[:2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def validate_manifest(manifest: dict, errors: list[str]) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        errors.append("release manifest schema mismatch")
    if manifest.get("paper_id") != "PAPER27":
        errors.append("release identity mismatch")
    if manifest.get("release_version") != "1.0":
        errors.append("release version mismatch")
    if manifest.get("receipt_self_exclusion") is not True:
        errors.append("receipt self-exclusion is not declared")

    policy = manifest.get("closure_policy", {})
    if policy.get("classes") != list(CLOSURE_CLASSES):
        errors.append("release closure classes mismatch")
    if policy.get("release_identity_classes") != list(RELEASE_IDENTITY_CLASSES):
        errors.append("release identity classes mismatch")

    declared: set[str] = set()
    class_counts = {name: 0 for name in CLOSURE_CLASSES}
    for artifact in manifest.get("artifacts", []):
        path_text = artifact.get("path", "")
        closure_class = artifact.get("closure_class")
        if closure_class not in CLOSURE_CLASSES:
            errors.append(f"invalid closure class for {path_text}: {closure_class}")
        else:
            class_counts[closure_class] += 1
        if path_text in declared:
            errors.append(f"duplicate manifest path: {path_text}")
            continue
        declared.add(path_text)
        try:
            path = resolve_relative(path_text)
        except (OSError, ValueError) as error:
            errors.append(str(error))
            continue
        if not path.is_file():
            errors.append(f"manifest artifact missing: {path_text}")
        elif sha256(path) != artifact.get("sha256"):
            errors.append(f"manifest digest mismatch: {path_text}")

    for closure_class, count in class_counts.items():
        if not count:
            errors.append(f"empty release closure class: {closure_class}")
    required_normative = {
        "papers/paper27/Paper XXVII.md",
        "papers/paper27/paper27_arxiv.pdf",
        "papers/paper27/references-v1.bib",
    }
    normative = {
        row["path"]
        for row in manifest.get("artifacts", [])
        if row.get("closure_class") == "normative-manuscript-build"
    }
    if not required_normative <= normative:
        errors.append("normative manuscript/build closure is incomplete")

    ignored = {MANIFEST.resolve(), RECEIPT.resolve()}
    package_files = {
        path.resolve()
        for path in PACKAGE.rglob("*")
        if path.is_file()
        and path.suffix != ".pyc"
        and "__pycache__" not in path.parts
        and path.resolve() not in ignored
    }
    declared_package_files = {
        resolve_relative(path_text)
        for path_text in declared
        if path_text.startswith("experiments/paper27/")
    }
    missing = sorted(
        path.relative_to(ROOT).as_posix()
        for path in package_files - declared_package_files
    )
    extra = sorted(
        path.relative_to(ROOT).as_posix()
        for path in declared_package_files - package_files
    )
    if missing:
        errors.append(f"unmanifested package files: {missing}")
    if extra:
        errors.append(f"manifest package files absent from inventory: {extra}")


def validate_theorem_input(errors: list[str]) -> None:
    try:
        payload = json.loads(THEOREM_INPUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"n=7 theorem input is unreadable: {error}")
        return
    if payload.get("schema") != THEOREM_INPUT_SCHEMA:
        errors.append("n=7 theorem input schema mismatch")
    if payload.get("projection_digest") != THEOREM_INPUT_PROJECTION:
        errors.append("n=7 theorem input projection digest mismatch")
    admission = payload.get("release_input", {})
    if admission.get("source_exact_sha256") != DISCOVERY_SOURCE_SHA256:
        errors.append("n=7 theorem input discovery-source binding mismatch")
    contexts = payload.get("contexts")
    if not isinstance(contexts, list) or len(contexts) != 35:
        errors.append("n=7 theorem input does not contain 35 contexts")
        return
    if admission.get("context_count") != len(contexts):
        errors.append("n=7 theorem input context count is inconsistent")
    if len({row.get("index") for row in contexts}) != len(contexts):
        errors.append("n=7 theorem input contains duplicate context indices")
    if len({row.get("defect") for row in contexts}) != len(contexts):
        errors.append("n=7 theorem input contains duplicate defects")


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


def focused_validation(errors: list[str]) -> list[dict]:
    results = PACKAGE / "results"
    commands = [
        [str(PACKAGE / "validation/validate_n6_entry_section_image.py"), str(results / "single_defect_n6_entry_section_image_v1.json")],
        [str(PACKAGE / "validation/validate_n6_type_ii_only_section.py"), str(results / "single_defect_n6_type_ii_only_section_v1.json")],
        [str(PACKAGE / "validation/validate_n7_extremal_negative_cell_exhaustion.py"), str(results / "single_defect_n7_extremal_negative_cell_exhaustion_v1.json"), "--paper", str(PACKAGE / "N7_LOW_TRANSPORT_PAPER_TABLES.md")],
    ]
    for command in commands:
        run_validator(command, errors)
    return [
        {
            "validator": Path(command[0]).relative_to(ROOT).as_posix(),
            "replay": False,
        }
        for command in commands
    ]


def artifact_rows(
    manifest: dict, closure_classes: tuple[str, ...] | None = None
) -> list[dict]:
    return [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in manifest["artifacts"]
        if closure_classes is None or row["closure_class"] in closure_classes
    ]


def closure_block(rows: list[dict]) -> dict:
    return {
        "artifact_count": len(rows),
        "closure_digest": canonical_digest(rows),
        "ordered_artifacts": rows,
    }


def receipt_payload(manifest: dict, replay_rows: list[dict]) -> dict:
    package_rows = [
        {
            "path": MANIFEST.relative_to(ROOT).as_posix(),
            "sha256": sha256(MANIFEST),
        },
        *artifact_rows(manifest),
    ]
    class_blocks = {
        closure_class: closure_block(artifact_rows(manifest, (closure_class,)))
        for closure_class in CLOSURE_CLASSES
    }
    payload = {
        "schema": RECEIPT_SCHEMA,
        "artifact_id": "PAPER27-V1-PUBLIC-EVIDENCE-VALIDATED",
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "replay": replay_rows,
        "manifest_binding": {
            "path": MANIFEST.relative_to(ROOT).as_posix(),
            "sha256": sha256(MANIFEST),
        },
        "release_identity": {
            "closure_classes": list(RELEASE_IDENTITY_CLASSES),
            **closure_block(artifact_rows(manifest, RELEASE_IDENTITY_CLASSES)),
        },
        "closure_classes": class_blocks,
        "package_inventory": closure_block(package_rows),
    }
    payload["content_sha256"] = canonical_digest(payload)
    return payload


def validate_receipt(manifest: dict, errors: list[str]) -> None:
    if not RECEIPT.is_file():
        errors.append("validation receipt is missing")
        return
    try:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"validation receipt is unreadable: {error}")
        return
    content_sha256 = receipt.pop("content_sha256", None)
    if content_sha256 != canonical_digest(receipt):
        errors.append("validation receipt content digest mismatch")
        return
    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append("validation receipt schema mismatch")
        return
    replay_rows = receipt.get("replay")
    if not isinstance(replay_rows, list):
        errors.append("validation receipt replay rows are missing")
        return
    expected = receipt_payload(manifest, replay_rows)
    expected.pop("content_sha256")
    if receipt != expected:
        errors.append("validation receipt is stale or not bound to the current closure")


def write_receipt(manifest: dict, replay_rows: list[dict]) -> None:
    RECEIPT.write_text(
        json.dumps(receipt_payload(manifest, replay_rows), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    validate_manifest(manifest, errors)
    validate_theorem_input(errors)
    replay_rows = focused_validation(errors)
    if not args.write_receipt:
        validate_receipt(manifest, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    if args.write_receipt:
        write_receipt(manifest, replay_rows)
        print(f"wrote {RECEIPT.relative_to(ROOT).as_posix()}")
    print("PASS Paper XXVII public package")


if __name__ == "__main__":
    main()
