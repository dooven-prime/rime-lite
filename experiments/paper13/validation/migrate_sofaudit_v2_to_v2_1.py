"""Explicitly migrate SOFAUDIT v2.0 artifacts and their SOFRS inputs to v2.1."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper12.validation.migrate_sofrs_v2_to_v2_1 import migrate_report
from experiments.paper12.validation.validate_sofrs_v2_1 import (
    build_validation_receipt as build_report_receipt,
    receipt_errors as report_receipt_errors,
    report_errors,
)
from experiments.paper13.validation import validate_sofaudit_v2 as v2_validator
from schemas.non_intervention import (
    SOFAUDIT_ATTRIBUTION_BOUNDARY,
    artifact_reference,
    write_json,
)


DEFAULT_OUTPUT_ROOT = PAPER_DIR / "results" / "v2.1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_v2_artifact(base: Path, reference: dict[str, Any]) -> Path:
    path, errors = v2_validator.resolve_artifact(base, reference)
    if errors:
        raise ValueError("; ".join(errors))
    return path


def _migrate_source_report(
    source_audit_path: Path,
    side: str,
    source: dict[str, Any],
    *,
    report_dir: Path,
    receipt_dir: Path,
) -> tuple[dict[str, Any], Path, Path]:
    old_ref = source["source_reports"][side]
    old_report_path = _resolve_v2_artifact(source_audit_path.parent, old_ref["artifact"])
    report_path = report_dir / old_report_path.name
    migrate_report(old_report_path, report_path)
    errors = report_errors(report_path)
    if errors:
        raise ValueError(f"{report_path}: " + "; ".join(errors))

    receipt_path = receipt_dir / old_report_path.name.replace(
        ".sofreport.json", ".validation-receipt.json"
    )
    receipt = build_report_receipt(report_path)
    write_json(receipt_path, receipt)
    errors = report_receipt_errors(receipt)
    if errors:
        raise ValueError(f"{receipt_path}: " + "; ".join(errors))

    migrated_ref = deepcopy(old_ref)
    migrated_ref["artifact"] = artifact_reference(report_path, ROOT)
    migrated_ref["validation_receipt"] = artifact_reference(receipt_path, ROOT)
    migrated_ref["sofrs_version"] = "2.1"
    migrated_ref["admission_basis"] = "native_sofrs_v2_1"
    return migrated_ref, report_path, receipt_path


def migrate_audit(
    source_path: Path,
    target_path: Path,
    *,
    report_dir: Path,
    report_receipt_dir: Path,
) -> dict[str, Any]:
    source_path = source_path.resolve()
    source = load_json(source_path)
    if source.get("sofaudit_version") != "2.0":
        raise ValueError(f"{source_path} is not SOFAUDIT v2.0")
    errors = v2_validator.schema_errors(source, v2_validator.load_json(v2_validator.DEFAULT_SCHEMA))
    errors.extend(v2_validator.semantic_errors(source, source_path))
    if errors:
        raise ValueError(f"{source_path}: " + "; ".join(errors))

    target = deepcopy(source)
    migrated_paths: dict[str, tuple[Path, Path]] = {}
    for side in ("reference", "target"):
        migrated_ref, report_path, receipt_path = _migrate_source_report(
            source_path,
            side,
            source,
            report_dir=report_dir,
            receipt_dir=report_receipt_dir,
        )
        target["source_reports"][side] = migrated_ref
        migrated_paths[side] = (report_path, receipt_path)

    report_roles = {
        "reference-report": ("reference", 0),
        "reference-report-validation-receipt": ("reference", 1),
        "target-report": ("target", 0),
        "target-report-validation-receipt": ("target", 1),
    }
    normalized_artifacts = []
    for artifact in source["source_artifacts"]:
        normalized = deepcopy(artifact)
        role = artifact["role"]
        if role in report_roles:
            side, index = report_roles[role]
            replacement = artifact_reference(migrated_paths[side][index], ROOT)
        else:
            resolved = _resolve_v2_artifact(source_path.parent, artifact)
            replacement = artifact_reference(resolved, ROOT)
        normalized["uri"] = replacement["uri"]
        normalized["digest"] = replacement["digest"]
        normalized_artifacts.append(normalized)
    target["source_artifacts"] = normalized_artifacts

    for coordinate in target["coordinates"].values():
        binding = coordinate.get("report_item_binding", {})
        for side in ("reference", "target"):
            item_ref = binding.get(f"{side}_item_ref")
            if item_ref is not None:
                item_ref["artifact_digest"] = target["source_reports"][side]["artifact"]["digest"]

    target["sofaudit_version"] = "2.1"
    target["revision_provenance"] = {
        "kind": "explicit_v2_0_to_v2_1_migration",
        "source_version": "2.0",
        "source_artifact": artifact_reference(source_path, ROOT),
        "migration_implementation": artifact_reference(Path(__file__), ROOT),
    }
    target["attribution_boundary"] = SOFAUDIT_ATTRIBUTION_BOUNDARY
    write_json(target_path, target)
    return target


def default_sources() -> list[Path]:
    paths = sorted((PAPER_DIR / "results" / "audits").glob("*.sofaudit.json"))
    paths.extend(sorted((PAPER_DIR / "results" / "native").glob("**/*.sofaudit.json")))
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = args.sources or default_sources()
    if not sources:
        raise SystemExit("No SOFAUDIT v2.0 artifacts found.")
    audit_dir = args.output_root / "audits"
    report_dir = args.output_root / "source-reports" / "reports"
    report_receipt_dir = args.output_root / "source-reports" / "receipts"
    for source_path in sources:
        target_path = audit_dir / source_path.name
        migrate_audit(
            source_path,
            target_path,
            report_dir=report_dir,
            report_receipt_dir=report_receipt_dir,
        )
        print(f"MIGRATED {source_path} -> {target_path}")


if __name__ == "__main__":
    main()
