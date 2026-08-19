"""Explicitly migrate SOFRS v2.0 reports to semantic-revision v2.1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper12.validation.validate_sofrs_v2 import standalone_report_errors
from schemas.non_intervention import (
    SOFRS_OBJECT_TRANSITION_BOUNDARY,
    artifact_reference,
    write_json,
)
from schemas.sofrs.api import v2_report_validation_receipt_errors


DEFAULT_SOURCE_DIR = PAPER_DIR / "results" / "reports"
DEFAULT_OUTPUT_DIR = PAPER_DIR / "results" / "v2.1" / "reports"
SOURCE_RECEIPT_DIR = PAPER_DIR / "results" / "report-validation-receipts" / "paper12-v2"
V2_REPORT_CONTRACT = ROOT / "schemas" / "sofrs" / "v2.0.schema.json"
V2_RECEIPT_CONTRACT = ROOT / "schemas" / "sofrs" / "report-validation-receipt-v2.0.schema.json"
V2_VALIDATOR = PAPER_DIR / "validation" / "validate_sofrs_v2.py"
V2_RECEIPT_API = ROOT / "schemas" / "sofrs" / "api.py"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_source_receipt_path(source_path: Path) -> Path:
    """Return the frozen v2 receipt location owned by the source-report set."""

    source_path = source_path.resolve()
    if source_path.is_relative_to(PAPER_DIR / "results" / "reports"):
        return SOURCE_RECEIPT_DIR / (
            source_path.name.removesuffix(".sofreport.json")
            + ".validation-receipt.json"
        )
    if source_path.parent.name == "reports" and source_path.parent.parent.name == "source-reports":
        return source_path.parent.parent / "receipts" / (
            source_path.name.removesuffix(".sofreport.json")
            + ".validation-receipt.json"
        )
    raise ValueError(f"unsupported source-report location: {source_path}")


def source_validation_receipt(source_path: Path) -> dict[str, Any]:
    """Require the frozen v2 receipt before annotating a report as v2.1."""

    source_path = source_path.resolve()
    receipt_path = canonical_source_receipt_path(source_path)
    if not receipt_path.is_file():
        raise ValueError(f"missing v2.0 source validation receipt: {receipt_path}")

    source = load_json(source_path)
    receipt = load_json(receipt_path)
    expected_report_reference = {
        "report_id": source["report_id"],
        "sofrs_version": source["sofrs_version"],
        "record_kind": source["record_kind"],
        "artifact": artifact_reference(source_path, ROOT),
    }
    errors = v2_report_validation_receipt_errors(
        receipt,
        repository_root=ROOT,
        expected_report_reference=expected_report_reference,
    )
    if errors:
        raise ValueError(
            f"{receipt_path}: invalid v2.0 source validation receipt: "
            + "; ".join(errors)
        )
    return artifact_reference(receipt_path, ROOT)


def migrate_report(source_path: Path, target_path: Path) -> dict[str, Any]:
    source_path = source_path.resolve()
    source = load_json(source_path)
    if source.get("sofrs_version") != "2.0":
        raise ValueError(f"{source_path} is not SOFRS v2.0")
    errors = standalone_report_errors(source_path)
    if errors:
        raise ValueError(f"{source_path}: " + "; ".join(errors))
    source_receipt = source_validation_receipt(source_path)

    target = dict(source)
    target["sofrs_version"] = "2.1"
    target["revision_provenance"] = {
        "kind": "explicit_v2_0_to_v2_1_migration",
        "source_version": "2.0",
        "source_artifact": artifact_reference(source_path, ROOT),
        "source_validation_receipt": source_receipt,
        "migration_implementation": artifact_reference(Path(__file__), ROOT),
    }
    target["object_transition_boundary"] = SOFRS_OBJECT_TRANSITION_BOUNDARY
    write_json(target_path, target)
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = args.sources or sorted(DEFAULT_SOURCE_DIR.glob("*.sofreport.json"))
    if not sources:
        raise SystemExit("No SOFRS v2.0 reports found.")
    for source_path in sources:
        target_path = args.output_dir / source_path.name
        migrate_report(source_path, target_path)
        print(f"MIGRATED {source_path} -> {target_path}")


if __name__ == "__main__":
    main()
