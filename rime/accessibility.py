"""
Accessibility Completeness: R1/R2/D computation.

Core functions for the (R1, R2) => D theorem:
  - compute_R1 / compute_R2 -- discrete accessibility data
  - compute_lie_depth_matrix -- D matrix via Lie filtration
  - single_term_bridge_audit / matrix_nondeg_audit -- bridge analysis
  - accessibility_signature -- convenience wrapper

All functions operate on sector bases Vs and skew-Hermitian generators Xs.
"""
import numpy as np
from itertools import combinations


# ============================================================
# Internal helpers
# ============================================================

def _gram_schmidt(vecs, tol=1e-8):
    """Orthonormalize a list of complex vectors. Two passes for stability.

    Uses full complex inner product <b|v> = vdot(b, v), not real part only.
    """
    for _ in range(2):
        for p in range(len(vecs)):
            for q in range(p):
                coeff = np.vdot(vecs[q], vecs[p])
                vecs[p] = vecs[p] - coeff * vecs[q]
            nrm = np.linalg.norm(vecs[p])
            if nrm > tol:
                vecs[p] = vecs[p] / nrm
    return [v for v in vecs if np.linalg.norm(v) > tol]


def _project_out(v, basis_vecs):
    """Project v out of span(basis_vecs). Returns residual.

    Uses full complex inner product: coeff = vdot(b, v).
    """
    result = v.copy()
    for b in basis_vecs:
        coeff = np.vdot(b, result)
        result = result - coeff * b
    return result


def _rank_real_blocks(blocks, tol=1e-8):
    """Real rank of a set of complex matrices (stack real/imag, SVD)."""
    if not blocks:
        return 0
    d_i, d_j = blocks[0].shape
    if d_i == 0 or d_j == 0:
        return 0
    data = np.zeros((len(blocks), 2 * d_i * d_j))
    for k, M in enumerate(blocks):
        data[k, :d_i * d_j] = M.real.reshape(-1)
        data[k, d_i * d_j:] = M.imag.reshape(-1)
    _, s, _ = np.linalg.svd(data, full_matrices=False)
    return int(np.sum(s > tol * max(1.0, s[0])))


def sector_block_norm(Vs, X, i, j):
    """Frobenius norm of the projected block Q_i X Q_j.

    Args:
        Vs: list of sector bases, Vs[k] = (n, d_k).
        X: (n,n) observable matrix.
        i, j: sector indices.

    Returns:
        float Frobenius norm of Vs[i]^H X Vs[j].
    """
    return float(np.linalg.norm(Vs[i].conj().T @ X @ Vs[j], 'fro'))


def projector_block_norm(Qs, X, i, j):
    """Frobenius norm of the projector-cut block Q_i X Q_j.

    Args:
        Qs: list of projector matrices.
        X: (n,n) observable matrix.
        i, j: sector indices.

    Returns:
        float Frobenius norm of Qs[i] @ X @ Qs[j].
    """
    return float(np.linalg.norm(Qs[i] @ X @ Qs[j], 'fro'))


def offdiag_count(mat):
    """Count truthy off-diagonal entries in a square matrix."""
    n = mat.shape[0]
    return int(sum(bool(mat[i, j]) for i in range(n) for j in range(n) if i != j))


def compute_direct_support(Vs, Xs, tol=1e-8):
    """Aggregate direct sector support over an observable family.

    support[i,j] is True iff some X in Xs has ||Q_i X Q_j||_F > tol.
    Diagonal entries are left False.
    """
    n_sec = len(Vs)
    support = np.zeros((n_sec, n_sec), dtype=bool)
    for X in Xs:
        for i in range(n_sec):
            for j in range(n_sec):
                if i != j and sector_block_norm(Vs, X, i, j) > tol:
                    support[i, j] = True
    return support


def compute_length_two_support(Vs, Xs, tol=1e-8):
    """Aggregate length-two word support over an observable family.

    support[i,j] is True iff some product XY has ||Q_i XY Q_j||_F > tol.
    This is a word/transport diagnostic, not the commutator R2 invariant.
    """
    n_sec = len(Vs)
    support = np.zeros((n_sec, n_sec), dtype=bool)
    for X in Xs:
        for Y in Xs:
            XY = X @ Y
            for i in range(n_sec):
                for j in range(n_sec):
                    if i != j and sector_block_norm(Vs, XY, i, j) > tol:
                        support[i, j] = True
    return support


def compute_word_depth_matrix(Vs, Xs, max_depth=4, tol=1e-8, frozen=999):
    """Compute first accessibility depth using words in the observables.

    Depth 1 uses generators, depth 2 uses products of two generators, etc.
    This is useful for transport/PDE/control diagnostics. It is distinct from
    compute_lie_depth_matrix, which uses the Lie filtration.
    """
    n_sec = len(Vs)
    dim = Xs[0].shape[0]
    D = np.full((n_sec, n_sec), frozen, dtype=int)
    np.fill_diagonal(D, 0)

    words = [np.eye(dim, dtype=Xs[0].dtype)]
    for depth in range(1, max_depth + 1):
        words = [X @ W for X in Xs for W in words]
        for i in range(n_sec):
            for j in range(n_sec):
                if i == j or D[i, j] != frozen:
                    continue
                if any(sector_block_norm(Vs, W, i, j) > tol for W in words):
                    D[i, j] = depth
    return D


def plateau_fraction(D, depth, frozen=999):
    """Fraction of off-diagonal sector pairs reachable by a given depth."""
    n_sec = D.shape[0]
    total = n_sec * (n_sec - 1)
    if total == 0:
        return 0.0
    reached = sum(
        1 for i in range(n_sec) for j in range(n_sec)
        if i != j and D[i, j] != frozen and D[i, j] <= depth
    )
    return reached / total


# ============================================================
# R1 / R2 computation
# ============================================================

def compute_R1(Vs, Xs, tol=1e-8):
    """Compute generator support matrix.

    R1[g, i, j] = True  iff  ||Q_i X_g Q_j||_F > tol.

    Args:
        Vs: list of sector bases, Vs[k] = (n, d_k).
        Xs: list of (n,n) skew-Hermitian generator matrices.
        tol: Frobenius norm threshold for "non-zero".

    Returns:
        boolean array of shape (n_gens, n_sec, n_sec).
    """
    n_gens = len(Xs)
    n_sec = len(Vs)
    R1 = np.zeros((n_gens, n_sec, n_sec), dtype=bool)
    for g in range(n_gens):
        for i in range(n_sec):
            for j in range(n_sec):
                block = Vs[i].conj().T @ Xs[g] @ Vs[j]
                if np.linalg.norm(block, 'fro') > tol:
                    R1[g, i, j] = True
    return R1


def compute_R2(Vs, Xs, tol=1e-8):
    """Compute commutator survival matrix.

    R2[cp, i, j] = True  iff  ||Q_i [X_g, X_h] Q_j||_F > tol,
    where cp indexes (g, h) pairs with g < h.

    Args:
        Vs: list of sector bases.
        Xs: list of generator matrices.
        tol: Frobenius norm threshold.

    Returns:
        boolean array of shape (n_pairs, n_sec, n_sec),
        and list of (g, h) pair tuples.
    """
    n_gens = len(Xs)
    n_sec = len(Vs)
    n_pairs = n_gens * (n_gens - 1) // 2
    R2 = np.zeros((n_pairs, n_sec, n_sec), dtype=bool)
    pairs = []

    cp = 0
    for g in range(n_gens):
        for h in range(g + 1, n_gens):
            pairs.append((g, h))
            comm = Xs[g] @ Xs[h] - Xs[h] @ Xs[g]
            for i in range(n_sec):
                for j in range(n_sec):
                    block = Vs[i].conj().T @ comm @ Vs[j]
                    if np.linalg.norm(block, 'fro') > tol:
                        R2[cp, i, j] = True
            cp += 1

    return R2, pairs


def compute_R2_per_generator(R2_by_pair, n_gens):
    """Convert per-commutator-pair R2 to per-generator R2.

    R2_gen[g, i, j] = True if any commutator involving g connects i->j.

    Args:
        R2_by_pair: boolean array of shape (n_pairs, n_sec, n_sec).
        n_gens: number of generators.

    Returns:
        boolean array of shape (n_gens, n_sec, n_sec).
    """
    n_pairs, n_sec, _ = R2_by_pair.shape
    R2_gen = np.zeros((n_gens, n_sec, n_sec), dtype=bool)
    cp = 0
    for g in range(n_gens):
        for h in range(g + 1, n_gens):
            for i in range(n_sec):
                for j in range(n_sec):
                    if R2_by_pair[cp, i, j]:
                        R2_gen[g, i, j] = True
                        R2_gen[h, i, j] = True
            cp += 1
    return R2_gen


# ============================================================
# Lie filtration and depth matrix
# ============================================================

def compute_lie_filtration(Xs, max_depth=4, tol=1e-8):
    """Compute Lie filtration basis by depth.

    Depth 0: generators
    Depth 1: commutators [X_g, X_h]
    Depth d>=2: [basis_{d-1}, generators]

    Args:
        Xs: list of (n,n) skew-Hermitian generator matrices.
        max_depth: maximum depth to compute.
        tol: Gram-Schmidt norm threshold.

    Returns:
        list of lists: per_depth[d] = list of vectorized basis matrices.
    """
    n_total = Xs[0].shape[0]
    per_depth = []

    # Depth 0: generators
    basis_vecs = [X.flatten() for X in Xs]
    basis_vecs = _gram_schmidt(basis_vecs, tol)
    per_depth.append(basis_vecs[:])

    # Depth 1: commutators
    depth1 = []
    n_gens = len(Xs)
    for g, h in combinations(range(n_gens), 2):
        comm = Xs[g] @ Xs[h] - Xs[h] @ Xs[g]
        v = _project_out(comm.flatten(), basis_vecs)
        nrm = np.linalg.norm(v)
        if nrm > tol:
            depth1.append(v / nrm)
            basis_vecs.append(v / nrm)
    per_depth.append(depth1[:])

    # Depth 2+: nested commutators
    for d in range(2, max_depth):
        layer = []
        for v_prev in per_depth[-1]:
            mat_prev = v_prev.reshape(n_total, n_total)
            for X in Xs:
                nested = mat_prev @ X - X @ mat_prev
                v = _project_out(nested.flatten(), basis_vecs)
                nrm = np.linalg.norm(v)
                if nrm > tol:
                    layer.append(v / nrm)
                    basis_vecs.append(v / nrm)
        per_depth.append(layer)

    return per_depth


def compute_lie_depth_matrix(Vs, Xs, max_depth=4, tol=1e-8):
    """Compute accessibility depth matrix D via Lie filtration.

    D[i, j] = first depth d where some Lie basis element connects sector i to j.
    D[i, i] = 0 (diagonal).
    D[i, j] = 999 if Frozen (no connection through any depth).

    Args:
        Vs: list of sector bases.
        Xs: list of generator matrices.
        max_depth: maximum depth to probe.
        tol: rank threshold.

    Returns:
        D: (n_sec, n_sec) int matrix.
        per_depth: list of basis vector lists per depth.
        cum_bases: cumulative basis vectors per depth.
    """
    n_total = Xs[0].shape[0]
    n_sec = len(Vs)

    per_depth = compute_lie_filtration(Xs, max_depth, tol)

    # Cumulative bases
    cum_bases = []
    cum = []
    for layer in per_depth:
        cum = cum + layer
        cum_bases.append(cum[:])

    D = np.full((n_sec, n_sec), -1)
    for i in range(n_sec):
        D[i, i] = 0

    for i in range(n_sec):
        for j in range(n_sec):
            if i == j:
                continue
            found = False
            for d_idx, cb in enumerate(cum_bases):
                mats = [v.reshape(n_total, n_total) for v in cb]
                blocks = [Vs[i].conj().T @ M @ Vs[j] for M in mats]
                if _rank_real_blocks(blocks, tol) > 0:
                    D[i, j] = d_idx
                    found = True
                    break
            if not found:
                D[i, j] = 999  # Frozen

    return D, per_depth, cum_bases


# ============================================================
# Single-term bridge audit
# ============================================================

def single_term_bridge_audit(Vs, Xs, tol=1e-8):
    """Enumerate all single-term commutator bridges.

    For each (i, j, g, h) with g != h, computes per-intermediate-sector
    contributions T_k^{gh} = Q_i X_g Q_k X_h Q_j and classifies each
    k-contribution as dead or alive.

    A single-term bridge has exactly one k with alive T_k^{gh} and zero
    cross-term T_k^{hg}, or vice versa.

    Args:
        Vs: list of sector bases.
        Xs: list of generator matrices.
        tol: Frobenius norm threshold.

    Returns:
        list of dicts with keys: type, i, j, g, h, k, A, B, prod,
        a_nrm, b_nrm, prod_nrm, d_i, d_k, d_j, orientation.
        'g' and 'h' are always the ORIGINAL generator indices (never swapped).
        'orientation' is 'gh' or 'hg' -- which ordering the single-term uses.
        'A' = Q_i X_{first} Q_k, 'B' = Q_k X_{second} Q_j.
        The vanishing cross-term is Q_i X_{vanishing} Q_k where
        vanishing = h for orientation='gh', vanishing = g for orientation='hg'.
    """
    n_sec = len(Vs)
    n_gens = len(Xs)
    bridges = []

    for g in range(n_gens):
        for h in range(n_gens):
            if g == h:
                continue
            for i in range(n_sec):
                for j in range(n_sec):
                    alive_gh = []
                    alive_hg = []

                    for k in range(n_sec):
                        A_gh = Vs[i].conj().T @ Xs[g] @ Vs[k]
                        B_gh = Vs[k].conj().T @ Xs[h] @ Vs[j]
                        term_gh = A_gh @ B_gh
                        nrm_gh = np.linalg.norm(term_gh, 'fro')
                        if nrm_gh > tol:
                            alive_gh.append((k, nrm_gh, A_gh, B_gh, term_gh))

                        A_hg = Vs[i].conj().T @ Xs[h] @ Vs[k]
                        B_hg = Vs[k].conj().T @ Xs[g] @ Vs[j]
                        term_hg = A_hg @ B_hg
                        nrm_hg = np.linalg.norm(term_hg, 'fro')
                        if nrm_hg > tol:
                            alive_hg.append((k, nrm_hg, A_hg, B_hg, term_hg))

                    if len(alive_gh) == 1 and len(alive_hg) == 0:
                        k, nrm, A, B, term = alive_gh[0]
                        bridges.append({
                            'type': 'single', 'orientation': 'gh',
                            'i': i, 'j': j,
                            'g': g, 'h': h, 'k': k,
                            'A': A, 'B': B, 'prod': term,
                            'a_nrm': np.linalg.norm(A, 'fro'),
                            'b_nrm': np.linalg.norm(B, 'fro'),
                            'prod_nrm': nrm,
                            'd_i': Vs[i].shape[1], 'd_k': Vs[k].shape[1],
                            'd_j': Vs[j].shape[1],
                        })
                    elif len(alive_hg) == 1 and len(alive_gh) == 0:
                        k, nrm, A, B, term = alive_hg[0]
                        bridges.append({
                            'type': 'single', 'orientation': 'hg',
                            'i': i, 'j': j,
                            'g': g, 'h': h, 'k': k,
                            'A': A, 'B': B, 'prod': term,
                            'a_nrm': np.linalg.norm(A, 'fro'),
                            'b_nrm': np.linalg.norm(B, 'fro'),
                            'prod_nrm': nrm,
                            'd_i': Vs[i].shape[1], 'd_k': Vs[k].shape[1],
                            'd_j': Vs[j].shape[1],
                        })

    return bridges


def matrix_nondeg_audit(bridges, tol=1e-8):
    """Check dimension + full rank conditions for single-term bridges.

    Adds keys to each bridge dict:
      rank_A, rank_B, dim_ok, full_col_rank, full_row_rank,
      structural, product_zero

    Args:
        bridges: list of bridge dicts from single_term_bridge_audit().
        tol: rank tolerance.

    Returns:
        The same list with additional keys added in-place.
    """
    for b in bridges:
        A, B = b['A'], b['B']
        d_i, d_k, d_j = b['d_i'], b['d_k'], b['d_j']

        rank_A = np.linalg.matrix_rank(A, tol=tol)
        rank_B = np.linalg.matrix_rank(B, tol=tol)

        dim_ok = d_k <= min(d_i, d_j)
        full_col_rank = (d_k <= d_i) and (rank_A == d_k)
        full_row_rank = (d_k <= d_j) and (rank_B == d_k)
        structural = full_col_rank or full_row_rank

        b['rank_A'] = rank_A
        b['rank_B'] = rank_B
        b['dim_ok'] = dim_ok
        b['full_col_rank'] = full_col_rank
        b['full_row_rank'] = full_row_rank
        b['structural'] = structural
        b['product_zero'] = b['prod_nrm'] <= tol

    return bridges


# ============================================================
# Kappa depth values (numeric, for Papers II/III)
# ============================================================

def compute_kappa_depth_matrix(Vs, Xs, max_depth=4, tol=1e-8):
    """Compute kappa_d[i,j] = max_{C in Lie^(d)} ||Q_i C Q_j||_F for each depth.

    Uses the Lie filtration basis from compute_lie_filtration(). At each depth d,
    iterates over the orthonormal basis of Lie^(d) and records the maximum
    Frobenius norm of each projected block.

    This gives the numeric kappa_d values (Paper III), not the binary D matrix.
    kappa_d[i,j] > 0 iff D[i,j] <= d.

    Args:
        Vs: list of sector bases.
        Xs: list of generator matrices.
        max_depth: maximum Lie filtration depth.
        tol: threshold for zero.

    Returns:
        list of (n_sec, n_sec) arrays, kappa_by_depth[d] = kappa_d matrix.
    """
    n_total = Xs[0].shape[0]
    n_sec = len(Vs)
    per_depth = compute_lie_filtration(Xs, max_depth, tol)

    kappa_by_depth = []
    for layer in per_depth:
        kappa_d = np.zeros((n_sec, n_sec))
        for v in layer:
            M = v.reshape(n_total, n_total)
            for i in range(n_sec):
                for j in range(n_sec):
                    block = Vs[i].conj().T @ M @ Vs[j]
                    nrm = np.linalg.norm(block, 'fro')
                    if nrm > kappa_d[i, j]:
                        kappa_d[i, j] = nrm
        kappa_by_depth.append(kappa_d)

    return kappa_by_depth


def compute_kappa_01(Vs, Xs):
    """Compute kappa_0 and kappa_1 from sector bases and Lie generators.

    kappa_0[i,j] = max_g ||Q_i X_g Q_j||_F        (direct generator transport)
    kappa_1[i,j] = max_{g,h} ||Q_i [X_g,X_h] Q_j||_F  (commutator transport)

    This is the Lie-algebraic counterpart to the transport tensor K.
    For Paper II/III: kappa_0 corresponds to transport via generators,
    kappa_1 corresponds to transport via commutators.

    Args:
        Vs: list of sector bases.
        Xs: list of skew-Hermitian generator matrices.

    Returns:
        (kappa0, kappa1) -- two (n_sec, n_sec) arrays.
    """
    n_sec = len(Vs)
    n_gens = len(Xs)

    kappa0 = np.zeros((n_sec, n_sec))
    for a in range(n_sec):
        for b in range(n_sec):
            max_k0 = 0.0
            for X in Xs:
                nrm = np.linalg.norm(Vs[a].conj().T @ X @ Vs[b], 'fro')
                max_k0 = max(max_k0, nrm)
            kappa0[a, b] = max_k0

    kappa1 = np.zeros((n_sec, n_sec))
    for a in range(n_sec):
        for b in range(n_sec):
            max_k1 = 0.0
            for g in range(n_gens):
                for h in range(g + 1, n_gens):
                    comm = Xs[g] @ Xs[h] - Xs[h] @ Xs[g]
                    nrm = np.linalg.norm(Vs[a].conj().T @ comm @ Vs[b], 'fro')
                    if nrm > max_k1:
                        max_k1 = nrm
            kappa1[a, b] = max_k1

    return kappa0, kappa1


def compute_transport_tensor(Vs, rhos):
    """Compute transport tensor K from sector bases and unitary representations.

    K[i,j] = max_g ||Q_i rho(g) Q_j||_F   (Paper II, eq.1)

    This is the maximum Frobenius norm of the projected representation
    matrix across all generators. K measures direct (depth-0) transport
    between sectors.

    Args:
        Vs: list of sector bases.
        rhos: list of unitary representation matrices rho(g).

    Returns:
        (n_sec, n_sec) array.
    """
    n_sec = len(Vs)
    K = np.zeros((n_sec, n_sec))
    for a in range(n_sec):
        for b in range(n_sec):
            max_K = 0.0
            for rho_g in rhos:
                nrm = np.linalg.norm(Vs[a].conj().T @ rho_g @ Vs[b], 'fro')
                max_K = max(max_K, nrm)
            K[a, b] = max_K
    return K


# ============================================================
# Convenience
# ============================================================

def compute_signature_from_D(D):
    """Extract (A0, A1, A2, Ainf) from a depth matrix.

    A0 = direct edges (excluding diagonal), A1 = commutator,
    A2 = nested commutator, Ainf = Frozen.

    Warns if the matrix contains entries with D >= 3 that are not Frozen (999),
    since these are not counted in the returned tuple.
    """
    n_sec = D.shape[0]
    A0 = int(np.sum(D == 0)) - n_sec
    A1 = int(np.sum(D == 1))
    A2 = int(np.sum(D == 2))
    Ainf = int(np.sum(D == 999))
    other = int(np.sum((D >= 3) & (D != 999)))
    if other > 0:
        import warnings
        warnings.warn(
            f"Found {other} entries with D >= 3 (not Frozen). "
            f"These are NOT reflected in (A0,A1,A2,Ainf)."
        )
    return (A0, A1, A2, Ainf)


def accessibility_signature(Vs, Xs, max_depth=4, tol=1e-8):
    """Convenience: compute R1, R2, D, and signature in one call.

    Args:
        Vs: list of sector bases.
        Xs: list of generator matrices.
        max_depth: maximum Lie filtration depth.
        tol: norm/rank threshold.

    Returns:
        dict with keys: R1, R2, R2_pairs, R2_gen, D, sig, per_depth,
                        cum_bases, n_sec, n_gens.
    """
    R1 = compute_R1(Vs, Xs, tol)
    R2, R2_pairs = compute_R2(Vs, Xs, tol)
    R2_gen = compute_R2_per_generator(R2, len(Xs))
    D, per_depth, cum_bases = compute_lie_depth_matrix(Vs, Xs, max_depth, tol)
    sig = compute_signature_from_D(D)

    return {
        'R1': R1,
        'R2': R2,
        'R2_pairs': R2_pairs,
        'R2_gen': R2_gen,
        'D': D,
        'sig': sig,
        'per_depth': per_depth,
        'cum_bases': cum_bases,
        'n_sec': len(Vs),
        'n_gens': len(Xs),
    }


# ============================================================
# AccessibilityEngine — unified audit wrapper (2026-07-04)
# ============================================================

class AccessibilityEngine:
    """Unified wrapper for R1/R2/D computation on a sectorized observable framework.

    Inspired by Yang 2026's InvariantEngine pattern: a single object that
    holds the system (Vs, Xs) and provides scoped audit methods.

    Usage:
        engine = AccessibilityEngine(Vs, Xs)
        summary = engine.audit()           # full audit
        d_matrix = engine.depth()           # D matrix only
        r1, r2 = engine.support()           # R1, R2 only
        frozen = engine.frozen_pairs()      # frozen pair counts
    """

    def __init__(self, Vs, Xs, tol=1e-8, max_depth=4, seed=42):
        """Initialize engine with sectorized observable framework.

        Args:
            Vs: list of sector bases, each (dim, d_k).
            Xs: list of (dim, dim) skew-Hermitian generator matrices.
            tol: Frobenius norm threshold for "nonzero".
            max_depth: maximum Lie depth to probe.
            seed: for reproducible random linear combinations in Lie filtration.
        """
        self.Vs = Vs
        self.Xs = Xs
        self.tol = tol
        self.max_depth = max_depth
        self.seed = seed
        self._cache = {}

    @property
    def n_sec(self):
        return len(self.Vs)

    @property
    def n_gen(self):
        return len(self.Xs)

    @property
    def sector_dims(self):
        return [V.shape[1] for V in self.Vs]

    # ---- cached computations ----

    def _get_R1(self):
        if 'R1' not in self._cache:
            self._cache['R1'] = compute_R1(self.Vs, self.Xs, tol=self.tol)
        return self._cache['R1']

    def _get_R2(self):
        if 'R2_arr' not in self._cache:
            R2_arr, R2_pairs = compute_R2(self.Vs, self.Xs, tol=self.tol)
            self._cache['R2_arr'] = R2_arr
            self._cache['R2_pairs'] = R2_pairs
        return self._cache['R2_arr'], self._cache['R2_pairs']

    def _get_D(self):
        if 'D' not in self._cache:
            D, per_depth, cum_bases = compute_lie_depth_matrix(
                self.Vs, self.Xs, max_depth=self.max_depth, tol=self.tol)
            self._cache['D'] = D
            self._cache['per_depth'] = per_depth
            self._cache['cum_bases'] = cum_bases
        return self._cache['D'], self._cache['per_depth'], self._cache['cum_bases']

    # ---- scoped queries ----

    def support(self):
        """Return (R1, R2_arr, R2_pairs)."""
        return self._get_R1(), *self._get_R2()

    def depth(self):
        """Return (D, per_depth)."""
        D, per_depth, _ = self._get_D()
        return D, per_depth

    def frozen_pairs(self):
        """Return counts of R1-frozen, D-frozen, and D-repaired pairs."""
        R1 = self._get_R1()
        D, _, _ = self._get_D()
        ns = self.n_sec
        offdiag = ~np.eye(ns, dtype=bool)
        R1_graph = np.zeros((ns, ns), dtype=bool)
        for g in range(self.n_gen):
            R1_graph |= R1[g]
        frozen_R1 = ns * (ns - 1) - int(np.sum(R1_graph & offdiag))
        frozen_D = sum(1 for i in range(ns) for j in range(ns)
                       if i != j and D[i, j] >= self.max_depth)
        repaired = sum(1 for i in range(ns) for j in range(ns)
                       if i != j and not R1_graph[i, j] and D[i, j] < self.max_depth)
        return {'frozen_R1': frozen_R1, 'frozen_D': frozen_D, 'D_repaired': repaired}

    def per_sector_depth(self):
        """Return per-sector D matrix rows as dict."""
        D, _, _ = self._get_D()
        rows = {}
        for i in range(self.n_sec):
            rows[i] = [int(D[i, j]) for j in range(self.n_sec) if i != j]
        return rows

    def audit(self):
        """Full audit returning all metrics.

        Convention:
            R1_pct/R2_pct are off-diagonal accessibility densities. Diagonal
            block support is still reported separately as
            R1_tensor_pct/R2_tensor_pct. Frozen-pair counts are always
            off-diagonal sector-pair counts.
        """
        R1 = self._get_R1()
        R2_arr, R2_pairs = self._get_R2()
        D, per_depth, _ = self._get_D()
        frozen = self.frozen_pairs()
        ns, ng = self.n_sec, self.n_gen
        offdiag = ~np.eye(ns, dtype=bool)

        r1_tensor_possible = ng * ns * ns
        r2_tensor_possible = len(R2_pairs) * ns * ns
        r1_offdiag_possible = ng * ns * (ns - 1)
        r2_offdiag_possible = len(R2_pairs) * ns * (ns - 1)
        r1_tensor_count = int(np.sum(R1))
        r2_tensor_count = int(np.sum(R2_arr))
        r1_offdiag_count = int(np.sum(R1[:, offdiag]))
        r2_offdiag_count = int(np.sum(R2_arr[:, offdiag]))
        d_vals = [D[i, j] for i in range(ns) for j in range(ns) if i != j]

        return {
            'n_sec': ns, 'n_gen': ng,
            'sector_dims': self.sector_dims,
            'R1_count': r1_offdiag_count,
            'R2_count': r2_offdiag_count,
            'R1_tensor_count': r1_tensor_count,
            'R2_tensor_count': r2_tensor_count,
            'R1_pct': 100 * r1_offdiag_count / r1_offdiag_possible if r1_offdiag_possible else 0,
            'R2_pct': 100 * r2_offdiag_count / r2_offdiag_possible if r2_offdiag_possible else 0,
            'R1_offdiag_pct': 100 * r1_offdiag_count / r1_offdiag_possible if r1_offdiag_possible else 0,
            'R2_offdiag_pct': 100 * r2_offdiag_count / r2_offdiag_possible if r2_offdiag_possible else 0,
            'R1_tensor_pct': 100 * r1_tensor_count / r1_tensor_possible if r1_tensor_possible else 0,
            'R2_tensor_pct': 100 * r2_tensor_count / r2_tensor_possible if r2_tensor_possible else 0,
            'D_max': int(max(d_vals)) if d_vals else -1,
            'D_mean': float(np.mean(d_vals)) if d_vals else -1,
            'per_depth_sizes': [len(pd) for pd in per_depth],
            **frozen,
        }

    def __repr__(self):
        return (f"AccessibilityEngine({self.n_sec} sectors, {self.n_gen} gens, "
                f"dims={self.sector_dims})")


# Also expose at module level
__all__ = [
    'sector_block_norm', 'projector_block_norm', 'offdiag_count',
    'compute_direct_support', 'compute_length_two_support',
    'compute_word_depth_matrix', 'plateau_fraction',
    'compute_R1', 'compute_R2', 'compute_R2_per_generator',
    'compute_lie_filtration', 'compute_lie_depth_matrix',
    'single_term_bridge_audit',
    'compute_kappa_depth_matrix',
    'accessibility_signature',
    'AccessibilityEngine',
]
