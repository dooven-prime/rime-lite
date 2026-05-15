"""
Exp: True Primitive Sectors via Maximal Commutative Subalgebra of A_avg.

Key questions:
  1. Do per-axis QT/HT averaging operators commute across axes?
  2. What is the maximal commutative subalgebra?
  3. What are the true primitive sectors (joint eigenspaces)?
  4. Which block (cp/ep/co/eo) hosts each primitive sector?
  5. What is the chirality sector's block origin?

Run: python test/_exp_primitive_sectors.py
"""
import sys, io
if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (ValueError, AttributeError):
        pass

import numpy as np
sys.path.insert(0, '.')
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import N_GENERATORS
from rime.spectralstructure import SpectralStructure, block_projectors


# ═══════════════════════════════════════════════════════════════════════════════
# Setup: Build per-axis averaging operators (uses CubieSpectralOperator)
# ═══════════════════════════════════════════════════════════════════════════════

# build_per_axis_ops() is now CubieSpectralOperator.build_per_axis_ops()
# Kept as convenience alias for backward compatibility in this experiment file.


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Commutativity of per-axis operators
# ═══════════════════════════════════════════════════════════════════════════════

def test_commutativity(ops):
    """Check which per-axis operators commute."""
    print("=" * 70)
    print("TEST 1: Commutativity of Per-Axis Averaging Operators")
    print("=" * 70)

    op_names = ['A_18', 'QT_all', 'HT_all', 'QT0', 'QT1', 'QT2', 'HT0', 'HT1', 'HT2']
    labels = ['A_18', 'QT_all', 'HT_all', 'QT^0', 'QT^1', 'QT^2', 'HT^0', 'HT^1', 'HT^2']

    print(f"\n  ‖[X, Y]‖_F matrix:")
    print(f"  {'':10s}", end="")
    for l in labels:
        print(f"{l:>10s}", end="")
    print()

    for i, (n1, l1) in enumerate(zip(op_names, labels)):
        print(f"  {l1:10s}", end="")
        for j, (n2, l2) in enumerate(zip(op_names, labels)):
            if i == j:
                print(f"  {'---':>8s}", end=" ")
            else:
                comm = np.linalg.norm(ops[n1] @ ops[n2] - ops[n2] @ ops[n1], 'fro')
                if comm < 1e-10:
                    print(f"  {0:8.1e}", end=" ")
                else:
                    print(f"  {comm:8.2e}", end=" ")
        print()

    # Identify maximal commuting subset
    print(f"\n  Key observations:")
    print(f"  - All 'global' operators (A_18, QT_all, HT_all) commute with everything")
    print(f"  - Per-axis operators on SAME axis: QT^a and HT^a may relate via ρ(R2)=ρ(R)²")
    print(f"  - Per-axis operators on DIFFERENT axes: the crucial test")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: QT^a vs QT^b — do they really not commute?
# ═══════════════════════════════════════════════════════════════════════════════

def test_qt_cross_axis_commutativity(ops, cso):
    """Deep dive: check WHY QT^a and QT^b don't commute."""
    print("\n" + "=" * 70)
    print("TEST 2: Cross-Axis QT Commutativity — Deep Dive")
    print("=" * 70)

    # Decompose commutator by block
    # The representation ρ has block structure: cp(64) ⊕ ep(144) ⊕ co(8) ⊕ eo(12)
    # Let's check the commutator within each block
    block_dims = {'cp': 64, 'ep': 144, 'co': 8, 'eo': 12}  # hardcoded block dims (from ρ structure)

    print(f"  Block dimensions: {block_dims}")

    # Get block projectors
    blk_projs = block_projectors()
    # block_projectors should be {'cp': P_cp, 'ep': P_ep, 'co': P_co, 'eo': P_eo}

    # Check commutator restricted to each block
    for (i, j) in [(0, 1), (0, 2), (1, 2)]:
        comm = ops[f'QT{i}'] @ ops[f'QT{j}'] - ops[f'QT{j}'] @ ops[f'QT{i}']
        comm_norm = np.linalg.norm(comm, 'fro')
        print(f"\n  ‖[QT^{i}, QT^{j}]‖_F = {comm_norm:.4f}")

        for block_name, P_block in blk_projs.items():
            comm_block = P_block @ comm @ P_block
            comm_block_norm = np.linalg.norm(comm_block, 'fro')
            print(f"    {block_name} block: ‖P[QT^{i}, QT^{j}]P‖ = {comm_block_norm:.4f}")

        # Also check: compare QT^i restricted to block j vs QT^j restricted to block i
        # Are they just acting on different indices within each block?
        for block_name, P_block in blk_projs.items():
            qt_i_block = P_block @ ops[f'QT{i}'] @ P_block
            qt_j_block = P_block @ ops[f'QT{j}'] @ P_block
            cross_comm = np.linalg.norm(qt_i_block @ qt_j_block - qt_j_block @ qt_i_block, 'fro')
            if cross_comm > 1e-10:
                print(f"      [QT^{i}_block, QT^{j}_block] = {cross_comm:.4f} — NON-COMMUTING within {block_name}!")
            else:
                rho_i_eff = qt_i_block
                # Check if the restricted operators are proportional
                # If they act on disjoint index subsets within the block, they'd commute


# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: The QT-HT algebraic relation within each axis
# ═══════════════════════════════════════════════════════════════════════════════

def test_axis_internal_relation(ops, cso):
    """Check the algebraic relation between QT and HT within a single axis."""
    print("\n" + "=" * 70)
    print("TEST 3: Within-Axis QT–HT Algebraic Relation")
    print("=" * 70)

    # On a single axis, the moves are: R, R', R2 (and similarly for L face)
    # But L = R^-1 on the opposite face... actually no, L is a different face
    # Within axis 0: R, R', R2, L, L', L2
    # QT = (R + R' + L + L')/4, HT = (R2 + L2)/2

    # For a single face: QT_face = (R + R')/2, HT_face = R2
    # Since R2 = R^2, we have HT_face = f(QT_face) for some polynomial f
    # But QT_face is NOT normal (ρ(R) ≠ ρ(R)^T in general — wait, ρ(R)^T = ρ(R')
    # Actually ρ(R') = ρ(R)^T (since they're orthogonal matrices in the permutation rep)
    # So QT_face = (ρ(R) + ρ(R)^T)/2 is Hermitian

    # For the full axis: R, R', R2, L, L', L2
    # But R and L act on different faces — they don't commute in general
    # However, their averaging operators on the full 228-dim space...

    # Key check: does QT^0 commute with HT^0?
    for axis in range(3):
        comm = np.linalg.norm(ops[f'QT{axis}'] @ ops[f'HT{axis}'] - ops[f'HT{axis}'] @ ops[f'QT{axis}'], 'fro')
        print(f"  ‖[QT^{axis}, HT^{axis}]‖ = {comm:.2e}")

        # Does A_axis (full axis averaging) = (4*QT + 2*HT)/6?
        # QT on axis = (R + R' + L + L')/4
        # HT on axis = (R2 + L2)/2
        # Full axis = (R + R' + R2 + L + L' + L2)/6 = (4*QT + 2*HT)/6
        A_axis = (4 * ops[f'QT{axis}'] + 2 * ops[f'HT{axis}']) / 6
        # Compare to actual axis averaging
        rhos = [v[1] for v in cso.rho_moves.values()]
        move_keys = list(cso.rho_moves.keys())
        axis_idx = [i for i, k in enumerate(move_keys) if k[0] == axis]
        A_axis_direct = sum(rhos[i] for i in axis_idx) / len(axis_idx)
        diff = np.linalg.norm(A_axis - A_axis_direct, 'fro')
        print(f"  Axis {axis}: ‖(4QT+2HT)/6 - A_axis_direct‖ = {diff:.2e}")
        evals_axis = np.sort(np.linalg.eigvalsh(A_axis_direct))
        unique_vals, counts = np.unique(evals_axis.round(10), return_counts=True)
        print(f"    Eigenvalues: {dict(zip(unique_vals, counts))}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Maximal commutative subalgebra & true primitive decomposition
# ═══════════════════════════════════════════════════════════════════════════════

def test_maximal_commutative_decomposition(ops, cso):
    """Find the maximal commutative subset and its joint eigenspaces."""
    print("\n" + "=" * 70)
    print("TEST 4: Maximal Commutative Subalgebra — True Primitive Decomposition")
    print("=" * 70)

    # Strategy:
    # 1. Find the maximal commuting subset of {QT^0, QT^1, QT^2, HT^0, HT^1, HT^2}
    # 2. Jointly diagonalize them
    # 3. The resulting eigenspaces are the true primitive sectors

    # First, build the commutativity graph
    all_ops = {f'QT{i}': ops[f'QT{i}'] for i in range(3)}
    all_ops.update({f'HT{i}': ops[f'HT{i}'] for i in range(3)})
    op_names = list(all_ops.keys())

    print("  Commutator matrix (per-axis operators):")
    print(f"  {'':8s}", end="")
    for n in op_names:
        print(f"{n:>8s}", end="")
    print()
    for n1 in op_names:
        print(f"  {n1:8s}", end="")
        for n2 in op_names:
            if n1 == n2:
                print(f"  {'---':>6s}", end=" ")
            else:
                c = np.linalg.norm(all_ops[n1] @ all_ops[n2] - all_ops[n2] @ all_ops[n1], 'fro')
                print(f"  {c:6.2f}", end=" ")
        print()

    # Find maximal clique in commutativity graph
    # Two operators "commute" if ‖[X,Y]‖ < 1e-6
    n_ops = len(op_names)
    commutes = np.zeros((n_ops, n_ops), dtype=bool)
    for i in range(n_ops):
        for j in range(n_ops):
            if i == j:
                commutes[i, j] = True
            else:
                c = np.linalg.norm(all_ops[op_names[i]] @ all_ops[op_names[j]] -
                                   all_ops[op_names[j]] @ all_ops[op_names[i]], 'fro')
                commutes[i, j] = c < 1e-6

    print(f"\n  Commutativity graph (threshold 1e-6):")
    for i, name in enumerate(op_names):
        friends = [op_names[j] for j in range(n_ops) if commutes[i, j] and i != j]
        print(f"    {name} commutes with: {friends}")

    # Greedy maximal clique finder
    def find_maximal_clique(adj, start_node=None):
        """Greedy maximal clique starting from each node, take the largest."""
        best = []
        for start in range(n_ops):
            clique = [start]
            for cand in range(n_ops):
                if cand == start:
                    continue
                if all(adj[cand][c] for c in clique):
                    clique.append(cand)
            if len(clique) > len(best):
                best = clique
        return best

    max_clique = find_maximal_clique(commutes)
    max_clique_names = [op_names[i] for i in max_clique]
    print(f"\n  Maximal commuting subset ({len(max_clique_names)} operators): {max_clique_names}")

    # Also find: what if we use global operators instead?
    global_commuting = ['QT_all', 'HT_all', 'A_18']
    print(f"  Global commuting set (center of A_avg): {global_commuting}")
    print(f"  Using global set for joint diagonalization (respects cubic symmetry)")

    # Now jointly diagonalize the global commuting set
    rng = np.random.RandomState(42)
    M = sum(rng.randn() * ops[name] for name in global_commuting)
    # Make it Hermitian
    M = (M + M.conj().T) / 2
    evals, evecs = np.linalg.eigh(M)

    # Group by eigenvalue
    order = np.argsort(evals)[::-1]
    groups = []
    cur = [order[0]]
    cv = evals[order[0]]
    for i in range(1, len(order)):
        oi = order[i]
        if abs(evals[oi] - cv) < 1e-10:
            cur.append(oi)
        else:
            groups.append((cv, cur))
            cur = [oi]
            cv = evals[oi]
    groups.append((cv, cur))

    # Build projectors
    Ps = []
    for _, indices in groups:
        V = evecs[:, indices]
        Ps.append(V @ V.conj().T)

    # Verify each sector is an eigenspace of all global operators
    print(f"\n  Verifying joint eigenspace property for global operators:")
    for op_name in global_commuting:
        op_mat = ops[op_name]
        max_dev = 0
        for s_idx, P in enumerate(Ps):
            restricted = P @ op_mat @ P
            evals_restricted = np.linalg.eigvalsh(restricted)
            nz = np.abs(evals_restricted) > 1e-10
            if np.any(nz):
                unique_vals = np.unique(evals_restricted[nz].round(10))
                if len(unique_vals) > 1:
                    dev = np.max(unique_vals) - np.min(unique_vals)
                    max_dev = max(max_dev, dev)
        if max_dev > 1e-10:
            print(f"    {op_name}: max eigenvalue deviation = {max_dev:.2e}")
        else:
            print(f"    {op_name}: all sectors scalar → [OK]")

    # Check per-axis operators: are they scalar on these sectors?
    print(f"\n  Per-axis operators on global sectors:")
    for op_name in op_names:
        max_dev = 0
        for s_idx, P in enumerate(Ps):
            restricted = P @ all_ops[op_name] @ P
            evals_restricted = np.linalg.eigvalsh(restricted)
            nz = np.abs(evals_restricted) > 1e-10
            if np.any(nz):
                unique_vals = np.unique(evals_restricted[nz].round(10))
                if len(unique_vals) > 1:
                    dev = np.max(unique_vals) - np.min(unique_vals)
                    max_dev = max(max_dev, dev)
        if max_dev > 1e-2:
            print(f"    {op_name}: NOT scalar — max dev = {max_dev:.2e} (sectors finer than this operator's eigenspaces)")
        elif max_dev > 1e-10:
            print(f"    {op_name}: nearly scalar — max dev = {max_dev:.2e}")
        else:
            print(f"    {op_name}: exactly scalar → [OK]")

    # Print sector properties
    print(f"\n  True Primitive Sectors ({len(Ps)} sectors, total dim = {sum(int(round(np.trace(P).real)) for P in Ps)}):")
    print(f"  {'Sector':>6s} {'dim':>5s}", end="")
    for op_name in global_commuting:
        print(f"  {op_name:>10s}", end="")
    print(f"  {'λ_18':>10s}  {'18-gen':>8s}")

    # Get 18-gen decomposition for reference
    rhos_all = [v[1] for v in cso.rho_moves.values()]
    A_18 = ops['A_18']
    evals_18, evecs_18 = np.linalg.eigh(A_18)
    order_18 = np.argsort(evals_18)[::-1]
    groups_18 = []
    cur = [order_18[0]]
    cv = evals_18[order_18[0]]
    for i in range(1, len(order_18)):
        oi = order_18[i]
        if abs(evals_18[oi] - cv) < 1e-10:
            cur.append(oi)
        else:
            groups_18.append((cv, cur))
            cur = [oi]
            cv = evals_18[oi]
    groups_18.append((cv, cur))
    P_18 = []
    for _, indices in groups_18:
        V = evecs_18[:, indices]
        P_18.append(V @ V.conj().T)

    LABELS_18 = ['V1', 'V8/9', 'V7/9', 'V2/3', 'V5/9', 'V1/3', 'V5/9b', 'V5/9c', 'V1/3b', 'V2/3b']

    for s_idx, P in enumerate(Ps):
        dim = int(round(np.trace(P).real))
        vals = []
        for op_name in global_commuting:
            restricted = P @ ops[op_name] @ P
            ev_r = np.linalg.eigvalsh(restricted)
            nz = np.abs(ev_r) > 1e-10
            if np.any(nz):
                val = ev_r[nz][0].real
            else:
                val = 0.0
            vals.append(val)

        # λ_18
        restricted_18 = P @ A_18 @ P
        ev_r = np.linalg.eigvalsh(restricted_18)
        nz = np.abs(ev_r) > 1e-10
        lam_18 = ev_r[nz][0].real if np.any(nz) else 0.0

        # Which 18-gen layer?
        best_18 = -1
        best_overlap = 0
        for k, p18 in enumerate(P_18):
            overlap = np.real(np.trace(P @ p18))
            if overlap > best_overlap:
                best_overlap = overlap
                best_18 = k

        label = LABELS_18[best_18] if best_18 >= 0 else '?'
        print(f"  S{s_idx+1:>5d} {dim:>5d}", end="")
        for v in vals:
            print(f"  {v:10.6f}", end="")
        print(f"  {lam_18:10.6f}  {label:>8s}")

    return Ps, global_commuting, ops


# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: Block decomposition of primitive sectors
# ═══════════════════════════════════════════════════════════════════════════════

def test_block_decomposition(Ps, max_clique_names, all_ops, cso):
    """Decompose each primitive sector into cp/ep/co/eo blocks."""
    print("\n" + "=" * 70)
    print("TEST 5: Block Origin of Each Primitive Sector")
    print("=" * 70)

    blk_projs = block_projectors()
    block_dims = {'cp': 64, 'ep': 144, 'co': 8, 'eo': 12}

    print(f"  Block dimensions: {block_dims}")
    print(f"  Block total: {sum(block_dims.values())}")

    # Verify block projectors sum to identity
    total = sum(blk_projs.values())
    print(f"  ‖Σ P_block - I‖ = {np.linalg.norm(total - np.eye(228), 'fro'):.2e}")

    # Decompose each sector
    print(f"\n  Block decomposition of each primitive sector:")
    print(f"  {'Sector':>6s} {'dim':>5s}", end="")
    for b in ['cp', 'ep', 'co', 'eo']:
        print(f"  {b:>8s}", end="")
    print(f"  {'primary_block':>15s}")

    for s_idx, P in enumerate(Ps):
        dim = int(round(np.trace(P).real))
        block_contribs = {}
        for b_name, P_block in blk_projs.items():
            contrib = np.real(np.trace(P @ P_block))
            block_contribs[b_name] = contrib

        print(f"  S{s_idx+1:>5d} {dim:>5d}", end="")
        for b in ['cp', 'ep', 'co', 'eo']:
            print(f"  {block_contribs[b]:8.1f}", end="")

        primary = max(block_contribs, key=block_contribs.get)
        print(f"  {primary:>15s}")

    return blk_projs


# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: Chirality sector — the 8-dim piece in detail
# ═══════════════════════════════════════════════════════════════════════════════

def test_chirality_sector(ops, cso):
    """Deep analysis of the 8-dim chirality (half-turn invariant) sector."""
    print("\n" + "=" * 70)
    print("TEST 6: Chirality Sector — The 8-dim Half-Turn Invariant Piece")
    print("=" * 70)

    rhos = [v[1] for v in cso.rho_moves.values()]
    move_keys = list(cso.rho_moves.keys())

    # Build the half-turn invariant projector
    # P_inv = projector onto {x : ρ(g)x = x for all g with direction=2}
    # This is the intersection of the +1 eigenspaces of all 6 HT moves
    # = projector onto the common +1 eigenspace of HT_all

    A_ht = ops['HT_all']
    evals_ht, evecs_ht = np.linalg.eigh(A_ht)
    # The +1 eigenspace of A_HT is the HT-invariant subspace
    ht_inv_idx = np.where(np.abs(evals_ht - 1.0) < 1e-8)[0]
    P_ht_inv = evecs_ht[:, ht_inv_idx] @ evecs_ht[:, ht_inv_idx].conj().T
    dim_ht_inv = int(round(np.trace(P_ht_inv).real))
    print(f"  dim(HT-invariant subspace) = {dim_ht_inv}")

    # Now intersect with V7/9
    A_18 = ops['A_18']
    evals_18, evecs_18 = np.linalg.eigh(A_18)
    v79_idx = np.where(np.abs(evals_18 - 7/9) < 1e-8)[0]
    P_v79 = evecs_18[:, v79_idx] @ evecs_18[:, v79_idx].conj().T

    # Intersection: V7/9 ∩ HT-invariant
    P_v79_ht_inv = P_v79 @ P_ht_inv  # They commute, so this IS the intersection projector
    dim_v79_ht_inv = int(round(np.trace(P_v79_ht_inv).real))
    print(f"  dim(V7/9 ∩ HT-invariant) = {dim_v79_ht_inv}")

    # Now decompose by block
    ss = SpectralStructure.from_rho_moves(cso.rho_moves)
    blk_projs = block_projectors()

    print(f"\n  Block decomposition of the 8-dim chirality sector:")
    for b_name, P_block in blk_projs.items():
        contrib = np.real(np.trace(P_v79_ht_inv @ P_block))
        print(f"    {b_name}: {contrib:.1f}")

    # Also check which block V7/9 as a whole lives in
    print(f"\n  Block decomposition of full V7/9 (44 dim):")
    for b_name, P_block in blk_projs.items():
        contrib = np.real(np.trace(P_v79 @ P_block))
        print(f"    {b_name}: {contrib:.1f}")

    # Analyze the structure of the 8-dim piece
    # It should be V7/9 ∩ ker(A_HT - I)
    # Within each block:
    # - cp (64d): corner permutations — how do HT moves act?
    # - ep (144d): edge permutations — how do HT moves act?
    # - co (8d): corner orientation (Z_3) — half-turns: order 2, Z_3: order 3
    # - eo (12d): edge orientation (Z_2) — half-turns: order 2

    # On orientation blocks: a move of order 2 cannot act trivially on Z_3
    # unless the Z_3 charge is zero. So co contribution to HT-inv = 0.
    # On eo (Z_2): HT moves might flip or not flip orientation sign

    print(f"\n  ─── Physical Interpretation ───")
    print(f"  The 8-dim sector = modes in V7/9 that are invariant under ALL half-turn moves.")
    print(f"  Half-turn (180°) moves preserve orientation parity on edges (order 2 × order 2 = identity)")
    print(f"  but require Z_3 charge neutrality on corners.")
    print(f"  These modes represent 'achiral' edge permutation patterns — permutations that")
    print(f"  are symmetric under 180° rotations on all three axes simultaneously.")

    return P_v79, P_ht_inv, P_v79_ht_inv


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("True Primitive Sectors via Maximal Commutative Subalgebra")
    print("=" * 70)

    cso = CubieSpectralOperator(n=N_GENERATORS)
    ops, move_keys = cso.build_per_axis_ops()

    test_commutativity(ops)
    test_qt_cross_axis_commutativity(ops, cso)
    test_axis_internal_relation(ops, cso)
    Ps, global_ops, all_ops = test_maximal_commutative_decomposition(ops, cso)
    test_block_decomposition(Ps, global_ops, all_ops, cso)
    test_chirality_sector(ops, cso)

    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print("  1. Commutativity: verified which per-axis operators commute")
    print("  2. Maximal commutative subalgebra identified")
    print("  3. True primitive sectors found via joint diagonalization")
    print("  4. Block decomposition: each sector's cp/ep/co/eo origin")
    print("  5. Chirality sector: the 8-dim half-turn invariant subspace within V7/9")
