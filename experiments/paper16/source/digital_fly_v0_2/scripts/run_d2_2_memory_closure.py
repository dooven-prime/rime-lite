#!/usr/bin/env python3
"""Run the registered D2.2 order-1 history-fiber obstruction test.

The protocol groups same-sector unit initial states by an exact rational
signature for their first coarse successor.  A pair with the same ``(z1,z0)``
history but different ``z2`` is a direct obstruction to deterministic order-1
coarse closure on the registered witness domain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "digital_fly_v0" / "results" / "carrier_v0_manifest.json"
DEFAULT_ADMISSION = (
    ROOT / "digital_fly_v0_1" / "results" / "sd1_operator_admission_v0_1.json"
)
DEFAULT_D2_1 = (
    ROOT / "digital_fly_v0_2" / "results" / "d2_1_markov_closure_v0_2.json"
)
DEFAULT_OUTPUT = (
    ROOT / "digital_fly_v0_2" / "results" / "d2_2_memory_closure_v0_2.json"
)

ALPHA = 0.2
GAMMA = 1.0
X_MAX = 1.0
HISTORY_NUMERICAL_TOLERANCE = 1e-12
FUTURE_SEPARATION_TOLERANCE = 1e-12
PROXY_SIGN_MAP = {
    "acetylcholine": 1,
    "dopamine": 1,
    "gaba": -1,
    "glutamate": 1,
    "histamine": 1,
    "octopamine": 1,
    "serotonin": 1,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def normalized_values(
    rows: np.ndarray, values: np.ndarray, n: int
) -> tuple[np.ndarray, np.ndarray]:
    row_abs_float = np.bincount(
        rows, weights=np.abs(values).astype(np.float64), minlength=n
    )
    row_abs = row_abs_float.astype(np.int64)
    if not np.array_equal(row_abs_float, row_abs.astype(np.float64)):
        raise ValueError("absolute row masses are not exactly representable integers")
    if len(rows) and np.any(row_abs[rows] <= 0):
        raise ValueError("an admitted edge has zero absolute source-row mass")
    return values.astype(np.float64, copy=False) / row_abs[rows], row_abs


def sector_mean(
    x: np.ndarray, sector_codes: np.ndarray, sector_sizes: np.ndarray
) -> np.ndarray:
    sums = np.bincount(sector_codes, weights=x, minlength=len(sector_sizes))
    return sums / sector_sizes


def trajectory_prefix(
    source: int,
    operator: sparse.csr_matrix,
    sector_codes: np.ndarray,
    sector_sizes: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = operator.shape[0]
    x0 = np.zeros(n, dtype=np.float64)
    x0[source] = 1.0
    drive0 = GAMMA * (operator.T @ x0)
    x1 = (1.0 - ALPHA) * x0 + ALPHA * np.clip(drive0, 0.0, X_MAX)
    drive1 = GAMMA * (operator.T @ x1)
    x2 = (1.0 - ALPHA) * x1 + ALPHA * np.clip(drive1, 0.0, X_MAX)
    return (
        sector_mean(x0, sector_codes, sector_sizes),
        sector_mean(x1, sector_codes, sector_sizes),
        sector_mean(x2, sector_codes, sector_sizes),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--admission", type=Path, default=DEFAULT_ADMISSION)
    parser.add_argument("--d2-1", type=Path, default=DEFAULT_D2_1)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    admission = json.loads(args.admission.read_text(encoding="utf-8"))
    d2_1 = json.loads(args.d2_1.read_text(encoding="utf-8"))
    if manifest.get("status") != "validated_for_pilot":
        raise ValueError("frozen carrier manifest is not validated_for_pilot")
    if admission.get("status") != "COMPLETED + VALIDATED":
        raise ValueError("SD1 operator-admission receipt is not validated")
    if d2_1.get("d2_1_status") != "FAILED_FIRST_ORDER_MARKOV_CLOSURE":
        raise ValueError("D2.1 prerequisite is not the registered closure failure")
    if d2_1.get("operator_hashes", {}).get("Y_known_pm") != {
        "raw": admission["operators"]["Y_known_pm"]["raw_operator_sha256"],
        "normalized": admission["operators"]["Y_known_pm"]["normalized_operator_sha256"],
    }:
        raise ValueError("D2.1 receipt is not bound to the admitted Y_known_pm operator")

    artifacts = manifest["artifacts"]
    edge_path = ROOT / artifacts["edges"]
    node_path = ROOT / artifacts["nodes"]
    edges = np.load(edge_path)
    rows = edges["row"].astype(np.int64, copy=False)
    cols = edges["col"].astype(np.int64, copy=False)
    raw_weights = edges["weight"].astype(np.int64, copy=False)
    nodes = pd.read_parquet(node_path)
    n = len(nodes)

    nt_labels = nodes["consensus_nt"].astype(str).to_numpy()
    sigma = np.asarray(
        [PROXY_SIGN_MAP.get(label, 0) for label in nt_labels], dtype=np.int8
    )
    known_mask = sigma[rows] != 0
    known_rows = rows[known_mask]
    known_cols = cols[known_mask]
    known_weights = raw_weights[known_mask]
    known_values = known_weights * sigma[known_rows].astype(np.int64)
    known_norm, row_abs = normalized_values(known_rows, known_values, n)
    operator = sparse.csr_matrix(
        (known_norm, (known_rows, known_cols)), shape=(n, n)
    )

    actual_hashes = {
        "raw": hash_operator(known_rows, known_cols, known_values, (n, n)),
        "normalized": hash_operator(known_rows, known_cols, known_norm, (n, n)),
    }
    expected = admission["operators"]["Y_known_pm"]
    hash_checks = {
        "raw": actual_hashes["raw"] == expected["raw_operator_sha256"],
        "normalized": actual_hashes["normalized"]
        == expected["normalized_operator_sha256"],
    }
    if not all(hash_checks.values()):
        raise ValueError(f"Y_known_pm hash mismatch: {hash_checks}")

    sector_values = nodes["superclass"].astype("string").fillna("<missing>").astype(str)
    sector_labels = sorted(sector_values.unique().tolist())
    sector_lookup = {label: index for index, label in enumerate(sector_labels)}
    sector_codes = np.asarray(
        [sector_lookup[value] for value in sector_values], dtype=np.int32
    )
    sector_sizes = np.bincount(
        sector_codes, minlength=len(sector_labels)
    ).astype(np.float64)
    sector_count = len(sector_labels)

    positive = known_values > 0
    positive_mass = sparse.coo_matrix(
        (
            known_weights[positive].astype(np.int64, copy=False),
            (known_rows[positive], sector_codes[known_cols[positive]]),
        ),
        shape=(n, sector_count),
        dtype=np.int64,
    ).tocsr().toarray()
    combined = np.column_stack((row_abs, positive_mass))
    common_gcd = np.gcd.reduce(combined, axis=1)
    nonzero_rows = np.flatnonzero(row_abs > 0)
    if np.any(common_gcd[nonzero_rows] <= 0):
        raise ValueError("invalid exact history signature denominator")
    reduced_denominator = np.zeros(n, dtype=np.int64)
    reduced_numerators = np.zeros_like(positive_mass)
    reduced_denominator[nonzero_rows] = (
        row_abs[nonzero_rows] // common_gcd[nonzero_rows]
    )
    reduced_numerators[nonzero_rows] = (
        positive_mass[nonzero_rows] // common_gcd[nonzero_rows, None]
    )

    groups: dict[tuple[int, int, bytes], list[int]] = {}
    for source in nonzero_rows:
        key = (
            int(sector_codes[source]),
            int(reduced_denominator[source]),
            reduced_numerators[source].tobytes(),
        )
        groups.setdefault(key, []).append(int(source))
    candidate_groups = [members for members in groups.values() if len(members) >= 2]
    candidate_groups.sort(key=lambda members: (sector_labels[sector_codes[members[0]]], members[0]))

    witness = None
    groups_examined = 0
    candidate_pairs_examined = 0
    max_history_linf_error = 0.0
    for members in candidate_groups:
        groups_examined += 1
        reference = members[0]
        z0_ref, z1_ref, z2_ref = trajectory_prefix(
            reference, operator, sector_codes, sector_sizes
        )
        for candidate in members[1:]:
            candidate_pairs_examined += 1
            z0_candidate, z1_candidate, z2_candidate = trajectory_prefix(
                candidate, operator, sector_codes, sector_sizes
            )
            history_z0_linf = float(np.linalg.norm(z0_candidate - z0_ref, ord=np.inf))
            history_z1_linf = float(np.linalg.norm(z1_candidate - z1_ref, ord=np.inf))
            history_linf = max(history_z0_linf, history_z1_linf)
            max_history_linf_error = max(max_history_linf_error, history_linf)
            if history_linf > HISTORY_NUMERICAL_TOLERANCE:
                raise ValueError(
                    "exact history signature failed its numerical cross-check"
                )
            future_difference = z2_candidate - z2_ref
            future_l1 = float(np.linalg.norm(future_difference, ord=1))
            future_linf = float(np.linalg.norm(future_difference, ord=np.inf))
            if future_linf <= FUTURE_SEPARATION_TOLERANCE:
                continue
            source_sector = int(sector_codes[reference])
            denominator = int(reduced_denominator[reference])
            numerator = reduced_numerators[reference]
            witness = {
                "sector": sector_labels[source_sector],
                "sector_index": source_sector,
                "sector_size": int(sector_sizes[source_sector]),
                "node_a_index": reference,
                "node_b_index": candidate,
                "node_a_body_id": int(nodes.iloc[reference]["bodyId"]),
                "node_b_body_id": int(nodes.iloc[candidate]["bodyId"]),
                "exact_history_signature": {
                    "source_sector": sector_labels[source_sector],
                    "reduced_denominator": denominator,
                    "nonzero_positive_mass_numerators_by_target_sector": {
                        sector_labels[index]: int(value)
                        for index, value in enumerate(numerator)
                        if value != 0
                    },
                    "meaning": "exact rational positive normalized row mass by target sector; with identical source sector this proves z0,z1 equality",
                },
                "history_cross_check": {
                    "z0_linf_difference": history_z0_linf,
                    "z1_linf_difference": history_z1_linf,
                    "tolerance": HISTORY_NUMERICAL_TOLERANCE,
                    "z0_a": z0_ref.tolist(),
                    "z0_b": z0_candidate.tolist(),
                    "z1_a": z1_ref.tolist(),
                    "z1_b": z1_candidate.tolist(),
                },
                "next_coarse_state": {
                    "z2_a": z2_ref.tolist(),
                    "z2_b": z2_candidate.tolist(),
                    "difference": future_difference.tolist(),
                    "l1_difference": future_l1,
                    "linf_difference": future_linf,
                    "separation_tolerance": FUTURE_SEPARATION_TOLERANCE,
                    "nonzero_sector_count_at_tolerance": int(
                        np.count_nonzero(
                            np.abs(future_difference) > FUTURE_SEPARATION_TOLERANCE
                        )
                    ),
                },
            }
            break
        if witness is not None:
            break

    order_1_status = (
        "FAILED_ORDER_1_MEMORY_CLOSURE"
        if witness is not None
        else "NO_ORDER_1_HISTORY_FIBER_WITNESS_ON_REGISTERED_DOMAIN"
    )
    output = {
        "schema": "rime.exploratory.digital-fly-d2-2-memory-closure.v0_2",
        "status": "COMPLETED + VALIDATED",
        "evidence_level": "Computational Observation",
        "d2_2_status": order_1_status,
        "purpose": "exact-history-fiber obstruction test for deterministic order-1 coarse dynamics",
        "v0_artifact_boundary": "frozen v0 carrier, v0.1 admission, and D2.1 receipt are read-only",
        "carrier": "Y_known_pm",
        "sign_semantics": "neurotransmitter_proxy",
        "physiological_sign_claim": False,
        "source_provenance": {
            "carrier_manifest_sha256": sha256_file(args.manifest),
            "operator_admission_sha256": sha256_file(args.admission),
            "d2_1_receipt_sha256": sha256_file(args.d2_1),
            "edge_artifact_sha256": sha256_file(edge_path),
            "node_artifact_sha256": sha256_file(node_path),
        },
        "registration": {
            "memory_order": 1,
            "history": "Psi_1(x0)=(z1,z0); current coarse state plus one lag; zero inputs",
            "target": "T_2(x0)=z2",
            "observation": "O_mean over superclass",
            "initial_states": "same-sector unit basis states",
            "alpha": ALPHA,
            "gamma": GAMMA,
            "x_max": X_MAX,
            "input": "u0=u1=0",
            "activation": "clipped_relu(phi(z)=min(x_max,max(0,z)))",
            "normalization": "absolute outgoing-row-L1",
            "history_equality_gate": "exact reduced integer signature of positive normalized row mass by target sector plus identical source sector",
            "history_numerical_tolerance": HISTORY_NUMERICAL_TOLERANCE,
            "future_separation_tolerance": FUTURE_SEPARATION_TOLERANCE,
            "selection_rule": "candidate groups ordered by sector label and first node; first node is reference; stop at first tolerance-separated z2",
        },
        "operator_hashes": {"Y_known_pm": actual_hashes},
        "hash_checks_against_admission": hash_checks,
        "candidate_surface": {
            "nonzero_outgoing_rows": int(len(nonzero_rows)),
            "exact_history_signature_groups": len(groups),
            "collision_groups_with_at_least_two_states": len(candidate_groups),
            "states_in_collision_groups": int(sum(len(group) for group in candidate_groups)),
            "groups_examined_before_stop": groups_examined,
            "candidate_pairs_examined_before_stop": candidate_pairs_examined,
            "max_history_linf_cross_check_error": max_history_linf_error,
        },
        "history_fiber_witness": witness,
        "factorization_statement": {
            "history_map": "Psi_1(x0) = (z1,z0)",
            "target_map": "T_2(x0) = z2",
            "order_1_law": "T_2 = F_bar_1 o Psi_1, equivalently z2=F_bar_1(z1,z0,u1,u0)",
            "necessary_and_sufficient_history_fiber_condition": "on the registered history image, equal H_1 histories imply equal z2",
            "witness_condition": "H_1(a)=H_1(b) exactly but z2(a)!=z2(b) above registered tolerance",
            "canonical_claim": "Adding one coarse lag does not restore deterministic closure",
        },
        "claim_boundary": {
            "supports": [
                "registered exact-history-fiber obstruction at memory order 1",
                "failure of deterministic order-1 coarse closure on the registered witness domain",
            ],
            "does_not_support": [
                "an order-1 obstruction in a named superclass sector; the registered first witness lies in the <missing> bucket",
                "failure of memory orders k>=2",
                "failure of approximate or stochastic predictive models",
                "failure of other observation maps, partitions, carriers, or dynamics",
                "physiological, causal, behavioral, embodied, or intelligence claims",
            ],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": output["status"],
                "d2_2_status": order_1_status,
                "collision_groups": len(candidate_groups),
                "pairs_examined": candidate_pairs_examined,
                "hash_checks": hash_checks,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
