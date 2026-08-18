"""Build the conservative Paper IX v2.1 deformation-record migration ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.non_intervention import artifact_reference, resolve_reference, write_json


SCHEMA = ROOT / "schemas" / "sofdeformation" / "deformation-record-migration-v2.1.schema.json"
OUTPUT = PAPER_DIR / "results" / "deformation-record-migration-v2.1.json"
TRAJECTORY_RECORDS = (
    ("rate-hierarchy", "rate_hierarchy.json", "Theorem"),
    ("nn-training-response", "nn_training_sof_tau.json", "Computational Observation"),
    ("calibrated-response", "calibrated_response.json", "Computational Certificate"),
)
STATIC_RECORDS = ("nn_activation_sof.json",)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_ledger() -> dict[str, Any]:
    records = []
    for record_id, filename, claim_status in TRAJECTORY_RECORDS:
        source_path = PAPER_DIR / "results" / filename
        records.append(
            {
                "record_id": record_id,
                "source_artifact": artifact_reference(source_path, ROOT),
                "object_deformation_status": "NOT_DECLARED",
                "object_trajectory_status": "NOT_DECLARED",
                "trajectory_provenance": "LEGACY_RECORD_ONLY",
                "observation_record_status": "RECORDED",
                "deformation_record_status": "MIGRATED_AS_RECORDED_TRAJECTORY",
                "object_transition_model": "NOT_DECLARED",
                "mechanism_label_status": "NOT_DECLARED",
                "causal_mechanism_status": "NOT_ESTABLISHED",
                "claim_status": claim_status,
                "negative_boundary": (
                    "Migration retypes the retained sampled trajectory as a DeformationRecord; "
                    "it does not infer an ObjectDeformation, ObjectTrajectory, "
                    "intervention, or causal mechanism."
                ),
            }
        )
    excluded = []
    for filename in STATIC_RECORDS:
        source_path = PAPER_DIR / "results" / filename
        excluded.append(
            {
                "source_artifact": artifact_reference(source_path, ROOT),
                "record_kind": "SOFObservationRecord",
                "deformation_record_status": "NOT_APPLICABLE_STATIC",
                "reason": "The retained artifact is a static observation census, not a recorded trajectory.",
            }
        )
    return {
        "schema_version": "paper9-deformation-record-migration-v2.1",
        "revision_title": "Non-Intervention and Attribution Boundary Revision",
        "migration_class": "semantic_type_migration",
        "type_partition": {
            "object_deformation": "ObjectDeformation",
            "object_trajectory": "ObjectTrajectory",
            "trajectory_relation": "ORDERED_PATH_SPECIALIZATION",
            "observation_record": "SOFObservationRecord",
            "deformation_record": "DeformationRecord",
            "identity_status": "DISTINCT_TYPES",
        },
        "records": records,
        "excluded_static_records": excluded,
        "negative_boundary": [
            "ObjectTrajectory is an ordered-path specialization of ObjectDeformation.",
            "Neither ObjectDeformation nor ObjectTrajectory is a DeformationRecord.",
            "A mechanism label is not causal identification.",
            "Migration does not manufacture an object-transition model absent from the source artifact.",
        ],
    }


def validation_errors(payload: dict[str, Any]) -> list[str]:
    errors = sorted(
        error.message
        for error in Draft202012Validator(load_json(SCHEMA)).iter_errors(payload)
    )
    for index, record in enumerate(payload.get("records", [])):
        _, reference_errors = resolve_reference(
            record["source_artifact"], root=ROOT, label=f"record[{index}] source"
        )
        errors.extend(reference_errors)
    for index, record in enumerate(payload.get("excluded_static_records", [])):
        _, reference_errors = resolve_reference(
            record["source_artifact"], root=ROOT, label=f"excluded[{index}] source"
        )
        errors.extend(reference_errors)
    return errors


def main(*, write_result: bool = False) -> None:
    payload = build_ledger()
    errors = validation_errors(payload)
    if errors:
        raise SystemExit("Paper IX v2.1 migration failed: " + "; ".join(errors))
    if write_result:
        write_json(OUTPUT, payload)
        print(f"WROTE {OUTPUT}")
    else:
        if not OUTPUT.is_file() or load_json(OUTPUT) != payload:
            raise SystemExit(f"STALE {OUTPUT}; rerun with --write-result")
        print(f"PASS {OUTPUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    main(write_result=parser.parse_args().write_result)
