"""9-Sector Transport Tensor + κ Depth Hierarchy.

Computes K_αβ = max_g ‖P_α ρ(g) P_β‖_F and κ₀/κ₁/κ₂ on the 9 primitive
sectors from Center{A_18, QT_all, HT_all}.

Answers:
  - Which sectors are transport-coupled? (direct accessibility)
  - Which couplings are M₂-mediated vs center-isolated vs EP-only?
  - How does the transport graph relate to A_EP ≅ M₂⁴ ⊕ M₁⁴?
  - Mediation vs curvature correspondence at the 9-sector level
"""
import itertools
import time
import numpy as np

from rime.cubieoperator import CubieSpectralOperator
from rime.spectralstructure import block_projectors

TOL = 1e-10


def _lam_to_layer(lam):
    """Map eigenvalue to canonical layer label."""
    for ref, label in [(1.0, 'V₁'), (8/9, 'V₈/₉'), (7/9, 'V₇/₉'),
                        (2/3, 'V₂/₃'), (5/9, 'V₅/₉'), (1/3, 'V₁/₃')]:
        if abs(lam - ref) < 1e-5:
            return label
    return f'λ={lam:.4f}'


def _print_kappa_matrix(Kmat, n_sectors, sector_dims):
    """Print a kappa matrix with sector labels."""
    print(f"   {'':>6}", end="")
    for j in range(n_sectors):
        print(f"  S_{j}({sector_dims[j]:3d})", end="")
    print()
    for i in range(n_sectors):
        print(f"   S_{i}({sector_dims[i]:3d})", end="")
        for j in range(n_sectors):
            val = Kmat[i, j]
            if val > 0.1:
                print(f"  {val:6.2f}  ", end="")
            elif val > TOL:
                print(f"  {val:6.4f}  ", end="")
            else:
                print(f"    0     ", end="")
        print()


def main():
    print("=" * 70)
    print("9-Sector Transport Tensor K_αβ + κ Hierarchy")
    print("=" * 70)

    t0 = time.perf_counter()
    cso = CubieSpectralOperator(n=18)

    # ── 1. Get 9 primitive sectors ──
    print("\n1. Computing 9 primitive sectors from Center{A_18, QT_all, HT_all}...")
    result = cso.center_decomposition()
    sector_projs = result['projectors']
    sector_info = result['sectors']
    n_sectors = len(sector_projs)
    sector_dims = [int(np.round(np.trace(P).real)) for P in sector_projs]
    print(f"   {n_sectors} sectors: dims = {sector_dims}, sum = {sum(sector_dims)}")

    for i, (info, dim) in enumerate(zip(sector_info, sector_dims)):
        print(f"   S_{i} (dim={dim:3d}): λ_QT={info['lam_QT']:.4f}, "
              f"λ_HT={info['lam_HT']:.4f}, λ_18={info['lam_18']:.4f}")

    # ── 2. Block composition of each sector ──
    print("\n2. Block composition per sector:")
    P_blocks = block_projectors()
    block_projs = {'cp': P_blocks['cp'], 'ep': P_blocks['ep'],
                   'co': P_blocks['co'], 'eo': P_blocks['eo']}

    sector_blocks = []
    for Pi in sector_projs:
        blocks = {}
        for name, Pb in block_projs.items():
            overlap = int(np.round(np.trace(Pi @ Pb).real))
            if overlap > 0:
                blocks[name] = overlap
        sector_blocks.append(blocks)

    print(f"   {'Sector':<8} {'dim':<6} {'cp':<6} {'ep':<6} {'co':<6} {'eo':<6} {'layer'}")
    print(f"   {'-'*55}")
    for i, blocks in enumerate(sector_blocks):
        cp_dim = blocks.get('cp', 0)
        ep_dim = blocks.get('ep', 0)
        co_dim = blocks.get('co', 0)
        eo_dim = blocks.get('eo', 0)
        layer = _lam_to_layer(sector_info[i]['lam_18'])
        print(f"   S_{i:<6} {sector_dims[i]:<6} {cp_dim:<6} {ep_dim:<6} "
              f"{co_dim:<6} {eo_dim:<6} {layer}")

    # ── 3. Transport tensor K_αβ ──
    print("\n3. Computing transport tensor K_αβ = max_g ‖P_α ρ(g) P_β‖_F...")
    rho_list = cso.rho_matrices()
    print(f"   Using {len(rho_list)} generators")

    K = np.zeros((n_sectors, n_sectors))
    for i in range(n_sectors):
        Pi = sector_projs[i]
        for j in range(n_sectors):
            Pj = sector_projs[j]
            K[i, j] = max(np.linalg.norm(Pi @ rho_g @ Pj, 'fro') for rho_g in rho_list)

    # ── 4. Display K_αβ ──
    print(f"\n4. Transport tensor K_αβ ({n_sectors}×{n_sectors}):")
    _print_kappa_matrix(K, n_sectors, sector_dims)

    # ── 5. Transport graph analysis ──
    print(f"\n5. Transport graph analysis:")

    edges = [(i, j) for i in range(n_sectors) for j in range(n_sectors)
             if i != j and K[i, j] > TOL]
    print(f"\n   Direct accessibility (K_αβ > 0): {len(edges)} directed edges")
    for i, j in edges:
        print(f"     S_{i} → S_{j}  (K={K[i, j]:.2f})")

    isolated = [i for i in range(n_sectors)
                if not any(K[i, j] > TOL or K[j, i] > TOL for j in range(n_sectors) if j != i)]
    print(f"\n   Isolated sectors (K=0 with all others): {isolated}")

    hub_scores = []
    for i in range(n_sectors):
        out_deg = sum(1 for j in range(n_sectors) if j != i and K[i, j] > TOL)
        in_deg = sum(1 for j in range(n_sectors) if j != i and K[j, i] > TOL)
        hub_scores.append((out_deg + in_deg, i, out_deg, in_deg))
    hub_scores.sort(reverse=True)
    print(f"\n   Hub ranking (by total degree):")
    for score, i, out_d, in_d in hub_scores[:4]:
        layer = _lam_to_layer(sector_info[i]['lam_18'])
        print(f"     S_{i} ({layer}, dim={sector_dims[i]}): deg={score} (out={out_d}, in={in_d})")

    # ── 6. Compositional accessibility ──
    print(f"\n6. Compositional accessibility (length-2 paths):")

    A_direct = (K > TOL).astype(int)
    np.fill_diagonal(A_direct, 0)
    A_path2 = (A_direct @ A_direct) > 0
    np.fill_diagonal(A_path2, 0)

    mediation_pairs = []
    for i in range(n_sectors):
        for j in range(n_sectors):
            if i != j and A_path2[i, j] and not A_direct[i, j]:
                mediators = [k for k in range(n_sectors)
                             if k != i and k != j and A_direct[i, k] and A_direct[k, j]]
                mediation_pairs.append((i, j, mediators))

    print(f"   Direct edges: {len(edges)}")
    print(f"   Length-2 reachable pairs: {int(np.sum(A_path2))}")
    print(f"   Mediation pairs (path-2 reachable but NOT direct): {len(mediation_pairs)}")
    if mediation_pairs:
        print(f"\n   Mediation paradox pairs:")
        for i, j, mediators in mediation_pairs:
            lam_i = sector_info[i]['lam_18']
            lam_j = sector_info[j]['lam_18']
            med_str = ','.join(str(m) for m in mediators)
            print(f"     S_{i} ⇝ S_{j}  via S_{{{med_str}}} (λ_i={lam_i:.3f}, λ_j={lam_j:.3f})")

    # ── 7. Transport × Block Composition ──
    print(f"\n7. Transport × Block Composition:")
    for i, j in edges:
        shared = set(sector_blocks[i].keys()) & set(sector_blocks[j].keys())
        print(f"   S_{i}→S_{j}: shared blocks = {shared}, K={K[i, j]:.2f}")

    # ── 8. Transport × A_EP ──
    print(f"\n8. Transport × A_EP (M₂⁴ ⊕ M₁⁴):")

    ep_sectors = [i for i, blocks in enumerate(sector_blocks) if 'ep' in blocks]
    non_ep_sectors = [i for i, blocks in enumerate(sector_blocks) if 'ep' not in blocks]

    print(f"   Sectors with EP content: {ep_sectors}")
    print(f"   Sectors without EP content: {non_ep_sectors}")

    print(f"   Max K(EP↔EP): {np.max(K[np.ix_(ep_sectors, ep_sectors)]):.2f}")
    if non_ep_sectors:
        print(f"   Max K(EP↔non-EP): {np.max(K[np.ix_(ep_sectors, non_ep_sectors)]):.2f}")
        print(f"   Max K(non-EP↔non-EP): {np.max(K[np.ix_(non_ep_sectors, non_ep_sectors)]):.2f}")

    # V₂/₃ selectivity
    v23_idx = next((i for i, blocks in enumerate(sector_blocks)
                    if abs(sector_info[i]['lam_18'] - 2/3) < 1e-6), None)
    if v23_idx is not None:
        print(f"\n   V₂/₃ (S_{v23_idx}) transport selectivity:")
        for j, kval in sorted(((j, K[v23_idx, j]) for j in range(n_sectors)
                                if j != v23_idx and K[v23_idx, j] > TOL),
                               key=lambda x: -x[1]):
            has_ep = 'ep' in sector_blocks[j]
            print(f"     → S_{j} (dim={sector_dims[j]}, ep={has_ep}): K={kval:.2f}")

    # ── 9. Lie accessibility κ₀/κ₁/κ₂ at 9-sector level ──
    print(f"\n{'='*70}")
    print("9. LIE ACCESSIBILITY κ_d(α,β) at 9-Sector Level")
    print("=" * 70)

    A_gens = cso.compute_lie_generators()
    n_gens = len(A_gens)
    print(f"   Using {n_gens} Lie generators A_g = log ρ(g)")

    # -- κ₀: single-generator Lie transport --
    print("\n9a. κ₀(α,β) = max_g ‖P_α A_g P_β‖_F:")
    kappa0 = np.zeros((n_sectors, n_sectors))
    for i in range(n_sectors):
        Pi = sector_projs[i]
        for j in range(n_sectors):
            Pj = sector_projs[j]
            kappa0[i, j] = max(np.linalg.norm(Pi @ Ag @ Pj, 'fro') for Ag in A_gens)
    _print_kappa_matrix(kappa0, n_sectors, sector_dims)

    # -- κ₁: commutator-mediated --
    print("\n9b. κ₁(α,β) = max_{g<h} ‖P_α [A_g, A_h] P_β‖_F:")
    # Pre-compute all commutators
    comms = [A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
             for g in range(n_gens) for h in range(g + 1, n_gens)]
    kappa1 = np.zeros((n_sectors, n_sectors))
    for i in range(n_sectors):
        Pi = sector_projs[i]
        for j in range(n_sectors):
            Pj = sector_projs[j]
            kappa1[i, j] = max(np.linalg.norm(Pi @ comm @ Pj, 'fro') for comm in comms)
    _print_kappa_matrix(kappa1, n_sectors, sector_dims)

    # -- κ₂: nested double-commutator (sampled) --
    triples = list(itertools.combinations(range(n_gens), 3))
    rng = np.random.default_rng(42)
    if len(triples) > 200:
        triples = [triples[i] for i in rng.choice(len(triples), 200, replace=False)]

    print(f"\n9c. κ₂(α,β) = max ‖P_α [[A_g, A_h], A_k] P_β‖_F ({len(triples)} sampled):")
    # Pre-compute nested commutators
    nested_comms = []
    for g, h, k in triples:
        comm_gh = A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
        nested_comms.append(comm_gh @ A_gens[k] - A_gens[k] @ comm_gh)

    kappa2 = np.zeros((n_sectors, n_sectors))
    for i in range(n_sectors):
        Pi = sector_projs[i]
        for j in range(n_sectors):
            Pj = sector_projs[j]
            kappa2[i, j] = max(np.linalg.norm(Pi @ nc @ Pj, 'fro') for nc in nested_comms)
    _print_kappa_matrix(kappa2, n_sectors, sector_dims)

    # -- κ depth hierarchy analysis --
    print(f"\n9d. κ Depth Hierarchy Analysis:")
    print(f"   {'Pair':<12} {'κ₀':>8} {'κ₁':>8} {'κ₂':>8} {'κ₁/κ₀':>10}  Type")

    curvature_pairs = []
    for i in range(n_sectors):
        for j in range(i + 1, n_sectors):
            if kappa0[i, j] < TOL and kappa1[i, j] > TOL:
                curvature_pairs.append((i, j, kappa0[i, j], kappa1[i, j], kappa2[i, j]))
            elif kappa0[i, j] > TOL:
                ratio = kappa1[i, j] / kappa0[i, j]
                if ratio > 100:
                    curvature_pairs.append((i, j, kappa0[i, j], kappa1[i, j], kappa2[i, j]))

    curvature_pairs.sort(key=lambda x: -(x[4] / max(x[3], 1e-15)))
    for i, j, k0, k1, k2 in curvature_pairs:
        ratio = k1 / max(k0, 1e-15)
        pair_type = "curvature-only" if k0 < TOL else "enhanced"
        lam_i = sector_info[i]['lam_18']
        lam_j = sector_info[j]['lam_18']
        print(f"   S_{i}↔S_{j}     {k0:8.4f} {k1:8.2f} {k2:8.2f} {ratio:10.1e}  "
              f"{pair_type}  (λ_i={lam_i:.2f}, λ_j={lam_j:.2f})")

    # -- Mediation vs Curvature correspondence --
    print(f"\n9e. Mediation ↭ Curvature Correspondence:")
    mediation_set = {(min(i, j), max(i, j)) for i, j, _ in mediation_pairs}
    curvature_set = {(i, j) for i in range(n_sectors) for j in range(i + 1, n_sectors)
                     if kappa0[i, j] < TOL and kappa1[i, j] > TOL}

    print(f"   Mediation pairs (K=0, path-2 reachable): {len(mediation_set)}")
    print(f"   Curvature pairs (κ₀=0, κ₁>0):           {len(curvature_set)}")
    print(f"   Both mediation AND curvature:           {len(mediation_set & curvature_set)}")

    both = mediation_set & curvature_set
    if both:
        for i, j in sorted(both):
            med_list = [m for a, b, m in mediation_pairs if (min(a, b), max(a, b)) == (i, j)]
            med_str = ','.join(str(m) for m in (med_list[0] if med_list else []))
            print(f"     S_{i}↔S_{j}: K=0, path-2 via S_{{{med_str}}}, κ₀≈0, κ₁={kappa1[i, j]:.2f}")

    only_mediation = mediation_set - curvature_set
    if only_mediation:
        print(f"   Mediation-only: {len(only_mediation)}")
        for i, j in sorted(only_mediation):
            print(f"     S_{i}↔S_{j}: K=0, κ₁={kappa1[i, j]:.4f}")

    only_curvature = curvature_set - mediation_set
    if only_curvature:
        print(f"   Curvature-only: {len(only_curvature)}")
        for i, j in sorted(only_curvature):
            print(f"     S_{i}↔S_{j}: κ₀=0, κ₁={kappa1[i, j]:.2f}, K={K[i, j]:.2f}")

    # -- Enhancement ratios --
    print(f"\n9f. Enhancement ratios (κ₁/κ₀) for direct transport edges:")
    for i, j in edges:
        if kappa0[i, j] > TOL:
            ratio = kappa1[i, j] / kappa0[i, j]
            print(f"   S_{i}→S_{j}: κ₀={kappa0[i, j]:.2f}, κ₁={kappa1[i, j]:.2f}, ratio={ratio:.1f}")
        else:
            print(f"   S_{i}→S_{j}: κ₀={kappa0[i, j]:.4f}, κ₁={kappa1[i, j]:.2f} — CURVATURE-DOMINATED")

    print(f"\nTotal time: {time.perf_counter() - t0:.1f}s")


if __name__ == '__main__':
    main()
