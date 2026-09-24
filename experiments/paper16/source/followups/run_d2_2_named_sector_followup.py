#!/usr/bin/env python3
"""Search named superclass sectors for an exact D2.2 history-fiber witness."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy import sparse


FOLLOWUPS = Path(__file__).resolve().parent
DESIGN_PATH = FOLLOWUPS / "d2_2_named_sector_followup.design-v1.json"
REGISTRATION_PATH = FOLLOWUPS / "d2_2_named_sector_followup.registration-v1.1.json"
DEFAULT_OUTPUT = FOLLOWUPS / "results" / "d2_2_named_sector_followup.v1.json"

PROXY_SIGN_MAP = {
    "acetylcholine": 1,
    "dopamine": 1,
    "gaba": -1,
    "glutamate": 1,
    "histamine": 1,
    "octopamine": 1,
    "serotonin": 1,
}
ALPHA = Fraction(1, 5)
DECAY = Fraction(4, 5)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def hash_operator(
    rows: np.ndarray, cols: np.ndarray, data: np.ndarray, shape: tuple[int, int]
) -> str:
    digest = hashlib.sha256()
    digest.update(np.asarray(shape, dtype=np.int64).tobytes())
    for array in (rows, cols, data):
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(np.asarray(contiguous.shape, dtype=np.int64).tobytes())
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def resolve_bound_path(relative: str) -> Path:
    return (FOLLOWUPS / relative).resolve()


def exact_row_abs_mass(
    rows: np.ndarray, weights: np.ndarray, node_count: int
) -> tuple[np.ndarray, int]:
    """Accumulate nonnegative row masses without a floating-point round trip."""
    if rows.dtype != np.int64 or weights.dtype != np.int64:
        raise TypeError("exact row-mass accumulation requires int64 inputs")
    if np.any(weights < 0):
        raise ValueError("exact row-mass accumulation received a negative weight")
    overflow_upper_bound = int(weights.max(initial=0)) * int(len(weights))
    if overflow_upper_bound > np.iinfo(np.int64).max:
        raise OverflowError("declared int64 row-mass accumulation bound is unsafe")
    row_abs = np.zeros(node_count, dtype=np.int64)
    np.add.at(row_abs, rows, weights)
    return row_abs, overflow_upper_bound


def verify_registration() -> tuple[dict, dict]:
    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    registration = json.loads(REGISTRATION_PATH.read_text(encoding="utf-8"))
    if registration.get("status") != "REGISTERED_READY_TO_EXECUTE":
        raise ValueError("A2 is not registered for execution")
    if registration.get("execution_authority") != "A2_NAMED_SECTOR_FOLLOWUP_ONLY":
        raise ValueError("unexpected A2 execution authority")
    if registration.get("design_sha256") != sha256_file(DESIGN_PATH):
        raise ValueError("registration design binding mismatch")
    if registration.get("producer", {}).get("sha256") != sha256_file(Path(__file__)):
        raise ValueError("registration producer binding mismatch")
    runtime = registration.get("runtime", {})
    actual_runtime = {
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "pandas_version": pd.__version__,
    }
    if runtime != actual_runtime:
        raise ValueError("registered A2 runtime mismatch")
    for entry in design["bound_inputs"]:
        path = resolve_bound_path(entry["path"])
        if not path.is_file() or sha256_file(path) != entry["sha256"]:
            raise ValueError(f"bound input mismatch: {entry['role']}")
    return design, registration


class ExactDynamics:
    def __init__(self, design: dict):
        bound = {entry["role"]: entry for entry in design["bound_inputs"]}
        edge_path = resolve_bound_path(bound["CARRIER_EDGES"]["path"])
        node_path = resolve_bound_path(bound["CARRIER_NODES_AND_SECTORS"]["path"])
        admission_path = resolve_bound_path(bound["OPERATOR_ADMISSION"]["path"])
        frozen_path = resolve_bound_path(bound["FROZEN_D2_2_CONTROL"]["path"])

        edges = np.load(edge_path)
        rows = edges["row"].astype(np.int64, copy=False)
        cols = edges["col"].astype(np.int64, copy=False)
        weights = edges["weight"].astype(np.int64, copy=False)
        self.nodes = pd.read_parquet(node_path)
        self.n = len(self.nodes)
        signs = np.asarray(
            [
                PROXY_SIGN_MAP.get(str(value), 0)
                for value in self.nodes["consensus_nt"]
            ],
            dtype=np.int8,
        )
        known = signs[rows] != 0
        known_rows = rows[known]
        known_cols = cols[known]
        known_weights = weights[known]
        known_values = known_weights * signs[known_rows].astype(np.int64)
        self.row_abs, self.row_abs_overflow_upper_bound = exact_row_abs_mass(
            known_rows, known_weights, self.n
        )
        normalized = known_values.astype(np.float64) / self.row_abs[known_rows]

        admission = json.loads(admission_path.read_text(encoding="utf-8"))
        expected = admission["operators"]["Y_known_pm"]
        shape = (self.n, self.n)
        self.raw_digest = hash_operator(known_rows, known_cols, known_values, shape)
        self.normalized_digest = hash_operator(
            known_rows, known_cols, normalized, shape
        )
        if self.raw_digest != expected["raw_operator_sha256"]:
            raise ValueError("raw Y_known_pm digest mismatch")
        if self.normalized_digest != expected["normalized_operator_sha256"]:
            raise ValueError("normalized Y_known_pm digest mismatch")
        if self.normalized_digest != design["carrier"]["normalized_operator_sha256"]:
            raise ValueError("design Y_known_pm digest mismatch")

        matrix = sparse.csr_matrix(
            (known_values, (known_rows, known_cols)), shape=shape, dtype=np.int64
        )
        matrix.sum_duplicates()
        matrix.sort_indices()
        self.indptr = matrix.indptr.astype(np.int64, copy=False)
        self.indices = matrix.indices.astype(np.int64, copy=False)
        self.numerators = matrix.data.astype(np.int64, copy=False)
        self.body_ids = self.nodes["bodyId"].astype("int64").to_numpy()

        sector_values = (
            self.nodes["superclass"].astype("string").fillna("<missing>").astype(str)
        )
        self.sector_labels = sorted(sector_values.unique().tolist())
        lookup = {label: index for index, label in enumerate(self.sector_labels)}
        self.sector_codes = sector_values.map(lookup).to_numpy(dtype=np.int16)
        self.sector_sizes = np.bincount(
            self.sector_codes, minlength=len(self.sector_labels)
        ).astype(np.int64)
        self.frozen = json.loads(frozen_path.read_text(encoding="utf-8"))

        positive = known_values > 0
        positive_mass = sparse.coo_matrix(
            (
                known_weights[positive],
                (known_rows[positive], self.sector_codes[known_cols[positive]]),
            ),
            shape=(self.n, len(self.sector_labels)),
            dtype=np.int64,
        ).tocsr().toarray()
        combined = np.column_stack((self.row_abs, positive_mass))
        common_gcd = np.gcd.reduce(combined, axis=1)
        self.nonzero_rows = np.flatnonzero(self.row_abs > 0)
        self.reduced_denominator = np.zeros(self.n, dtype=np.int64)
        self.reduced_numerators = np.zeros_like(positive_mass)
        self.reduced_denominator[self.nonzero_rows] = (
            self.row_abs[self.nonzero_rows] // common_gcd[self.nonzero_rows]
        )
        self.reduced_numerators[self.nonzero_rows] = (
            positive_mass[self.nonzero_rows]
            // common_gcd[self.nonzero_rows, None]
        )

    def groups(self) -> list[list[int]]:
        groups: dict[tuple[int, int, bytes], list[int]] = {}
        for source in self.nonzero_rows:
            key = (
                int(self.sector_codes[source]),
                int(self.reduced_denominator[source]),
                self.reduced_numerators[source].tobytes(),
            )
            groups.setdefault(key, []).append(int(source))
        collisions = [members for members in groups.values() if len(members) >= 2]
        collisions.sort(
            key=lambda members: (
                self.sector_labels[self.sector_codes[members[0]]],
                members[0],
            )
        )
        return collisions

    def exact_z2(self, source: int) -> tuple[Fraction, ...]:
        x1: dict[int, Fraction] = {source: DECAY}
        start, stop = self.indptr[source : source + 2]
        denominator = int(self.row_abs[source])
        for target, numerator in zip(
            self.indices[start:stop].tolist(), self.numerators[start:stop].tolist()
        ):
            if numerator <= 0:
                continue
            x1[target] = x1.get(target, Fraction()) + ALPHA * Fraction(
                int(numerator), denominator
            )

        drive: dict[int, Fraction] = {}
        for node, value in x1.items():
            start, stop = self.indptr[node : node + 2]
            if start == stop:
                continue
            denominator = int(self.row_abs[node])
            for target, numerator in zip(
                self.indices[start:stop].tolist(),
                self.numerators[start:stop].tolist(),
            ):
                drive[target] = drive.get(target, Fraction()) + value * Fraction(
                    int(numerator), denominator
                )

        x2 = {node: DECAY * value for node, value in x1.items()}
        for target, value in drive.items():
            clipped = min(Fraction(1), max(Fraction(), value))
            if clipped:
                x2[target] = x2.get(target, Fraction()) + ALPHA * clipped

        sums = [Fraction() for _ in self.sector_labels]
        for node, value in x2.items():
            sums[int(self.sector_codes[node])] += value
        return tuple(
            value / int(self.sector_sizes[index])
            for index, value in enumerate(sums)
        )

    def signature(self, source: int) -> dict:
        numerators = self.reduced_numerators[source]
        return {
            "source_sector": self.sector_labels[int(self.sector_codes[source])],
            "reduced_denominator": int(self.reduced_denominator[source]),
            "nonzero_positive_mass_numerators_by_target_sector": {
                self.sector_labels[index]: int(value)
                for index, value in enumerate(numerators)
                if value
            },
        }

    def exact_pair(self, reference: int, candidate: int) -> dict | None:
        left = self.exact_z2(reference)
        right = self.exact_z2(candidate)
        differences = [b - a for a, b in zip(left, right)]
        if not any(differences):
            return None
        return {
            "sector": self.sector_labels[int(self.sector_codes[reference])],
            "node_a_index": reference,
            "node_b_index": candidate,
            "node_a_body_id": int(self.body_ids[reference]),
            "node_b_body_id": int(self.body_ids[candidate]),
            "exact_history_signature": self.signature(reference),
            "exact_z2_difference": {
                self.sector_labels[index]: {
                    "numerator": str(value.numerator),
                    "denominator": str(value.denominator),
                    "decimal": float(value),
                }
                for index, value in enumerate(differences)
                if value
            },
            "nonzero_sector_count": sum(bool(value) for value in differences),
            "exact_future_separation": True,
        }


def run_followup() -> dict:
    design, registration = verify_registration()
    dynamics = ExactDynamics(design)
    groups = dynamics.groups()
    named_groups = [
        group
        for group in groups
        if dynamics.sector_labels[int(dynamics.sector_codes[group[0]])]
        != "<missing>"
    ]
    missing_groups = [
        group
        for group in groups
        if dynamics.sector_labels[int(dynamics.sector_codes[group[0]])]
        == "<missing>"
    ]

    named_witness = None
    named_groups_examined = 0
    named_pairs_examined = 0
    for members in named_groups:
        named_groups_examined += 1
        reference = members[0]
        for candidate in members[1:]:
            named_pairs_examined += 1
            named_witness = dynamics.exact_pair(reference, candidate)
            if named_witness is not None:
                break
        if named_witness is not None:
            break

    frozen_witness = dynamics.frozen["history_fiber_witness"]
    frozen_control = dynamics.exact_pair(
        int(frozen_witness["node_a_index"]),
        int(frozen_witness["node_b_index"]),
    )
    frozen_matches = bool(
        frozen_control
        and frozen_control["sector"] == "<missing>"
        and frozen_control["node_a_body_id"] == frozen_witness["node_a_body_id"]
        and frozen_control["node_b_body_id"] == frozen_witness["node_b_body_id"]
    )

    named_outcome = (
        "EXACT_NAMED_SECTOR_WITNESS_FOUND"
        if named_witness is not None
        else "NO_NAMED_SECTOR_WITNESS_FOUND_ON_REGISTERED_DOMAIN"
    )
    payload = {
        "schema": "rime.exploratory.digital-fly-d2-2-named-sector-followup.v1",
        "status": "COMPLETED",
        "evidence_level": "Computational Certificate",
        "design": {"path": DESIGN_PATH.name, "sha256": sha256_file(DESIGN_PATH)},
        "registration": {
            "path": REGISTRATION_PATH.name,
            "sha256": sha256_file(REGISTRATION_PATH),
        },
        "producer": {
            "path": Path(__file__).name,
            "sha256": sha256_file(Path(__file__)),
        },
        "carrier": {
            "name": "Y_known_pm",
            "raw_operator_sha256": dynamics.raw_digest,
            "normalized_operator_sha256": dynamics.normalized_digest,
        },
        "typed_named": {
            "outcome": named_outcome,
            "named_collision_group_count": len(named_groups),
            "groups_examined": named_groups_examined,
            "candidate_pairs_examined": named_pairs_examined,
            "witness": named_witness,
        },
        "missing_bucket": {
            "outcome": (
                "FROZEN_CONTROL_WITNESS_RECONFIRMED"
                if frozen_matches
                else "FROZEN_CONTROL_MISMATCH"
            ),
            "collision_group_count": len(missing_groups),
            "frozen_witness_exact_replay": frozen_control,
        },
        "exact_dynamics": {
            "alpha": "1/5",
            "gamma": 1,
            "x_max": 1,
            "activation": "exact clipped ReLU over Fraction values",
            "history_identity": design["history_identity"],
            "row_abs_accumulation": "int64 np.add.at over nonnegative integer weights",
            "row_abs_int64_overflow_upper_bound": dynamics.row_abs_overflow_upper_bound,
            "floating_future_separation_tolerance_used": False,
        },
        "selection_order": design["selection_order"],
        "immutability": design["immutability"],
        "claim_boundary": design["claim_boundary"],
    }
    payload["result_content_sha256"] = canonical_sha256(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run_followup()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "typed_named": result["typed_named"],
                "missing_bucket": {
                    "outcome": result["missing_bucket"]["outcome"]
                },
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
