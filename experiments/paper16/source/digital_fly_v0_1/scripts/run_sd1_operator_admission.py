#!/usr/bin/env python3
"""Build and validate the SD1 matched-support operator admission receipt.

This is an admission-only artifact.  It does not run signed dynamics.  The
registered sign map is explicitly a transmitter-only proxy because the frozen
S1 carrier does not contain receptor-context evidence.
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
DEFAULT_OUTPUT = (
    ROOT
    / "digital_fly_v0_1"
    / "results"
    / "sd1_operator_admission_v0_1.json"
)


def portable_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()
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
UNKNOWN_LABELS = ("nt_missing", "unclear")


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


def resolve_manifest_paths(manifest_path: Path, manifest: dict) -> tuple[Path, Path]:
    artifacts = manifest.get("artifacts", {})
    edge_path = Path(artifacts.get("edges", ""))
    node_path = Path(artifacts.get("nodes", ""))
    if not edge_path.is_absolute():
        edge_path = ROOT / edge_path
    if not node_path.is_absolute():
        node_path = ROOT / node_path
    if not edge_path.is_file() or not node_path.is_file():
        raise FileNotFoundError(
            f"carrier artifacts are missing: edges={edge_path}, nodes={node_path}"
        )
    return edge_path, node_path


def normalized_data(rows: np.ndarray, values: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    row_abs = np.bincount(rows, weights=np.abs(values).astype(np.float64), minlength=n)
    if np.any(row_abs[rows] <= 0.0):
        raise ValueError("an admitted edge has a zero absolute source-row mass")
    data = values.astype(np.float64, copy=False) / row_abs[rows]
    return data, row_abs


def operator_receipt(
    name: str,
    rows: np.ndarray,
    cols: np.ndarray,
    values: np.ndarray,
    n: int,
    normalized: np.ndarray,
    row_abs: np.ndarray,
) -> dict:
    normalized_row_abs = np.bincount(
        rows, weights=np.abs(normalized), minlength=n
    )
    nonzero_rows = int(np.count_nonzero(row_abs))
    return {
        "name": name,
        "shape": [int(n), int(n)],
        "edge_count": int(len(rows)),
        "nonzero_rows": nonzero_rows,
        "zero_rows": int(n - nonzero_rows),
        "raw_weight_sum": int(np.asarray(values, dtype=np.int64).sum()),
        "raw_abs_weight_sum": int(np.abs(values).astype(np.int64).sum()),
        "raw_abs_row_l1_max": float(np.max(row_abs, initial=0.0)),
        "normalized_abs_row_l1_max": float(np.max(normalized_row_abs, initial=0.0)),
        "normalized_abs_row_l1_closure": bool(
            np.all(normalized_row_abs <= 1.0 + ADMISSION_TOLERANCE)
        ),
        "raw_operator_sha256": hash_operator(rows, cols, values, (n, n)),
        "normalized_operator_sha256": hash_operator(
            rows, cols, normalized, (n, n)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "validated_for_pilot":
        raise ValueError("frozen S1 carrier manifest is not validated_for_pilot")
    edge_path, node_path = resolve_manifest_paths(args.manifest, manifest)

    edges = np.load(edge_path)
    rows = edges["row"].astype(np.int64, copy=False)
    cols = edges["col"].astype(np.int64, copy=False)
    weights = edges["weight"].astype(np.int64, copy=False)
    nodes = pd.read_parquet(node_path)
    n = len(nodes)
    if len(rows) != len(cols) or len(rows) != len(weights):
        raise ValueError("edge arrays have inconsistent lengths")
    if len(rows) and int(max(rows.max(), cols.max())) >= n:
        raise ValueError("edge index exceeds frozen node universe")
    if np.any(weights <= 0):
        raise ValueError("SD1 admission expects positive frozen release weights")

    decomposition = manifest.get("operator_family", {}).get("decomposition_receipt", {})
    required_decomposition_checks = (
        "edge_count_identity_holds",
        "weight_sum_identity_holds",
        "exact_one_source_label_per_admitted_edge",
    )
    if not all(decomposition.get(key) is True for key in required_decomposition_checks):
        raise ValueError("frozen NT decomposition receipt is not closed")

    labels = nodes["consensus_nt"].astype(str).to_numpy()
    source_labels = labels[rows]
    source_sigma = np.asarray(
        [PROXY_SIGN_MAP.get(label, 0) for label in source_labels], dtype=np.int8
    )
    known_mask = source_sigma != 0
    unknown_mask = ~known_mask
    known_rows = rows[known_mask]
    known_cols = cols[known_mask]
    known_magnitudes = weights[known_mask]
    known_sigma = source_sigma[known_mask]
    known_pm_rows = rows[known_mask].copy()
    known_pm_cols = cols[known_mask].copy()
    full_values = weights
    known_plus_values = known_magnitudes.copy()
    known_pm_values = known_magnitudes * known_sigma.astype(np.int64)

    known_plus_normalized, known_plus_row_abs = normalized_data(
        known_rows, known_plus_values, n
    )
    known_pm_normalized, known_pm_row_abs = normalized_data(
        known_rows, known_pm_values, n
    )
    full_plus_normalized, full_plus_row_abs = normalized_data(rows, full_values, n)

    support_equal = bool(
        np.array_equal(known_rows, known_pm_rows)
        and np.array_equal(known_cols, known_pm_cols)
    )
    raw_magnitude_delta = int(
        np.max(
            np.abs(
                known_plus_values.astype(np.int64)
                - np.abs(known_pm_values).astype(np.int64)
            ),
            initial=0,
        )
    )
    normalized_magnitude_delta = float(
        np.max(
            np.abs(known_plus_normalized - np.abs(known_pm_normalized)),
            initial=0.0,
        )
    )
    known_plus_zero_rows = int(n - np.count_nonzero(known_plus_row_abs))
    full_plus_zero_rows = int(n - np.count_nonzero(full_plus_row_abs))
    sign_counts = {
        "positive": int(np.count_nonzero(known_pm_values > 0)),
        "negative": int(np.count_nonzero(known_pm_values < 0)),
        "zero": int(np.count_nonzero(known_pm_values == 0)),
    }
    full_abs_mass = int(np.abs(full_values).sum())
    known_abs_mass = int(np.abs(known_magnitudes).sum())
    full_edge_count = int(len(rows))
    known_edge_count = int(len(known_rows))
    checks = {
        "known_plus_support_equals_known_pm": support_equal,
        "known_plus_raw_magnitudes_equal_known_pm": raw_magnitude_delta == 0,
        "known_plus_normalized_magnitudes_equal_known_pm": normalized_magnitude_delta
        <= ADMISSION_TOLERANCE,
        "known_plus_and_known_pm_edge_count_equal": len(known_rows) == len(known_pm_rows),
        "full_plus_absolute_row_l1_closed": bool(
            np.all(
                np.bincount(rows, weights=np.abs(full_plus_normalized), minlength=n)
                <= 1.0 + ADMISSION_TOLERANCE
            )
        ),
        "known_plus_absolute_row_l1_closed": bool(
            np.all(
                np.bincount(
                    known_rows, weights=np.abs(known_plus_normalized), minlength=n
                )
                <= 1.0 + ADMISSION_TOLERANCE
            )
        ),
        "known_pm_absolute_row_l1_closed": bool(
            np.all(
                np.bincount(
                    known_rows, weights=np.abs(known_pm_normalized), minlength=n
                )
                <= 1.0 + ADMISSION_TOLERANCE
            )
        ),
    }
    if not all(checks.values()):
        raise ValueError(f"SD1 operator admission failed: {checks}")

    status = "COMPLETED + VALIDATED"
    output = {
        "schema": "rime.exploratory.digital-fly-sd1-operator-admission.v0_1",
        "status": status,
        "evidence_level": "Computational Observation",
        "purpose": "matched-support sign admission only; signed dynamics not run",
        "v0_artifact_boundary": "frozen v0 carrier is read-only; this is a new v0.1 receipt",
        "dynamics_status": "NOT_RUN",
        "carrier_manifest": portable_path(args.manifest),
        "source_provenance": {
            "carrier_manifest_sha256": sha256_file(args.manifest),
            "edge_artifact_sha256": sha256_file(edge_path),
            "node_artifact_sha256": sha256_file(node_path),
            "source_manifest_declared_hashes": manifest.get("source_artifact", {}),
        },
        "node_universe_count": int(n),
        "operator_orientation": "source_row_target_column; incoming=Y.T@x",
        "registration": {
            "sigma_semantics": "neurotransmitter_proxy",
            "physiological_sign_claim": False,
            "sign_context": "transmitter-only proxy; receptor evidence not present in frozen S1 carrier",
            "proxy_sign_map": PROXY_SIGN_MAP,
            "unknown_labels": list(UNKNOWN_LABELS),
            "absolute_row_l1_normalization": "Y_norm[i,j] = Y[i,j] / sum_j |Y[i,j]|",
            "admission_tolerance": ADMISSION_TOLERANCE,
        },
        "operators": {
            "Y_full_plus": operator_receipt(
                "Y_full_plus", rows, cols, full_values, n, full_plus_normalized, full_plus_row_abs
            ),
            "Y_known_plus": operator_receipt(
                "Y_known_plus",
                known_rows,
                known_cols,
                known_plus_values,
                n,
                known_plus_normalized,
                known_plus_row_abs,
            ),
            "Y_known_pm": operator_receipt(
                "Y_known_pm",
                known_rows,
                known_pm_cols,
                known_pm_values,
                n,
                known_pm_normalized,
                known_pm_row_abs,
            ),
        },
        "coverage": {
            "full_edge_count": full_edge_count,
            "known_sign_edge_count": known_edge_count,
            "unresolved_edge_count": int(np.count_nonzero(unknown_mask)),
            "known_sign_edge_fraction": known_edge_count / full_edge_count,
            "unresolved_edge_fraction": int(np.count_nonzero(unknown_mask)) / full_edge_count,
            "full_raw_abs_weight_mass": full_abs_mass,
            "known_sign_raw_abs_weight_mass": known_abs_mass,
            "unresolved_raw_abs_weight_mass": int(np.abs(weights[unknown_mask]).sum()),
            "known_sign_weight_mass_fraction": known_abs_mass / full_abs_mass,
            "unresolved_weight_mass_fraction": int(np.abs(weights[unknown_mask]).sum()) / full_abs_mass,
            "zero_rows_full_plus": full_plus_zero_rows,
            "zero_rows_known_plus": known_plus_zero_rows,
            "zero_row_delta_known_minus_full": known_plus_zero_rows - full_plus_zero_rows,
            "known_sign_labels": sorted(PROXY_SIGN_MAP),
            "node_count_by_nt_label": decomposition.get("node_count_by_label", {}),
            "nt_missing_node_count": int(decomposition.get("nt_missing_node_count", 0)),
            "unclear_node_count": int(decomposition.get("unclear_node_count", 0)),
            "edge_count_by_nt_label": decomposition.get("edge_count_by_label", {}),
            "weight_sum_by_nt_label": decomposition.get("weight_sum_by_label", {}),
            "node_vs_edge_scope_note": (
                "node counts describe the admitted node universe; edge and weight "
                "counts describe outgoing support carried by admitted edges"
            ),
            "unknown_source_label_counts": {
                label: int(np.count_nonzero(source_labels == label))
                for label in UNKNOWN_LABELS
            },
        },
        "matched_support": {
            "known_plus_support_equals_known_pm": support_equal,
            "known_plus_raw_magnitude_equals_known_pm": raw_magnitude_delta == 0,
            "known_plus_normalized_magnitude_max_abs_delta": normalized_magnitude_delta,
            "known_plus_normalized_magnitude_equals_known_pm": normalized_magnitude_delta
            <= ADMISSION_TOLERANCE,
            "signed_value_counts": sign_counts,
            "sign_changes_from_plus": int(np.count_nonzero(known_pm_values < 0)),
        },
        "nt_decomposition_receipt": {
            "identity": "Y_admitted = sum_a Y^(a) + Y^(unclear) + Y^(nt_missing)",
            "missing_and_unclear_are_distinct_labels": True,
            "edge_count_identity_holds": bool(decomposition["edge_count_identity_holds"]),
            "weight_sum_identity_holds": bool(decomposition["weight_sum_identity_holds"]),
            "exact_one_source_label_per_admitted_edge": bool(
                decomposition["exact_one_source_label_per_admitted_edge"]
            ),
        },
        "checks": checks,
        "comparison_roles": {
            "Y_full_plus_vs_Y_known_plus": "sign-coverage loss",
            "Y_known_plus_vs_Y_known_pm": "sign effect on identical support and magnitudes",
        },
        "claim_boundary": {
            "supports": [
                "matched-support operator admission",
                "registered sign-coverage and raw-weight-mass accounting",
                "absolute-row-L1 normalization closure",
            ],
            "does_not_support": [
                "signed dynamics or reachable-regime claim",
                "physiological excitation/inhibition claim",
                "causal, behavioral, or in-vivo claim",
            ],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": status, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
