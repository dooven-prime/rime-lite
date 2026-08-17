#!/usr/bin/env python
"""Summarize a completed orbit census without changing its raw records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from incidence_profiles import profile_invariant_signature, source_artifact, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for path in sorted(args.directory.glob("*.json")):
        if path.name == "summary.json":
            continue
        profile = json.loads(path.read_text(encoding="utf-8"))
        counts = profile["counts"]
        rows.append(
            {
                "file": path.name,
                "orbit_id": profile["family"].get("orbit_id"),
                "operator_count": profile["family"]["operator_count"],
                "sector_count": profile["sector_frame"]["sector_count"],
                "total_supported_routes": counts["total_supported_routes"],
                "protected_routes": counts["protected_routes"],
                "unprotected_zero": counts["unprotected_zero"],
                "zero_over_all_supported": counts["zero_over_all_supported"],
                "zero_over_unprotected": counts["zero_over_unprotected"],
                "zero_mechanism_counts": counts["zero_mechanism_counts"],
                "profile_signature": profile_invariant_signature(profile),
            }
        )
    signatures = {}
    for row in rows:
        key = json.dumps(row["profile_signature"], sort_keys=True)
        signatures[key] = signatures.get(key, 0) + 1
    payload = {
        "schema": "rime.incidence-profile-orbit-summary.v1",
        "claim_status": "Computational Observation",
        "directory": args.directory.as_posix(),
        "orbit_count": len(rows),
        "distinct_profile_signature_count": len(signatures),
        "rows": rows,
        "signature_multiplicities": sorted(signatures.values()),
        "interpretation": (
            "Fixed-frame profiles are comparable because all rows use the same "
            "canonical sector frame. Endogenous profiles require the serialized "
            "projector-overlap alignment and refinement relation."
        ),
        "provenance": {
            "source_artifacts": [
                source_artifact(Path(__file__)),
                *(source_artifact(path) for path in sorted(args.directory.glob("*.json"))),
            ]
        },
    }
    write_json(args.output, payload)
    print(f"summarized {len(rows)} orbit profiles; {len(signatures)} distinct signatures")


if __name__ == "__main__":
    main()
