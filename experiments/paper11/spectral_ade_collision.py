"""Paper XI audit: smooth spectral pair-gap local-model evidence.

Claim status:
    - Taxonomy evidence for the smooth-discriminant branch of Paper XI.
    - Positive local-model candidates: pairwise A1/fold candidates along a
      one-parameter Rubik generator-weight path, plus simultaneous pair-gap
      response diagnostics along a two-weight diagonal path.
    - Not a universal ADE classification theorem for SOF walls.

The audit varies one QT generator weight from 0.01 to 1.0, forms a fixed
separating Hermitian spectral probe

    M(alpha) = QT(alpha) + beta HT(alpha),

and counts adjacent eigenvalue gaps that close at the canonical endpoint while
being separated at the starting point. The canonical QT/HT point is a high-order
critical endpoint where many branches collapse simultaneously; the counted
closures are pairwise A1 collision candidates along the approach.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


TOL_START = 1e-4
TOL_END = 1e-4
BETA = 0.314159
N_STEPS = 100


def qt_ht_indices(n_gens: int = 18) -> tuple[list[int], list[int]]:
    """Return QT/HT indices for the canonical face-turn ordering.

    The historical Rubik move order stores each face as quarter, inverse-quarter,
    half-turn. Thus indices congruent to 2 modulo 3 are HT and the remaining
    indices are QT.
    """

    qt_idx = [idx for idx in range(n_gens) if idx % 3 != 2]
    ht_idx = [idx for idx in range(n_gens) if idx % 3 == 2]
    return qt_idx, ht_idx


def spectral_path(beta: float = BETA, n_steps: int = N_STEPS) -> dict:
    op = CubieSpectralOperator()
    rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    qt_idx, ht_idx = qt_ht_indices(len(rhos))
    target = qt_idx[0]

    alphas = np.linspace(0.01, 1.0, n_steps)
    history: list[list[float]] = []
    for alpha in alphas:
        weights = np.ones(len(rhos))
        weights[target] = alpha
        QT = sum(weights[i] * rhos[i] for i in qt_idx) / sum(weights[i] for i in qt_idx)
        HT = sum(weights[i] * rhos[i] for i in ht_idx) / sum(weights[i] for i in ht_idx)
        M = QT + beta * HT
        M = (M + M.conj().T) / 2.0
        history.append(sorted(np.linalg.eigvalsh(M), reverse=True))

    collisions = []
    n_eigs = len(history[0])
    for idx in range(n_eigs - 1):
        gap_start = abs(history[0][idx] - history[0][idx + 1])
        gap_end = abs(history[-1][idx] - history[-1][idx + 1])
        if gap_start > TOL_START and gap_end < TOL_END:
            collisions.append(
                {
                    "idx": (idx, idx + 1),
                    "gap_start": float(gap_start),
                    "gap_end": float(gap_end),
                    "class": "A1 collision candidate",
                }
            )

    return {
        "record_version": "paper11-rubik-spectral-endpoint-v1.0",
        "claim_status": "Computational Certificate",
        "n_eigs": n_eigs,
        "n_collisions": len(collisions),
        "collisions": collisions,
        "beta": beta,
        "target_index": target,
        "qt_count": len(qt_idx),
        "ht_count": len(ht_idx),
        "trajectory_event": {
            "orientation": "endpoint_to_interior",
            "parameter_bracket": [float(alphas[-1]), float(alphas[0])],
            "before_state": {
                "adjacent_gaps": [
                    collision["gap_end"] for collision in collisions
                ]
            },
            "after_state": {
                "adjacent_gaps": [
                    collision["gap_start"] for collision in collisions
                ]
            },
            "raw_numeric_direction": "increase",
            "event_semantics": "collision_exit",
        },
    }


def diagonal_pair_gap_search(beta: float = BETA, n_steps: int = 25) -> dict:
    """Search for simultaneous pair-gap responses along a diagonal 2D path.

    This is a diagnostic, not a singularity classification: two independently
    indexed gaps reaching comparable half-closure times along the same diagonal
    path are recorded without identifying them as an A2/cusp unfolding.
    """

    op = CubieSpectralOperator()
    rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    qt_idx, ht_idx = qt_ht_indices(len(rhos))
    g1, g2 = qt_idx[0], qt_idx[1]

    alphas = np.linspace(0.02, 1.0, n_steps)
    history: list[list[float]] = []
    for t in alphas:
        weights = np.ones(len(rhos))
        weights[g1] = t
        weights[g2] = t
        QT = sum(weights[i] * rhos[i] for i in qt_idx) / sum(weights[i] for i in qt_idx)
        HT = sum(weights[i] * rhos[i] for i in ht_idx) / sum(weights[i] for i in ht_idx)
        M = QT + beta * HT
        M = (M + M.conj().T) / 2.0
        history.append(sorted(np.linalg.eigvalsh(M), reverse=True))

    pairs: list[tuple[int, float]] = []
    n_eigs = len(history[0])
    for idx in range(n_eigs - 1):
        gap_start = abs(history[0][idx] - history[0][idx + 1])
        gap_end = abs(history[-1][idx] - history[-1][idx + 1])
        if gap_start > 1e-3 and gap_end < 1e-6:
            pairs.append((idx, float(gap_start)))

    half_times: list[tuple[int, float]] = []
    for idx, gap_start in pairs:
        gaps = [abs(history[k][idx] - history[k][idx + 1]) for k in range(n_steps)]
        for step, gap in enumerate(gaps):
            if gap < 0.5 * gap_start:
                half_times.append((idx, float(alphas[step])))
                break

    half_times.sort(key=lambda item: item[1])
    candidates = []
    for left, right in zip(half_times, half_times[1:]):
        if abs(left[1] - right[1]) < 1e-6:
            candidates.append(
                {
                    "pair1": (left[0], left[0] + 1),
                    "pair2": (right[0], right[0] + 1),
                    "t": left[1],
                    "class": "simultaneous pair-gap half-closure diagnostic",
                }
            )

    return {
        "n_pairs": len(pairs),
        "n_simultaneous": len(candidates),
        "candidates": candidates,
    }


def pair_gap_resolution_audit(
    beta: float = BETA,
    resolutions: tuple[int, ...] = (25, 50, 100, 200),
) -> dict[int, dict]:
    """Audit how pair-gap response counts change with sampling resolution."""

    return {
        n_steps: diagonal_pair_gap_search(beta=beta, n_steps=n_steps)
        for n_steps in resolutions
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = spectral_path()
    print("=" * 72)
    print("  Paper XI: Rubik Spectral Pair-Gap Local-Model Audit")
    print("=" * 72)
    print(f"QT generators: {result['qt_count']}; HT generators: {result['ht_count']}")
    print(f"Deformation: vary QT generator index {result['target_index']} from 0.01 to 1.0")
    print(f"Spectral probe: M(alpha)=QT(alpha)+beta HT(alpha), beta={result['beta']}")
    print(f"Eigenvalues tracked: {result['n_eigs']}")
    print(f"A1 pairwise collision candidates: {result['n_collisions']}")
    print()
    print(f"  {'idx':>10s}  {'gap_start':>12s}  {'gap_end':>12s}  class")
    print(f"  {'-' * 10}  {'-' * 12}  {'-' * 12}  {'-' * 24}")
    for collision in result["collisions"][:8]:
        print(
            f"  {str(collision['idx']):>10s}  "
            f"{collision['gap_start']:>12.4e}  "
            f"{collision['gap_end']:>12.2e}  "
            f"{collision['class']}"
        )
    if result["n_collisions"] > 8:
        print(f"  ... and {result['n_collisions'] - 8} more")

    pair_gap = diagonal_pair_gap_search(beta=result["beta"])
    resolution_audit = pair_gap_resolution_audit(beta=result["beta"])
    print()
    print("=" * 72)
    print("  Simultaneous Pair-Gap Search: Two-Weight Diagonal Path")
    print("=" * 72)
    print(f"Diagonal-path separated-to-merged pairs: {pair_gap['n_pairs']}")
    print(f"Simultaneous pair-gap responses at default resolution: {pair_gap['n_simultaneous']}")
    for candidate in pair_gap["candidates"][:3]:
        print(
            "  pairs "
            f"{candidate['pair1']} and {candidate['pair2']} "
            f"both half-close at t={candidate['t']:.3f}"
        )
    print("Resolution audit:")
    for n_steps, audit in resolution_audit.items():
        print(
            f"  n_steps={n_steps:>3d}: "
            f"{audit['n_simultaneous']} simultaneous pair responses"
        )
    print()
    print("Interpretation:")
    print("  - pairwise spectral gaps close at the canonical endpoint (A1-type candidates);")
    print("  - simultaneous pair-gap response counts depend on sampling resolution;")
    print("  - simultaneous pair-gap responses are not identified as A2/cusp unfoldings;")
    print("  - the canonical QT/HT point is a higher-order endpoint where many branches collapse;")
    print("  - this is smooth-branch local-model evidence, not an ADE classification theorem.")
    print("Done.")
    if args.output:
        payload = {
            "record_version": "paper11-rubik-spectral-endpoint-v1.0",
            "claim_status": "Computational Certificate",
            "producer": "experiments/paper11/spectral_ade_collision.py",
            "spectral_endpoint": result,
            "simultaneous_pair_gap": pair_gap,
            "resolution_audit": resolution_audit,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
