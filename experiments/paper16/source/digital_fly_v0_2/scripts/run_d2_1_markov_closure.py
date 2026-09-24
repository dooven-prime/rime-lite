#!/usr/bin/env python3
"""Run the registered D2.1 first-order coarse-dynamics closure test.

The test uses the frozen ``Y_known_pm`` carrier and the linear observation
``O_mean``.  Unit states supported on two nodes in the same sector have the
same coarse input.  If their one-step coarse outputs differ, ``O_mean`` cannot
factor the node-level update through any deterministic first-order coarse law.
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
DEFAULT_OUTPUT = ROOT / "digital_fly_v0_2" / "results" / "d2_1_markov_closure_v0_2.json"


def portable_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()

ALPHA = 0.2
GAMMA = 1.0
X_MAX = 1.0
FIBER_TOLERANCE = 1e-12
ADMISSION_TOLERANCE = 1e-12
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
) -> np.ndarray:
    row_abs = np.bincount(
        rows, weights=np.abs(values).astype(np.float64), minlength=n
    )
    if len(rows) and np.any(row_abs[rows] <= 0.0):
        raise ValueError("an admitted edge has zero absolute source-row mass")
    return values.astype(np.float64, copy=False) / row_abs[rows]


def sector_mean_unit_state(
    source: int,
    source_sector: int,
    target_cols: np.ndarray,
    target_values: np.ndarray,
    sector_codes: np.ndarray,
    sector_sizes: np.ndarray,
    sector_count: int,
) -> np.ndarray:
    """Return O_mean(F_Y(e_source)) for one signed normalized source row."""

    drive = GAMMA * target_values
    activated = np.clip(drive, 0.0, X_MAX)
    next_state = np.bincount(
        sector_codes[target_cols],
        weights=ALPHA * activated,
        minlength=sector_count,
    ).astype(np.float64, copy=False)
    next_state /= sector_sizes
    next_state[source_sector] += (1.0 - ALPHA) / sector_sizes[source_sector]
    return next_state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--admission", type=Path, default=DEFAULT_ADMISSION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    admission = json.loads(args.admission.read_text(encoding="utf-8"))
    if manifest.get("status") != "validated_for_pilot":
        raise ValueError("frozen carrier manifest is not validated_for_pilot")
    if admission.get("status") != "COMPLETED + VALIDATED":
        raise ValueError("SD1 operator-admission receipt is not validated")
    if not all(admission.get("checks", {}).values()):
        raise ValueError("SD1 operator-admission checks are not all true")

    artifacts = manifest["artifacts"]
    edge_path = ROOT / artifacts["edges"]
    node_path = ROOT / artifacts["nodes"]
    edges = np.load(edge_path)
    rows = edges["row"].astype(np.int64, copy=False)
    cols = edges["col"].astype(np.int64, copy=False)
    raw_weights = edges["weight"].astype(np.int64, copy=False)
    nodes = pd.read_parquet(node_path)
    n = len(nodes)
    if len(rows) and int(max(rows.max(), cols.max())) >= n:
        raise ValueError("edge index exceeds frozen node universe")

    labels_nt = nodes["consensus_nt"].astype(str).to_numpy()
    sigma = np.asarray(
        [PROXY_SIGN_MAP.get(label, 0) for label in labels_nt], dtype=np.int8
    )
    known_mask = sigma[rows] != 0
    known_rows = rows[known_mask]
    known_cols = cols[known_mask]
    known_weights = raw_weights[known_mask]
    known_values = known_weights * sigma[known_rows].astype(np.int64)
    known_norm = normalized_values(known_rows, known_values, n)

    actual_hashes = {
        "Y_known_pm": {
            "raw": hash_operator(known_rows, known_cols, known_values, (n, n)),
            "normalized": hash_operator(known_rows, known_cols, known_norm, (n, n)),
        }
    }
    expected = admission["operators"]["Y_known_pm"]
    hash_checks = {
        "raw": actual_hashes["Y_known_pm"]["raw"] == expected["raw_operator_sha256"],
        "normalized": actual_hashes["Y_known_pm"]["normalized"]
        == expected["normalized_operator_sha256"],
    }
    if not all(hash_checks.values()):
        raise ValueError(f"Y_known_pm hash mismatch: {hash_checks}")

    sector_values = nodes["superclass"].astype("string").fillna("<missing>").astype(str)
    sector_labels = sorted(sector_values.unique().tolist())
    sector_lookup = {label: i for i, label in enumerate(sector_labels)}
    sector_codes = np.asarray(
        [sector_lookup[value] for value in sector_values], dtype=np.int32
    )
    sector_sizes = np.bincount(
        sector_codes, minlength=len(sector_labels)
    ).astype(np.float64)

    order = np.argsort(known_rows, kind="mergesort")
    sorted_rows = known_rows[order]
    sorted_cols = known_cols[order]
    sorted_norm = known_norm[order]
    row_starts = np.flatnonzero(
        np.r_[True, sorted_rows[1:] != sorted_rows[:-1]]
    )
    row_ends = np.r_[row_starts[1:], len(sorted_rows)]

    first_by_sector: dict[int, tuple[int, np.ndarray]] = {}
    witness_count_by_sector: dict[int, int] = {}
    witness_l1_by_sector: dict[int, list[float]] = {}
    representative_by_sector: dict[int, dict] = {}
    primary = None
    for start, end in zip(row_starts, row_ends):
        source = int(sorted_rows[start])
        source_sector = int(sector_codes[source])
        coarse_next = sector_mean_unit_state(
            source,
            source_sector,
            sorted_cols[start:end],
            sorted_norm[start:end],
            sector_codes,
            sector_sizes,
            len(sector_labels),
        )
        reference = first_by_sector.get(source_sector)
        if reference is None:
            first_by_sector[source_sector] = (source, coarse_next)
            continue
        reference_source, reference_next = reference
        defect = coarse_next - reference_next
        defect_l1 = float(np.linalg.norm(defect, ord=1))
        defect_linf = float(np.linalg.norm(defect, ord=np.inf))
        if defect_linf > FIBER_TOLERANCE:
            witness = {
                "sector": sector_labels[source_sector],
                "sector_index": source_sector,
                "sector_size": int(sector_sizes[source_sector]),
                "node_a_index": reference_source,
                "node_b_index": source,
                "node_a_body_id": int(nodes.iloc[reference_source]["bodyId"]),
                "node_b_body_id": int(nodes.iloc[source]["bodyId"]),
                "input_fiber": {
                    "states": "unit basis e_a and e_b",
                    "observation": "O_mean(e_a) == O_mean(e_b)",
                    "input_l1_difference": 0.0,
                    "input_linf_difference": 0.0,
                },
                "one_step_output": {
                    "observation": "O_mean(F_Y(e))",
                    "l1_defect": defect_l1,
                    "linf_defect": defect_linf,
                    "nonzero_sector_count": int(
                        np.count_nonzero(np.abs(defect) > FIBER_TOLERANCE)
                    ),
                    "reference_vector": reference_next.tolist(),
                    "candidate_vector": coarse_next.tolist(),
                    "difference_vector": defect.tolist(),
                },
            }
            witness_count_by_sector[source_sector] = (
                witness_count_by_sector.get(source_sector, 0) + 1
            )
            witness_l1_by_sector.setdefault(source_sector, []).append(defect_l1)
            representative_by_sector.setdefault(source_sector, witness)
            if primary is None or (
                defect_l1,
                reference_source,
                source,
            ) > (
                primary["one_step_output"]["l1_defect"],
                primary["node_a_index"],
                primary["node_b_index"],
            ):
                primary = witness

    witness_count = sum(witness_count_by_sector.values())
    if not witness_count:
        status = "NO_HOSTILE_WITNESS_ON_REGISTERED_CARRIER"
        primary = None
    else:
        status = "FAILED_FIRST_ORDER_MARKOV_CLOSURE"

    output = {
        "schema": "rime.exploratory.digital-fly-d2-1-markov-closure.v0_2",
        "status": "COMPLETED + VALIDATED",
        "evidence_level": "Computational Observation",
        "d2_1_status": status,
        "purpose": "fiber inconsistency test for first-order coarse dynamical descent",
        "v0_artifact_boundary": "frozen v0 carrier and v0.1 SD1 admission receipt are read-only",
        "carrier": "Y_known_pm",
        "sign_semantics": "neurotransmitter_proxy",
        "physiological_sign_claim": False,
        "carrier_manifest": portable_path(args.manifest),
        "operator_admission_receipt": portable_path(args.admission),
        "source_provenance": {
            "carrier_manifest_sha256": sha256_file(args.manifest),
            "operator_admission_sha256": sha256_file(args.admission),
            "edge_artifact_sha256": sha256_file(edge_path),
            "node_artifact_sha256": sha256_file(node_path),
        },
        "registration": {
            "question": "Does O_mean composed with one node-level update factor through O_mean?",
            "observation": "O_mean(x)[i] = mean_{j in S_i} x[j]",
            "state_pair_protocol": "unit basis states on two nonzero outgoing rows in the same superclass sector",
            "input": "u = 0",
            "alpha": ALPHA,
            "gamma": GAMMA,
            "x_max": X_MAX,
            "activation": "clipped_relu(phi(z)=min(x_max,max(0,z)))",
            "normalization": "absolute outgoing-row-L1; sum_j |Y_norm[i,j]| = 1 on nonzero rows",
            "fiber_tolerance": FIBER_TOLERANCE,
            "selection_rule": "first reference row per sector; record every first-reference inconsistency; primary is maximum reference L1 defect",
            "operator_orientation": "source_row_target_column; incoming=Y.T@x",
        },
        "operator_hashes": actual_hashes,
        "hash_checks_against_admission": hash_checks,
        "observation_receipt": {
            "field": "superclass",
            "sector_count": len(sector_labels),
            "labels": sector_labels,
            "sector_sizes": {
                label: int(sector_sizes[index])
                for index, label in enumerate(sector_labels)
            },
            "nonzero_outgoing_rows": int(len(row_starts)),
            "sectors_with_nonzero_outgoing_rows": len(first_by_sector),
        },
        "fiber_witness_summary": {
            "first_reference_inconsistency_witnesses": witness_count,
            "count_by_sector": {
                sector_labels[index]: count
                for index, count in sorted(witness_count_by_sector.items())
            },
            "defect_l1_range_by_sector": {
                sector_labels[index]: {
                    "min": min(values),
                    "max": max(values),
                }
                for index, values in sorted(witness_l1_by_sector.items())
            },
            "representative_witness_per_sector": [
                representative_by_sector[index]
                for index in sorted(representative_by_sector)
            ],
        },
        "primary_reference_l1_defect": (
            None
            if primary is None
            else primary["one_step_output"]["l1_defect"]
        ),
        "primary_witness": primary,
        "factorization_statement": {
            "map": "O_mean o F_Y",
            "first_order_coarse_law": "z_next = F_bar(z, u)",
            "necessary_and_sufficient_fiber_condition": "for all x,y: O_mean(x)=O_mean(y) implies O_mean(F_Y(x,u))=O_mean(F_Y(y,u))",
            "witness_condition": "O_mean(e_a) = O_mean(e_b) but O_mean(F_Y(e_a)) != O_mean(F_Y(e_b))",
            "fiber_condition": "O_mean o F_Y must be constant on every O_mean-fiber",
            "interpretation": "a valid witness rules out every deterministic first-order coarse law through O_mean on the registered carrier and protocol",
        },
        "claim_boundary": {
            "supports": [
                "registered fiber inconsistency for O_mean",
                "failure of deterministic first-order Markov descent through O_mean on Y_known_pm",
                "model-relative dynamic descent defect",
            ],
            "does_not_support": [
                "failure of all memory-augmented coarse laws",
                "failure of other observation maps",
                "physiological E/I or biological causality claim",
                "behavior, embodiment, intelligence, or consciousness claim",
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
                "d2_1_status": status,
                "witness_count": witness_count,
                "hash_checks": hash_checks,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
