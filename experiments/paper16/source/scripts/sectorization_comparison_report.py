#!/usr/bin/env python3
"""Assemble the first sectorization-comparison profile.

This report intentionally compares only the two completed low-cardinality
partitions (superclass and somaSide).  Sparse/high-cardinality fields remain
in ``sectorization_field_audit_v1.json`` and are not promoted to graph claims.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def read(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def d2_row(field: str, filename: str, field_audit: dict) -> dict:
    data = read(filename)
    core = data["typed_core"]
    relay = data["relay_strict"]
    inclusive = data["coverage_inclusive"]
    return {
        "sector_field": field,
        "sector_count_including_missing_and_unannotated": data["universe"].get(
            "sector_count_including_missing",
            field_audit["distinct_nonmissing_labels"] + 2,
        ),
        "d2": {
            "typed_core": {"quotient_triples": core["macro_triple_count"], "lifted": core["lifted_triple_count"], "LP2": core["lift_precision_2"]},
            "relay_strict": {"quotient_triples": relay["macro_triple_count"], "lifted": relay["lifted_triple_count"], "LP2": relay["lift_precision_2"]},
            "coverage_inclusive": {"quotient_triples": inclusive["macro_triple_count"], "lifted": inclusive["lifted_triple_count"], "LP2": inclusive["lift_precision_2"]},
        },
        "source_artifact": filename,
    }


def main() -> None:
    field_audit = read("sectorization_field_audit_v1.json")
    superclass_d2 = d2_row("superclass", "path_lifting_audit_full_v3.json", field_audit["fields"]["superclass"])
    soma_d2 = d2_row("somaSide", "path_lifting_audit_full_v3_somaSide.json", field_audit["fields"]["somaSide"])
    superclass_d3 = read("path_lifting_depth3_audit_full_v1.json")
    soma_d3 = read("path_lifting_depth3_audit_full_somaSide_v1.json")

    result = {
        "schema": "rime.exploratory.male-cns-sectorization-comparison.v1",
        "release": "MaleCNS v1.0",
        "scope": "first low-cardinality comparison; static support only",
        "partitions": {
            "superclass": {
                "field_audit": field_audit["fields"]["superclass"],
                "depth2": superclass_d2,
                "depth3": superclass_d3["carrier_rules"],
            },
            "somaSide": {
                "field_audit": field_audit["fields"]["somaSide"],
                "depth2": soma_d2,
                "depth3": soma_d3["carrier_rules"],
            },
        },
        "deferred_partitions": {
            field: {
                "field_audit": field_audit["fields"][field],
                "status": "restricted_or_high_cardinality; no whole-universe route comparison admitted in this phase",
            }
            for field in ["type", "flywireType", "itoleeHl", "trumanHl", "class", "subclass", "somaNeuromere", "entryNerve", "exitNerve", "rootSide"]
        },
        "interpretation": {
            "LP2_LP3": "support liftability under a fixed carrier rule; not a biological transmission probability",
            "partition_comparison": "descriptive contrast; no partition is ranked without matched sector-size and label-permutation null",
            "coverage": "superclass and somaSide retain <missing>; endpoint IDs absent from annotations remain <unannotated>",
            "next_step": "declare matched null and, if warranted, run the same profile for one predeclared restricted partition",
        },
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    output = RESULTS / "sectorization_comparison_v1.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for field, payload in result["partitions"].items():
        core = payload["depth2"]["d2"]["typed_core"]["LP2"]
        d3 = payload["depth3"]["typed_core"]["LP3"]
        print(f"{field}: typed-core LP2={core:.6f}, LP3={d3:.6f}")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
