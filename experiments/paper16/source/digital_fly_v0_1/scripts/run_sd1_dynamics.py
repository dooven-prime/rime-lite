#!/usr/bin/env python3
"""Run the registered SD1 matched-support signed-dynamics pilot.

This is deliberately smaller than an attractor census.  It compares
``Y_known_plus`` with ``Y_known_pm`` on identical support and magnitudes, and
uses ``Y_full_plus`` only as a coverage-loss reference.  The sign map remains
a transmitter-only proxy; this script therefore does not make a physiological
excitation/inhibition claim.
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
DEFAULT_OUTPUT = ROOT / "digital_fly_v0_1" / "results" / "sd1_dynamics_v0_1.json"


def portable_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()

ALPHA = 0.2
GAMMA_GRID = (0.9, 1.0, 1.1)
STEPS = 40
X_MAX = 1.0
PULSE = 1.0
INITIAL_STATE_AMPLITUDE = 0.1
NOISE_STD = 0.0
SEED = 20260916
CONVERGENCE_TOLERANCE = 1e-8
PROFILE_EPSILON = 1e-12
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
    matrix = sparse.csr_matrix((normalized, (rows, cols)), shape=(n, n))
    return matrix, normalized


def sector_mean(x: np.ndarray, sector_codes: np.ndarray, sector_count: int) -> np.ndarray:
    sums = np.bincount(sector_codes, weights=x, minlength=sector_count)
    counts = np.bincount(sector_codes, minlength=sector_count)
    return np.divide(sums, counts, out=np.zeros(sector_count), where=counts > 0)


def run_pair(
    operator_a: sparse.csr_matrix,
    operator_b: sparse.csr_matrix,
    gamma: float,
    source: int,
    sector_codes: np.ndarray,
    sector_count: int,
    branch: str,
) -> dict:
    n = operator_a.shape[0]
    xa = np.zeros(n, dtype=np.float64)
    xb = np.zeros(n, dtype=np.float64)
    if branch == "initial_state_probe":
        xa[source] = INITIAL_STATE_AMPLITUDE
        xb[source] = INITIAL_STATE_AMPLITUDE
    elif branch not in {"zero_input", "external_stimulation", "initial_state_probe"}:
        raise ValueError(f"unknown branch: {branch}")

    sector_a = []
    sector_b = []
    norms_a = []
    norms_b = []
    deltas_a = []
    deltas_b = []
    sat_a = []
    sat_b = []
    state_difference_l1 = []
    state_difference_l2 = []
    state_difference_linf = []
    for t in range(STEPS):
        drive_a = gamma * (operator_a.T @ xa)
        drive_b = gamma * (operator_b.T @ xb)
        if branch == "external_stimulation" and t == 0:
            drive_a[source] += PULSE
            drive_b[source] += PULSE
        xa_next = (1.0 - ALPHA) * xa + ALPHA * np.clip(drive_a, 0.0, X_MAX)
        xb_next = (1.0 - ALPHA) * xb + ALPHA * np.clip(drive_b, 0.0, X_MAX)
        sector_a.append(sector_mean(xa_next, sector_codes, sector_count))
        sector_b.append(sector_mean(xb_next, sector_codes, sector_count))
        norms_a.append(float(np.linalg.norm(xa_next)))
        norms_b.append(float(np.linalg.norm(xb_next)))
        deltas_a.append(float(np.linalg.norm(xa_next - xa)))
        deltas_b.append(float(np.linalg.norm(xb_next - xb)))
        sat_a.append(float(np.mean(xa_next >= X_MAX)))
        sat_b.append(float(np.mean(xb_next >= X_MAX)))
        difference = xa_next - xb_next
        state_difference_l1.append(float(np.linalg.norm(difference, ord=1)))
        state_difference_l2.append(float(np.linalg.norm(difference)))
        state_difference_linf.append(float(np.linalg.norm(difference, ord=np.inf)))
        xa, xb = xa_next, xb_next

    sector_a = np.asarray(sector_a)
    sector_b = np.asarray(sector_b)
    return {
        "branch": branch,
        "steps": STEPS,
        "sector_a": sector_a,
        "sector_b": sector_b,
        "norm_a": norms_a,
        "norm_b": norms_b,
        "delta_a": deltas_a,
        "delta_b": deltas_b,
        "sat_a": sat_a,
        "sat_b": sat_b,
        "state_difference_l1": state_difference_l1,
        "state_difference_l2": state_difference_l2,
        "state_difference_linf": state_difference_linf,
    }


def operator_summary(run: dict, side: str) -> dict:
    norm = np.asarray(run[f"norm_{side}"], dtype=np.float64)
    delta = np.asarray(run[f"delta_{side}"], dtype=np.float64)
    saturation = np.asarray(run[f"sat_{side}"], dtype=np.float64)
    return {
        "final_norm_l2": float(norm[-1]),
        "max_norm_l2": float(norm.max(initial=0.0)),
        "final_step_delta_l2": float(delta[-1]),
        "converged_at_tolerance": bool(delta[-1] < CONVERGENCE_TOLERANCE),
        "max_saturation_fraction": float(saturation.max(initial=0.0)),
        "final_saturation_fraction": float(saturation[-1]),
        "l2_norm_history": norm.tolist(),
        "step_delta_l2_history": delta.tolist(),
        "saturation_fraction_history": saturation.tolist(),
    }


def profile(history: np.ndarray, labels: list[str]) -> dict:
    area = np.abs(history).sum(axis=0)
    total = float(area.sum())
    if total <= PROFILE_EPSILON:
        return {
            "status": "ZERO_RESPONSE",
            "total_absolute_response": total,
            "normalized_allocation": None,
            "area": {label: float(area[i]) for i, label in enumerate(labels)},
        }
    probabilities = area / total
    return {
        "status": "VALID",
        "total_absolute_response": total,
        "normalized_allocation": {label: float(probabilities[i]) for i, label in enumerate(labels)},
        "area": {label: float(area[i]) for i, label in enumerate(labels)},
        "peak_absolute_response": {label: float(np.abs(history[:, i]).max(initial=0.0)) for i, label in enumerate(labels)},
        "peak_time_step": {label: int(np.argmax(np.abs(history[:, i])) + 1) for i, label in enumerate(labels)},
    }


def profile_metrics(left: dict, right: dict) -> dict:
    if left.get("normalized_allocation") is None or right.get("normalized_allocation") is None:
        return {"status": "NUMERICALLY_DEGENERATE", "reason": "zero_or_missing_response_profile"}
    labels = list(left["normalized_allocation"])
    p = np.asarray([left["normalized_allocation"][label] for label in labels])
    q = np.asarray([right["normalized_allocation"][label] for label in labels])
    p_norm = float(np.linalg.norm(p))
    q_norm = float(np.linalg.norm(q))
    cosine = float(np.dot(p, q) / (p_norm * q_norm)) if p_norm and q_norm else None
    from scipy.spatial.distance import jensenshannon

    return {
        "status": "VALID",
        "cosine_similarity": cosine,
        "cosine_distance": None if cosine is None else 1.0 - cosine,
        "jensen_shannon_divergence_base2": float(jensenshannon(p, q, base=2.0) ** 2),
    }


def pair_branch_receipt(run: dict, labels: list[str], side_a: str, side_b: str) -> dict:
    return {
        "operator_a": operator_summary(run, side_a),
        "operator_b": operator_summary(run, side_b),
        "paired_state_difference": {
            "l1_history": run["state_difference_l1"],
            "l2_history": run["state_difference_l2"],
            "linf_history": run["state_difference_linf"],
            "peak_l2": float(max(run["state_difference_l2"], default=0.0)),
            "final_l2": float(run["state_difference_l2"][-1]) if run["state_difference_l2"] else 0.0,
        },
        "sector_history_a": run["sector_a"].tolist(),
        "sector_history_b": run["sector_b"].tolist(),
    }


def run_pair_protocol(operator_a: sparse.csr_matrix, operator_b: sparse.csr_matrix, gamma: float, source: int, sector_codes: np.ndarray, labels: list[str], name_a: str, name_b: str) -> dict:
    zero = run_pair(operator_a, operator_b, gamma, source, sector_codes, len(labels), "zero_input")
    stim = run_pair(operator_a, operator_b, gamma, source, sector_codes, len(labels), "external_stimulation")
    init = run_pair(operator_a, operator_b, gamma, source, sector_codes, len(labels), "initial_state_probe")
    response_a = profile(stim["sector_a"] - zero["sector_a"], labels)
    response_b = profile(stim["sector_b"] - zero["sector_b"], labels)
    response_metrics = profile_metrics(response_a, response_b)
    persistence = {}
    for side in ("a", "b"):
        response_norm = np.linalg.norm(stim[f"sector_{side}"] - zero[f"sector_{side}"], axis=1)
        peak = float(response_norm.max(initial=0.0))
        persistence[side] = {
            "peak_sector_response_l2": peak,
            "final_sector_response_l2": float(response_norm[-1]),
            "final_over_peak": float(response_norm[-1] / peak) if peak > PROFILE_EPSILON else None,
            "integrated_sector_response_l2": float(response_norm.sum()),
        }
    return {
        "gamma": gamma,
        "operator_pair": [name_a, name_b],
        "zero_input": pair_branch_receipt(zero, labels, "a", "b"),
        "external_stimulation": pair_branch_receipt(stim, labels, "a", "b"),
        "initial_state_probe": pair_branch_receipt(init, labels, "a", "b"),
        "response_profile_a": response_a,
        "response_profile_b": response_b,
        "response_profile_metrics": response_metrics,
        "response_persistence": persistence,
        "initial_state_dependence": {
            "operator_a_final_norm_l2": float(init["norm_a"][-1]),
            "operator_b_final_norm_l2": float(init["norm_b"][-1]),
            "operator_a_max_norm_l2": float(max(init["norm_a"], default=0.0)),
            "operator_b_max_norm_l2": float(max(init["norm_b"], default=0.0)),
        },
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
    if admission.get("status") != "COMPLETED + VALIDATED" or admission.get("dynamics_status") != "NOT_RUN":
        raise ValueError("SD1 operator-admission receipt is not a clean dynamics input")
    if not all(admission.get("checks", {}).values()):
        raise ValueError("SD1 operator-admission checks are not all true")

    artifacts = manifest["artifacts"]
    edge_path = ROOT / artifacts["edges"]
    node_path = ROOT / artifacts["nodes"]
    edges = np.load(edge_path)
    rows = edges["row"].astype(np.int64, copy=False)
    cols = edges["col"].astype(np.int64, copy=False)
    raw_weights = edges["weight"].astype(np.int64, copy=False)
    weights = raw_weights.astype(np.float64, copy=False)
    nodes = pd.read_parquet(node_path)
    n = len(nodes)
    if len(rows) and int(max(rows.max(), cols.max())) >= n:
        raise ValueError("edge index exceeds frozen node universe")

    labels_nt = nodes["consensus_nt"].astype(str).to_numpy()
    sigma = np.asarray([PROXY_SIGN_MAP.get(label, 0) for label in labels_nt], dtype=np.int8)
    known_mask = sigma[rows] != 0
    known_rows = rows[known_mask]
    known_cols = cols[known_mask]
    known_weights = raw_weights[known_mask]
    known_sigma = sigma[known_rows]

    full_plus, full_norm = normalized_operator(rows, cols, raw_weights, n)
    known_plus, known_plus_norm = normalized_operator(known_rows, known_cols, known_weights, n)
    known_pm_values = known_weights * known_sigma.astype(np.int64)
    known_pm, known_pm_norm = normalized_operator(known_rows, known_cols, known_pm_values, n)

    expected_hashes = admission["operators"]
    actual_hashes = {
        "Y_full_plus": {
            "raw": hash_operator(rows, cols, raw_weights, (n, n)),
            "normalized": hash_operator(rows, cols, full_norm, (n, n)),
        },
        "Y_known_plus": {
            "raw": hash_operator(known_rows, known_cols, known_weights, (n, n)),
            "normalized": hash_operator(known_rows, known_cols, known_plus_norm, (n, n)),
        },
        "Y_known_pm": {
            "raw": hash_operator(known_rows, known_cols, known_pm_values, (n, n)),
            "normalized": hash_operator(known_rows, known_cols, known_pm_norm, (n, n)),
        },
    }
    expected_hash_lookup = {
        "Y_full_plus": (expected_hashes["Y_full_plus"]["raw_operator_sha256"], expected_hashes["Y_full_plus"]["normalized_operator_sha256"]),
        "Y_known_plus": (expected_hashes["Y_known_plus"]["raw_operator_sha256"], expected_hashes["Y_known_plus"]["normalized_operator_sha256"]),
        "Y_known_pm": (expected_hashes["Y_known_pm"]["raw_operator_sha256"], expected_hashes["Y_known_pm"]["normalized_operator_sha256"]),
    }
    hash_checks = {
        name: actual_hashes[name]["raw"] == raw_hash and actual_hashes[name]["normalized"] == norm_hash
        for name, (raw_hash, norm_hash) in expected_hash_lookup.items()
    }
    if not all(hash_checks.values()):
        raise ValueError(f"operator hash mismatch against admission receipt: {hash_checks}")

    sector_values = nodes["superclass"].astype("string").fillna("<missing>").astype(str)
    sector_labels = sorted(sector_values.unique().tolist())
    sector_codes = np.asarray([sector_labels.index(value) for value in sector_values], dtype=np.int32)
    source = int(np.argmax(np.bincount(rows, minlength=n))) if n else 0
    if int(nodes.iloc[source]["bodyId"]) != 10093:
        raise ValueError("registered SD1 source changed")

    sign_runs = []
    coverage_runs = []
    for gamma in GAMMA_GRID:
        sign_runs.append(run_pair_protocol(known_plus, known_pm, gamma, source, sector_codes, sector_labels, "Y_known_plus", "Y_known_pm"))
        coverage_runs.append(run_pair_protocol(full_plus, known_plus, gamma, source, sector_codes, sector_labels, "Y_full_plus", "Y_known_plus"))

    output = {
        "schema": "rime.exploratory.digital-fly-sd1-dynamics.v0_1",
        "status": "COMPLETED + VALIDATED",
        "evidence_level": "Computational Observation",
        "purpose": "matched-support signed structural proxy dynamics; coverage reference included; no attractor census",
        "v0_artifact_boundary": "frozen v0 carrier and SD1 operator-admission receipt are read-only",
        "dynamics_status": "COMPLETED + VALIDATED",
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
            "operator_pair_primary": ["Y_known_plus", "Y_known_pm"],
            "operator_pair_coverage_reference": ["Y_full_plus", "Y_known_plus"],
            "alpha": ALPHA,
            "gamma_grid": list(GAMMA_GRID),
            "gain_bands": {"0.9": "subcritical_reference", "1.0": "critical_boundary", "1.1": "supercritical_probe"},
            "steps": STEPS,
            "x_max": X_MAX,
            "pulse": PULSE,
            "initial_state_probe_amplitude": INITIAL_STATE_AMPLITUDE,
            "noise_std": NOISE_STD,
            "seed": SEED,
            "activation": "clipped_relu(phi(z)=min(x_max,max(0,z)))",
            "normalization": "absolute outgoing-row-L1; sum_j |Y_norm[i,j]| = 1 on nonzero rows",
            "same_support_and_magnitudes_primary_pair": True,
            "seed_semantics": "deterministic branch; seed retained for protocol identity and has no state-update effect",
        },
        "theory_receipt": {
            "q_bound_formula": "q = (1-alpha) + alpha*gamma",
            "q_bound_by_gamma": {str(gamma): (1.0 - ALPHA) + ALPHA * gamma for gamma in GAMMA_GRID},
            "q_bound_interpretation": "contraction-type bound applies to 1-Lipschitz dynamics below gamma=1; gamma=1 is boundary and gamma=1.1 is a probe",
            "row_absolute_l1_closure": True,
        },
        "operator_hashes": actual_hashes,
        "hash_checks_against_admission": hash_checks,
        "source": {
            "node_index": source,
            "body_id": int(nodes.iloc[source]["bodyId"]),
            "superclass": str(nodes.iloc[source]["superclass"]),
            "consensus_nt": str(nodes.iloc[source]["consensus_nt"]),
        },
        "observation": {
            "field": "superclass",
            "labels": sector_labels,
            "definition": "Z_i(t) = mean_{j in S_i} x_j(t)",
            "estimand": "single-source sector-mean response; no sector quotient as state carrier",
            "sector_sizes": {label: int(np.count_nonzero(sector_codes == i)) for i, label in enumerate(sector_labels)},
        },
        "intervention_typing": {
            "external_stimulation": "u_j(t) != 0; source pulse at t=0",
            "state_perturbation": "x_j(t) -> x_j(t) + delta; not run",
            "structural_lesion": "not run in SD1 dynamics; reserved for D1/O1 extension",
        },
        "primary_sign_effect": {
            "definition": "Delta_sign(t) = ||x_known_pm(t) - x_known_plus(t)||",
            "response_definition": "paired stimulated-minus-zero sector response profiles on identical support and magnitudes",
            "runs": sign_runs,
        },
        "coverage_reference": {
            "definition": "Delta_coverage(t) = ||x_full_plus(t) - x_known_plus(t)||",
            "interpretation": "coverage-loss reference only; not a sign effect",
            "runs": coverage_runs,
        },
        "claim_boundary": {
            "supports": [
                "model-relative sign-effect and coverage-effect comparison",
                "registered gain-band response, clipping, convergence, persistence, and initial-state summaries",
                "transmitter-only signed structural proxy dynamics",
            ],
            "does_not_support": [
                "physiological excitation/inhibition claim",
                "receptor-validated connectivity",
                "biological causality or in-vivo equivalence",
                "attractor, limit-cycle, multistability, behavior, embodiment, intelligence, or consciousness claim",
            ],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": output["status"], "hash_checks": hash_checks}, indent=2))


if __name__ == "__main__":
    main()
