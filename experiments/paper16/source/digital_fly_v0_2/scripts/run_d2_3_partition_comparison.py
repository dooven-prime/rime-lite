#!/usr/bin/env python3
"""Run the registered D2.3 partition-level descent comparison.

This is a matched first-reference fiber test for the linear mean observations
over ``superclass`` and ``somaSide``.  It reports collision availability and
obstruction separately; finding no witness is never promoted to closure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "digital_fly_v0" / "results" / "carrier_v0_manifest.json"
DEFAULT_ADMISSION = (
    ROOT / "digital_fly_v0_1" / "results" / "sd1_operator_admission_v0_1.json"
)
DEFAULT_D2_1 = (
    ROOT / "digital_fly_v0_2" / "results" / "d2_1_markov_closure_v0_2.json"
)
DEFAULT_D2_2 = (
    ROOT / "digital_fly_v0_2" / "results" / "d2_2_memory_closure_v0_2.json"
)
DEFAULT_OUTPUT = (
    ROOT / "digital_fly_v0_2" / "results" / "d2_3_partition_comparison_v0_2.json"
)

ALPHA = 0.2
GAMMA = 1.0
X_MAX = 1.0
FIBER_TOLERANCE = 1e-12
PROXY_SIGN_MAP = {
    "acetylcholine": 1,
    "dopamine": 1,
    "gaba": -1,
    "glutamate": 1,
    "histamine": 1,
    "octopamine": 1,
    "serotonin": 1,
}
PARTITIONS = ("superclass", "somaSide")


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
) -> np.ndarray:
    row_abs = np.bincount(
        rows, weights=np.abs(values).astype(np.float64), minlength=n
    )
    if len(rows) and np.any(row_abs[rows] <= 0.0):
        raise ValueError("an admitted edge has zero absolute source-row mass")
    return values.astype(np.float64, copy=False) / row_abs[rows]


def one_step_sector_mean(
    source: int,
    source_sector: int,
    target_cols: np.ndarray,
    target_values: np.ndarray,
    sector_codes: np.ndarray,
    sector_sizes: np.ndarray,
    sector_count: int,
) -> np.ndarray:
    positive = np.clip(GAMMA * target_values, 0.0, X_MAX)
    output = np.bincount(
        sector_codes[target_cols], weights=ALPHA * positive, minlength=sector_count
    ).astype(np.float64, copy=False)
    output /= sector_sizes
    output[source_sector] += (1.0 - ALPHA) / sector_sizes[source_sector]
    return output


def compare_partition(
    field: str,
    nodes: pd.DataFrame,
    known_rows: np.ndarray,
    known_cols: np.ndarray,
    known_norm: np.ndarray,
) -> dict:
    values = nodes[field].astype("string").fillna("<missing>").astype(str)
    labels = sorted(values.unique().tolist())
    lookup = {label: index for index, label in enumerate(labels)}
    codes = np.asarray([lookup[value] for value in values], dtype=np.int32)
    sizes = np.bincount(codes, minlength=len(labels)).astype(np.float64)

    order = np.argsort(known_rows, kind="mergesort")
    sorted_rows = known_rows[order]
    sorted_cols = known_cols[order]
    sorted_norm = known_norm[order]
    starts = np.flatnonzero(np.r_[True, sorted_rows[1:] != sorted_rows[:-1]])
    ends = np.r_[starts[1:], len(sorted_rows)]

    by_sector: dict[int, list[tuple[int, np.ndarray]]] = {}
    for start, end in zip(starts, ends):
        source = int(sorted_rows[start])
        sector = int(codes[source])
        next_mean = one_step_sector_mean(
            source,
            sector,
            sorted_cols[start:end],
            sorted_norm[start:end],
            codes,
            sizes,
            len(labels),
        )
        by_sector.setdefault(sector, []).append((source, next_mean))

    tested_states = sum(len(items) for items in by_sector.values())
    collision_sectors = {
        sector: items for sector, items in by_sector.items() if len(items) >= 2
    }
    witness_count_by_sector: dict[int, int] = {}
    witness_l1_by_sector: dict[int, list[float]] = {}
    representatives: dict[int, dict] = {}
    primary = None
    for sector, items in collision_sectors.items():
        reference_source, reference_next = items[0]
        for source, next_mean in items[1:]:
            defect = next_mean - reference_next
            l1 = float(np.linalg.norm(defect, ord=1))
            linf = float(np.linalg.norm(defect, ord=np.inf))
            if linf <= FIBER_TOLERANCE:
                continue
            witness = {
                "sector": labels[sector],
                "sector_index": sector,
                "sector_size": int(sizes[sector]),
                "node_a_index": reference_source,
                "node_b_index": source,
                "node_a_body_id": int(nodes.iloc[reference_source]["bodyId"]),
                "node_b_body_id": int(nodes.iloc[source]["bodyId"]),
                "input_fiber": {
                    "states": "unit basis e_a and e_b",
                    "observation": f"O_mean^{field}(e_a) == O_mean^{field}(e_b)",
                    "input_l1_difference": 0.0,
                    "input_linf_difference": 0.0,
                },
                "one_step_output": {
                    "observation": f"O_mean^{field}(F_Y(e))",
                    "reference_vector": reference_next.tolist(),
                    "candidate_vector": next_mean.tolist(),
                    "difference_vector": defect.tolist(),
                    "l1_defect": l1,
                    "linf_defect": linf,
                    "nonzero_sector_count": int(
                        np.count_nonzero(np.abs(defect) > FIBER_TOLERANCE)
                    ),
                },
            }
            witness_count_by_sector[sector] = witness_count_by_sector.get(sector, 0) + 1
            witness_l1_by_sector.setdefault(sector, []).append(l1)
            representatives.setdefault(sector, witness)
            if primary is None or (
                l1,
                reference_source,
                source,
            ) > (
                primary["one_step_output"]["l1_defect"],
                primary["node_a_index"],
                primary["node_b_index"],
            ):
                primary = witness

    witness_count = sum(witness_count_by_sector.values())
    if witness_count:
        status = "FAILED_FIRST_ORDER_CLOSURE"
    elif collision_sectors:
        status = "NO_OBSTRUCTION_FOUND_ON_REGISTERED_DOMAIN"
    else:
        status = "NOT_COMPARABLE_UNDER_REGISTERED_FIBER_PROTOCOL"

    return {
        "partition": field,
        "observation": f"O_mean^{field}",
        "status": status,
        "labels": labels,
        "representation_dimension": int(len(labels)),
        "node_to_observation_dimension_ratio": float(len(nodes) / len(labels)),
        "sector_sizes": {
            label: int(sizes[index]) for index, label in enumerate(labels)
        },
        "sector_size_profile": {
            "min": int(np.min(sizes)),
            "median": float(np.median(sizes)),
            "max": int(np.max(sizes)),
        },
        "tested_microscopic_states": int(tested_states),
        "tested_fibers": int(len(by_sector)),
        "collision_fibers": int(len(collision_sectors)),
        "states_in_collision_fibers": int(sum(len(items) for items in collision_sectors.values())),
        "first_reference_inconsistency_witnesses": int(witness_count),
        "witness_count_by_sector": {
            labels[index]: count
            for index, count in sorted(witness_count_by_sector.items())
        },
        "reference_l1_defect_range_by_sector": {
            labels[index]: {"min": min(values), "max": max(values)}
            for index, values in sorted(witness_l1_by_sector.items())
        },
        "representative_witness_per_sector": [
            representatives[index] for index in sorted(representatives)
        ],
        "primary_reference_witness": primary,
        "primary_reference_l1_defect": (
            None if primary is None else primary["one_step_output"]["l1_defect"]
        ),
        "fiber_protocol": {
            "input_states": "unit basis states from nonzero outgoing source rows",
            "fiber_equality": "same partition sector gives exact equal O_mean input",
            "comparison": "first source row per sector versus every later source row",
            "tolerance": FIBER_TOLERANCE,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--admission", type=Path, default=DEFAULT_ADMISSION)
    parser.add_argument("--d2-1", type=Path, default=DEFAULT_D2_1)
    parser.add_argument("--d2-2", type=Path, default=DEFAULT_D2_2)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    admission = json.loads(args.admission.read_text(encoding="utf-8"))
    d2_1 = json.loads(args.d2_1.read_text(encoding="utf-8"))
    d2_2 = json.loads(args.d2_2.read_text(encoding="utf-8"))
    if manifest.get("status") != "validated_for_pilot":
        raise ValueError("frozen carrier manifest is not validated_for_pilot")
    if admission.get("status") != "COMPLETED + VALIDATED":
        raise ValueError("SD1 operator-admission receipt is not validated")
    if d2_1.get("d2_1_status") != "FAILED_FIRST_ORDER_MARKOV_CLOSURE":
        raise ValueError("D2.1 prerequisite is not validated")
    if d2_2.get("d2_2_status") != "FAILED_ORDER_1_MEMORY_CLOSURE":
        raise ValueError("D2.2 prerequisite is not validated")
    expected_hashes = {
        "raw": admission["operators"]["Y_known_pm"]["raw_operator_sha256"],
        "normalized": admission["operators"]["Y_known_pm"]["normalized_operator_sha256"],
    }
    if d2_1.get("operator_hashes", {}).get("Y_known_pm") != expected_hashes:
        raise ValueError("D2.1 is not bound to admitted Y_known_pm")
    if d2_2.get("operator_hashes", {}).get("Y_known_pm") != expected_hashes:
        raise ValueError("D2.2 is not bound to admitted Y_known_pm")

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
    known_norm = normalized_values(known_rows, known_values, n)
    actual_hashes = {
        "raw": hash_operator(known_rows, known_cols, known_values, (n, n)),
        "normalized": hash_operator(known_rows, known_cols, known_norm, (n, n)),
    }
    hash_checks = {
        "raw": actual_hashes["raw"] == expected_hashes["raw"],
        "normalized": actual_hashes["normalized"] == expected_hashes["normalized"],
    }
    if not all(hash_checks.values()):
        raise ValueError(f"Y_known_pm hash mismatch: {hash_checks}")

    partition_results = {
        field: compare_partition(field, nodes, known_rows, known_cols, known_norm)
        for field in PARTITIONS
    }
    output = {
        "schema": "rime.exploratory.digital-fly-d2-3-partition-comparison.v0_2",
        "status": "COMPLETED + VALIDATED",
        "evidence_level": "Computational Observation",
        "d2_3_status": "COMPLETED + VALIDATED",
        "purpose": "matched first-reference fiber comparison across registered linear partitions",
        "v0_artifact_boundary": "frozen v0 carrier, v0.1 admission, D2.1 and D2.2 receipts are read-only",
        "carrier": "Y_known_pm",
        "sign_semantics": "neurotransmitter_proxy",
        "physiological_sign_claim": False,
        "source_provenance": {
            "carrier_manifest_sha256": sha256_file(args.manifest),
            "operator_admission_sha256": sha256_file(args.admission),
            "d2_1_receipt_sha256": sha256_file(args.d2_1),
            "d2_2_receipt_sha256": sha256_file(args.d2_2),
            "edge_artifact_sha256": sha256_file(edge_path),
            "node_artifact_sha256": sha256_file(node_path),
        },
        "registration": {
            "question": "Does changing the coarse representation reduce the registered dynamic-descent obstruction?",
            "comparison_order": "partition first; nonlinear observation functionals not run",
            "partitions": list(PARTITIONS),
            "observation_family": "sector mean; linear map for both registered partitions",
            "input": "u = 0",
            "alpha": ALPHA,
            "gamma": GAMMA,
            "x_max": X_MAX,
            "activation": "clipped_relu(phi(z)=min(x_max,max(0,z)))",
            "normalization": "absolute outgoing-row-L1",
            "fiber_tolerance": FIBER_TOLERANCE,
            "selection_rule": "exhaustive first-reference comparison over all nonzero outgoing source rows; no prevalence claim",
            "no_obstruction_semantics": "absence of a witness is not promoted to closure",
        },
        "operator_hashes": {"Y_known_pm": actual_hashes},
        "hash_checks_against_admission": hash_checks,
        "partition_results": partition_results,
        "claim_boundary": {
            "supports": [
                "matched partition-level first-reference obstruction comparison",
                "collision availability and representation-conditioned dynamic descent status",
            ],
            "does_not_support": [
                "closure when no witness is found",
                "obstruction prevalence from first-reference witness counts",
                "comparison of nonlinear observation functionals",
                "partition superiority without compression/null calibration",
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
                "partition_status": {
                    field: result["status"]
                    for field, result in partition_results.items()
                },
                "witness_counts": {
                    field: result["first_reference_inconsistency_witnesses"]
                    for field, result in partition_results.items()
                },
                "hash_checks": hash_checks,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
