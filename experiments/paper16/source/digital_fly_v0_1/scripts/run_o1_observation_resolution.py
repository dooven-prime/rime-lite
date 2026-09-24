#!/usr/bin/env python3
"""Run the registered O1 observation-resolution profile.

O1 keeps a single node-basis carrier and asks how a paired structural-lesion
effect survives four readouts.  It is intentionally a small source-stratified
profile, not a source census or a behavioral experiment.
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
DEFAULT_ADMISSION = ROOT / "digital_fly_v0_1" / "results" / "sd1_operator_admission_v0_1.json"
DEFAULT_OUTPUT = ROOT / "digital_fly_v0_1" / "results" / "o1_observation_resolution_v0_1.json"


def portable_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()

ALPHA = 0.2
GAMMA = 1.0
STEPS = 40
X_MAX = 1.0
PULSE = 1.0
NOISE_STD = 0.0
SEED = 20260916
QUANTILE = 0.95
QUANTILE_METHOD = "linear"
PROFILE_EPSILON = 1e-12
PROXY_SIGN_MAP = {
    "acetylcholine": 1,
    "dopamine": 1,
    "gaba": -1,
    "glutamate": 1,
    "histamine": 1,
    "octopamine": 1,
    "serotonin": 1,
}

# Explicitly registered source strata. These are acetylcholine sources chosen
# to keep NT class fixed while spanning a clear small/medium/large sector-size
# range and approximately matching known outgoing degree/raw mass. The receipt
# records the matching quantities and target-sector diversity.
REGISTERED_SOURCES = {
    "small": {"sector": "vnc_sensory_tbc", "body_id": 836544},
    "medium": {"sector": "sensory_ascending", "body_id": 64272},
    "large": {"sector": "ol_intrinsic", "body_id": 530902},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_operator(rows: np.ndarray, cols: np.ndarray, data: np.ndarray, shape: tuple[int, int]) -> str:
    digest = hashlib.sha256()
    digest.update(np.asarray(shape, dtype=np.int64).tobytes())
    for array in (rows, cols, data):
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(np.asarray(contiguous.shape, dtype=np.int64).tobytes())
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def normalized_operator(rows: np.ndarray, cols: np.ndarray, values: np.ndarray, n: int) -> tuple[sparse.csr_matrix, np.ndarray]:
    row_abs = np.bincount(rows, weights=np.abs(values).astype(np.float64), minlength=n)
    if np.any(row_abs[rows] <= 0.0):
        raise ValueError("an admitted edge has zero absolute source-row mass")
    normalized = values.astype(np.float64, copy=False) / row_abs[rows]
    return sparse.csr_matrix((normalized, (rows, cols)), shape=(n, n)), normalized


def observations(
    x: np.ndarray,
    sector_codes: np.ndarray,
    sector_labels: list[str],
    local_targets: np.ndarray,
) -> dict[str, np.ndarray]:
    count = len(sector_labels)
    sums = np.bincount(sector_codes, weights=x, minlength=count)
    counts = np.bincount(sector_codes, minlength=count)
    mean = np.divide(sums, counts, out=np.zeros(count), where=counts > 0)
    rms = np.zeros(count, dtype=np.float64)
    q95 = np.zeros(count, dtype=np.float64)
    for i in range(count):
        values = x[sector_codes == i]
        if len(values):
            rms[i] = float(np.sqrt(np.mean(values * values)))
            q95[i] = float(np.quantile(values, QUANTILE, method=QUANTILE_METHOD))
    local = np.asarray(
        [float(np.mean(x[local_targets])) if len(local_targets) else 0.0], dtype=np.float64
    )
    return {"mean": mean, "rms": rms, "q95": q95, "local": local}


def run_trajectory(
    operator: sparse.csr_matrix,
    source: int,
    sector_codes: np.ndarray,
    sector_labels: list[str],
    local_targets: np.ndarray,
    pulse: float,
) -> dict:
    n = operator.shape[0]
    x = np.zeros(n, dtype=np.float64)
    histories = {name: [] for name in ("mean", "rms", "q95", "local")}
    l2_norm = []
    step_delta = []
    saturation = []
    for t in range(STEPS):
        drive = GAMMA * (operator.T @ x)
        if t == 0 and pulse:
            drive[source] += pulse
        x_next = (1.0 - ALPHA) * x + ALPHA * np.clip(drive, 0.0, X_MAX)
        obs = observations(x_next, sector_codes, sector_labels, local_targets)
        for name, value in obs.items():
            histories[name].append(value)
        l2_norm.append(float(np.linalg.norm(x_next)))
        step_delta.append(float(np.linalg.norm(x_next - x)))
        saturation.append(float(np.mean(x_next >= X_MAX)))
        x = x_next
    return {
        "pulse": pulse,
        "mean_history": np.asarray(histories["mean"]),
        "rms_history": np.asarray(histories["rms"]),
        "q95_history": np.asarray(histories["q95"]),
        "local_history": np.asarray(histories["local"]),
        "l2_norm_history": l2_norm,
        "step_delta_l2_history": step_delta,
        "saturation_fraction_history": saturation,
    }


def effect_summary(effect: np.ndarray, labels: list[str]) -> dict:
    if effect.ndim != 2 or not np.all(np.isfinite(effect)):
        return {"status": "NUMERICALLY_DEGENERATE"}
    area = np.abs(effect).sum(axis=0)
    signed = effect.sum(axis=0)
    peak = np.abs(effect).max(axis=0)
    peak_t = np.argmax(np.abs(effect), axis=0) + 1
    total = float(area.sum())
    return {
        "status": "VALID" if total > PROFILE_EPSILON else "ZERO_RESPONSE",
        "dimension_labels": labels,
        "integrated_absolute_effect": {label: float(area[i]) for i, label in enumerate(labels)},
        "integrated_signed_effect": {label: float(signed[i]) for i, label in enumerate(labels)},
        "peak_absolute_effect": {label: float(peak[i]) for i, label in enumerate(labels)},
        "peak_time_step": {label: int(peak_t[i]) for i, label in enumerate(labels)},
        "total_integrated_absolute_effect": total,
        "max_absolute_effect": float(peak.max(initial=0.0)),
    }


def branch_summary(run: dict) -> dict:
    delta = np.asarray(run["step_delta_l2_history"])
    sat = np.asarray(run["saturation_fraction_history"])
    return {
        "final_l2_norm": float(run["l2_norm_history"][-1]),
        "max_l2_norm": float(max(run["l2_norm_history"], default=0.0)),
        "final_step_delta_l2": float(delta[-1]),
        "converged_at_tolerance_1e-8": bool(delta[-1] < 1e-8),
        "max_saturation_fraction": float(sat.max(initial=0.0)),
        "final_saturation_fraction": float(sat[-1]),
    }


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
    if admission.get("status") != "COMPLETED + VALIDATED" or not all(admission.get("checks", {}).values()):
        raise ValueError("SD1 operator-admission receipt is not validated")

    edge_path = ROOT / manifest["artifacts"]["edges"]
    node_path = ROOT / manifest["artifacts"]["nodes"]
    edges = np.load(edge_path)
    rows = edges["row"].astype(np.int64, copy=False)
    cols = edges["col"].astype(np.int64, copy=False)
    raw_weights = edges["weight"].astype(np.int64, copy=False)
    nodes = pd.read_parquet(node_path)
    n = len(nodes)
    nt = nodes["consensus_nt"].astype(str).to_numpy()
    sector_values = nodes["superclass"].astype("string").fillna("<missing>").astype(str).to_numpy()
    sector_labels = sorted(np.unique(sector_values).tolist())
    sector_codes = np.asarray([sector_labels.index(value) for value in sector_values], dtype=np.int32)

    sigma_by_node = np.asarray([PROXY_SIGN_MAP.get(value, 0) for value in nt], dtype=np.int8)
    known_mask = sigma_by_node[rows] != 0
    known_rows = rows[known_mask]
    known_cols = cols[known_mask]
    known_weights = raw_weights[known_mask]
    known_sigma = sigma_by_node[known_rows]
    known_values = known_weights * known_sigma.astype(np.int64)
    operator, normalized_values = normalized_operator(known_rows, known_cols, known_values, n)
    expected = admission["operators"]["Y_known_pm"]
    actual_raw_hash = hash_operator(known_rows, known_cols, known_values, (n, n))
    actual_norm_hash = hash_operator(known_rows, known_cols, normalized_values, (n, n))
    hash_checks = {
        "raw": actual_raw_hash == expected["raw_operator_sha256"],
        "normalized": actual_norm_hash == expected["normalized_operator_sha256"],
    }
    if not all(hash_checks.values()):
        raise ValueError(f"Y_known_pm hash mismatch: {hash_checks}")

    node_degree = np.bincount(known_rows, minlength=n)
    node_mass = np.bincount(known_rows, weights=known_weights, minlength=n)
    target_sector_pairs = sparse.coo_matrix(
        (np.ones(len(known_rows), dtype=np.int8), (known_rows, sector_codes[known_cols])),
        shape=(n, len(sector_labels)),
    ).tocsr()
    target_sector_count = np.diff(target_sector_pairs.indptr)

    source_receipts = {}
    for stratum, registration in REGISTERED_SOURCES.items():
        body_id = registration["body_id"]
        matches = np.flatnonzero(nodes["bodyId"].to_numpy() == body_id)
        if len(matches) != 1:
            raise ValueError(f"registered body_id not unique: {body_id}")
        source = int(matches[0])
        if str(sector_values[source]) != registration["sector"]:
            raise ValueError(f"source {body_id} changed sector")
        if str(nt[source]) != "acetylcholine" or node_degree[source] <= 0:
            raise ValueError(f"source {body_id} is not an active known-sign acetylcholine source")
        targets = np.unique(known_cols[known_rows == source])
        source_receipts[stratum] = {
            "body_id": body_id,
            "node_index": source,
            "sector": str(sector_values[source]),
            "sector_size": int(np.count_nonzero(sector_values == sector_values[source])),
            "consensus_nt": str(nt[source]),
            "known_out_degree": int(node_degree[source]),
            "known_out_raw_weight_mass": int(node_mass[source]),
            "known_out_target_sector_count": int(target_sector_count[source]),
            "local_target_node_count": int(len(targets)),
            "local_target_definition": "unique direct known-sign targets of the registered source",
        }

    results = {}
    lesion_hashes = {}
    for stratum, source_info in source_receipts.items():
        source = source_info["node_index"]
        local_targets = np.unique(known_cols[known_rows == source])
        lesion = operator.copy().tolil()
        lesion[source, :] = 0.0
        lesion = lesion.tocsr()
        lesion.eliminate_zeros()
        lesion_hashes[stratum] = {
            "lesion_type": "structural_lesion_remove_all_outgoing_source_edges",
            "source_node_index": source,
            "baseline_normalized_operator_sha256": actual_norm_hash,
            "lesion_nnz": int(lesion.nnz),
        }
        base_zero = run_trajectory(operator, source, sector_codes, sector_labels, local_targets, 0.0)
        base_stim = run_trajectory(operator, source, sector_codes, sector_labels, local_targets, PULSE)
        lesion_zero = run_trajectory(lesion, source, sector_codes, sector_labels, local_targets, 0.0)
        lesion_stim = run_trajectory(lesion, source, sector_codes, sector_labels, local_targets, PULSE)
        effects = {}
        labels_by_obs = {
            "mean": sector_labels,
            "rms": sector_labels,
            "q95": sector_labels,
            "local": ["direct_target_mean"],
        }
        for obs_name, labels in labels_by_obs.items():
            base_delta = base_stim[f"{obs_name}_history"] - base_zero[f"{obs_name}_history"]
            lesion_delta = lesion_stim[f"{obs_name}_history"] - lesion_zero[f"{obs_name}_history"]
            effect = lesion_delta - base_delta
            effects[obs_name] = effect_summary(effect, labels)
        mean_total = effects["mean"]["total_integrated_absolute_effect"]
        for value in effects.values():
            value["visibility_ratio_to_mean"] = (
                value["total_integrated_absolute_effect"] / mean_total
                if mean_total > PROFILE_EPSILON else None
            )
        results[stratum] = {
            "source": source_info,
            "protocol": {
                "carrier": "Y_known_pm",
                "gamma": GAMMA,
                "alpha": ALPHA,
                "steps": STEPS,
                "pulse": PULSE,
                "noise_std": NOISE_STD,
                "seed": SEED,
                "observation_order": "mean, rms, q95, local",
            },
            "branches": {
                "base_zero": branch_summary(base_zero),
                "base_stimulation": branch_summary(base_stim),
                "lesion_zero": branch_summary(lesion_zero),
                "lesion_stimulation": branch_summary(lesion_stim),
            },
            "paired_effect_definition": "E_O = (O(x_lesion+stim)-O(x_lesion,zero)) - (O(x_base+stim)-O(x_base,zero))",
            "effects": effects,
        }

    output = {
        "schema": "rime.exploratory.digital-fly-o1-observation-resolution.v0_1",
        "status": "COMPLETED + VALIDATED",
        "evidence_level": "Computational Observation",
        "purpose": "paired lesion visibility across declared observation functionals and source-sector sizes",
        "v0_artifact_boundary": "frozen v0 carrier and SD1 operator-admission receipt are read-only",
        "dynamics_status": "COMPLETED + VALIDATED",
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
        "operator_orientation": "source_row_target_column; incoming=Y.T@x",
        "registration": {
            "source_strata": list(REGISTERED_SOURCES),
            "registered_sources": REGISTERED_SOURCES,
            "gamma": GAMMA,
            "alpha": ALPHA,
            "steps": STEPS,
            "x_max": X_MAX,
            "pulse": PULSE,
            "noise_std": NOISE_STD,
            "seed": SEED,
            "lesion": "remove all outgoing edges from the registered source row; no renormalization of other rows",
            "source_matching": "same acetylcholine class; source-sector size stratified; outgoing known degree, raw mass, and target-sector count recorded",
        },
        "observation_contract": {
            "O_mean": "sector mean",
            "O_rms": "sqrt(sector mean of x^2)",
            "O_q95": "sector 0.95 quantile with linear interpolation",
            "O_local": "mean activity over unique direct known-sign target nodes of the registered source",
            "empty_sector_policy": "zero vector; no empty sectors in frozen carrier",
            "profile_epsilon": PROFILE_EPSILON,
            "max_not_used": True,
        },
        "operator_hash": {
            "Y_known_pm_raw": actual_raw_hash,
            "Y_known_pm_normalized": actual_norm_hash,
            "matches_admission": hash_checks,
        },
        "source_receipts": source_receipts,
        "lesion_receipts": lesion_hashes,
        "results": results,
        "claim_boundary": {
            "supports": [
                "model-relative observation-resolution profile",
                "paired structural-lesion visibility comparison across source-sector sizes",
                "mean-observation dilution versus local and distributional readouts",
            ],
            "does_not_support": [
                "biological necessity or causal lesion claim",
                "physiological E/I claim",
                "behavior, embodiment, intelligence, or consciousness claim",
            ],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": output["status"], "hash_checks": hash_checks}, indent=2))


if __name__ == "__main__":
    main()
