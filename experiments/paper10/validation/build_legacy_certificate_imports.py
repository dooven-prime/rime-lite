"""Build source-addressed imports for legacy Registry certificate rows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V1_PATH = ROOT / "registry" / "paper10-release-v1.0.registry.json"
RESULT_PATH = (
    ROOT
    / "experiments"
    / "paper10"
    / "results"
    / "legacy_certificate_imports_v2.json"
)
SOURCE_PATHS = (
    "experiments/paper5/validation/path_commutator_cancellation.py",
    "experiments/quantum/quantum_accessibility_universality.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    source = json.loads(V1_PATH.read_text(encoding="utf-8"))
    entries = {entry["id"]: entry for entry in source["entries"]}
    cancellation = entries["synthetic-type-iii-iv"]["diagnostics"][0]
    quantum = entries["quantum-gates"]["diagnostics"]
    quantum_values = {item["name"]: item["value"] for item in quantum}

    assert cancellation["value"] == "constructed positive and negative controls"
    assert quantum_values == {
        "Pauli repair": 0,
        "Clifford+CNOT repair": 6,
    }

    return {
        "schema": "paper10.legacy-certificate-imports.v2",
        "artifact_role": "versioned_migration_result",
        "authority": (
            "Source-addressed import of finite certificate values from the "
            "immutable Registry v1.0 snapshot. This artifact does not claim a "
            "fresh scientific recomputation."
        ),
        "source_snapshot": {
            "path": "registry/paper10-release-v1.0.registry.json",
            "sha256": sha256(V1_PATH),
        },
        "source_scripts": [
            {
                "path": relative,
                "sha256": sha256(ROOT / relative),
            }
            for relative in SOURCE_PATHS
        ],
        "records": {
            "constructed_commutator_cancellation": {
                "value": cancellation["value"],
                "claim_status": "Computational Certificate",
                "negative_boundary": (
                    "Migrated mechanism control; no fresh genericity or "
                    "completion claim is made."
                ),
            },
            "quantum_static_repair": {
                "carrier_id": "quantum.gates.principal-log-skew.hall-v1",
                "generator_registration": {
                    "gate_labels": ["H", "S", "CNOT"],
                    "embedding": (
                        "H and S act on the first qubit; CNOT acts on the "
                        "ordered two-qubit computational basis"
                    ),
                    "matrix_logarithm": "scipy.linalg.logm principal matrix logarithm",
                    "skew_extraction": "X -> (X - X^*) / 2",
                    "fallback": "X -> (U - U^*) / 2 only if logm raises",
                    "normalization": "none",
                },
                "hall_filtration": {
                    "convention": (
                        "depth 0 contains the registered generators; depth 1 "
                        "contains simple commutators; each later layer brackets "
                        "a generator with the preceding layer and removes the "
                        "cumulative real-linear span"
                    ),
                    "declared_level_count": 4,
                    "tested_depth_indices": [0, 1, 2, 3],
                },
                "cutoff": 4,
                "cutoff_semantics": (
                    "legacy four-level cutoff label; the source engine indexes "
                    "the tested Hall levels by 0,1,2,3"
                ),
                "zero_tolerance": 1e-6,
                "pair_scope": "off_diagonal_ordered",
                "pauli_repair_count": quantum_values["Pauli repair"],
                "clifford_cnot_repair_count": quantum_values[
                    "Clifford+CNOT repair"
                ],
                "claim_status": "Computational Certificate",
                "negative_boundary": (
                    "Migrated finite cutoff census; unreached at cutoff is not "
                    "exact infinite depth."
                ),
            },
        },
    }


def main() -> None:
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(build(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {RESULT_PATH}")


if __name__ == "__main__":
    main()
