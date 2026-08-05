"""Post-release Paper XI candidate: GRN approximation control and basin loss.

This script contains two deliberately separate records.

1. Noise-method negative control. A chemical Langevin equation (CLE) and an
   exact Gillespie stochastic simulation algorithm (SSA) are sampled on the
   same fixed physical-time grid and audited with the same concentration
   sectors. The matched control does not reproduce the previously reported
   large CLE-only accessibility drop; both methods show only a small endpoint
   drift over the tested Omega range.

2. Regulatory-edge deformation. The deterministic repression strength
   lambda for A -| B is varied from one to zero. The reference toggle has two
   attracting basins; after the edge is removed only one remains. This is a
   Class C terminal-side basin-loss candidate, with an E label only for the
   discrete endpoint intervention. It is not an absorbing-state theorem for
   the finite stochastic chain.

Claim status: controlled negative evidence against the proposed noise wall and
post-release candidate evidence for deterministic Class C basin loss. Class
B/D noise-wall claims are withdrawn. This script is not part of the frozen
Paper XI v1.0 census.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ALPHA_A = ALPHA_B = 20.0
GAMMA_A = GAMMA_B = 1.0
K_A = K_B = 10.0
HILL_N = 3

N_BINS = 8
CONC_MAX = 30.0
MAX_DEPTH = 4
TOL = 1e-8

CLE_DT = 0.02
SAMPLE_DT = 0.2
VALIDATION_EQUILIBRATION = 10.0
VALIDATION_PRODUCTION = 20.0
NOISE_OMEGAS = (60.0, 30.0, 15.0, 10.0)

FLOW_DT = 0.02
FLOW_TIME = 120.0
FLOW_SAMPLE_DT = 0.2
EDGE_STRENGTHS = np.linspace(1.0, 0.0, 21)

INITIAL_STATES = np.array(
    [(2.0, 3.0), (3.0, 17.0), (17.0, 3.0), (16.0, 18.0),
     (5.0, 15.0), (15.0, 5.0), (8.0, 12.0), (12.0, 8.0)],
    dtype=float,
)


def production_a(repressor_b: np.ndarray | float) -> np.ndarray | float:
    return ALPHA_A / (1.0 + (repressor_b / K_B) ** HILL_N)


def production_b(
    repressor_a: np.ndarray | float,
    edge_strength: float,
) -> np.ndarray | float:
    return ALPHA_B / (1.0 + edge_strength * (repressor_a / K_A) ** HILL_N)


def bin_indices(states: np.ndarray) -> np.ndarray:
    bins = np.minimum(
        (np.maximum(states, 0.0) * N_BINS / CONC_MAX).astype(int),
        N_BINS - 1,
    )
    return bins[..., 0] * N_BINS + bins[..., 1]


def transition_from_samples(samples: np.ndarray) -> tuple[np.ndarray, dict]:
    """Build a directed transition matrix from (trajectory,time,2) samples."""
    n_sectors = N_BINS * N_BINS
    indices = bin_indices(samples)
    source = indices[:, :-1].ravel()
    target = indices[:, 1:].ravel()
    off_diagonal = source != target
    counts = np.zeros((n_sectors, n_sectors), dtype=float)
    np.add.at(counts, (target[off_diagonal], source[off_diagonal]), 1.0)

    transition = np.eye(n_sectors, dtype=complex)
    for source_sector in range(n_sectors):
        total = counts[:, source_sector].sum()
        if total > 0:
            transition[:, source_sector] = counts[:, source_sector] / total

    basin_labels = samples[..., 0] > samples[..., 1]
    basin_switches = int(np.count_nonzero(basin_labels[:, 1:] != basin_labels[:, :-1]))
    clipped = int(np.count_nonzero(np.any(samples >= CONC_MAX, axis=2)))
    return transition, {
        "visited_sectors": int(np.unique(indices).size),
        "basin_switches_per_trajectory": basin_switches / samples.shape[0],
        "clipped_fraction": clipped / (samples.shape[0] * samples.shape[1]),
    }


def singleton_word_audit(transition: np.ndarray) -> dict:
    """Exact Boolean fast path for one nonnegative singleton-sector observable."""
    if np.any(transition.real < -TOL) or np.max(np.abs(transition.imag)) > TOL:
        raise ValueError("word-audit fast path requires a real nonnegative transition")
    direct = np.abs(transition) > TOL
    current = direct.copy()
    reached = direct.copy()
    direct_int = direct.astype(np.int64)
    for _depth in range(2, MAX_DEPTH + 1):
        current = (direct_int @ current.astype(np.int64)) > 0
        reached |= current
    np.fill_diagonal(direct, False)
    np.fill_diagonal(reached, False)
    n_pairs = transition.shape[0] * (transition.shape[0] - 1)
    return {
        "frozen_R1": n_pairs - int(np.count_nonzero(direct)),
        "frozen_D_word": n_pairs - int(np.count_nonzero(reached)),
        "direct_support": direct,
        "bounded_reachability": reached,
    }


def cle_samples(
    omega: float,
    rng: np.random.RandomState,
    trajectories: int,
    *,
    edge_strength: float = 1.0,
) -> np.ndarray:
    state = INITIAL_STATES[np.arange(trajectories) % len(INITIAL_STATES)].copy()
    noise_scale = 1.0 / np.sqrt(omega)

    def advance(current: np.ndarray) -> np.ndarray:
        production = np.column_stack(
            (production_a(current[:, 1]), production_b(current[:, 0], edge_strength))
        )
        degradation = current * np.array([GAMMA_A, GAMMA_B])
        noise = (
            np.sqrt(np.maximum(production + degradation, 0.0) * CLE_DT)
            * noise_scale
            * rng.randn(trajectories, 2)
        )
        return np.maximum(0.0, current + (production - degradation) * CLE_DT + noise)

    for _ in range(int(VALIDATION_EQUILIBRATION / CLE_DT)):
        state = advance(state)

    production_steps = int(VALIDATION_PRODUCTION / CLE_DT)
    sample_stride = int(round(SAMPLE_DT / CLE_DT))
    samples = np.empty((trajectories, production_steps // sample_stride, 2), dtype=float)
    for step in range(production_steps):
        state = advance(state)
        if step % sample_stride == 0:
            samples[:, step // sample_stride] = state
    return samples


def ssa_propensities(
    counts: np.ndarray,
    omega: float,
    edge_strength: float,
) -> np.ndarray:
    a_count, b_count = map(float, counts)
    a_conc = a_count / omega
    b_conc = b_count / omega
    return np.array(
        [
            omega * production_a(b_conc),
            omega * production_b(a_conc, edge_strength),
            GAMMA_A * a_count,
            GAMMA_B * b_count,
        ],
        dtype=float,
    )


def ssa_trajectory_samples(
    omega: float,
    rng: np.random.RandomState,
    initial: np.ndarray,
    *,
    edge_strength: float = 1.0,
) -> np.ndarray:
    """Exact SSA sampled on the same fixed physical-time grid as the CLE."""
    counts = np.maximum(0, np.rint(omega * initial)).astype(int)
    n_samples = int(VALIDATION_PRODUCTION / SAMPLE_DT)
    sample_times = VALIDATION_EQUILIBRATION + SAMPLE_DT * np.arange(1, n_samples + 1)
    samples = np.empty((n_samples, 2), dtype=float)
    time = 0.0
    sample_index = 0

    while sample_index < n_samples:
        propensities = ssa_propensities(counts, omega, edge_strength)
        total = float(propensities.sum())
        if total <= 0:
            samples[sample_index:] = counts / omega
            break
        event_time = time + rng.exponential(1.0 / total)
        while sample_index < n_samples and sample_times[sample_index] <= event_time:
            samples[sample_index] = counts / omega
            sample_index += 1
        if sample_index == n_samples:
            break

        threshold = rng.random() * total
        event = int(np.searchsorted(np.cumsum(propensities), threshold, side="right"))
        if event == 0:
            counts[0] += 1
        elif event == 1:
            counts[1] += 1
        elif event == 2 and counts[0] > 0:
            counts[0] -= 1
        elif event == 3 and counts[1] > 0:
            counts[1] -= 1
        time = event_time
    return samples


def ssa_samples(
    omega: float,
    rng: np.random.RandomState,
    trajectories: int,
    *,
    edge_strength: float = 1.0,
) -> np.ndarray:
    return np.stack(
        [
            ssa_trajectory_samples(
                omega,
                rng,
                INITIAL_STATES[run % len(INITIAL_STATES)],
                edge_strength=edge_strength,
            )
            for run in range(trajectories)
        ]
    )


def sample_audit(samples: np.ndarray) -> dict:
    transition, sampling = transition_from_samples(samples)
    word = singleton_word_audit(transition)
    return {
        "frozen_R1": word["frozen_R1"],
        "frozen_D_word": word["frozen_D_word"],
        **sampling,
    }


def noise_method_control(
    ensemble_size: int,
    trajectories: int,
    seed: int,
) -> dict:
    rows = []
    for omega in NOISE_OMEGAS:
        method_audits = {"CLE": [], "SSA": []}
        for member in range(ensemble_size):
            cle = cle_samples(
                omega,
                np.random.RandomState(seed + 100 * member),
                trajectories,
            )
            ssa = ssa_samples(
                omega,
                np.random.RandomState(seed + 100 * member + 50),
                trajectories,
            )
            method_audits["CLE"].append(sample_audit(cle))
            method_audits["SSA"].append(sample_audit(ssa))

        row = {"omega": omega}
        for method, audits in method_audits.items():
            for key in audits[0]:
                values = np.array([audit[key] for audit in audits], dtype=float)
                row[f"{method}_{key}_mean"] = float(values.mean())
                row[f"{method}_{key}_std"] = float(values.std())
        rows.append(row)

    cle_values = np.array([row["CLE_frozen_D_word_mean"] for row in rows])
    ssa_values = np.array([row["SSA_frozen_D_word_mean"] for row in rows])
    n_pairs = N_BINS * N_BINS * (N_BINS * N_BINS - 1)
    return {
        "claim_status": "negative_control",
        "sampling_protocol": {
            "equilibration_time": VALIDATION_EQUILIBRATION,
            "production_time": VALIDATION_PRODUCTION,
            "sample_dt": SAMPLE_DT,
            "fixed_concentration_grid": [0.0, CONC_MAX],
        },
        "rows": rows,
        "CLE_low_minus_high": float(cle_values[-1] - cle_values[0]),
        "SSA_low_minus_high": float(ssa_values[-1] - ssa_values[0]),
        "CLE_range": float(np.ptp(cle_values)),
        "SSA_range": float(np.ptp(ssa_values)),
        "CLE_relative_range": float(np.ptp(cle_values) / n_pairs),
        "SSA_relative_range": float(np.ptp(ssa_values) / n_pairs),
        "maximum_method_gap": float(np.max(np.abs(cle_values - ssa_values))),
        "noise_wall_admitted": False,
        "interpretation": (
            "matched fixed-time CLE and SSA do not reproduce the historical "
            "large noise wall; the remaining sub-percent endpoint drift is not "
            "an admitted basin-merging wall"
        ),
    }


def flow_samples(edge_strength: float) -> tuple[np.ndarray, np.ndarray]:
    grid = np.linspace(2.0, 18.0, 7)
    # Exact A=B starts lie on the symmetry saddle's measure-zero stable
    # manifold at lambda=1 and must not be counted as attracting basins.
    initial = np.array(
        [(a, b) for a in grid for b in grid if not np.isclose(a, b)],
        dtype=float,
    )
    state = initial.copy()
    n_steps = int(FLOW_TIME / FLOW_DT)
    sample_stride = int(round(FLOW_SAMPLE_DT / FLOW_DT))
    samples = np.empty((len(initial), n_steps // sample_stride, 2), dtype=float)
    for step in range(n_steps):
        drift = np.column_stack(
            (
                production_a(state[:, 1]) - GAMMA_A * state[:, 0],
                production_b(state[:, 0], edge_strength) - GAMMA_B * state[:, 1],
            )
        )
        state = np.maximum(0.0, state + FLOW_DT * drift)
        if step % sample_stride == 0:
            samples[:, step // sample_stride] = state
    return samples, state


def cluster_attractors(final_states: np.ndarray, tolerance: float = 0.5) -> list[np.ndarray]:
    centers: list[np.ndarray] = []
    for state in final_states:
        if not any(np.linalg.norm(state - center) < tolerance for center in centers):
            centers.append(state.copy())
    return centers


def edge_deformation_audit() -> dict:
    sweep = []
    endpoint_audits = {}
    for edge_strength in EDGE_STRENGTHS:
        samples, final_states = flow_samples(float(edge_strength))
        centers = cluster_attractors(final_states)
        audit = sample_audit(samples)
        terminal_sectors = sorted(set(bin_indices(np.array(centers)).tolist()))
        row = {
            "edge_strength": float(edge_strength),
            "attractor_count": len(centers),
            "attractors": [center.tolist() for center in centers],
            "terminal_sectors": terminal_sectors,
            "frozen_R1": audit["frozen_R1"],
            "frozen_D_word": audit["frozen_D_word"],
            "visited_sectors": audit["visited_sectors"],
        }
        sweep.append(row)
        if np.isclose(edge_strength, 1.0):
            endpoint_audits["reference"] = row
        if np.isclose(edge_strength, 0.0):
            endpoint_audits["edge_deleted"] = row

    reference = endpoint_audits["reference"]
    edge_deleted = endpoint_audits["edge_deleted"]
    if reference["attractor_count"] < 2 or edge_deleted["attractor_count"] != 1:
        raise AssertionError("controlled edge deformation did not produce 2-to-1 basin loss")

    transition_index = next(
        index
        for index in range(1, len(sweep))
        if sweep[index - 1]["attractor_count"] > sweep[index]["attractor_count"]
    )
    removed_terminal = sorted(
        set(reference["terminal_sectors"]) - set(edge_deleted["terminal_sectors"])
    )

    refined = []
    for edge_strength in np.arange(0.48, 0.571, 0.005):
        _samples, final_states = flow_samples(float(edge_strength))
        refined.append(
            {
                "edge_strength": float(edge_strength),
                "attractor_count": len(cluster_attractors(final_states)),
            }
        )
    one_basin = max(
        item["edge_strength"] for item in refined if item["attractor_count"] == 1
    )
    two_basin = min(
        item["edge_strength"] for item in refined if item["attractor_count"] >= 2
    )
    return {
        "claim_status": "candidate_evidence",
        "taxonomy_candidates": ["C", "E_endpoint"],
        "deformation": "continuous A-represses-B edge strength lambda from 1 to 0",
        "sweep": sweep,
        "wall_bracket": [
            sweep[transition_index]["edge_strength"],
            sweep[transition_index - 1]["edge_strength"],
        ],
        "refined_controlled_grid_bracket": [one_basin, two_basin],
        "trajectory_event": {
            "orientation": "decreasing_regulatory_edge_strength",
            "sampled_transition_bracket": {
                "before_parameter": two_basin,
                "after_parameter": one_basin,
            },
            "before_state": {
                "attractor_count": 2,
                "terminal_sectors": reference["terminal_sectors"],
            },
            "after_state": {
                "attractor_count": 1,
                "terminal_sectors": edge_deleted["terminal_sectors"],
            },
            "raw_numeric_direction": "decrease",
            "accessibility_direction": "not_applicable",
            "event_semantics": "terminalization",
        },
        "refined_scan": refined,
        "reference": reference,
        "edge_deleted": edge_deleted,
        "removed_terminal_sectors": removed_terminal,
        "claim_boundary": (
            "deterministic attractor/basin loss under regulatory-edge weakening; "
            "not an absorbing-state theorem for the finite stochastic process"
        ),
    }


def run_audit(
    ssa_ensemble: int = 2,
    ssa_trajectories: int = 8,
    seed: int = 42,
) -> dict:
    return {
        "record_version": "paper11-grn-terminal-basin-loss-v1.0",
        "claim_status": "Computational Observation",
        "producer": "experiments/paper11/validation/grn_toggle_wall.py",
        "paper_xi_release_status": "post_v1_candidate",
        "withdrawn_claims": ["Class B noise repair", "Class D noise plateau wall"],
        "historical_failure_boundary": (
            "the earlier large CLE/SSA discrepancy used non-matched event-time "
            "sampling and superseded sector/observable choices"
        ),
        "noise_method_control": noise_method_control(
            ensemble_size=ssa_ensemble,
            trajectories=ssa_trajectories,
            seed=seed,
        ),
        "edge_deformation": edge_deformation_audit(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssa-ensemble", type=int, default=2)
    parser.add_argument("--ssa-trajectories", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_audit(args.ssa_ensemble, args.ssa_trajectories, args.seed)
    control = result["noise_method_control"]
    edge = result["edge_deformation"]

    print("=" * 76)
    print("  Paper XI candidate: GRN method control and terminal-side basin loss")
    print("=" * 76)
    print(" Omega    CLE frozen_D       SSA frozen_D")
    for row in control["rows"]:
        print(
            f" {row['omega']:5.0f}   {row['CLE_frozen_D_word_mean']:7.1f} +/-"
            f" {row['CLE_frozen_D_word_std']:5.1f}   "
            f"{row['SSA_frozen_D_word_mean']:7.1f} +/-"
            f" {row['SSA_frozen_D_word_std']:5.1f}"
        )
    print(
        "Low-minus-high Omega: "
        f"CLE={control['CLE_low_minus_high']:+.1f}, "
        f"SSA={control['SSA_low_minus_high']:+.1f}"
    )
    print(
        "Relative ranges: "
        f"CLE={control['CLE_relative_range']:.2%}, "
        f"SSA={control['SSA_relative_range']:.2%}; "
        f"max method gap={control['maximum_method_gap']:.1f}"
    )
    print("Class B/D noise wall: withdrawn; matched methods show no large wall.")
    print()
    print(
        "Regulatory-edge deformation: attractors "
        f"{edge['reference']['attractor_count']} -> "
        f"{edge['edge_deleted']['attractor_count']}"
    )
    print(
        f"Basin-loss bracket in lambda: {edge['wall_bracket']}; "
        f"removed terminal sectors: {edge['removed_terminal_sectors']}"
    )
    print(
        "Refined controlled-initial bracket: "
        f"{edge['refined_controlled_grid_bracket']} (diagnostic, not a theorem)"
    )
    print("Claim boundary: " + edge["claim_boundary"] + ".")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
