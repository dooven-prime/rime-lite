"""Generate the paper-owned Cerny and rare-run family records."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper26.pair_chain import (  # noqa: E402
    cerny_transition,
    pair_chain_diagnostics,
    rare_run_transition,
    shortest_reset_length,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_closure() -> list[dict]:
    sources = (
        "experiments/paper26/pair_chain.py",
        "experiments/paper26/generate_family_results.py",
    )
    return [{"path": source, "sha256": _sha256(ROOT / source)} for source in sources]


def _write(name: str, payload: dict) -> None:
    payload["source_artifacts"] = _source_closure()
    path = RESULTS / name
    path.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"WROTE {path.relative_to(ROOT).as_posix()}")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    cerny_rows = []
    for n in range(3, 17):
        diagnostics = pair_chain_diagnostics(cerny_transition(n))
        expected_h2 = n**3 - 3 * n**2 / 2 + (n % 2) / 2
        cerny_rows.append(
            {
                "n": n,
                "reset_length": shortest_reset_length(cerny_transition(n)),
                "H2": diagnostics["H2"],
                "expected_H2": expected_h2,
                "gap": diagnostics["gap"],
                "n3_gap": n**3 * diagnostics["gap"],
                "gap_times_H2": diagnostics["gap"] * diagnostics["H2"],
            }
        )
    _write(
        "cerny_pair_chain_v1.json",
        {
            "schema": "rime.paper26.cerny-pair-chain.v1",
            "evidence": {
                "exact_fields": {
                    "status": "COMPUTATIONAL_REPRODUCTION_OF_PROVED_FORMULAS",
                    "fields": ["n", "reset_length", "expected_H2"],
                },
                "numerical_fields": {
                    "status": "BOUNDED_FLOAT64_OBSERVATION",
                    "fields": ["H2", "gap", "n3_gap", "gap_times_H2"],
                    "absolute_replay_tolerance": 1e-9,
                    "arithmetic": "NumPy float64 linear algebra",
                },
                "attribution": {
                    "expected_H2": "uniform-input specialization of Gusev 2014",
                    "perron_fields": "Paper XXVI finite reproductions",
                },
            },
            "pi_squared_over_8": math.pi**2 / 8,
            "rows": cerny_rows,
        },
    )

    rare_rows = []
    for n in range(2, 17):
        diagnostics = pair_chain_diagnostics(rare_run_transition(n))
        rare_rows.append(
            {
                "n": n,
                "reset_length": shortest_reset_length(rare_run_transition(n)),
                "H2": diagnostics["H2"],
                "expected_H2": 2**n - 2,
                "gap": diagnostics["gap"],
                "gap_times_H2": diagnostics["gap"] * diagnostics["H2"],
            }
        )
    _write(
        "rare_run_pair_chain_v1.json",
        {
            "schema": "rime.paper26.rare-run-pair-chain.v1",
            "evidence": {
                "exact_fields": {
                    "status": "COMPUTATIONAL_REPRODUCTION_OF_PROVED_FORMULAS",
                    "fields": ["n", "reset_length", "expected_H2"],
                },
                "numerical_fields": {
                    "status": "BOUNDED_FLOAT64_OBSERVATION",
                    "fields": ["H2", "gap", "gap_times_H2"],
                    "absolute_replay_tolerance": 1e-9,
                    "arithmetic": "NumPy float64 linear algebra",
                },
            },
            "rows": rare_rows,
        },
    )


if __name__ == "__main__":
    main()
