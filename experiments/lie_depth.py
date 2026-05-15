"""
Lie Closure Transport Verification — Paper III Critical Test

Key question: Does the full Lie algebra L = Lie{A_g} restore coupling
between spectral sectors that individual Lie generators cannot bridge?

Specifically: with correct logm, we know P_i A_g P_j != 0 for all (i,j).
But the user observed a "one-way barrier" pattern where dB_i/dt ~ 0 in
one direction. Does the Lie closure maintain this directionality, or do
commutators [A_g, A_h] restore symmetric coupling?

Run: python test/_exp_lie_closure_transport.py
"""
import sys
import io
if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (ValueError, AttributeError):
        pass

import numpy as np
from scipy.linalg import logm, expm
import time

sys.path.insert(0, '.')
from rime.cubieoperator import CubieSpectralOperator
from rime.base import DATA_DIR
import os

TOL = 1e-10
FIG_DIR = os.path.join(DATA_DIR, 'paper_figures')


def analyze_lie_closure():
    """Compute Lie algebra closure transport across spectral sectors."""
    print("=" * 70)
    print("Lie Closure Transport Verification")
    print("=" * 70)

    t0 = time.time()
    cso = CubieSpectralOperator(n=18)
    print(f"Init: {time.time() - t0:.1f}s")

    # Get spectral layers
    layers = sorted(cso._layers, reverse=True)
    lam_labels = ['V1', 'V8/9', 'V7/9', 'V2/3', 'V5/9', 'V1/3']
    n_layers = len(layers)

    # Get projectors
    P = {lam: cso._layers[lam]['projector'] for lam in layers}

    # Get Lie generators A_g = log(rho(g))
    print("\nComputing Lie generators (logm)...")
    A_gens = cso.compute_lie_generators()
    print(f"  {len(A_gens)} generators, dim={A_gens[0].shape[0]}")

    # Verify expm fidelity
    rhos = [v[1] for v in cso.rho_moves.values()]
    max_err = max(np.max(np.abs(expm(Ag) - rho))
                  for Ag, rho in zip(A_gens, rhos))
    print(f"  expm(A_g) fidelity: max|expm(A_g)-rho| = {max_err:.2e}")

    # ── Level 0: Individual A_g projected transport ──
    print(f"\n{'='*70}")
    print("Level 0: Individual Lie generators P_i A_g P_j")
    print(f"{'='*70}")

    kappa_0 = np.zeros((n_layers, n_layers))
    for i, lam_i in enumerate(layers):
        Pi = P[lam_i]
        for j, lam_j in enumerate(layers):
            Pj = P[lam_j]
            norms = [np.linalg.norm(Pi @ Ag @ Pj, 'fro') for Ag in A_gens]
            kappa_0[i, j] = max(norms)

    print("kappa_0 = max_g ||P_i A_g P_j||_F:")
    header = "         " + "".join(f"{lam_labels[i]:>10s}" for i in range(n_layers))
    print(header)
    for i in range(n_layers):
        row = f"  {lam_labels[i]:>6s} "
        for j in range(n_layers):
            row += f"  {kappa_0[i,j]:8.2e}"
        print(row)

    # Asymmetry check
    asym_0 = max(abs(kappa_0[i,j] - kappa_0[j,i]) for i in range(n_layers) for j in range(n_layers))
    print(f"\n  Max asymmetry |kappa_ij - kappa_ji| = {asym_0:.2e}")

    # ── Level 1: Commutator transport [A_g, A_h] ──
    print(f"\n{'='*70}")
    print("Level 1: Commutator transport P_i [A_g, A_h] P_j")
    print(f"{'='*70}")

    n_gen = len(A_gens)
    # Sample commutator pairs (all n*(n-1)/2 pairs)
    commutator_norms = np.zeros((n_layers, n_layers, n_gen, n_gen))
    for g in range(n_gen):
        for h in range(g + 1, n_gen):
            comm = A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
            for i in range(n_layers):
                Pi = P[layers[i]]
                for j in range(n_layers):
                    Pj = P[layers[j]]
                    commutator_norms[i, j, g, h] = np.linalg.norm(Pi @ comm @ Pj, 'fro')
                    commutator_norms[i, j, h, g] = commutator_norms[i, j, g, h]

    kappa_1 = np.max(commutator_norms, axis=(2, 3))

    print("kappa_1 = max_{g,h} ||P_i [A_g, A_h] P_j||_F:")
    print(header)
    for i in range(n_layers):
        row = f"  {lam_labels[i]:>6s} "
        for j in range(n_layers):
            row += f"  {kappa_1[i,j]:8.2e}"
        print(row)

    asym_1 = max(abs(kappa_1[i,j] - kappa_1[j,i]) for i in range(n_layers) for j in range(n_layers))
    print(f"\n  Max asymmetry |kappa1_ij - kappa1_ji| = {asym_1:.2e}")

    # ── Level 2: Higher commutators (depth-2 nested) ──
    print(f"\n{'='*70}")
    print("Level 2: Nested commutator transport P_i [[A_g, A_h], A_k] P_j")
    print(f"{'='*70}")

    # Sample a subset (too many combinations for n_gen=18: 18*17*16/2 = 2448)
    import itertools
    max_samples = 200
    triple_pairs = list(itertools.combinations(range(n_gen), 3))
    if len(triple_pairs) > max_samples:
        rng = np.random.RandomState(42)
        triple_pairs = [triple_pairs[i] for i in rng.choice(len(triple_pairs), max_samples, replace=False)]
        print(f"  Sampling {max_samples} of {len(list(itertools.combinations(range(n_gen), 3)))} depth-2 commutators")

    kappa_2 = np.zeros((n_layers, n_layers))
    for g, h, k in triple_pairs:
        comm_gh = A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
        nested = comm_gh @ A_gens[k] - A_gens[k] @ comm_gh
        for i in range(n_layers):
            Pi = P[layers[i]]
            for j in range(n_layers):
                Pj = P[layers[j]]
                nrm = np.linalg.norm(Pi @ nested @ Pj, 'fro')
                kappa_2[i, j] = max(kappa_2[i, j], nrm)

    print("kappa_2 = max ||P_i [[A_g, A_h], A_k] P_j||_F (sampled):")
    print(header)
    for i in range(n_layers):
        row = f"  {lam_labels[i]:>6s} "
        for j in range(n_layers):
            row += f"  {kappa_2[i,j]:8.2e}"
        print(row)

    asym_2 = max(abs(kappa_2[i,j] - kappa_2[j,i]) for i in range(n_layers) for j in range(n_layers))
    print(f"\n  Max asymmetry |kappa2_ij - kappa2_ji| = {asym_2:.2e}")

    # ── Key Analysis: Directed Accessibility ──
    print(f"\n{'='*70}")
    print("DIRECTED ACCESSIBILITY ANALYSIS")
    print(f"{'='*70}")

    # Identify the V2/3-V5/9 pair
    v23_idx = next(i for i, lam in enumerate(layers) if abs(lam - 2/3) < 1e-6)
    v59_idx = next(i for i, lam in enumerate(layers) if abs(lam - 5/9) < 1e-6)

    print(f"\n  V2/3 (lam={layers[v23_idx]:.6f}) <-> V5/9 (lam={layers[v59_idx]:.6f}):")
    print(f"    Level 0 (A_g):        V2/3->V5/9: {kappa_0[v23_idx, v59_idx]:.4f}  "
          f"V5/9->V2/3: {kappa_0[v59_idx, v23_idx]:.4f}  "
          f"ratio: {kappa_0[v23_idx, v59_idx]/max(kappa_0[v59_idx, v23_idx], 1e-15):.2f}")
    print(f"    Level 1 ([A_g,A_h]):  V2/3->V5/9: {kappa_1[v23_idx, v59_idx]:.4f}  "
          f"V5/9->V2/3: {kappa_1[v59_idx, v23_idx]:.4f}  "
          f"ratio: {kappa_1[v23_idx, v59_idx]/max(kappa_1[v59_idx, v23_idx], 1e-15):.2f}")
    print(f"    Level 2 (nested):     V2/3->V5/9: {kappa_2[v23_idx, v59_idx]:.4f}  "
          f"V5/9->V2/3: {kappa_2[v59_idx, v23_idx]:.4f}  "
          f"ratio: {kappa_2[v23_idx, v59_idx]/max(kappa_2[v59_idx, v23_idx], 1e-15):.2f}")

    # Check all off-diagonal pairs for directed structure
    print(f"\n  Full directed asymmetry (Level 0):")
    for i in range(n_layers):
        for j in range(i+1, n_layers):
            ratio_ij = kappa_0[i,j] / max(kappa_0[j,i], 1e-15)
            ratio_ji = kappa_0[j,i] / max(kappa_0[i,j], 1e-15)
            if ratio_ij > 2 or ratio_ji > 2:
                print(f"    {lam_labels[i]}->{lam_labels[j]}: {kappa_0[i,j]:.4f}  "
                      f"{lam_labels[j]}->{lam_labels[i]}: {kappa_0[j,i]:.4f}  "
                      f"directed ratio: {max(ratio_ij, ratio_ji):.1f}x")

    print(f"\n  Full directed asymmetry (Level 1 - commutators):")
    for i in range(n_layers):
        for j in range(i+1, n_layers):
            ratio_ij = kappa_1[i,j] / max(kappa_1[j,i], 1e-15)
            ratio_ji = kappa_1[j,i] / max(kappa_1[i,j], 1e-15)
            if ratio_ij > 2 or ratio_ji > 2:
                print(f"    {lam_labels[i]}->{lam_labels[j]}: {kappa_1[i,j]:.4f}  "
                      f"{lam_labels[j]}->{lam_labels[i]}: {kappa_1[j,i]:.4f}  "
                      f"directed ratio: {max(ratio_ij, ratio_ji):.1f}x")

    # ── Exponential map: does exp(t L) create transport? ──
    print(f"\n{'='*70}")
    print("EXPONENTIAL FLOW: Does exp(tA) bridge sectors?")
    print(f"{'='*70}")

    # Pick one generator and check short-time expansion
    # The question: is P_i exp(t A_g) P_j = 0 + O(t) or = 0 + O(t^2)?
    # If O(t) term is nonzero, continuous flow immediately bridges.
    # If O(t) term is zero but O(t^2) is nonzero, then curvature (commutator) does it.

    # The O(t) term = P_i A_g P_j
    # The O(t^2) term involves A_g^2, which includes commutator effects via
    # A_g^2 = something that contains cross-sector info

    # Test: for each generator, check the Taylor expansion terms
    print("\n  Taylor expansion: ||P_i exp(t A_g) P_j|| for small t")
    print("  (O(t) = linear, O(t^2) = commutator-mediated, O(t^3) = higher Lie)")

    t_vals = [1e-4, 1e-3, 1e-2, 1e-1]
    for g_idx in [0, 1, 6, 7, 8]:  # Sample a few generators
        Ag = A_gens[g_idx]
        gen_key = list(cso.rho_moves.keys())[g_idx]
        print(f"\n  Generator {gen_key}:")
        for t in t_vals:
            exp_tA = expm(t * Ag)
            for i in range(n_layers):
                Pi = P[layers[i]]
                for j in range(n_layers):
                    if i == j:
                        continue
                    nrm = np.linalg.norm(Pi @ exp_tA @ Pj, 'fro')
                    if nrm > 1e-12:
                        # Determine scaling: log(nrm) / log(t) gives exponent
                        print(f"    t={t:.0e}: {lam_labels[i]}->{lam_labels[j]}: ||P_i e^(tA) P_j|| = {nrm:.2e}")
                        break

    # ── Summary ──
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    # Ratio matrix: how much does commutator enhance transport?
    print("\n  Enhancement ratio kappa_1 / kappa_0:")
    ratio_10 = np.zeros((n_layers, n_layers))
    for i in range(n_layers):
        for j in range(n_layers):
            ratio_10[i,j] = kappa_1[i,j] / max(kappa_0[i,j], 1e-15)

    print(header)
    for i in range(n_layers):
        row = f"  {lam_labels[i]:>6s} "
        for j in range(n_layers):
            row += f"  {ratio_10[i,j]:8.1f}"
        print(row)

    # Check if any zero entries in kappa_0 become nonzero in kappa_1
    print("\n  Pairs where commutator creates NEW coupling (kappa_0 < tol, kappa_1 > tol):")
    new_couplings = []
    for i in range(n_layers):
        for j in range(n_layers):
            if kappa_0[i,j] < TOL * 1000 and kappa_1[i,j] > TOL * 1000:
                new_couplings.append((i, j, kappa_1[i,j]))
    if new_couplings:
        for i, j, val in new_couplings:
            print(f"    {lam_labels[i]} -> {lam_labels[j]}: kappa_1 = {val:.2e}")
    else:
        print("    None. Commutators do not create new inter-sector coupling channels.")

    # Final verdict
    print(f"\n  FINAL VERDICT:")
    if asym_0 > 0.1 or asym_1 > 0.1:
        print(f"  Directed asymmetry detected in Lie transport.")
        print(f"  Level 0 asymmetry: {asym_0:.4f}")
        print(f"  Level 1 asymmetry: {asym_1:.4f}")
        print(f"  VERDICT: Continuous limit induces DIRECTED spectral accessibility.")
    else:
        print(f"  No significant directed asymmetry (all ratios near 1.0).")
        print(f"  VERDICT: Continuous limit is symmetrically accessible.")

    print(f"\nDone in {time.time() - t0:.1f}s")


if __name__ == '__main__':
    analyze_lie_closure()
