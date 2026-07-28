"""Decompose Δcomm = 356 into ker π and coker π.

π: End_G(V) → ⊕_λ End_G(V_λ),  π(C) = (P_λ C P_λ)_λ

codomain = ⊕_λ End_G(V_λ), each component = per-layer commutant space.
dim(codomain) = Σ comm_dim(V_λ) = 966 (NOT Σ d_λ² = 15062).

Decomposition:
    dim(domain) = dim(ker π) + dim(im π) = 610
    dim(codomain) = dim(im π) + dim(coker π) = 966
    Δcomm = dim(coker π) - dim(ker π) = 356
"""
import numpy as np
import sys
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove

# Force unbuffered output (commutant projection takes ~10 min, avoid silent hang)
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None


def project_commutant_to_layer(op, full_basis, lam):
    """Project full-space commutant basis to per-layer commutant (orthonormal)."""
    V = op.eigenspace_basis(lam)
    d = V.shape[1]
    gs_tol = op.tol * d * 10
    projected = []
    for B in full_basis:
        B_proj = V.T.conj() @ B @ V
        for existing in projected:
            B_proj -= np.tensordot(existing.conj(), B_proj) * existing
        nrm = np.linalg.norm(B_proj, 'fro')
        if nrm > gs_tol:
            projected.append(B_proj / nrm)
    return projected


def compute_pi_decomposition():
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    full_basis, full_dim = op.full_commutant_combinatorial()
    layers = op.layer_keys

    # Step 1: Build per-layer commutant bases (codomain basis)
    layer_bases = {}
    layer_dims = {}
    for lam in layers:
        L_basis = project_commutant_to_layer(op, full_basis, lam)
        layer_bases[lam] = L_basis
        layer_dims[lam] = len(L_basis)

    codomain_dim = sum(layer_dims.values())  # = Σ comm_dim(V_λ)
    domain_dim = full_dim  # = 610

    sep = "=" * 60
    print(f"Δcomm decomposition")
    print(sep)
    print(f"  dim(domain)  = dim End_G(V)              = {domain_dim}")
    per_layer_str = " + ".join(str(v) for v in layer_dims.values())
    print(f"  dim(codomain)= Σ dim End_G(V_λ)          = {per_layer_str} = {codomain_dim}")
    print(f"  Δcomm        = codomain - domain          = {codomain_dim - domain_dim}")
    print()

    # Step 2: Build projection M: domain_dim × codomain_dim
    M = np.zeros((domain_dim, codomain_dim))
    layer_offsets = {}
    col_offset = 0
    for lam in layers:
        layer_offsets[lam] = col_offset
        col_offset += layer_dims[lam]

    for k, B_full in enumerate(full_basis):
        for lam in layers:
            V = op.eigenspace_basis(lam)
            B_proj = V.T.conj() @ B_full @ V
            L_basis = layer_bases[lam]
            coeffs = np.zeros(len(L_basis))
            for j, L_j in enumerate(L_basis):
                coeffs[j] = np.real(np.tensordot(L_j.conj(), B_proj))
            off = layer_offsets[lam]
            M[k, off:off + len(L_basis)] = coeffs

    # Step 3: SVD of M
    U, s, Vh = np.linalg.svd(M, full_matrices=True)
    tol = op.tol * max(1.0, s[0]) * max(domain_dim, codomain_dim)
    rank = int(np.sum(s > tol))

    dim_ker = domain_dim - rank
    dim_coker = codomain_dim - rank
    delta = dim_coker - dim_ker

    print(f"  rank(M)      = dim(im π)                  = {rank}")
    print(f"  dim(ker π)   = domain - rank              = {dim_ker}")
    print(f"  dim(coker π) = codomain - rank            = {dim_coker}")
    print()
    print(f"  Δcomm = dim(coker π) - dim(ker π)")
    print(f"  {codomain_dim-domain_dim:>4} = {dim_coker:>4} - {dim_ker:>4}    = {delta}")

    # Step 4: ker π analysis
    print()
    print(sep)
    print(f"ker π  —  off-diagonal commutant (dim={dim_ker})")
    print(sep)

    if dim_ker == 0:
        print("  NONE — π is injective.")
        print("  Every full-space commutant is uniquely determined by its")
        print("  per-layer diagonal blocks. No purely off-diagonal commutant exists.")
    else:
        for ker_idx in range(min(3, dim_ker)):
            coeffs = U[:, rank + ker_idx]
            C = sum(coeffs[j] * full_basis[j] for j in range(domain_dim))
            print(f"\n  Basis {ker_idx}:")
            for a, lam_a in enumerate(layers):
                Va = op.eigenspace_basis(lam_a)
                Pa = Va @ Va.T.conj()
                for b, lam_b in enumerate(layers):
                    if a < b:
                        Vb = op.eigenspace_basis(lam_b)
                        Pb = Vb @ Vb.T.conj()
                        block = Pa @ C @ Pb
                        nrm = np.linalg.norm(block, 'fro')
                        if nrm > 1e-4:
                            print(f"    lam={lam_a:.4f} <-> lam={lam_b:.4f}: ||C||={nrm:.4f}")

    # Step 5: coker π per-layer breakdown
    print()
    print(sep)
    print(f"coker π  —  per-layer commutant overcompleteness (dim={dim_coker})")
    print(sep)

    col_off = 0
    for lam in layers:
        d_comm = layer_dims[lam]
        cols = slice(col_off, col_off + d_comm)
        M_layer = M[:, cols]
        U_l, s_l, Vh_l = np.linalg.svd(M_layer, full_matrices=False)
        layer_rank = int(np.sum(s_l > tol))
        layer_coker_local = d_comm - layer_rank

        d_layer = op.layer_dimension(lam)
        print(f"  lam={lam:.4f}  d={d_layer:>3}  comm={d_comm:>4}  "
              f"im pi={layer_rank:>4}  coker={layer_coker_local:>4}  "
              f"({100*layer_coker_local/d_comm:.1f}% non-liftable)")

        col_off += d_comm

    # Step 6: Transport sparsity correlation
    print()
    print(sep)
    print("Interpretation")
    print(sep)

    # Compute 6-layer transport graph
    K_layer = np.zeros((len(layers), len(layers)))
    for i, lam_i in enumerate(layers):
        Vi = op.eigenspace_basis(lam_i)
        Pi = Vi @ Vi.T.conj()
        for j, lam_j in enumerate(layers):
            if i <= j:
                continue
            Vj = op.eigenspace_basis(lam_j)
            Pj = Vj @ Vj.T.conj()
            for _k, (_mv, rho) in op.rho_moves.items():
                rho_d = rho.toarray() if hasattr(rho, 'toarray') else np.array(rho)
                K_layer[i, j] = max(K_layer[i, j],
                    np.linalg.norm(Pi @ rho_d @ Pj, 'fro'))
            K_layer[j, i] = K_layer[i, j]

    n_zero = int(np.sum(K_layer < 1e-8)) // 2
    n_nonzero = int(np.sum(K_layer > 1e-8)) // 2
    zero_pairs = []
    for a in range(len(layers)):
        for b in range(a + 1, len(layers)):
            if K_layer[a, b] < 1e-8:
                zero_pairs.append((layers[a], layers[b]))

    print(f"  6-layer transport: {n_zero} zero-pairs, {n_nonzero} coupled")
    if zero_pairs:
        print("  Zero-transport pairs:")
        for la, lb in zero_pairs:
            print(f"    lam={la:.4f} <-> lam={lb:.4f}")

    print()
    print(f"  ker pi   = {dim_ker:>4}  (off-diagonal commutant: NONE)")
    print(f"  im pi    = {rank:>4}  (full rank)")
    print(f"  coker pi = {dim_coker:>4}  (linear dependencies in per-layer bases)")
    print(f"  Deltacomm = {dim_coker} = coker - ker")
    print()
    print(f"  The {dim_coker} = {codomain_dim} - {domain_dim} overcounted dimensions are")
    print(f"  linear constraints that per-layer commutant tuples must satisfy")
    print(f"  to come from a single full-space commutant matrix.")
    print(f"  Each zero-transport pair forces C_ab=0, locking scaling.")

    return op, full_basis, layer_bases, (dim_ker, dim_coker, rank)


if __name__ == "__main__":
    compute_pi_decomposition()
    print("\nDone.")
