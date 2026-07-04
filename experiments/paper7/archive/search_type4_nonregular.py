"""Paper VII archive: Type IV incidence search in non-regular representations.

Strategies:
  A. Permutation representation of S4 on k-element subsets
  B. Direct sum of selected irreps (not all irreps)
  C. Use rho(g) directly as generators (group-algebraic accessibility)
  D. Block-diagonal embedding: synthetic Type IV ⊕ group representation
"""

from __future__ import annotations

import numpy as np
from itertools import combinations
from scipy.linalg import logm
from rime.rep_utils import symmetric_group, compose_perm, skew_log_generators

TOL = 1e-8


# ============================================================
# Strategy A: Permutation representations
# ============================================================

def k_subsets(n, k):
    """Return all k-element subsets of {0,...,n-1} as sorted tuples."""
    from itertools import combinations
    return list(combinations(range(n), k))


def perm_action_on_ksubsets(perm, subsets):
    """Action of a permutation on k-subsets: {a,b,...} -> {perm[a], perm[b], ...}."""
    result = [0] * len(subsets)
    for i, s in enumerate(subsets):
        acted = tuple(sorted(perm[x] for x in s))
        result[i] = subsets.index(acted)
    return tuple(result)


def build_permutation_rep(n, k, gen_perms):
    """Build permutation representation on k-element subsets.

    Returns (Vs, Xs, elements, rho_fn, dims).
    Uses full joint diagonalization of center operators for sector decomposition.
    """
    from rime.spectral_utils import joint_diag_sectors, build_projectors
    from rime.rep_utils import (
        sector_bases_from_projectors, class_sum_center_ops,
        symmetrized_generator_center_ops,
    )

    S_n = symmetric_group(n)
    subsets = k_subsets(n, k)
    d = len(subsets)
    idx = {s: i for i, s in enumerate(subsets)}

    def rho_fn(p):
        """Permutation rep on k-subsets."""
        M = np.zeros((d, d), dtype=complex)
        for i, s in enumerate(subsets):
            acted = tuple(sorted(p[x] for x in s))
            M[idx[acted], i] = 1.0
        return M

    # For center operators, use the full S_n
    def class_key_sn(p):
        visited = [False] * len(p)
        cycles = []
        for start in range(len(p)):
            if not visited[start]:
                cur, clen = start, 0
                while not visited[cur]:
                    visited[cur] = True
                    cur = p[cur]
                    clen += 1
                if clen > 1:
                    cycles.append(clen)
        return tuple(sorted(cycles))

    center_ops = class_sum_center_ops(S_n, rho_fn, class_key=class_key_sn)
    gen_rhos = [rho_fn(p) for p in gen_perms]
    center_ops.extend(symmetrized_generator_center_ops(gen_rhos))

    sectors_raw = joint_diag_sectors(center_ops, tol=1e-8)
    projs = build_projectors(sectors_raw, d)
    Vs = sector_bases_from_projectors(projs)
    Xs = skew_log_generators(gen_rhos)

    return Vs, Xs, [V.shape[1] for V in Vs]


def check_type_iv(Vs, Xs, tol=TOL):
    """Check all (i,k,j,g,h) for Type IV: A≠0, B≠0, AB=0."""
    n_sec = len(Vs)
    n_gens = len(Xs)
    results = []

    for i in range(n_sec):
        for j in range(n_sec):
            if i == j:
                continue
            for g in range(n_gens):
                for h in range(n_gens):
                    if g == h:
                        continue
                    for k in range(n_sec):
                        A = Vs[i].conj().T @ Xs[g] @ Vs[k]
                        B = Vs[k].conj().T @ Xs[h] @ Vs[j]
                        a_nrm = float(np.linalg.norm(A, 'fro'))
                        b_nrm = float(np.linalg.norm(B, 'fro'))
                        if a_nrm > tol and b_nrm > tol:
                            AB = A @ B
                            ab_nrm = float(np.linalg.norm(AB, 'fro'))
                            if ab_nrm <= tol:
                                results.append({
                                    'g': g, 'h': h, 'i': i, 'j': j, 'k': k,
                                    'rank_A': int(np.linalg.matrix_rank(A, tol=tol)),
                                    'rank_B': int(np.linalg.matrix_rank(B, tol=tol)),
                                    'd_i': Vs[i].shape[1], 'd_k': Vs[k].shape[1],
                                    'd_j': Vs[j].shape[1],
                                    'a_nrm': a_nrm, 'b_nrm': b_nrm, 'ab_nrm': ab_nrm,
                                })
    return results


# ============================================================
# Strategy B: Direct sum of irreps
# ============================================================

def build_s4_irreps():
    """Return the 5 irreducible representations of S4.

    S4 irreps: trivial(1), sign(1), standard(3), sign⊗standard(3), 2-dim(2)
    Total dimension: 1+1+3+3+2 = 10. But regular rep is 24 (with multiplicities).
    We build the direct sum of ONE copy of each irrep.
    """
    S4 = symmetric_group(4)

    # Trivial rep
    def trivial_rep(p):
        return np.array([[1.0]], dtype=complex)

    # Sign rep
    def sign_rep(p):
        visited = [False] * len(p)
        swaps = 0
        for start in range(len(p)):
            if not visited[start]:
                cur, clen = start, 0
                while not visited[cur]:
                    visited[cur] = True
                    cur = p[cur]
                    clen += 1
                swaps += clen - 1
        return np.array([[1.0 if swaps % 2 == 0 else -1.0]], dtype=complex)

    # Standard 3-dim irrep: from the 4-dim permutation rep removing the trivial summand
    # ρ_perm on basis e0,e1,e2,e3. The trivial subrep is span{(1,1,1,1)}.
    # The standard rep is the orthogonal complement, with basis:
    # v0 = (1,-1,0,0)/√2, v1 = (1,1,-2,0)/√6, v2 = (1,1,1,-3)/√12
    def standard_rep(p):
        M = np.zeros((4, 4), dtype=complex)
        for i, j in enumerate(p):
            M[j, i] = 1.0
        # Remove trivial component via projection
        P_triv = np.ones((4, 4)) / 4.0
        P_std = np.eye(4) - P_triv
        # Apply to get action on std subspace, then project to 3x3
        M_std = P_std @ M @ P_std
        # Get 3-dim basis
        evals, evecs = np.linalg.eigh(P_std)
        basis = evecs[:, evals > 0.5]
        return basis.conj().T @ M @ basis

    # Sign ⊗ standard: multiply standard matrices by sign
    def sign_std_rep(p):
        std_M = standard_rep(p)
        sgn = sign_rep(p)[0, 0]
        return sgn * std_M

    # 2-dim irrep: S4/V4 ≅ S3, the standard rep of S3
    # S4 acts on the 3 cosets of V4, giving a 3-dim rep that splits as trivial ⊕ 2-dim
    # The 2-dim part is the standard rep of S3
    # We can get it from the action on the 3 cosets of V4
    # V4 = {id, (12)(34), (13)(24), (14)(23)}
    v4_elements = [
        (0, 1, 2, 3),  # id
        (1, 0, 3, 2),  # (12)(34)
        (2, 3, 0, 1),  # (13)(24)
        (3, 2, 1, 0),  # (14)(23)
    ]

    # Coset representatives
    coset_reps = [(0, 1, 2, 3), (1, 0, 2, 3), (0, 2, 1, 3)]

    def coset_index(p):
        """Which coset does p belong to? Check if p is in coset_reps[i] * V4."""
        for i, rep in enumerate(coset_reps):
            inv_rep = tuple(rep.index(x) for x in range(4))
            product = compose_perm(inv_rep, p)
            if product in v4_elements:
                return i
        return -1

    def two_dim_rep(p):
        M_3 = np.zeros((3, 3), dtype=complex)
        for i in range(3):
            rep_i = coset_reps[i]
            acted = compose_perm(p, rep_i)
            j = coset_index(acted)
            M_3[j, i] = 1.0
        # Remove trivial component
        P_triv = np.ones((3, 3)) / 3.0
        P_2d = np.eye(3) - P_triv
        M_2d_ambient = P_2d @ M_3 @ P_2d
        evals, evecs = np.linalg.eigh(P_2d)
        basis = evecs[:, evals > 0.5]
        return basis.conj().T @ M_3 @ basis

    reps = [trivial_rep, sign_rep, standard_rep, sign_std_rep, two_dim_rep]
    names = ["trivial", "sign", "standard", "sign*std", "2d"]

    # Build matrices for each group element
    all_mats = {name: [] for name in names}
    for p in S4:
        for name, rep_fn in zip(names, reps):
            all_mats[name].append(rep_fn(p))

    return all_mats, names, S4


def build_direct_sum_irrep_system(selected_irreps, gen_perms):
    """Build a system from a direct sum of selected S4 irreps.

    Uses center operators from the direct sum representation.
    """
    from rime.spectral_utils import joint_diag_sectors, build_projectors
    from rime.rep_utils import (
        sector_bases_from_projectors, class_sum_center_ops,
        symmetrized_generator_center_ops,
    )

    all_mats, all_names, S4 = build_s4_irreps()

    # Build direct sum representation
    irrep_mats = [all_mats[name] for name in selected_irreps]
    dims_irreps = [mats[0].shape[0] for mats in irrep_mats]
    total_dim = sum(dims_irreps)

    def rho_fn(p):
        M = np.zeros((total_dim, total_dim), dtype=complex)
        offset = 0
        for mats, d in zip(irrep_mats, dims_irreps):
            # Find p in S4
            p_idx = S4.index(p)
            M[offset:offset+d, offset:offset+d] = mats[p_idx]
            offset += d
        return M

    def class_key_sn(p):
        visited = [False] * len(p)
        cycles = []
        for start in range(len(p)):
            if not visited[start]:
                cur, clen = start, 0
                while not visited[cur]:
                    visited[cur] = True
                    cur = p[cur]
                    clen += 1
                if clen > 1:
                    cycles.append(clen)
        return tuple(sorted(cycles))

    center_ops = class_sum_center_ops(S4, rho_fn, class_key=class_key_sn)
    gen_rhos = [rho_fn(p) for p in gen_perms]
    center_ops.extend(symmetrized_generator_center_ops(gen_rhos))

    sectors_raw = joint_diag_sectors(center_ops, tol=1e-8)
    projs = build_projectors(sectors_raw, total_dim)
    Vs = sector_bases_from_projectors(projs)
    Xs = skew_log_generators(gen_rhos)

    return Vs, Xs, [V.shape[1] for V in Vs], selected_irreps, dims_irreps


# ============================================================
# Strategy C: Use rho(g) as generators (group-algebraic)
# ============================================================

def check_type_iv_rho(Vs, rhos, tol=TOL):
    """Check Type IV using rho(g) matrices directly (not skew-log)."""
    n_sec = len(Vs)
    n_gens = len(rhos)
    results = []

    for i in range(n_sec):
        for j in range(n_sec):
            if i == j:
                continue
            for g in range(n_gens):
                for h in range(n_gens):
                    if g == h:
                        continue
                    for k in range(n_sec):
                        A = Vs[i].conj().T @ rhos[g] @ Vs[k]
                        B = Vs[k].conj().T @ rhos[h] @ Vs[j]
                        a_nrm = float(np.linalg.norm(A, 'fro'))
                        b_nrm = float(np.linalg.norm(B, 'fro'))
                        if a_nrm > tol and b_nrm > tol:
                            AB = A @ B
                            ab_nrm = float(np.linalg.norm(AB, 'fro'))
                            if ab_nrm <= tol:
                                results.append({
                                    'g': g, 'h': h, 'i': i, 'j': j, 'k': k,
                                    'rank_A': int(np.linalg.matrix_rank(A, tol=tol)),
                                    'rank_B': int(np.linalg.matrix_rank(B, tol=tol)),
                                    'd_i': Vs[i].shape[1], 'd_k': Vs[k].shape[1],
                                    'd_j': Vs[j].shape[1],
                                })
    return results


# ============================================================
# Main
# ============================================================

def main():
    np.random.seed(42)

    # ---- Strategy A: Permutation representations ----
    print("=" * 72)
    print("STRATEGY A: Permutation representations (non-regular)")
    print("=" * 72)

    S4 = symmetric_group(4)
    gen_perms = [(1, 0, 2, 3), (1, 2, 3, 0)]  # (12), (1234)

    for n, k in [(4, 1), (4, 2), (5, 2)]:
        print(f"\n  S{n} on {k}-subsets:")
        try:
            Vs, Xs, dims = build_permutation_rep(n, k, gen_perms if n == 4 else
                [(1, 0, 2, 3, 4), (1, 2, 3, 4, 0)])
            print(f"    Total dim: {sum(dims)}, sectors: {len(Vs)}, dims={dims}")
            iv = check_type_iv(Vs, Xs)
            if iv:
                print(f"    *** TYPE IV FOUND: {len(iv)} candidates ***")
                for c in iv[:5]:
                    print(f"      X{c['g']}->S{c['k']}->X{c['h']} for S{c['i']}->S{c['j']}: "
                          f"dims=({c['d_i']},{c['d_k']},{c['d_j']}), "
                          f"ranks=({c['rank_A']},{c['rank_B']})")
            else:
                # Also check with rho directly
                print(f"    No Type IV with skew-log. Trying rho directly...")
                # Build rhos
                subsets = k_subsets(n, k)
                d = len(subsets)
                idx_map = {s: i for i, s in enumerate(subsets)}
                gen_perms_actual = gen_perms if n == 4 else [(1, 0, 2, 3, 4), (1, 2, 3, 4, 0)]
                rhos = []
                for gp in gen_perms_actual:
                    M = np.zeros((d, d), dtype=complex)
                    for i, s in enumerate(subsets):
                        acted = tuple(sorted(gp[x] for x in s))
                        M[idx_map[acted], i] = 1.0
                    rhos.append(M)
                # Use the same sectors
                iv_rho = check_type_iv_rho(Vs, rhos)
                if iv_rho:
                    print(f"    *** TYPE IV with rho: {len(iv_rho)} candidates ***")
                    for c in iv_rho[:5]:
                        print(f"      rho{c['g']}->S{c['k']}->rho{c['h']} for S{c['i']}->S{c['j']}: "
                              f"dims=({c['d_i']},{c['d_k']},{c['d_j']})")
                else:
                    print(f"    No Type IV with rho either.")
        except Exception as e:
            print(f"    Error: {e}")

    # ---- Strategy B: Direct sum of irreps ----
    print()
    print("=" * 72)
    print("STRATEGY B: Direct sum of selected S4 irreps")
    print("=" * 72)

    # Try: standard ⊕ standard (two 3-dim copies) = 6-dim total
    for selected in [
        ['standard', 'standard'],       # 3+3=6
        ['standard', 'sign*std'],       # 3+3=6
        ['standard', '2d'],             # 3+2=5
        ['standard', 'standard', '2d'], # 3+3+2=8
    ]:
        print(f"\n  Selected: {selected}")
        try:
            Vs, Xs, dims, names, irrep_dims = build_direct_sum_irrep_system(
                selected, gen_perms)
            print(f"    Total dim: {sum(dims)}, sectors: {len(Vs)}, dims={dims}")
            print(f"    Irrep dims: {irrep_dims}")
            iv = check_type_iv(Vs, Xs)
            if iv:
                print(f"    *** TYPE IV FOUND: {len(iv)} candidates ***")
                for c in iv[:5]:
                    print(f"      X{c['g']}->S{c['k']}->X{c['h']} for S{c['i']}->S{c['j']}: "
                          f"dims=({c['d_i']},{c['d_k']},{c['d_j']}), "
                          f"ranks=({c['rank_A']},{c['rank_B']})")
            else:
                # Try rho directly
                all_mats, all_names, S4_full = build_s4_irreps()
                irrep_mats = [all_mats[name] for name in selected]
                irrep_dims_raw = [mats[0].shape[0] for mats in irrep_mats]
                total_dim = sum(irrep_dims_raw)
                rhos = []
                for gp in gen_perms:
                    M = np.zeros((total_dim, total_dim), dtype=complex)
                    offset = 0
                    for mats, d in zip(irrep_mats, irrep_dims_raw):
                        p_idx = S4_full.index(gp)
                        M[offset:offset+d, offset:offset+d] = mats[p_idx]
                        offset += d
                    rhos.append(M)
                iv_rho = check_type_iv_rho(Vs, rhos)
                if iv_rho:
                    print(f"    *** TYPE IV with rho: {len(iv_rho)} candidates ***")
                    for c in iv_rho[:5]:
                        print(f"      rho{c['g']}->S{c['k']}->rho{c['h']}: "
                              f"dims=({c['d_i']},{c['d_k']},{c['d_j']})")
                else:
                    print(f"    No Type IV with skew-log or rho.")
        except Exception as e:
            import traceback
            print(f"    Error: {e}")
            traceback.print_exc()

    # ---- Strategy D: Hybrid — group rep blocks checked separately ----
    print()
    print("=" * 72)
    print("STRATEGY D: Check S4 regular rep blocks for rank-deficient products")
    print("=" * 72)
    print("  Computing all blocks of X_g in S4 regular rep and checking")
    print("  for rank deficiency patterns that COULD produce AB=0...")

    from rime.rep_utils import build_system_from_perms

    system = build_system_from_perms(S4, [(1, 0, 2, 3), (2, 0, 1, 3), (1, 2, 3, 0)])
    Vs = system['Vs']
    Xs = system['Xs']

    # Check: for each X_g, compute all blocks. Look for rank-deficient blocks.
    n_sec = len(Vs)
    for g_idx, X in enumerate(Xs):
        n_rank_deficient = 0
        for i in range(n_sec):
            for k in range(n_sec):
                A = Vs[i].conj().T @ X @ Vs[k]
                a_nrm = float(np.linalg.norm(A, 'fro'))
                if a_nrm > TOL:
                    rank_A = int(np.linalg.matrix_rank(A, tol=TOL))
                    d_i, d_k = Vs[i].shape[1], Vs[k].shape[1]
                    max_rank = min(d_i, d_k)
                    if rank_A < max_rank:
                        n_rank_deficient += 1
        print(f"  X[{g_idx}]: {n_rank_deficient} rank-deficient blocks out of {n_sec*n_sec}")

    # Now the key test: for ALL pairs of generators, check if any pair of INTERMEDIATE
    # blocks produces AB=0.
    print()
    print("  Exhaustive check: for each (g,h) pair of S4 elements, each (i,k,j),")
    print("  does Q_i X_g Q_k * Q_k X_h Q_j = 0 with both factors nonzero?")

    # Compute X for all S4 elements
    n_total = len(S4)
    idx_s4 = {p: i for i, p in enumerate(S4)}
    def rho_fn(p):
        M = np.zeros((n_total, n_total), dtype=complex)
        for i, pe in enumerate(S4):
            r = tuple(p[pe[k]] for k in range(len(p)))
            M[idx_s4[r], i] = 1.0
        return M

    all_rhos = [rho_fn(p) for p in S4[:24]]  # All 24 elements
    all_Xs = skew_log_generators(all_rhos)

    n_block_products = 0
    n_ab_zero = 0
    n_rank_issue = 0  # rank(A)+rank(B) <= d_k cases

    for g_idx in range(len(all_Xs)):
        for h_idx in range(len(all_Xs)):
            if g_idx == h_idx:
                continue
            for i in range(n_sec):
                for k in range(n_sec):
                    A = Vs[i].conj().T @ all_Xs[g_idx] @ Vs[k]
                    a_nrm = float(np.linalg.norm(A, 'fro'))
                    if a_nrm <= TOL:
                        continue
                    for j in range(n_sec):
                        B = Vs[k].conj().T @ all_Xs[h_idx] @ Vs[j]
                        b_nrm = float(np.linalg.norm(B, 'fro'))
                        if b_nrm <= TOL:
                            continue
                        n_block_products += 1
                        AB = A @ B
                        ab_nrm = float(np.linalg.norm(AB, 'fro'))
                        if ab_nrm <= TOL:
                            n_ab_zero += 1
                            rank_A = int(np.linalg.matrix_rank(A, tol=TOL))
                            rank_B = int(np.linalg.matrix_rank(B, tol=TOL))
                            if n_ab_zero <= 5:
                                print(f"    AB=0: g={S4[g_idx]}, h={S4[h_idx]}, "
                                      f"i={i}, k={k}, j={j}, "
                                      f"dims=({Vs[i].shape[1]},{Vs[k].shape[1]},{Vs[j].shape[1]}), "
                                      f"ranks=({rank_A},{rank_B})")

    print(f"  Total block products checked: {n_block_products}")
    print(f"  AB=0 occurrences: {n_ab_zero}")

    if n_ab_zero == 0:
        print()
        print("  *** STRUCTURAL RESULT: In the S4 regular representation with")
        print("  center-based sectors, for ALL group elements g,h and ALL sector")
        print("  triples (i,k,j): if Q_i X_g Q_k != 0 and Q_k X_h Q_j != 0,")
        print("  then (Q_i X_g Q_k)(Q_k X_h Q_j) != 0.")
        print()
        print("  This means Type IV (AB=0) is IMPOSSIBLE in the regular")
        print("  representation. It is a purely deformation-space phenomenon.")


if __name__ == "__main__":
    main()
