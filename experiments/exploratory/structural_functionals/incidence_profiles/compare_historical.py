#!/usr/bin/env python
"""Compare regenerated profiles with a historical local result snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from incidence_profiles import source_artifact, write_json


HERE = Path(__file__).resolve().parent
PROTOCOL_DIRECTORIES = ("axis_balanced_fixed", "axis_balanced_endogenous")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_scientific_projection(payload: dict) -> dict:
    """Remove historical floating tie-break labels, retaining alignment geometry."""
    projected = json.loads(json.dumps(payload))
    projected.pop("provenance", None)
    projected.pop("claim_status", None)
    alignment = projected.get("sector_frame", {}).get("alignment_to_full")
    if not isinstance(alignment, dict) or "relation" not in alignment:
        return projected

    for key in (
        "best_reference_for_target",
        "best_target_for_reference",
        "maximizing_reference_sectors_for_target",
        "maximizing_target_sectors_for_reference",
        "selector_tolerance",
    ):
        alignment.pop(key, None)

    target_rows = []
    for row in alignment.get("target_in_reference_containment", []):
        target_rows.append(
            {
                "target_sector": row["target_sector"],
                "minimum_residual": row.get("minimum_residual", row.get("residual")),
            }
        )
    alignment["target_in_reference_containment"] = target_rows

    reference_rows = []
    for row in alignment.get("reference_in_target_containment", []):
        reference_rows.append(
            {
                "reference_sector": row["reference_sector"],
                "minimum_residual": row.get("minimum_residual", row.get("residual")),
            }
        )
    alignment["reference_in_target_containment"] = reference_rows
    return projected


def compare(left, right, path="", *, atol: float, rtol: float):
    if (
        isinstance(left, (int, float))
        and not isinstance(left, bool)
        and isinstance(right, (int, float))
        and not isinstance(right, bool)
    ):
        delta = abs(float(left) - float(right))
        return ([], delta) if math.isclose(left, right, abs_tol=atol, rel_tol=rtol) else (
            [{"path": path, "historical": left, "migrated": right}],
            delta,
        )
    if type(left) is not type(right):
        return ([{"path": path, "historical": left, "migrated": right}], 0.0)
    if isinstance(left, dict):
        mismatches = []
        maximum_delta = 0.0
        ignored = {"provenance", "claim_status"}
        for key in sorted((set(left) | set(right)) - ignored):
            child_path = f"{path}/{key}"
            if key not in left or key not in right:
                mismatches.append(
                    {
                        "path": child_path,
                        "historical": left.get(key, "<missing>"),
                        "migrated": right.get(key, "<missing>"),
                    }
                )
                continue
            child_mismatches, child_delta = compare(
                left[key], right[key], child_path, atol=atol, rtol=rtol
            )
            mismatches.extend(child_mismatches)
            maximum_delta = max(maximum_delta, child_delta)
        return mismatches, maximum_delta
    if isinstance(left, list):
        if len(left) != len(right):
            return (
                [{"path": f"{path}/length", "historical": len(left), "migrated": len(right)}],
                0.0,
            )
        mismatches = []
        maximum_delta = 0.0
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            child_mismatches, child_delta = compare(
                left_item,
                right_item,
                f"{path}/{index}",
                atol=atol,
                rtol=rtol,
            )
            mismatches.extend(child_mismatches)
            maximum_delta = max(maximum_delta, child_delta)
        return mismatches, maximum_delta
    return (
        ([], 0.0)
        if left == right
        else ([{"path": path, "historical": left, "migrated": right}], 0.0)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("historical_results", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/migration_validation.json"),
    )
    parser.add_argument("--atol", type=float, default=1e-11)
    parser.add_argument("--rtol", type=float, default=1e-11)
    args = parser.parse_args()

    migrated_results = HERE / "results"
    records = []
    migrated_paths = []
    for directory_name in PROTOCOL_DIRECTORIES:
        historical_directory = args.historical_results / directory_name
        migrated_directory = migrated_results / directory_name
        for historical_path in sorted(historical_directory.glob("*.json")):
            migrated_path = migrated_directory / historical_path.name
            if not migrated_path.is_file():
                raise FileNotFoundError(migrated_path)
            historical = stable_scientific_projection(
                json.loads(historical_path.read_text(encoding="utf-8"))
            )
            migrated = stable_scientific_projection(
                json.loads(migrated_path.read_text(encoding="utf-8"))
            )
            mismatches, maximum_delta = compare(
                historical,
                migrated,
                atol=args.atol,
                rtol=args.rtol,
            )
            records.append(
                {
                    "protocol_directory": directory_name,
                    "file": historical_path.name,
                    "historical_sha256": sha256(historical_path),
                    "migrated_sha256": sha256(migrated_path),
                    "scientific_fields_match": not mismatches,
                    "maximum_compared_numeric_delta": maximum_delta,
                    "mismatches": mismatches,
                }
            )
            migrated_paths.append(migrated_path)

    payload = {
        "schema": "rime.incidence-profile-migration-validation.v1",
        "claim_status": "Computational Certificate",
        "certificate_kind": "finite_migration_equivalence",
        "historical_source_label": "local pre-migration rime incidence-profile snapshot",
        "comparison_policy": {
            "ignored_fields": [
                "claim_status",
                "provenance",
                "historical single-index overlap/containment tie-break selectors",
            ],
            "absolute_tolerance": args.atol,
            "relative_tolerance": args.rtol,
            "non_numeric_fields": "exact equality",
        },
        "profile_count": len(records),
        "all_scientific_fields_match": all(
            record["scientific_fields_match"] for record in records
        ),
        "maximum_compared_numeric_delta": max(
            (record["maximum_compared_numeric_delta"] for record in records),
            default=0.0,
        ),
        "records": records,
        "provenance": {
            "source_artifacts": [
                source_artifact(Path(__file__)),
                *(source_artifact(path) for path in migrated_paths),
            ]
        },
        "boundary": (
            "The certificate checks migrated scientific fields against historical "
            "bytes. It does not make the historical repository a runtime dependency "
            "and does not itself promote any artifact into Paper VII evidence; "
            "promotion requires a separate paper-local registration."
        ),
    }
    assert payload["profile_count"] == 38
    assert payload["all_scientific_fields_match"]
    write_json(args.output, payload)
    print(
        "historical migration comparison passed for 38 profiles; "
        f"max numeric delta={payload['maximum_compared_numeric_delta']:.3e}"
    )


if __name__ == "__main__":
    main()
