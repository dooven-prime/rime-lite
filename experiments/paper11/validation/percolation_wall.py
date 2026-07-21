"""Post-release Paper XI candidate: nested percolation wall audit.

Claim status: computational candidate evidence for Classes B/E.

Each ensemble member is generated from one fixed symmetric threshold matrix
U.  The graph path G(p) = {ij : U_ij < p} is therefore nested.  The raw
adjacency matrix is used as a general word-transport observable: applying
degree normalization and then skew-symmetrizing can cancel existing edges and
would invalidate the monotone-support control.

This is not part of the frozen Paper XI v1.0 census and is not Class A spectral
collision evidence.
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
    compute_direct_support,
    compute_word_depth_matrix,
    offdiag_count,
)

N_NODES = 20
P_SWEEP = np.linspace(0.0, 0.30, 16)
MAX_DEPTH = 6
FROZEN = 999
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
        frozen=FROZEN,
    )
    n = adjacency.shape[0]
    n_pairs = n * (n - 1)
    reached = depth != FROZEN
    np.fill_diagonal(reached, False)
    return {
        "R1": r1,
        "reached": reached,
        "frozen_R1": n_pairs - offdiag_count(r1),
        "frozen_D_word": int(n_pairs - np.count_nonzero(reached)),
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

        fdw = np.array([item["frozen_D_word"] for item in audits], dtype=float)
        sweep.append(
            {
                "p": float(p),
                "frozen_R1_mean": float(np.mean([item["frozen_R1"] for item in audits])),
                "frozen_D_word_mean": float(fdw.mean()),
                "frozen_D_word_std": float(fdw.std()),
                "giant_component_mean": float(
                    np.mean([item["giant_component_fraction"] for item in audits])
                ),
            }
        )

    fdw_means = np.array([item["frozen_D_word_mean"] for item in sweep])
    fdw_stds = np.array([item["frozen_D_word_std"] for item in sweep])
    drops = np.diff(fdw_means)
    wall_index = int(np.argmin(drops)) + 1
    variance_index = int(np.argmax(fdw_stds))
    return {
        "claim_status": "candidate_evidence",
        "paper_xi_release_status": "post_v1_candidate",
        "taxonomy_candidates": ["B", "E"],
        "observable": "raw symmetric adjacency; general word transport",
        "ensemble_size": ensemble_size,
        "seed": seed,
        "max_depth": MAX_DEPTH,
        "sweep": sweep,
        "wall_p": sweep[wall_index]["p"],
        "wall_drop": float(drops[wall_index - 1]),
        "variance_peak_p": sweep[variance_index]["p"],
        "variance_peak_std": float(fdw_stds[variance_index]),
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
    print("  Paper XI candidate: nested percolation wall")
    print("=" * 72)
    print("     p   frozen_D mean +/- std   frozen_R1 mean   giant component")
    for row in result["sweep"]:
        print(
            f"  {row['p']:5.2f}   {row['frozen_D_word_mean']:7.1f} +/-"
            f" {row['frozen_D_word_std']:5.1f}       {row['frozen_R1_mean']:7.1f}"
            f"          {row['giant_component_mean']:.3f}"
        )
    print()
    print(f"Largest frozen-depth drop: p={result['wall_p']:.2f} ({result['wall_drop']:+.1f})")
    print(
        "Largest ensemble fluctuation: "
        f"p={result['variance_peak_p']:.2f} (std={result['variance_peak_std']:.1f})"
    )
    print("Nested direct support and bounded-depth reachability: verified monotone")
    print("Claim boundary: Classes B/E candidate; not Class A collision evidence.")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
