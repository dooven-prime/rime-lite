"""Independently validate the Paper XI route-incidence result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = ROOT / "experiments" / "paper7" / "results" / "incidence_geometry.json"
RESULT_PATH = ROOT / "experiments" / "paper11" / "results" / "route_incidence_result_v1.json"
CERT_PATH = ROOT / "experiments" / "paper11" / "results" / "route_incidence_validation_v1.json"
PRODUCER_PATH = Path(__file__).parent / "produce_route_incidence_result.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recompute_codimension(m: int, n: int, p: int) -> tuple[int, list[int]]:
    candidates = [
        ((m - rank) * (n - rank) + p * rank, rank)
        for rank in range(1, min(m, n - 1) + 1)
    ]
    minimum = min(value for value, _ in candidates)
    return minimum, [rank for value, rank in candidates if value == minimum]


def main() -> None:
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    recomputed = {}
    for row in source["configurations"]:
        codimension, minimizers = recompute_codimension(row["m"], row["n"], row["p"])
        assert codimension == row["type_iv_codimension"]
        assert minimizers == row["minimizing_rank_a"]
        for double in row["fixed_double_rank_strata"]:
            assert double["relative_codimension_in_rank_pair_stratum"] == (
                double["rank_a"] * double["rank_b"]
            )
        recomputed[row["label"]] = codimension

    assert result["canonical_input"]["sha256"] == sha256(INPUT_PATH)
    assert result["summary"]["configuration_count"] == len(source["configurations"])
    assert result["summary"]["type_iv_codimensions"] == recomputed

    certificate = {
        "schema": "paper11-validation-certificate-v1.0",
        "claim_status": "Computational Certificate",
        "validator": "experiments/paper11/validation/validate_route_incidence_result.py",
        "validator_version": "1.0",
        "validator_independence": {
            "implementation_relation": "separate_formula_recomputation",
            "language_relation": "same_language",
            "runtime_relation": "separate_process",
            "input_source": "canonical_input_and_frozen_result",
            "producer_cache_used": False,
        },
        "canonical_input_sha256": sha256(INPUT_PATH),
        "producer_sha256": sha256(PRODUCER_PATH),
        "result_sha256": sha256(RESULT_PATH),
        "validator_sha256": sha256(Path(__file__)),
        "recomputed_summary": {
            "configuration_count": len(source["configurations"]),
            "type_iv_codimensions": recomputed,
        },
        "claim_scope": result["claim_scope"],
        "validation_status": "passed",
    }
    CERT_PATH.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    print(f"wrote {CERT_PATH}")


if __name__ == "__main__":
    main()
