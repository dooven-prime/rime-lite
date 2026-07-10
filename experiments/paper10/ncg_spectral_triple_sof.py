"""Paper X registry probe: finite spectral-triple SOF.

Scope:
    This script gives a lightweight noncommutative-geometry inspired SOF entry.
    It is a finite toy spectral triple, not a theorem about all spectral
    triples.  The point is registry portability:

        finite spectral triple data
          -> block projectors from D
          -> observable family from algebra/one-form blocks
          -> sector shadows and T7-style bridge diagnostic

Claim status:
    - Cross-species registry evidence for Paper X.
    - The Connes-distance obstruction is verified for the central finite
      algebra A0 = C^3 represented by block scalars.
    - The T7-style bridge is an SOF accessibility diagnostic, not a claim that
      Connes distance itself is repaired.
"""

from __future__ import annotations

import os
import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import projector_block_norm  # noqa: E402


SECTOR_DIM = 2
N_SECTORS = 3
DIM = SECTOR_DIM * N_SECTORS
TOL = 1e-10


def sector_projectors() -> list[np.ndarray]:
    projectors = []
    for i in range(N_SECTORS):
        q = np.zeros((DIM, DIM), dtype=complex)
        a = i * SECTOR_DIM
        b = a + SECTOR_DIM
        q[a:b, a:b] = np.eye(SECTOR_DIM)
        projectors.append(q)
    return projectors


def matrix_unit_block(i: int, j: int, scale: float = 1.0) -> np.ndarray:
    """A single sector-to-sector observable block."""
    x = np.zeros((DIM, DIM), dtype=complex)
    a = i * SECTOR_DIM
    b = a + SECTOR_DIM
    c = j * SECTOR_DIM
    d = c + SECTOR_DIM
    block = np.array([[1.0, 0.25], [-0.5, 0.75]], dtype=complex) * scale
    x[a:b, c:d] = block
    return x


def audit() -> dict:
    qs = sector_projectors()

    # Finite central algebra A0 = C^3 acting by block scalars on H.
    central_projections = qs
    masses = [0.0, 10.0, 20.0]
    D = np.diag(np.repeat(masses, SECTOR_DIM)).astype(complex)

    # For every central projection p, [D,p]=0.  If two states are supported on
    # different central blocks, c*p separates them with zero Lipschitz seminorm
    # for arbitrarily large c; hence the Connes distance is infinite in this
    # central-algebra model.
    commutator_norms = [
        float(np.linalg.norm(D @ p - p @ D, ord="fro"))
        for p in central_projections
    ]
    central_lipschitz_zero = max(commutator_norms) < TOL

    # Observable/one-form family: two adjacent bridge blocks and adjoints.
    x_lm = matrix_unit_block(0, 1)
    x_ml = x_lm.conj().T
    x_mr = matrix_unit_block(1, 2)
    x_rm = x_mr.conj().T
    observables = [x_lm, x_ml, x_mr, x_rm]

    direct_lr = max(projector_block_norm(qs, x, 0, 2) for x in observables)
    direct_rl = max(projector_block_norm(qs, x, 2, 0) for x in observables)

    bridge_lr = projector_block_norm(qs, x_lm @ x_mr, 0, 2)
    bridge_rl = projector_block_norm(qs, x_rm @ x_ml, 2, 0)

    t7_pairs = []
    if direct_lr < TOL and bridge_lr > TOL:
        t7_pairs.append(("L", "R"))
    if direct_rl < TOL and bridge_rl > TOL:
        t7_pairs.append(("R", "L"))

    return {
        "dim": DIM,
        "n_sectors": N_SECTORS,
        "masses": masses,
        "commutator_norms": commutator_norms,
        "central_lipschitz_zero": central_lipschitz_zero,
        "connes_distance_cross_blocks": "infinite",
        "direct_lr": direct_lr,
        "direct_rl": direct_rl,
        "bridge_lr": bridge_lr,
        "bridge_rl": bridge_rl,
        "t7_pairs": t7_pairs,
        "t7_count_ordered": len(t7_pairs),
    }


def main() -> None:
    result = audit()

    print("=" * 72)
    print("  Paper X Registry Probe: Finite Spectral-Triple SOF")
    print("=" * 72)
    print("SOF object:")
    print(f"  H_F dimension: {result['dim']}")
    print(f"  sectors from block-diagonal D: {result['n_sectors']}")
    print(f"  D masses: {result['masses']}")
    print()
    print("Central Connes-distance obstruction:")
    print(f"  max ||[D,p_i]||_F = {max(result['commutator_norms']):.2e}")
    print(f"  central Lipschitz seminorm zero: {result['central_lipschitz_zero']}")
    print("  cross-block central pure-state distance: infinite")
    print()
    print("SOF accessibility diagnostic:")
    print(f"  direct L->R block norm: {result['direct_lr']:.2e}")
    print(f"  bridge L->M->R norm:   {result['bridge_lr']:.2e}")
    print(f"  direct R->L block norm: {result['direct_rl']:.2e}")
    print(f"  bridge R->M->L norm:   {result['bridge_rl']:.2e}")
    print(f"  ordered T7-style bridge count: {result['t7_count_ordered']}")
    print()
    print("Claim status:")
    print("  finite NCG-inspired registry entry")
    print("  T7 bridge is an SOF shadow, not a Connes-distance repair theorem")
    print("Done.")


if __name__ == "__main__":
    main()
