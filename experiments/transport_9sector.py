"""
9-Sector Transport Tensor — Concrete Backbone of Transport Support Category

Computes K_αβ = max_g ‖P_α ρ(g) P_β‖_F on the 9 primitive sectors
from Z(A_avg) = Center{A_18, QT_all, HT_all}.

Answers:
  - Which sectors are transport-coupled? (direct accessibility)
  - Which couplings are M₂-mediated vs center-isolated vs EP-only?
  - How does the transport graph relate to A_EP ≅ M₂⁴ ⊕ M₁⁴?

Run: python test/canonical/_exp_transport_9sector.py
"""
import sys, io
if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (ValueError, AttributeError):
        pass

import numpy as np
from scipy.linalg import eigvalsh
import time

sys.path.insert(0, '.')
from rime.cubieoperator import CubieSpectralOperator
from rime.spectralstructure import block_projectors
from rime.cubie import CubieMove

TOL = 1e-10


def get_9_sector_projectors(cso):
    """Get the 8 primitive sector projectors from Center{A_18, QT_all, HT_all}.

    Uses CubieSpectralOperator.center_decomposition().
    Returns: projectors (list of 228×228 matrices), sectors (list of dicts)
    """
    result = cso.center_decomposition()
    projectors = result['projectors']
    sectors = result['sectors']
    return projectors, sectors


def get_block_decomposition(cso):
    """Get block projectors cp, ep, co, eo."""
    P = block_projectors()
    return {
        'cp': P['cp'],
        'ep': P['ep'],
        'co': P['co'],
        'eo': P['eo'],
    }


def analyze_sector_block_composition(cso, sector_projectors, block_projs):
    """For each primitive sector, compute its block composition.

    Returns: sector_blocks[i] = {block_name: dim_in_block}
    """
    sector_blocks = []
    for Pi in sector_projectors:
        blocks = {}
        total = 0
        for name, Pb in block_projs.items():
            overlap = np.trace(Pi @ Pb).real
            overlap_int = int(np.round(overlap))
            if overlap_int > 0:
                blocks[name] = overlap_int
                total += overlap_int
        sector_blocks.append(blocks)
    return sector_blocks


def main():
    print("=" * 70)
    print("9-Sector Transport Tensor K_αβ")
    print("=" * 70)

    t0 = time.time()
    cso = CubieSpectralOperator(n=18)

    # ── 1. Get 9 primitive sectors ──
    print("\n1. Computing 9 primitive sectors from Center{A_18, QT_all, HT_all}...")
    sector_projs, sector_info = get_9_sector_projectors(cso)
    n_sectors = len(sector_projs)
    sector_dims = [int(np.round(np.trace(P).real)) for P in sector_projs]
    print(f"   {n_sectors} sectors: dims = {sector_dims}, sum = {sum(sector_dims)}")

    for i, (info, dim) in enumerate(zip(sector_info, sector_dims)):
        print(f"   S_{i} (dim={dim:3d}): λ_QT={info['lam_QT']:.4f}, λ_HT={info['lam_HT']:.4f}, λ_18={info['lam_18']:.4f}")

    # ── 2. Block composition of each sector ──
    print("\n2. Block composition per sector:")
    block_projs = get_block_decomposition(cso)
    sector_blocks = analyze_sector_block_composition(cso, sector_projs, block_projs)

    print(f"   {'Sector':<8} {'dim':<6} {'cp':<6} {'ep':<6} {'co':<6} {'eo':<6} {'18-gen layer'}")
    print(f"   {'-'*55}")
    for i, blocks in enumerate(sector_blocks):
        cp_dim = blocks.get('cp', 0)
        ep_dim = blocks.get('ep', 0)
        co_dim = blocks.get('co', 0)
        eo_dim = blocks.get('eo', 0)
        dim = sector_dims[i]
        # Determine 18-gen layer from λ_18
        lam_18 = sector_info[i]['lam_18']
        if abs(lam_18 - 1.0) < 1e-6:
            layer = "V₁"
        elif abs(lam_18 - 7/9) < 1e-6:
            layer = "V₇/₉"
        elif abs(lam_18 - 2/3) < 1e-6:
            layer = "V₂/₃"
        elif abs(lam_18 - 5/9) < 1e-6:
            layer = "V₅/₉"
        elif abs(lam_18 - 1/3) < 1e-6:
            layer = "V₁/₃"
        else:
            layer = f"λ={lam_18:.4f}"
        print(f"   S_{i:<6} {dim:<6} {cp_dim:<6} {ep_dim:<6} {co_dim:<6} {eo_dim:<6} {layer}")

    # ── 3. Transport tensor K_αβ ──
    print("\n3. Computing transport tensor K_αβ = max_g ‖P_α ρ(g) P_β‖_F...")

    # Get all 18 ρ(g) matrices
    rho_moves_18 = CubieSpectralOperator.rho_moves(18)
    rho_list = []
    move_keys = []
    for key, (mv, rho) in rho_moves_18.items():
        rho_list.append(rho)
        move_keys.append(key)

    n_gens = len(rho_list)
    print(f"   Using {n_gens} generators")

    # Compute K_αβ
    K = np.zeros((n_sectors, n_sectors))
    for i in range(n_sectors):
        Pi = sector_projs[i]
        for j in range(n_sectors):
            Pj = sector_projs[j]
            max_norm = 0.0
            for rho_g in rho_list:
                T_ijg = Pi @ rho_g @ Pj
                norm_val = np.linalg.norm(T_ijg, 'fro')
                if norm_val > max_norm:
                    max_norm = norm_val
            K[i, j] = max_norm

    # ── 4. Display K_αβ ──
    print(f"\n4. Transport tensor K_αβ ({n_sectors}×{n_sectors}):")
    print(f"   {'':>6}", end="")
    for j in range(n_sectors):
        print(f"  S_{j}({sector_dims[j]:3d})", end="")
    print()
    for i in range(n_sectors):
        print(f"   S_{i}({sector_dims[i]:3d})", end="")
        for j in range(n_sectors):
            val = K[i, j]
            if val > 0.1:
                print(f"  {val:6.2f}  ", end="")
            elif val > TOL:
                print(f"  {val:6.4f}  ", end="")
            else:
                print(f"    0     ", end="")
        print()

    # ── 5. Transport graph analysis ──
    print(f"\n5. Transport graph analysis:")

    # Direct accessibility
    print(f"\n   Direct accessibility (K_αβ > 0):")
    edges = []
    for i in range(n_sectors):
        for j in range(n_sectors):
            if i != j and K[i, j] > TOL:
                edges.append((i, j))

    print(f"   {len(edges)} directed edges among {n_sectors} sectors:")
    for i, j in edges:
        print(f"     S_{i} → S_{j}  (K={K[i,j]:.2f})")

    # Find isolated sectors
    isolated = []
    for i in range(n_sectors):
        has_connection = any(K[i, j] > TOL or K[j, i] > TOL for j in range(n_sectors) if j != i)
        if not has_connection:
            isolated.append(i)
    print(f"\n   Isolated sectors (K=0 with all others): {isolated}")

    # Find hub sectors
    hub_scores = []
    for i in range(n_sectors):
        out_deg = sum(1 for j in range(n_sectors) if j != i and K[i, j] > TOL)
        in_deg = sum(1 for j in range(n_sectors) if j != i and K[j, i] > TOL)
        hub_scores.append((out_deg + in_deg, i, out_deg, in_deg))
    hub_scores.sort(reverse=True)
    print(f"\n   Hub ranking (by total degree):")
    for score, i, out_d, in_d in hub_scores[:4]:
        layer = "V₁" if abs(sector_info[i]['lam_18'] - 1.0) < 1e-6 else \
                "V₇/₉" if abs(sector_info[i]['lam_18'] - 7/9) < 1e-6 else \
                "V₂/₃" if abs(sector_info[i]['lam_18'] - 2/3) < 1e-6 else \
                "V₅/₉" if abs(sector_info[i]['lam_18'] - 5/9) < 1e-6 else \
                "V₁/₃"
        print(f"     S_{i} ({layer}, dim={sector_dims[i]}): deg={score} (out={out_d}, in={in_d})")

    # ── 6. Compositional accessibility ──
    print(f"\n6. Compositional accessibility (length-2 paths):")

    # Build direct accessibility matrix
    A_direct = (K > TOL).astype(int)
    np.fill_diagonal(A_direct, 0)

    # Length-2 reachability via matrix multiplication
    A_path2 = (A_direct @ A_direct) > 0
    np.fill_diagonal(A_path2, 0)

    # Mediation: pairs reachable via length-2 but NOT directly
    mediation_pairs = []
    for i in range(n_sectors):
        for j in range(n_sectors):
            if i != j and A_path2[i, j] and not A_direct[i, j]:
                # Find the mediating sector(s)
                mediators = [k for k in range(n_sectors)
                           if k != i and k != j and A_direct[i, k] and A_direct[k, j]]
                mediation_pairs.append((i, j, mediators))

    print(f"   Direct edges: {len(edges)}")
    print(f"   Length-2 reachable pairs: {np.sum(A_path2)}")
    print(f"   Mediation pairs (path-2 reachable but NOT direct): {len(mediation_pairs)}")
    if mediation_pairs:
        print(f"\n   Mediation paradox pairs:")
        for i, j, mediators in mediation_pairs:
            print(f"     S_{i} ⇝ S_{j}  via S_{{{','.join(str(m) for m in mediators)}}} (λ_i={sector_info[i]['lam_18']:.3f}, λ_j={sector_info[j]['lam_18']:.3f})")

    # ── 7. Relate to block composition ──
    print(f"\n7. Transport × Block Composition:")

    # Classify edges by block support
    for i, j in edges:
        blocks_i = sector_blocks[i]
        blocks_j = sector_blocks[j]
        shared = set(blocks_i.keys()) & set(blocks_j.keys())
        print(f"   S_{i}→S_{j}: shared blocks = {shared}, K={K[i,j]:.2f}")

    # ── 8. Relate to EP algebra AW structure ──
    print(f"\n8. Transport × A_EP (M₂⁴ ⊕ M₁⁴):")

    # Sectors with EP content
    ep_sectors = [i for i, blocks in enumerate(sector_blocks) if 'ep' in blocks]
    non_ep_sectors = [i for i, blocks in enumerate(sector_blocks) if 'ep' not in blocks]

    print(f"   Sectors with EP content: {ep_sectors}")
    print(f"   Sectors without EP content: {non_ep_sectors}")

    # Transport among EP sectors
    K_ep_ep = K[np.ix_(ep_sectors, ep_sectors)]
    K_ep_nonep = K[np.ix_(ep_sectors, non_ep_sectors)]
    K_nonep_nonep = K[np.ix_(non_ep_sectors, non_ep_sectors)]

    print(f"   Max K(EP↔EP): {np.max(K_ep_ep):.2f}")
    if len(non_ep_sectors) > 0:
        print(f"   Max K(EP↔non-EP): {np.max(K_ep_nonep):.2f}")
        print(f"   Max K(non-EP↔non-EP): {np.max(K_nonep_nonep):.2f}")
    else:
        print(f"   K(EP↔non-EP): N/A (no non-EP sectors with dimension > 0)")

    # V₂/₃ selectivity check
    v23_idx = None
    for i, blocks in enumerate(sector_blocks):
        if abs(sector_info[i]['lam_18'] - 2/3) < 1e-6:
            v23_idx = i
            break

    if v23_idx is not None:
        print(f"\n   V₂/₃ (S_{v23_idx}) transport selectivity:")
        v23_connections = [(j, K[v23_idx, j]) for j in range(n_sectors) if j != v23_idx and K[v23_idx, j] > TOL]
        v23_connections.sort(key=lambda x: -x[1])
        for j, kval in v23_connections:
            blocks_j = sector_blocks[j]
            has_ep = 'ep' in blocks_j
            print(f"     → S_{j} (dim={sector_dims[j]}, ep={has_ep}): K={kval:.2f}")

    # ── 9. Lie accessibility κ_d at 9-sector level ──
    print(f"\n{'='*70}")
    print("9. LIE ACCESSIBILITY κ_d(α,β) at 9-Sector Level")
    print("=" * 70)

    A_gens = cso.compute_lie_generators()
    n_gens = len(A_gens)
    print(f"   Using {n_gens} Lie generators A_g = log ρ(g)")

    # -- Depth 0: κ₀(α,β) = max_g ‖P_α A_g P_β‖_F --
    print("\n9a. κ₀(α,β) = max_g ‖P_α A_g P_β‖_F (individual Lie generators):")
    kappa0 = np.zeros((n_sectors, n_sectors))
    for i in range(n_sectors):
        for j in range(n_sectors):
            kappa0[i, j] = max(np.linalg.norm(sector_projs[i] @ Ag @ sector_projs[j], 'fro')
                              for Ag in A_gens)

    _print_kappa_matrix(kappa0, n_sectors, sector_dims, TOL)

    # -- Depth 1: κ₁(α,β) = max_{g<h} ‖P_α [A_g, A_h] P_β‖_F --
    print("\n9b. κ₁(α,β) = max_{g<h} ‖P_α [A_g, A_h] P_β‖_F (commutators):")
    kappa1 = np.zeros((n_sectors, n_sectors))
    for g in range(n_gens):
        for h in range(g + 1, n_gens):
            comm = A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
            for i in range(n_sectors):
                for j in range(n_sectors):
                    nrm = np.linalg.norm(sector_projs[i] @ comm @ sector_projs[j], 'fro')
                    kappa1[i, j] = max(kappa1[i, j], nrm)

    _print_kappa_matrix(kappa1, n_sectors, sector_dims, TOL)

    # -- Depth 2: κ₂(α,β) = max ‖P_α [[A_g, A_h], A_k] P_β‖_F --
    import itertools
    triples = list(itertools.combinations(range(n_gens), 3))
    rng = np.random.RandomState(42)
    max_samples = 200
    if len(triples) > max_samples:
        triples = [triples[i] for i in rng.choice(len(triples), max_samples, replace=False)]
    print(f"\n9c. κ₂(α,β) = max ‖P_α [[A_g, A_h], A_k] P_β‖_F ({len(triples)} nested commutators):")
    kappa2 = np.zeros((n_sectors, n_sectors))
    for g, h, k in triples:
        comm_gh = A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
        nested = comm_gh @ A_gens[k] - A_gens[k] @ comm_gh
        for i in range(n_sectors):
            for j in range(n_sectors):
                nrm = np.linalg.norm(sector_projs[i] @ nested @ sector_projs[j], 'fro')
                kappa2[i, j] = max(kappa2[i, j], nrm)

    _print_kappa_matrix(kappa2, n_sectors, sector_dims, TOL)

    # -- Analysis: κ depth hierarchy --
    print(f"\n9d. κ Depth Hierarchy Analysis:")
    print(f"   {'Pair':<12} {'κ₀':>8} {'κ₁':>8} {'κ₂':>8} {'κ₁/κ₀':>10}  Type")
    print(f"   {'-'*55}")

    # Find pairs where κ₀=0 but κ₁>0 (curvature-coupled / Class III at 9-sector level)
    curvature_pairs = []
    for i in range(n_sectors):
        for j in range(i + 1, n_sectors):
            if kappa0[i, j] < TOL and kappa1[i, j] > TOL:
                curvature_pairs.append((i, j, kappa0[i,j], kappa1[i,j], kappa2[i,j]))
            elif kappa0[i, j] > TOL:
                ratio = kappa1[i, j] / kappa0[i, j] if kappa0[i, j] > TOL else 0
                if ratio > 100:  # significant enhancement even with κ₀>0
                    curvature_pairs.append((i, j, kappa0[i,j], kappa1[i,j], kappa2[i,j]))

    curvature_pairs.sort(key=lambda x: -(x[4] / max(x[3], 1e-15)))  # sort by κ₂/κ₁
    for i, j, k0, k1, k2 in curvature_pairs:
        ratio = k1 / max(k0, 1e-15)
        lam_i = sector_info[i]['lam_18']
        lam_j = sector_info[j]['lam_18']
        pair_type = "curvature-only" if k0 < TOL else "enhanced"
        print(f"   S_{i}↔S_{j}     {k0:8.4f} {k1:8.2f} {k2:8.2f} {ratio:10.1e}  {pair_type} "
              f"(λ_i={lam_i:.2f}, λ_j={lam_j:.2f})")

    # -- Mediation vs Curvature correspondence --
    print(f"\n9e. Mediation ↭ Curvature Correspondence:")
    print(f"   Checking: are mediation pairs (K=0, path-2 reachable) exactly the curvature pairs (κ₀=0, κ₁>0)?")
    mediation_set = set()
    for i, j, _ in mediation_pairs:
        mediation_set.add((min(i, j), max(i, j)))
    curvature_set = set()
    for i in range(n_sectors):
        for j in range(i + 1, n_sectors):
            if kappa0[i, j] < TOL and kappa1[i, j] > TOL:
                curvature_set.add((i, j))

    print(f"   Mediation pairs (K=0, path-2 reachable): {len(mediation_set)}")
    print(f"   Curvature pairs (κ₀=0, κ₁>0):           {len(curvature_set)}")

    only_mediation = mediation_set - curvature_set
    only_curvature = curvature_set - mediation_set
    both = mediation_set & curvature_set

    print(f"   Both mediation AND curvature: {len(both)}")
    if both:
        for i, j in sorted(both):
            med_list = [m for a, b, m in mediation_pairs if (min(a,b), max(a,b)) == (i,j)]
            med_str = ','.join(str(m) for m in (med_list[0] if med_list else []))
            print(f"     S_{i}↔S_{j}: K=0, path-2 via S_{{{med_str}}}, κ₀≈0, κ₁={kappa1[i,j]:.2f}")
    if only_mediation:
        print(f"   Mediation-only: {len(only_mediation)}")
        for i, j in sorted(only_mediation):
            print(f"     S_{i}↔S_{j}: K=0, κ₁={kappa1[i,j]:.4f}")
    if only_curvature:
        print(f"   Curvature-only: {len(only_curvature)}")
        for i, j in sorted(only_curvature):
            print(f"     S_{i}↔S_{j}: κ₀=0, κ₁={kappa1[i,j]:.2f}, K={K[i,j]:.2f}")

    # Enhancement ratio summary
    print(f"\n9f. Enhancement ratios (κ₁/κ₀) for direct transport edges:")
    for i, j in edges:
        if kappa0[i, j] > TOL:
            ratio = kappa1[i, j] / kappa0[i, j]
            print(f"   S_{i}→S_{j}: κ₀={kappa0[i,j]:.2f}, κ₁={kappa1[i,j]:.2f}, ratio={ratio:.1f}")
        else:
            print(f"   S_{i}→S_{j}: κ₀={kappa0[i,j]:.4f}, κ₁={kappa1[i,j]:.2f} — CURVATURE-DOMINATED")

    print(f"\nTotal time: {time.time() - t0:.1f}s")


def _print_kappa_matrix(Kmat, n_sectors, sector_dims, TOL):
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


if __name__ == '__main__':
    main()
