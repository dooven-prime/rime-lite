#!/usr/bin/env python3
"""Audit candidate annotation fields before sectorization comparison.

This is a lightweight metadata/coverage pass.  It does not aggregate the
151M-edge table and does not infer biological modality from free-text labels.
The output records which fields are admissible as a broad partition, a
secondary axis, or only a restricted complete-case sensitivity analysis.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
ANNOTATIONS = DATA / "body-annotations-male-cns-v1.0-minconf-0.5.feather"

CANDIDATE_FIELDS = [
    "superclass",
    "type",
    "flywireType",
    "somaSide",
    "itoleeHl",
    "trumanHl",
    "class",
    "subclass",
    "somaNeuromere",
    "entryNerve",
    "exitNerve",
    "rootSide",
]


def normalize(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "<missing>"
    text = str(value).strip()
    return text if text and text.lower() != "nan" else "<missing>"


def recommendation(field: str, coverage: float, cardinality: int) -> tuple[str, str]:
    if field == "superclass":
        return "baseline_broad", "all annotation bodies; retain <missing> explicitly"
    if field == "somaSide" and coverage >= 0.5:
        return "secondary_axis", "all annotation bodies; retain <missing> explicitly"
    if field in {"type", "flywireType"} and coverage >= 0.5:
        return "finer_partition", "all annotation bodies only with high-cardinality warning"
    return "restricted_sensitivity", "complete-case or explicitly restricted universe"


def run() -> dict:
    frame = pd.read_feather(ANNOTATIONS, columns=["bodyId", *CANDIDATE_FIELDS])
    if frame["bodyId"].duplicated().any():
        raise ValueError("annotation bodyId is not unique")
    rows = len(frame)
    fields: dict[str, dict] = {}
    for field in CANDIDATE_FIELDS:
        labels = frame[field].map(normalize)
        counts = Counter(labels.tolist())
        nonmissing = rows - counts.get("<missing>", 0)
        coverage = nonmissing / rows if rows else None
        tier, universe_rule = recommendation(field, coverage or 0.0, len(counts) - (1 if "<missing>" in counts else 0))
        fields[field] = {
            "rows": rows,
            "nonmissing_rows": nonmissing,
            "missing_rows": counts.get("<missing>", 0),
            "coverage": coverage,
            "distinct_nonmissing_labels": len(counts) - (1 if "<missing>" in counts else 0),
            "top_labels": [
                {"label": label, "count": count}
                for label, count in counts.most_common(20)
            ],
            "comparison_role": tier,
            "universe_rule": universe_rule,
        }

    return {
        "schema": "rime.exploratory.male-cns-sectorization-field-audit.v1",
        "release": "MaleCNS v1.0",
        "input": "body-annotations-male-cns-v1.0-minconf-0.5.feather",
        "annotation_rows": rows,
        "body_id_unique": True,
        "fields": fields,
        "comparison_contract": {
            "primary_partition": "superclass",
            "secondary_candidates": ["somaSide", "type", "flywireType"],
            "restricted_candidates": ["itoleeHl", "trumanHl", "class", "subclass", "somaNeuromere", "entryNerve", "exitNerve", "rootSide"],
            "missing_label": "<missing>",
            "unannotated_endpoint_label": "<unannotated>",
            "no_native_binary_modality_field": True,
            "modality_policy": "do not infer motor/sensory sectors from regex labels; any derived map requires a versioned rule",
            "comparison_metrics": ["sector_count", "sector_size_profile", "support_density", "LP2", "LP3", "C2", "C3", "h2", "h3", "witness_multiplicity"],
            "null_requirement": "fixed graph with label permutation preserving sector-size profile, or another predeclared matched null",
            "scope": "field audit only; no graph-level sector comparison is claimed by this artifact",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit MaleCNS sectorization fields")
    parser.parse_args()
    result = run()
    RESULTS.mkdir(parents=True, exist_ok=True)
    output = RESULTS / "sectorization_field_audit_v1.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({field: {"coverage": data["coverage"], "distinct": data["distinct_nonmissing_labels"], "role": data["comparison_role"]} for field, data in result["fields"].items()}, indent=2, ensure_ascii=False))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
