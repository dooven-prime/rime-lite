"""Paper XI Kuramoto cutoff-unreached direction control.

Claim status: Computational Observation and diagnostic analogue.

Each ensemble member uses one matched natural-frequency sample and one matched
initial phase vector across the full coupling sweep.  Frequencies are centered,
which fixes the co-rotating frame used by the (r, psi) sectorization.  The raw
directed trajectory transition is audited as a general word observable.

The continuum Gaussian onset K_c is a reference scale, not a prediction for
the finite-window SOF wall.  The wall location also depends on finite N,
sampling duration, sector resolution, and maximum word depth.  This script is
not part of the frozen Paper XI v1.0 census.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from rime.accessibility import (  # noqa: E402
    UNREACHED_DEPTH,
    compute_direct_support,
    compute_word_depth_matrix,
    offdiag_count,
)
from experiments.observation import (  # noqa: E402
    utc_now,
    write_experiment_observation,
)

N_OSCILLATORS = 20
SIGMA = 0.8
DT = 0.02
EQUILIBRATION_TIME = 40.0
PRODUCTION_TIME = 80.0
STRIDE = 4
K_SWEEP = np.linspace(0.0, 3.0, 16)
K_CONTINUUM = 2.0 * SIGMA * np.sqrt(2.0 / np.pi)
N_R_BINS = 5
N_PSI_BINS = 6
N_SECTORS = N_R_BINS * N_PSI_BINS
MAX_DEPTH = 4
TOL = 1e-8


def simulate(K: float, frequencies: np.ndarray, initial: np.ndarray) -> np.ndarray:
    phases = initial.copy()
    equilibration_steps = int(EQUILIBRATION_TIME / DT)
    production_steps = int(PRODUCTION_TIME / DT)
    frames = np.zeros((production_steps // STRIDE, N_OSCILLATORS), dtype=float)

    def velocity(current: np.ndarray) -> np.ndarray:
        phase_difference = current[np.newaxis, :] - current[:, np.newaxis]
        return frequencies + K * np.sin(phase_difference).sum(axis=1) / N_OSCILLATORS

    for _ in range(equilibration_steps):
        phases += velocity(phases) * DT
    for step in range(production_steps):
        phases += velocity(phases) * DT
        if step % STRIDE == 0:
            frames[step // STRIDE] = phases
    return frames


def order_parameter(phases: np.ndarray) -> tuple[float, float]:
    value = np.mean(np.exp(1j * phases))
    return float(abs(value)), float(np.angle(value))


def sector_index(r: float, psi: float) -> int:
    r_bin = min(int(r * N_R_BINS), N_R_BINS - 1)
    psi_bin = min(int((psi + np.pi) * N_PSI_BINS / (2.0 * np.pi)), N_PSI_BINS - 1)
    return r_bin * N_PSI_BINS + psi_bin


def empirical_transition(trajectory: np.ndarray) -> tuple[np.ndarray, int]:
    counts = np.zeros((N_SECTORS, N_SECTORS), dtype=float)
    visited: set[int] = set()
    indices = [sector_index(*order_parameter(frame)) for frame in trajectory]
    for source, target in zip(indices[:-1], indices[1:]):
        visited.update((source, target))
        if source != target:
            counts[target, source] += 1.0
    transition = np.eye(N_SECTORS, dtype=complex)
    for source in range(N_SECTORS):
        total = counts[:, source].sum()
        if total > 0:
            transition[:, source] = counts[:, source] / total
    return transition, len(visited)


def standard_sectors(n: int) -> list[np.ndarray]:
    eye = np.eye(n, dtype=complex)
    return [eye[:, [j]] for j in range(n)]


def audit_one(K: float, frequencies: np.ndarray, initial: np.ndarray) -> dict:
    trajectory = simulate(K, frequencies, initial)
    transition, visited = empirical_transition(trajectory)
    sectors = standard_sectors(N_SECTORS)
    r1 = compute_direct_support(sectors, [transition], tol=TOL)
    depth = compute_word_depth_matrix(
        sectors,
        [transition],
        max_depth=MAX_DEPTH,
        tol=TOL,
        unreached=UNREACHED_DEPTH,
    )
    n_pairs = N_SECTORS * (N_SECTORS - 1)
    unreached_depth = sum(
        1
        for i in range(N_SECTORS)
        for j in range(N_SECTORS)
        if i != j and depth[i, j] == UNREACHED_DEPTH
    )
    sampled_r = [order_parameter(frame)[0] for frame in trajectory[::10]]
    return {
        "r_mean": float(np.mean(sampled_r)),
        "direct_unsupported_pairs": n_pairs - offdiag_count(r1),
        "word_unreached_at_cutoff_pairs": unreached_depth,
        "visited_sectors": visited,
    }


def run_audit(ensemble_size: int = 8, seed: int = 42) -> dict:
    member_parameters = []
    for member in range(ensemble_size):
        rng = np.random.RandomState(seed + member)
        frequencies = rng.randn(N_OSCILLATORS) * SIGMA
        frequencies -= frequencies.mean()
        initial = rng.uniform(-np.pi, np.pi, N_OSCILLATORS)
        member_parameters.append((frequencies, initial))

    member_sweeps = [[] for _ in range(ensemble_size)]
    sweep = []
    for K in K_SWEEP:
        audits = []
        for member, (frequencies, initial) in enumerate(member_parameters):
            audit = audit_one(float(K), frequencies, initial)
            member_sweeps[member].append(audit)
            audits.append(audit)
        row = {"K": float(K)}
        for key in audits[0]:
            values = np.array([item[key] for item in audits], dtype=float)
            row[f"{key}_mean"] = float(values.mean())
            row[f"{key}_std"] = float(values.std())
        sweep.append(row)

    unreached_means = np.array(
        [item["word_unreached_at_cutoff_pairs_mean"] for item in sweep]
    )
    changes = np.diff(unreached_means)
    wall_index = int(np.argmax(changes)) + 1
    low_index = int(np.argmin(np.abs(K_SWEEP - 0.8)))
    high_index = int(np.argmin(np.abs(K_SWEEP - 2.4)))
    paired_changes = np.array(
        [
            member_sweeps[member][high_index]["word_unreached_at_cutoff_pairs"]
            - member_sweeps[member][low_index]["word_unreached_at_cutoff_pairs"]
            for member in range(ensemble_size)
        ],
        dtype=float,
    )
    return {
        "claim_status": "Computational Observation",
        "curation_tags": ["PLATEAU_RATE", "NONSMOOTH_DISCRETE"],
        "taxonomy_role": "opposite-direction freezing control",
        "observable": "raw directed trajectory transition; general word transport",
        "ensemble_size": ensemble_size,
        "seed": seed,
        "continuum_onset_reference": float(K_CONTINUUM),
        "sweep": sweep,
        "wall_K": sweep[wall_index]["K"],
        "wall_increase": float(changes[wall_index - 1]),
        "paired_low_K": float(K_SWEEP[low_index]),
        "paired_high_K": float(K_SWEEP[high_index]),
        "paired_unreached_change_mean": float(paired_changes.mean()),
        "paired_unreached_change_std": float(paired_changes.std()),
        "freezing_fraction": float(np.mean(paired_changes > 0)),
        "claim_boundary": (
            "finite-N, finite-window sector-occupancy control; not a universal "
            "Kuramoto critical-coupling or wall-direction theorem"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ensemble", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--observation-output", type=Path)
    args = parser.parse_args()

    started_at = utc_now()
    started = perf_counter()
    result = run_audit(args.ensemble, args.seed)
    print("=" * 72)
    print("  Paper XI candidate: Kuramoto freezing-direction control")
    print("=" * 72)
    print(f"Continuum Gaussian onset reference: K_c={result['continuum_onset_reference']:.3f}")
    print("    K      <r> mean   unreached mean +/- std   visited mean")
    for row in result["sweep"]:
        print(
            f"  {row['K']:5.2f}      {row['r_mean_mean']:.3f}       "
            f"{row['word_unreached_at_cutoff_pairs_mean']:7.1f} +/- "
            f"{row['word_unreached_at_cutoff_pairs_std']:5.1f}"
            f"       {row['visited_sectors_mean']:5.1f}"
        )
    print()
    print(
        f"Largest mean freezing step: K={result['wall_K']:.2f} "
        f"({result['wall_increase']:+.1f})"
    )
    print(
        f"Matched K={result['paired_low_K']:.1f}->{result['paired_high_K']:.1f}: "
        f"delta unreached={result['paired_unreached_change_mean']:+.1f} +/- "
        f"{result['paired_unreached_change_std']:.1f}; "
        f"positive in {result['freezing_fraction']:.0%} of members"
    )
    print("Claim boundary: " + result["claim_boundary"] + ".")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.observation_output:
        write_experiment_observation(
            args.observation_output,
            root=ROOT,
            experiment_id="paper11.kuramoto-freezing-crossover",
            paper="paper11",
            command=[
                "python",
                "experiments/paper11/validation/kuramoto_wall.py",
                "--ensemble",
                str(args.ensemble),
                "--seed",
                str(args.seed),
            ],
            sources=[
                "experiments/paper11/validation/kuramoto_wall.py",
                "experiments/observation.py",
                "rime/accessibility.py",
            ],
            parameters={
                "ensemble_size": args.ensemble,
                "seed": args.seed,
                "n_oscillators": N_OSCILLATORS,
                "dt": DT,
                "equilibration_time": EQUILIBRATION_TIME,
                "production_time": PRODUCTION_TIME,
                "stride": STRIDE,
                "coupling_sweep": [float(value) for value in K_SWEEP],
                "sector_shape": [N_R_BINS, N_PSI_BINS],
                "word_cutoff": MAX_DEPTH,
                "tolerance": TOL,
            },
            observations=result,
            claim_status="Computational Observation",
            claim_scope=(
                "Finite-N matched-ensemble Kuramoto freezing-direction control "
                "under the declared sampling and sector policies."
            ),
            limitations=[
                result["claim_boundary"],
                "The cached observation does not replace release recomputation.",
                "The continuum onset is a reference scale, not a fitted wall law.",
            ],
            started_at_utc=started_at,
            elapsed_seconds=perf_counter() - started,
            distributions=["numpy"],
        )


if __name__ == "__main__":
    main()
