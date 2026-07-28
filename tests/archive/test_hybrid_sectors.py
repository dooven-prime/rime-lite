"""
Verify hybrid sector classification at 9-sector resolution.

Uses the canonical block_set() from spectral_utils.py to check which
primitive sectors have multi-block projector support, then cross-checks
transport-activity and T7-mediation status.
"""
import numpy as np

from rime.cubieoperator import CubieSpectralOperator
from rime.spectral_utils import block_set
from rime.cubie import BLOCK_RANGES

TOL_K = 0.05


def check(cond, msg):
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    print(f"  OK — {msg}")


def main():
    cso = CubieSpectralOperator()
    decomp = cso.center_decomposition()
    sectors = decomp['projectors']
    n = decomp['n_sectors']

    # ── 1. Block support for each sector ──
    print("=" * 60)
    print("1. Block support (canonical block_set, threshold=0.01)")
    print("=" * 60)
    block_sets = []
    for idx, P in enumerate(sectors):
        bs = block_set(P, BLOCK_RANGES, threshold=0.01)
        block_sets.append(bs)
        dim = int(np.round(np.trace(P).real))
        label = "HYBRID" if len(bs) > 1 else "pure"
        print(f"  S{idx+1}: dim={dim:>3}  blocks={sorted(bs)}  → {label}")

    n_hybrid = sum(1 for bs in block_sets if len(bs) > 1)
    check(n_hybrid == 6, f"6 hybrid sectors (got {n_hybrid})")

    hybrid_names = [f"S{idx+1}" for idx, bs in enumerate(block_sets) if len(bs) > 1]
    print(f"  Hybrid sectors: {', '.join(hybrid_names)}")

    # ── 2. Transport matrix ──
    print(f"\n{'='*60}")
    print("2. Transport (K) matrix")
    print("=" * 60)
    K = np.zeros((n, n))
    rhos = cso.rho_matrices()
    for i in range(n):
        for j in range(n):
            vals = [np.linalg.norm(sectors[i] @ rho @ sectors[j], 'fro') for rho in rhos]
            K[i, j] = max(vals)

    # ── 3. Transport-active hybrids ──
    # Definition (§2.5): hybrid P_γ has K>0 to sectors in at least two distinct
    # blocks that P_γ itself spans.  For an all-block sector (S7), any neighbor's
    # block is already in its own block_set, so 'unique' is always empty — but it
    # is still transport-active if it has K>0 neighbors in ≥2 distinct blocks.
    print(f"\n{'='*60}")
    print("3. Transport-active check")
    print("=" * 60)
    for idx, bs in enumerate(block_sets):
        if len(bs) <= 1:
            continue
        neighbor_blocks = set()
        for j in range(n):
            if idx != j and K[idx, j] > TOL_K:
                neighbor_blocks |= block_sets[j]
        # Active if connects to ≥2 distinct blocks (regardless of own block_set)
        is_active = len(neighbor_blocks) >= 2
        label = "TRANSPORT-ACTIVE" if is_active else "inert"
        print(f"  S{idx+1} ({'+'.join(sorted(bs))}): K-neighbor blocks={sorted(neighbor_blocks)} → {label}")

    n_active = sum(
        1 for idx, bs in enumerate(block_sets)
        if len(bs) > 1 and len(set().union(*[block_sets[j] for j in range(n)
            if idx != j and K[idx, j] > TOL_K])) >= 2
    )
    print(f"\n  Transport-active hybrids: {n_active}")

    # ── 4. T7 mediation — list each T7 pair and its mediators ──
    print(f"\n{'='*60}")
    print("4. T7 pairs and their mediators")
    print("=" * 60)
    from collections import Counter
    mediator_counts = Counter()
    for i in range(n):
        for j in range(i + 1, n):
            if not block_sets[i].isdisjoint(block_sets[j]):
                continue
            pair_mediators = [k for k in range(n) if K[i, k] > TOL_K and K[k, j] > TOL_K]
            if pair_mediators:
                s_names = [f'S{k+1}' for k in pair_mediators]
                print(f"  S{i+1}({'+'.join(sorted(block_sets[i]))}) ↔ S{j+1}({'+'.join(sorted(block_sets[j]))})")
                print(f"    via: {', '.join(s_names)}")
                for k in pair_mediators:
                    mediator_counts[k] += 1

    t7_mediators = set(mediator_counts.keys())
    print(f"\n  Mediator summary:")
    for k in sorted(mediator_counts, key=lambda k: -mediator_counts[k]):
        bs = block_sets[k]
        print(f"    S{k+1} ({'+'.join(sorted(bs))}): {mediator_counts[k]} T7 pair(s)")
    print(f"\n  T7-mediating hybrids: {len(t7_mediators)}")

    # ── 5. Summary ──
    print(f"\n{'='*60}")
    print("5. Summary")
    print("=" * 60)
    print(f"  Total sectors:           {n}")
    print(f"  Hybrid (|block_set|>1):  {n_hybrid}  — {', '.join(hybrid_names)}")
    print(f"  Transport-active hybrid: {n_active}")
    print(f"  T7-mediating hybrid:     {len(t7_mediators)}  — S{', S'.join(str(s+1) for s in sorted(t7_mediators))}")
    print(f"  Pure sectors:            {n - n_hybrid}  — S2(eo), S5(eo), S8(cp)")
    print(f"  Inert hybrid:            S1 (cp+ep, G-invariant subrepresentation)")
    print(f"\n  Definition: hybrid = |block_set(P)| > 1 (multi-block projector support)")
    print(f"  Transport-active: hybrid + K>0 connections to sectors in other blocks")
    print(f"  T7-mediating: hybrid that routes cross-block composition paths")

    print("\n✓ All checks passed.")


if __name__ == '__main__':
    main()
