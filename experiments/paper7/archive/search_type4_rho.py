"""Paper VII archive: Type IV incidence search using rho(g) directly.

Tests whether Q_i rho(g) Q_k * Q_k rho(h) Q_j = 0 can occur
with both factors nonzero, in the center-based sector decomposition.
"""

import numpy as np
from rime.rep_utils import build_system_from_perms, symmetric_group

TOL = 1e-8


def main():
    np.random.seed(42)
    S4 = symmetric_group(4)
    n_total = len(S4)
    idx_s4 = {p: i for i, p in enumerate(S4)}

    def rho_fn(p):
        M = np.zeros((n_total, n_total), dtype=complex)
        for i, pe in enumerate(S4):
            r = tuple(p[pe[k]] for k in range(len(p)))
            M[idx_s4[r], i] = 1.0
        return M

    # Use S4-3gen-B sectors
    gen_perms = [(1, 0, 2, 3), (2, 0, 1, 3), (1, 2, 3, 0)]
    system = build_system_from_perms(S4, gen_perms)
    Vs = system['Vs']
    n_sec = len(Vs)
    dims = [V.shape[1] for V in Vs]

    print("=" * 72)
    print("Type IV search: rho(g) in S4 regular rep")
    print("=" * 72)
    print(f"Sectors: {n_sec}, dims={dims}")

    # Compute rho for all 24 elements
    all_rhos = [rho_fn(p) for p in S4]

    # First: check rank of blocks
    print()
    print("Rank analysis of rho(g) blocks:")
    for g_idx in [0, 1, 2]:  # First 3 elements (identity + 2 others)
        p = S4[g_idx]
        n_full_rank = 0
        n_rank_def = 0
        n_nonzero = 0
        for i in range(n_sec):
            for k in range(n_sec):
                A = Vs[i].conj().T @ all_rhos[g_idx] @ Vs[k]
                a_nrm = float(np.linalg.norm(A, 'fro'))
                if a_nrm > TOL:
                    n_nonzero += 1
                    rank_A = int(np.linalg.matrix_rank(A, tol=TOL))
                    max_rank = min(Vs[i].shape[1], Vs[k].shape[1])
                    if rank_A == max_rank:
                        n_full_rank += 1
                    else:
                        n_rank_def += 1
                        print(f"  rho[{g_idx}] (perm={p}): S{i}->S{k}: "
                              f"rank={rank_A}/{max_rank}, dim=({Vs[i].shape[1]},{Vs[k].shape[1]})")
        print(f"  rho[{g_idx}] (perm={p}): {n_nonzero} nonzero blocks, "
              f"{n_full_rank} full rank, {n_rank_def} rank-deficient")

    # Exhaustive search: ALL element pairs, ALL sector triples
    print()
    print("Exhaustive AB=0 search with rho(g)...")
    n_checked = 0
    n_ab_zero = 0
    ab_zero_examples = []

    for g_idx in range(len(all_rhos)):
        for h_idx in range(len(all_rhos)):
            if g_idx == h_idx:
                continue
            for i in range(n_sec):
                for k in range(n_sec):
                    A = Vs[i].conj().T @ all_rhos[g_idx] @ Vs[k]
                    if np.linalg.norm(A, 'fro') <= TOL:
                        continue
                    d_i, d_k = Vs[i].shape[1], Vs[k].shape[1]
                    if d_k <= 1:  # Type IV impossible with 1-dim intermediate
                        continue
                    for j in range(n_sec):
                        B = Vs[k].conj().T @ all_rhos[h_idx] @ Vs[j]
                        if np.linalg.norm(B, 'fro') <= TOL:
                            continue
                        n_checked += 1
                        AB = A @ B
                        ab_nrm = float(np.linalg.norm(AB, 'fro'))
                        if ab_nrm <= TOL:
                            n_ab_zero += 1
                            if len(ab_zero_examples) < 10:
                                rank_A = int(np.linalg.matrix_rank(A, tol=TOL))
                                rank_B = int(np.linalg.matrix_rank(B, tol=TOL))
                                ab_zero_examples.append({
                                    'g_idx': g_idx, 'h_idx': h_idx,
                                    'i': i, 'k': k, 'j': j,
                                    'd_i': d_i, 'd_k': d_k,
                                    'd_j': Vs[j].shape[1],
                                    'rank_A': rank_A, 'rank_B': rank_B,
                                    'ab_nrm': ab_nrm,
                                })

    print(f"  Checked: {n_checked} products")
    print(f"  AB=0: {n_ab_zero}")

    if n_ab_zero > 0:
        print()
        print("  *** TYPE IV FOUND WITH rho(g)! ***")
        for ex in ab_zero_examples:
            print(f"    g={S4[ex['g_idx']]}, h={S4[ex['h_idx']]}, "
                  f"S{ex['i']}->S{ex['k']}->S{ex['j']}, "
                  f"dims=({ex['d_i']},{ex['d_k']},{ex['d_j']}), "
                  f"ranks=({ex['rank_A']},{ex['rank_B']})")
    else:
        print()
        print("  rho(g) also has NO Type IV.")
        print()
        print("  CONCLUSION: Both X_g = log(rho(g)) AND rho(g) have the property")
        print("  that Q_i M Q_k * Q_k N Q_j != 0 whenever both factors are nonzero,")
        print("  in the center-based sector decomposition of the S4 regular rep.")
        print()
        print("  Type IV is a robustly deformation-space phenomenon.")


if __name__ == "__main__":
    main()
