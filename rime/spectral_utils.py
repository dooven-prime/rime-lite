"""
Shared spectral utilities for experiment scripts.

Extracted from _exp_abelian_t7.py, _exp_minimal_t7.py, and others.
All functions work with raw numpy arrays — no CubieSpectralOperator dependency.

Sections:
  1. Joint diagonalization & sector classification
  2. Transport & Lie curvature (K, kappa_0, kappa_1)
  3. T7 detection
  4. Group element enumeration (inverse-closed subsets, etc.)
  5. Small group representations (S_3, abelian characters, etc.)
"""
import numpy as np
from scipy.linalg import logm
from itertools import combinations


# ============================================================
# 1. Joint diagonalization & sector classification
# ============================================================

def joint_diag_sectors(ops, tol=1e-10):
    """Find simultaneous eigenspaces of commuting Hermitian operators.

    Uses iterative subspace restriction: for each operator, diagonalize
    within each previously-found sector, splitting by eigenvalue.

    Args:
        ops: list of (n,n) Hermitian matrices that mutually commute.
        tol: eigenvalue grouping tolerance.

    Returns:
        List of (eigenvalue_tuple, indices) where eigenvalue_tuple is a tuple
        of eigenvalues (one per op, None if unresolved) and indices is a list
        of basis vector indices spanning the joint eigenspace.
        Sorted by first op's eigenvalue descending, then second, etc.
    """
    n = ops[0].shape[0]
    sectors = [(tuple([None] * len(ops)), list(range(n)))]

    for op_idx, op in enumerate(ops):
        new_sectors = []
        for evals_tuple, indices in sectors:
            if len(indices) <= 1:
                new_sectors.append((evals_tuple, indices))
                continue
            sub_op = op[np.ix_(indices, indices)]
            sub_evals, sub_evecs = np.linalg.eigh(sub_op)
            used = set()
            for i in range(len(indices)):
                if i in used:
                    continue
                group = [j for j in range(len(indices))
                         if abs(sub_evals[j] - sub_evals[i]) < tol]
                used.update(group)
                new_evals = list(evals_tuple)
                new_evals[op_idx] = round(sub_evals[i].real, 10)
                new_indices = [indices[j] for j in group]
                new_sectors.append((tuple(new_evals), new_indices))
        sectors = new_sectors

    sectors.sort(key=lambda x: tuple(
        -abs(e) if e is not None else 0 for e in x[0]
    ))
    return sectors


def build_projectors(sectors, dim_total):
    """Build projector matrices from sector (evals_tuple, indices) list.

    Args:
        sectors: output of joint_diag_sectors().
        dim_total: total dimension of the Hilbert space.

    Returns:
        List of (n,n) projector matrices, one per sector.
    """
    projectors = []
    for _, indices in sectors:
        P = np.zeros((dim_total, dim_total), dtype=complex)
        for i in indices:
            e_i = np.zeros(dim_total)
            e_i[i] = 1.0
            P += np.outer(e_i, e_i)
        projectors.append(P)
    return projectors


def classify_sectors(sectors, dim_a, dim_b=None, dim_total=None, tol=1e-10):
    """Classify each sector as pure-A ('A'), pure-B ('B'), or hybrid ('H').

    A sector is pure-A if its support lies entirely in the first dim_a
    basis vectors; pure-B if entirely in the remainder; hybrid otherwise.

    Args:
        sectors: output of joint_diag_sectors().
        dim_a: dimension of block A.
        dim_b: dimension of block B. If None, inferred from dim_total - dim_a.
        dim_total: total dimension. If None, inferred from sector indices.
        tol: numerical zero threshold.

    Returns:
        List of str: 'A', 'B', or 'H' for each sector.
    """
    if dim_total is None:
        all_indices = []
        for _, indices in sectors:
            all_indices.extend(indices)
        dim_total = max(all_indices) + 1 if all_indices else dim_a
    if dim_b is None:
        dim_b = dim_total - dim_a

    types = []
    for _, indices in sectors:
        P = np.zeros((dim_total, dim_total))
        for i in indices:
            e_i = np.zeros(dim_total)
            e_i[i] = 1.0
            P += np.outer(e_i, e_i)
        a_norm = np.linalg.norm(P[:dim_a, :])
        b_norm = np.linalg.norm(P[dim_a:, :])
        if a_norm < tol:
            types.append('B')
        elif b_norm < tol:
            types.append('A')
        else:
            types.append('H')
    return types


# ============================================================
# 2. Transport & Lie curvature
# ============================================================

def compute_transport_kappa(rhos, projectors, compute_kappa1=True, cso=None):
    """Compute transport tensor K, kappa_0, and optionally kappa_1.

    DEPRECATED: prefer CubieSpectralOperator.transport_kappa(projectors) which
    uses cached generators and Lie generators.  This standalone function is
    retained only for S₃ prototypes and exploratory scripts that have no CSO.

    If a CSO instance is passed via ``cso=``, this function DELEGATES to
    cso.transport_kappa(projectors, compute_kappa1) — the canonical path.

    Args:
        rhos: list of (n,n) unitary representation matrices ρ(g).
        projectors: list of (n,n) projector matrices.
        compute_kappa1: if True, also compute κ₁ (commutator-based).
        cso: optional CubieSpectralOperator for cached delegation.

    Returns:
        (K, kappa0, kappa1) — three (n_sec, n_sec) arrays.
    """
    import warnings
    if cso is not None:
        return cso.transport_kappa(projectors, compute_kappa1=compute_kappa1)

    warnings.warn(
        "compute_transport_kappa() without cso= is deprecated. "
        "Use cso.transport_kappa(projectors) for the canonical cached path.",
        DeprecationWarning, stacklevel=2)

    n_sec = len(projectors)
    K = np.zeros((n_sec, n_sec))
    kappa0 = np.zeros((n_sec, n_sec))
    kappa1 = np.zeros((n_sec, n_sec)) if compute_kappa1 else None

    A_gs = [logm(rho_g) for rho_g in rhos]

    for a in range(n_sec):
        Pa = projectors[a]
        for b in range(n_sec):
            Pb = projectors[b]
            max_K = 0.0
            max_k0 = 0.0
            for i, rho_g in enumerate(rhos):
                max_K = max(max_K, np.linalg.norm(Pa @ rho_g @ Pb, 'fro'))
                max_k0 = max(max_k0, np.linalg.norm(Pa @ A_gs[i] @ Pb, 'fro'))
            K[a, b] = max_K
            kappa0[a, b] = max_k0

    if compute_kappa1:
        for a in range(n_sec):
            Pa = projectors[a]
            for b in range(n_sec):
                Pb = projectors[b]
                max_k1 = 0.0
                for Ag in A_gs:
                    for Ah in A_gs:
                        comm = Ag @ Ah - Ah @ Ag
                        max_k1 = max(max_k1, np.linalg.norm(Pa @ comm @ Pb, 'fro'))
                kappa1[a, b] = max_k1

    return K, kappa0, kappa1


# ============================================================
# 3. T7 detection
# ============================================================

def find_t7_pairs(K, kappa0, kappa1, sector_types, tol=1e-8):
    """Find T7 pairs: cross-block (A<->B) pairs with K≈0, κ₀≈0, κ₁≈0.

    A T7 pair is a pair of pure sectors in different blocks that have:
      - Zero direct transport (K=0)
      - Zero Lie gradient (κ₀=0)
      - Zero Lie curvature (κ₁=0)
      - A length-2 composition path through a hybrid sector (has_path=True)

    Args:
        K, kappa0, kappa1: from compute_transport_kappa().
        sector_types: list of 'A'/'B'/'H' from classify_sectors().
        tol: threshold for "zero".

    Returns:
        List of (a, b, has_path, K_val, k0_val, k1_val) tuples.
        has_path is True if ∃ hybrid h with K[a,h]>tol and K[h,b]>tol.
    """
    n = len(sector_types)
    pairs = []
    for a in range(n):
        if sector_types[a] not in ('A', 'B'):
            continue
        for b in range(a + 1, n):
            if sector_types[b] not in ('A', 'B'):
                continue
            if sector_types[a] == sector_types[b]:
                continue  # same block

            # Check for composition path via hybrid
            has_path = False
            for h in range(n):
                if sector_types[h] == 'H':
                    if K[a, h] > tol and K[h, b] > tol:
                        has_path = True
                        break

            if K[a, b] < tol and kappa0[a, b] < tol and kappa1[a, b] < tol:
                pairs.append((a, b, has_path,
                              float(K[a, b]), float(kappa0[a, b]),
                              float(kappa1[a, b])))
    return pairs


def analyze_t7(rhos, block_slices, center_ops=None):
    """One-shot T7 analysis: build Center, diag, classify, compute transport.

    Args:
        rhos: list of (n,n) unitary matrices ρ(g) for g in generators.
        block_slices: list of (name, slice) tuples defining the block decomposition.
            e.g. [('A', slice(0,3)), ('B', slice(3,9))]
        center_ops: optional list of Hermitian operators for joint diagonalization.
            If None, uses the full averaging operator A = (1/|rhos|) Σ ρ(g).

    Returns:
        dict with keys: sectors, projectors, types, K, kappa0, kappa1,
                        t7_pairs, dim_total, dim_a, n_sectors,
                        n_pure_a, n_pure_b, n_hybrid, n_t7, n_true_t7.
    """
    n = rhos[0].shape[0]
    dim_a = block_slices[0][1].stop  # assume first block starts at 0

    if center_ops is None:
        A = sum(rhos) / len(rhos)
        center_ops = [A]

    sectors = joint_diag_sectors(center_ops)
    projectors = build_projectors(sectors, n)
    types = classify_sectors(sectors, dim_a)

    K, kappa0, kappa1 = compute_transport_kappa(rhos, projectors)
    t7_pairs = find_t7_pairs(K, kappa0, kappa1, types)

    n_pure_a = sum(1 for t in types if t == 'A')
    n_pure_b = sum(1 for t in types if t == 'B')
    n_hybrid = sum(1 for t in types if t == 'H')
    n_true_t7 = sum(1 for _, _, has_path, _, _, _ in t7_pairs if has_path)

    return {
        'sectors': sectors,
        'projectors': projectors,
        'types': types,
        'K': K, 'kappa0': kappa0, 'kappa1': kappa1,
        't7_pairs': t7_pairs,
        'dim_total': n, 'dim_a': dim_a,
        'n_sectors': len(sectors),
        'n_pure_a': n_pure_a, 'n_pure_b': n_pure_b, 'n_hybrid': n_hybrid,
        'n_t7': len(t7_pairs), 'n_true_t7': n_true_t7,
    }


# ============================================================
# 4. Group element enumeration
# ============================================================

def inv_closed_subsets(group_order, inverse_map=None):
    """Enumerate all inverse-closed subsets of {0, ..., group_order-1}.

    Args:
        group_order: size of the group.
        inverse_map: dict {element: inverse}. If None, assumes every element
            is self-inverse (e.g., Z_2^k).

    Returns:
        List of lists, each an inverse-closed subset.
    """
    if inverse_map is None:
        inverse_map = {i: i for i in range(group_order)}

    subsets = []
    for r in range(1, group_order + 1):
        for combo in combinations(range(group_order), r):
            inv_set = set(combo)
            if all(inverse_map[x] in inv_set for x in combo):
                subsets.append(list(combo))
    return subsets


# ============================================================
# 5. Small group representations
# ============================================================

# --- S_3 ---

S3_PERMUTATIONS = [
    (0, 1, 2),  # identity
    (1, 0, 2),  # (12)
    (0, 2, 1),  # (23)
    (2, 1, 0),  # (13)
    (1, 2, 0),  # (123)
    (2, 0, 1),  # (132)
]

S3_ORDER = {0: 1, 1: 2, 2: 2, 3: 2, 4: 3, 5: 3}
S3_INVERSES = {0: 0, 1: 1, 2: 2, 3: 3, 4: 5, 5: 4}


def perm_matrix(perm, n=None):
    """Build n×n permutation matrix from a permutation tuple."""
    if n is None:
        n = len(perm)
    P = np.zeros((n, n))
    for i, j in enumerate(perm):
        P[j, i] = 1.0  # column i → row j
    return P


def build_s3_std_rep(g_perm):
    """S_3 standard 2-dimensional irreducible representation.

    Acts on R^3 by permuting coordinates, then projects onto the
    orthogonal complement of (1,1,1). Basis:
      e1 = (1, -1, 0) / sqrt(2)
      e2 = (1, 1, -2) / sqrt(6)

    Args:
        g_perm: permutation tuple of (0,1,2) → (p0,p1,p2).

    Returns:
        (2,2) real orthogonal matrix.
    """
    P3 = np.eye(3)[list(g_perm)]
    e1 = np.array([1., -1., 0.]) / np.sqrt(2)
    e2 = np.array([1., 1., -2.]) / np.sqrt(6)
    E = np.column_stack([e1, e2])
    return E.T @ P3 @ E


def build_s3_sign_rep(g_perm):
    """S_3 sign representation: +1 for even permutations, -1 for odd.

    Returns:
        float scalar (not a matrix).
    """
    inv = 0
    for i in range(len(g_perm)):
        for j in range(i + 1, len(g_perm)):
            if g_perm[i] > g_perm[j]:
                inv += 1
    return 1.0 if inv % 2 == 0 else -1.0


def build_s3_trivial_rep(g_perm):
    """S_3 trivial representation. Returns 1.0."""
    return 1.0


def build_s3_regular_rep(g_idx):
    """S_3 regular representation: 6×6 permutation matrix.

    The regular rep acts on C[G] by left multiplication:
    ρ_reg(g) |h⟩ = |gh⟩ for basis {|0⟩,...,|5⟩} corresponding to S3_PERMUTATIONS.

    Args:
        g_idx: index into S3_PERMUTATIONS for the acting element.

    Returns:
        (6,6) permutation matrix.
    """
    # Build Cayley table for S_3
    perms = S3_PERMUTATIONS
    result_perm = [None] * 6
    for h_idx, h_perm in enumerate(perms):
        # Compute gh as tuple composition
        g_perm = perms[g_idx]
        gh = tuple(g_perm[h_perm[i]] for i in range(3))
        result_perm[h_idx] = perms.index(gh)
    return perm_matrix(tuple(result_perm), 6)


def build_s3_natural_rep(g_perm):
    """S_3 natural permutation representation: 3×3 permutation matrix."""
    return perm_matrix(g_perm, 3)


def build_block_diag_rho(rhos_a, rhos_b):
    """Build list of block-diagonal ρ(g) = ρ_A(g) ⊕ ρ_B(g).

    Args:
        rhos_a: list of (dim_a, dim_a) matrices for block A.
        rhos_b: list of (dim_b, dim_b) matrices for block B.

    Returns:
        List of (dim_a+dim_b, dim_a+dim_b) block-diagonal matrices.
    """
    result = []
    dim_a = rhos_a[0].shape[0]
    dim_b = rhos_b[0].shape[0]
    dim_total = dim_a + dim_b
    for rA, rB in zip(rhos_a, rhos_b):
        rho = np.zeros((dim_total, dim_total), dtype=complex)
        rho[:dim_a, :dim_a] = rA
        rho[dim_a:, dim_a:] = rB
        result.append(rho)
    return result


# --- Abelian groups ---

def z2z2_characters():
    """Return dict of Z_2 × Z_2 characters evaluated at {0, a, b, c=ab}.

    Characters: χ_00 (trivial), χ_10, χ_01, χ_11.
    χ_ij(a^p b^q) = (-1)^{i*p + j*q}.
    """
    return {
        'chi_00': np.array([1., 1., 1., 1.]),
        'chi_10': np.array([1., -1., 1., -1.]),
        'chi_01': np.array([1., 1., -1., -1.]),
        'chi_11': np.array([1., -1., -1., 1.]),
    }


def build_abelian_rho(chars_a, chars_b, char_table):
    """Build block-diagonal ρ for two sets of 1D characters.

    Args:
        chars_a: list of character names for block A.
        chars_b: list of character names for block B.
        char_table: dict {name: array of length group_order}.

    Returns:
        (rhos, dim_a, dim_b): list of block-diagonal matrices and dimensions.
    """
    group_order = len(next(iter(char_table.values())))
    rhos = []
    dim_a = len(chars_a)
    dim_b = len(chars_b)
    for g_idx in range(group_order):
        rho_A = np.diag([char_table[c][g_idx] for c in chars_a])
        rho_B = np.diag([char_table[c][g_idx] for c in chars_b])
        rho_g = np.zeros((dim_a + dim_b, dim_a + dim_b))
        rho_g[:dim_a, :dim_a] = rho_A
        rho_g[dim_a:, dim_a:] = rho_B
        rhos.append(rho_g)
    return rhos, dim_a, dim_b


# Convenience: build rho for a standard set of generators
def build_rho_from_gens(generators, rep_fn_a, rep_fn_b):
    """Build block-diagonal ρ from generator list and per-block rep functions.

    Args:
        generators: list of group elements (format depends on rep_fn).
        rep_fn_a: function element → matrix for block A.
        rep_fn_b: function element → matrix for block B.

    Returns:
        List of block-diagonal matrices, one per generator.
    """
    rhos_a = [rep_fn_a(g) for g in generators]
    rhos_b = [rep_fn_b(g) for g in generators]
    return build_block_diag_rho(rhos_a, rhos_b)


# ============================================================
# 6. Numerical irrep block detection
# ============================================================

def detect_irrep_blocks(generators, n_random_ops=8, tol=1e-6):
    """Detect irreducible representation blocks via random operator signatures.

    Constructs n_random_ops random Hermitian combinations of the generators,
    diagonalizes the first one, then clusters basis vectors whose signatures
    (diagonal values) agree across all random operators.

    Args:
        generators: list of (n,n) matrices ρ(g).
        n_random_ops: number of random Hermitian operators to use.
        tol: clustering tolerance for signature matching.

    Returns:
        (blocks, U, signatures) where blocks is a list of index lists sorted
        by decreasing size, U is the diagonalizing basis, and signatures is
        an (n, n_random_ops) array of diagonal values.
    """
    n = generators[0].shape[0]

    H_ops = []
    for _ in range(n_random_ops):
        coeffs = np.random.randn(len(generators))
        H = sum(c * (rho + rho.T.conj()) / 2
                for c, rho in zip(coeffs, generators))
        H_ops.append(H)

    eigvals_0, U = np.linalg.eigh(H_ops[0])
    idx = np.argsort(-np.abs(eigvals_0))
    U = U[:, idx]

    signatures = np.zeros((n, n_random_ops))
    for k, H in enumerate(H_ops):
        diag_H = np.real(np.diag(U.T.conj() @ H @ U))
        signatures[:, k] = diag_H

    adj = np.ones((n, n), dtype=bool)
    for k in range(n_random_ops):
        diff = np.abs(signatures[:, k:k + 1] - signatures[:, k:k + 1].T)
        adj = adj & (diff < tol * (1 + np.abs(signatures[:, k]).max()))

    visited = np.zeros(n, dtype=bool)
    blocks = []
    for i in range(n):
        if visited[i]:
            continue
        stack = [i]
        component = []
        while stack:
            j = stack.pop()
            if visited[j]:
                continue
            visited[j] = True
            component.append(j)
            neighbors = np.where(adj[j])[0]
            for nb in neighbors:
                if not visited[nb]:
                    stack.append(nb)
        blocks.append(sorted(component))

    blocks.sort(key=len, reverse=True)
    return blocks, U, signatures


def map_eigenspaces_to_irreps(V, w, irrep_blocks, U_irrep):
    """Map A-eigenspaces to detected irrep blocks.

    For each eigenvalue λ and each irrep block, computes the Frobenius
    overlap ‖P_irrep P_λ‖_F and checks whether the overlap is consistent
    with the irrep dimension.

    Args:
        V: eigenvector matrix of A.
        w: eigenvalues of A.
        irrep_blocks: list of index lists (from detect_irrep_blocks).
        U_irrep: basis in which irreps were detected.

    Returns:
        List of dicts with keys: lambda, irrep_idx, irrep_dim, overlap,
        overlap_vs_dim, is_matched, eigenspace_dim.
    """
    unique_w = np.unique(np.round(w, 6))
    mapping = []
    for lam in sorted(unique_w, reverse=True):
        mask = np.abs(w - lam) < 1e-6
        V_lam = V[:, mask]
        P_lam = V_lam @ V_lam.T.conj()
        d_lam = np.sum(mask)

        for i, block in enumerate(irrep_blocks):
            Ub = U_irrep[:, block]
            P_irrep = Ub @ Ub.T.conj()
            overlap = np.linalg.norm(P_irrep @ P_lam, 'fro')
            dim_b = len(block)
            is_matched = abs(overlap - np.sqrt(dim_b)) < 0.1 * np.sqrt(dim_b)
            mapping.append({
                'lambda': lam, 'irrep_idx': i, 'irrep_dim': dim_b,
                'overlap': overlap, 'overlap_vs_dim': overlap / np.sqrt(dim_b) if dim_b > 0 else 0,
                'is_matched': is_matched,
                'eigenspace_dim': d_lam,
            })

    return mapping


def verify_schur_on_irreps(generators, irrep_blocks, U_irrep, tol=1e-6):
    """Verify Schur's lemma on detected irrep blocks.

    For each block, checks that every generator ρ(g) restricted to the block
    is approximately scalar: ‖M − (Tr(M)/d)·I‖ ≈ 0.

    Args:
        generators: list of (n,n) matrices ρ(g).
        irrep_blocks: list of index lists (from detect_irrep_blocks).
        U_irrep: basis in which irreps were detected.
        tol: relative deviation threshold.

    Returns:
        List of dicts with keys: irrep_idx, dim, max_deviation,
        rel_deviation, is_irrep.
    """
    results = []
    for i, block in enumerate(irrep_blocks):
        Ub = U_irrep[:, block]
        d = len(block)
        max_dev = 0
        for rho_s in generators:
            M = Ub.T.conj() @ rho_s @ Ub
            c = np.trace(M) / d
            dev = np.linalg.norm(M - c * np.eye(d))
            max_dev = max(max_dev, dev)

        norm_factor = np.sqrt(d)
        rel_dev = max_dev / norm_factor if norm_factor > 0 else max_dev
        is_irrep = rel_dev < tol * 10
        results.append({
            'irrep_idx': i, 'dim': d,
            'max_deviation': max_dev, 'rel_deviation': rel_dev,
            'is_irrep': is_irrep,
        })
    return results
