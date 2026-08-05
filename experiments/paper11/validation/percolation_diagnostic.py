"""Paper XI nested-percolation sampled-trajectory diagnostic.

Claim status: Computational Observation with REPAIR and NONSMOOTH_DISCRETE
curation tags.  The largest adjacent sampled drop is not promoted to a wall
crossing because no upstream threshold discriminant is declared.

Each ensemble member is generated from one fixed symmetric threshold matrix
U.  The graph path G(p) = {ij : U_ij < p} is therefore nested.  The raw
adjacency matrix is used as a general word-transport observable: applying
degree normalization and then skew-symmetrizing can cancel existing edges and
would invalidate the monotone-support control.

This is not spectral-collision evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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

N_NODES = 20
P_SWEEP = np.linspace(0.0, 0.30, 16)
MAX_DEPTH = 6
TOL = 1e-8


def standard_sectors(n: int) -> list[np.ndarray]:
    eye = np.eye(n, dtype=complex)
    return [eye[:, [j]] for j in range(n)]


def generate_thresholds(n: int, rng: np.random.RandomState) -> np.ndarray:
    upper = np.triu(rng.random((n, n)), 1)
    thresholds = upper + upper.T
    np.fill_diagonal(thresholds, np.inf)
    return thresholds


def adjacency_at_p(thresholds: np.ndarray, p: float) -> np.ndarray:
    adjacency = (thresholds < p).astype(complex)
    np.fill_diagonal(adjacency, 0.0)
    return adjacency


def largest_component_fraction(adjacency: np.ndarray) -> float:
    n = adjacency.shape[0]
    unseen = set(range(n))
    largest = 0
    while unseen:
        stack = [unseen.pop()]
        size = 0
        while stack:
            node = stack.pop()
            size += 1
            neighbors = set(np.flatnonzero(adjacency[node]).tolist()) & unseen
            unseen.difference_update(neighbors)
            stack.extend(neighbors)
        largest = max(largest, size)
    return largest / n


def audit_adjacency(adjacency: np.ndarray, sectors: list[np.ndarray]) -> dict:
    r1 = compute_direct_support(sectors, [adjacency], tol=TOL)
    depth = compute_word_depth_matrix(
        sectors,
        [adjacency],
        max_depth=MAX_DEPTH,
        tol=TOL,
        unreached=UNREACHED_DEPTH,
    )
    n = adjacency.shape[0]
    n_pairs = n * (n - 1)
    reached = depth != UNREACHED_DEPTH
    np.fill_diagonal(reached, False)
    return {
        "R1": r1,
        "reached": reached,
        "direct_unsupported_pairs": n_pairs - offdiag_count(r1),
        "word_unreached_at_cutoff_pairs": int(
            n_pairs - np.count_nonzero(reached)
        ),
        "giant_component_fraction": largest_component_fraction(adjacency),
    }


def run_audit(ensemble_size: int = 32, seed: int = 42) -> dict:
    sectors = standard_sectors(N_NODES)
    thresholds = [
        generate_thresholds(N_NODES, np.random.RandomState(seed + member))
        for member in range(ensemble_size)
    ]
    per_member = [[] for _ in range(ensemble_size)]
    sweep = []

    for p in P_SWEEP:
        audits = []
        for member, member_thresholds in enumerate(thresholds):
            audit = audit_adjacency(adjacency_at_p(member_thresholds, float(p)), sectors)
            if per_member[member]:
                previous = per_member[member][-1]
                if np.any(previous["R1"] & ~audit["R1"]):
                    raise AssertionError("direct support decreased on a nested graph path")
                if np.any(previous["reached"] & ~audit["reached"]):
                    raise AssertionError("word reachability decreased on a nested graph path")
            per_member[member].append(audit)
            audits.append(audit)

        unreached = np.array(
            [item["word_unreached_at_cutoff_pairs"] for item in audits],
            dtype=float,
        )
        sweep.append(
            {
                "p": float(p),
                "direct_unsupported_pairs_mean": float(
                    np.mean([item["direct_unsupported_pairs"] for item in audits])
                ),
                "word_unreached_at_cutoff_pairs_mean": float(unreached.mean()),
                "word_unreached_at_cutoff_pairs_std": float(unreached.std()),
                "giant_component_mean": float(
                    np.mean([item["giant_component_fraction"] for item in audits])
                ),
            }
        )

    unreached_means = np.array(
        [item["word_unreached_at_cutoff_pairs_mean"] for item in sweep]
    )
    unreached_stds = np.array(
        [item["word_unreached_at_cutoff_pairs_std"] for item in sweep]
    )
    drops = np.diff(unreached_means)
    largest_drop_index = int(np.argmin(drops)) + 1
    variance_index = int(np.argmax(unreached_stds))
    before = sweep[largest_drop_index - 1]
    after = sweep[largest_drop_index]
    return {
        "record_version": "paper11-percolation-diagnostic-v1.0",
        "claim_status": "Computational Observation",
        "record_role": "trajectory_diagnostic",
        "wall_admission": "not_admitted",
        "diagnostic_kind": "largest_adjacent_sampled_drop",
        "producer": "experiments/paper11/validation/percolation_diagnostic.py",
        "curation_assignment": {
            "rulebook_version": "paper11-curation-tags-v1.0",
            "assignment_source": "derived",
            "tags": ["REPAIR", "NONSMOOTH_DISCRETE"],
            "override_reason": None,
        },
        "observable": "raw symmetric adjacency; general word transport",
        "primary_field": (
            "word.unreached_pair_count_at_cutoff"
            "[Y,cutoff=6,aggregation=ensemble_mean,ensemble_policy=seeded_nested_32]"
        ),
        "value_type": "ensemble_mean_of_integer_pair_counts",
        "negative_boundary": (
            "the support-graph equivalence uses a single entrywise-nonnegative "
            "letter and strict positivity; no signed, multi-letter, complex-weight, "
            "or tolerance-based cancellation claim is made"
        ),
        "ensemble_size": ensemble_size,
        "seed": seed,
        "max_depth": MAX_DEPTH,
        "sweep": sweep,
        "largest_sampled_drop_at_p": sweep[largest_drop_index]["p"],
        "largest_sampled_drop": float(drops[largest_drop_index - 1]),
        "trajectory_diagnostic": {
            "orientation": "increasing_edge_probability",
            "adjacent_sample_interval": {
                "left_sample": before["p"],
                "right_sample": after["p"],
            },
            "before_state": {
                "word_unreached_at_cutoff_pairs_mean": before[
                    "word_unreached_at_cutoff_pairs_mean"
                ]
            },
            "after_state": {
                "word_unreached_at_cutoff_pairs_mean": after[
                    "word_unreached_at_cutoff_pairs_mean"
                ]
            },
            "raw_numeric_direction": "decrease",
            "accessibility_direction": "increase",
            "diagnostic_semantics": "largest_adjacent_sampled_drop",
            "declared_wall_crossing": False,
        },
        "variance_peak_p": sweep[variance_index]["p"],
        "variance_peak_std": float(unreached_stds[variance_index]),
        "monotone_support_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ensemble", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_audit(ensemble_size=args.ensemble, seed=args.seed)
    print("=" * 72)
    print("  Paper XI candidate: nested percolation sampled diagnostic")
    print("=" * 72)
    print("     p   unreached mean +/- std   direct- mean   giant component")
    for row in result["sweep"]:
        print(
            f"  {row['p']:5.2f}   "
            f"{row['word_unreached_at_cutoff_pairs_mean']:7.1f} +/-"
            f" {row['word_unreached_at_cutoff_pairs_std']:5.1f}       "
            f"{row['direct_unsupported_pairs_mean']:7.1f}"
            f"          {row['giant_component_mean']:.3f}"
        )
    print()
    print(
        "Largest sampled cutoff-unreached drop: "
        f"p={result['largest_sampled_drop_at_p']:.2f} "
        f"({result['largest_sampled_drop']:+.1f})"
    )
    print(
        "Largest ensemble fluctuation: "
        f"p={result['variance_peak_p']:.2f} (std={result['variance_peak_std']:.1f})"
    )
    print("Nested direct support and bounded-depth reachability: verified monotone")
    print(
        "Claim boundary: profile-relative sampled diagnostic; no declared wall crossing."
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
