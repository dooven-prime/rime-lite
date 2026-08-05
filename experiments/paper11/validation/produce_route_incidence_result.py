"""Produce the Paper XI source-addressed route-incidence result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = ROOT / "experiments" / "paper7" / "results" / "incidence_geometry.json"
SOURCE_PATH = ROOT / "experiments" / "paper7" / "validation" / "incidence_variety_codim.py"
RESULT_PATH = ROOT / "experiments" / "paper11" / "results" / "route_incidence_result_v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    rows = source["configurations"]
    result = {
        "schema": "paper11-route-incidence-result-v1.0",
        "claim_status": "Computational Certificate",
        "producer": "experiments/paper11/validation/produce_route_incidence_result.py",
        "canonical_input": {
            "path": INPUT_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256(INPUT_PATH),
            "schema": source["schema"],
        },
        "upstream_source": {
            "owner": "paper7",
            "path": SOURCE_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256(SOURCE_PATH),
        },
        "summary": {
            "configuration_count": len(rows),
            "square_dimensions": [row["m"] for row in rows if row["m"] == row["n"] == row["p"]],
            "type_iv_codimensions": {
                row["label"]: row["type_iv_codimension"] for row in rows
            },
            "relative_codimension_formula": source["formulas"]["fixed_double_rank_relative_codimension"],
        },
        "claim_scope": (
            "exact finite dimension-table certificate for the free complex matrix-pair "
            "incidence locus AB=0; no represented-Rubik transversality claim"
        ),
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {RESULT_PATH}")


if __name__ == "__main__":
    main()
