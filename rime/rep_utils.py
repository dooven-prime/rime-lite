"""
Group representation utilities for the Accessibility Completeness framework.

Sections:
  1. Finite group enumeration -- symmetric_group, compose_perm, permutation_order, etc.
  2. Representations -- regular_rep, permutation_rep, block_diag_rep, skew_log_generators
  3. Sector tools -- class_sum_center_ops, symmetrized_generator_center_ops,
     sector_bases_from_projectors, block_matrix_in_sector_basis

All functions operate on raw numpy arrays. No CubieSpectralOperator dependency.
"""
import numpy as np
from scipy.linalg import logm
from itertools import permutations
from collections import defaultdict


# ============================================================
# 1. Finite group enumeration
# ============================================================

def symmetric_group(n):
    """Return all permutations of {0, ..., n-1} as list of tuples."""
    return list(permutations(range(n)))


def compose_perm(p, q):
    """Compose permutations: (p o q)[i] = p[q[i]]."""
    return tuple(p[q[i]] for i in range(len(p)))


def permutation_order(p):
    """Order of a permutation (LCM of cycle lengths)."""
    from math import gcd
    visited = [False] * len(p)
    order = 1
    for start in range(len(p)):
        if not visited[start]:
            cur, clen = start, 0
            while not visited[cur]:
                visited[cur] = True
                cur = p[cur]
                clen += 1
            if clen > 1:
                order = order * clen // gcd(order, clen)
    return order


def conjugacy_class_key(p):
    """Return sorted cycle lengths tuple (conjugacy class invariant for S_n)."""
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


def enumerate_group(group, multiply=None):
    """Enumerate all elements of a group given generators.

    DEPRECATED -- use symmetric_group(n) for S_n. Kept for non-symmetric groups.

    Args:
        group: list of generator elements.
        multiply: function(g, h) -> g*h. If None, uses compose_perm.

    Returns:
        (all_elements, index_map)
    """
    if multiply is None:
        multiply = compose_perm
    elements = list(group)
    idx_map = {e: i for i, e in enumerate(elements)}
    queue = list(elements)
    while queue:
        g = queue.pop(0)
        for gen in group:
            gh = multiply(g, gen)
            if gh not in idx_map:
                idx_map[gh] = len(elements)
                elements.append(gh)
                queue.append(gh)
    return elements, idx_map


# ============================================================
# 2. Representations
# ============================================================

def regular_rep(group, multiply=None):
    """Build regular representation of a finite group.

    rho(g) acts on C[G] basis {|h>: h in G} by left multiplication:
    rho(g) |h> = |g*h>.

    Args:
        group: list of group elements (any hashable type).
        multiply: function(g, h) -> g*h. If None, uses compose_perm.

    Returns:
        list of (|G|, |G|) permutation matrices, one per group element.
    """
    if multiply is None:
        multiply = compose_perm
    n = len(group)
    idx = {g: i for i, g in enumerate(group)}
    rhos = []
    for g in group:
        M = np.zeros((n, n), dtype=complex)
        for i, h in enumerate(group):
            gh = multiply(g, h)
            M[idx[gh], i] = 1.0
        rhos.append(M)
    return rhos


def permutation_rep(perms):
    """Build permutation representation matrices.

    Each permutation p acts on standard basis: e_i -> e_{p[i]}.

    Args:
        perms: list of permutation tuples (all same length n).

    Returns:
        list of (n, n) permutation matrices.
    """
    n = len(perms[0])
    result = []
    for p in perms:
        M = np.zeros((n, n), dtype=complex)
        for i, j in enumerate(p):
            M[j, i] = 1.0
        result.append(M)
    return result


def perm_matrix(perm, n=None):
    """Build n*n permutation matrix from a permutation tuple.

    Column j maps to row perm[j]: M[perm[j], j] = 1.
    """
    if n is None:
        n = len(perm)
    M = np.zeros((n, n))
    for j, i in enumerate(perm):
        M[i, j] = 1.0
    return M


def block_diag_rep(reps):
    """Build block-diagonal representation from a list of representation lists.

    Args:
        reps: list of lists, where reps[b] is a list of (d_b, d_b) matrices
              for block b. All blocks must have the same number of matrices.

    Returns:
        list of (sum(d_b), sum(d_b)) block-diagonal matrices.
    """
    n_blocks = len(reps)
    n_mats = len(reps[0])
    dims = [reps[b][0].shape[0] for b in range(n_blocks)]
    total_dim = sum(dims)

    result = []
    for m in range(n_mats):
        M = np.zeros((total_dim, total_dim), dtype=complex)
        offset = 0
        for b in range(n_blocks):
            d = dims[b]
            M[offset:offset + d, offset:offset + d] = reps[b][m]
            offset += d
        result.append(M)
    return result


def skew_log_generators(rhos):
    """Compute skew-Hermitian Lie algebra generators from unitary representations.

    X_g = (log rho(g) - log rho(g)^H) / 2

    Args:
        rhos: list of unitary representation matrices.

    Returns:
        list of skew-Hermitian matrices.
    """
    Xs = []
    for rg in rhos:
        X = logm(rg)
        X = (X - X.conj().T) / 2
        Xs.append(X)
    return Xs


def compute_A_operator(rhos):
    """Compute the average representation operator A = (1/|S|) * sum_g rho(g).

    Paper I central object: the spectral decomposition of A determines
    the eigenspace layers and sector structure.

    Args:
        rhos: list of unitary representation matrices rho(g).

    Returns:
        (n,n) Hermitian matrix.
    """
    A = sum(rhos) / len(rhos)
    return (A + A.conj().T) / 2


# ============================================================
# 3. Sector tools
# ============================================================

def class_sum_center_ops(group, rep_fn, hermitian=True, class_key=None):
    """Build center operators from conjugacy class sums.

    For each conjugacy class, sum rho(g) over class members.
    Identity class is skipped.

    Args:
        group: list of group elements.
        rep_fn: function element -> (n,n) matrix.
        hermitian: if True, symmetrize (C + C^H)/2.
        class_key: function element -> hashable class key.
                   Default: conjugacy_class_key (cycle-type, S_n specific).
                   Override for non-symmetric groups (e.g., lambda p: ...).

    Returns:
        list of (n,n) Hermitian center operators.
    """
    if class_key is None:
        class_key = conjugacy_class_key  # S_n cycle-type

    # Group by conjugacy class key
    classes = defaultdict(list)
    for g in group:
        key = class_key(g)
        classes[key].append(g)

    ops = []
    for key, elements in classes.items():
        if key == () or len(elements) <= 1:
            continue
        C = sum(rep_fn(g) for g in elements)
        if hermitian:
            C = (C + C.conj().T) / 2
        ops.append(C)
    return ops


def symmetrized_generator_center_ops(rho_gens):
    """Build center operators from symmetrized skew-log generators.

    For each generator rho_g: iX = (i * skew_log(rho_g) + h.c.) / 2

    Args:
        rho_gens: list of unitary generator matrices.

    Returns:
        list of Hermitian matrices.
    """
    ops = []
    for rg in rho_gens:
        X = logm(rg)
        X = (X - X.conj().T) / 2
        ops.append((1j * X + (1j * X).conj().T) / 2)
    return ops


def build_center_operators(group, gen_perms, rep_fn, class_key=None):
    """Convenience: build the standard set of center operators.

    Combines class_sum_center_ops + symmetrized_generator_center_ops,
    which is the standard recipe for sector decomposition in the
    Accessibility Completeness framework.

    Args:
        group: list of group elements (permutation tuples).
        gen_perms: list of generator permutations.
        rep_fn: function element -> (n,n) unitary matrix.
        class_key: passed through to class_sum_center_ops.
                   Default: conjugacy_class_key (cycle-type, S_n specific).

    Returns:
        list of Hermitian center operators.
    """
    ops = class_sum_center_ops(group, rep_fn, class_key=class_key)
    gen_rhos = [rep_fn(p) for p in gen_perms]
    ops.extend(symmetrized_generator_center_ops(gen_rhos))
    return ops


def sector_bases_from_projectors(projectors, tol=1e-8):
    """Extract orthonormal sector bases from projector matrices.

    Each projector P_i = V_i @ V_i^H where V_i columns form an orthonormal
    basis for sector i. Selects eigenvectors with eigenvalue > 1 - tol
    (projectors have eigenvalues 0 or 1, so this cleanly separates the
    1-eigenspace).

    Args:
        projectors: list of (n,n) Hermitian projector matrices.
        tol: eigenvalue selection threshold: evals > 1 - tol.

    Returns:
        list of (n, d_i) matrices V_i with orthonormal columns.
    """
    Vs = []
    for P in projectors:
        evals, evecs = np.linalg.eigh(P)
        Vs.append(evecs[:, evals > 1.0 - tol])
    return Vs


def basis_from_indices(dim, indices, dtype=complex):
    """Build an orthonormal coordinate-sector basis from selected indices.

    Args:
        dim: ambient dimension.
        indices: iterable of coordinate indices.
        dtype: dtype of the returned basis.

    Returns:
        (dim, len(indices)) matrix with coordinate basis columns.
    """
    eye = np.eye(dim, dtype=dtype)
    return eye[:, list(indices)]


def computational_basis_sectors(dim, dtype=complex):
    """Return one-dimensional computational-basis sector bases."""
    return [basis_from_indices(dim, [i], dtype=dtype) for i in range(dim)]


def orthonormal_columns(mat, tol=1e-8):
    """Return an orthonormal basis for the column span of mat."""
    q, r = np.linalg.qr(mat)
    if r.size == 0:
        return q[:, :0]
    diag = np.abs(np.diag(r))
    keep = diag > tol
    return q[:, keep]


def block_matrix_in_sector_basis(X, Vs, i, j):
    """Extract Q_i X Q_j as a dense (d_i, d_j) matrix.

    Args:
        X: (n,n) matrix in the original basis.
        Vs: list of sector bases, Vs[k] = (n, d_k).
        i, j: sector indices.

    Returns:
        (d_i, d_j) complex matrix.
    """
    return Vs[i].conj().T @ X @ Vs[j]


def sector_dimensions(Vs):
    """Return list of sector dimensions from sector bases."""
    return [V.shape[1] for V in Vs]


# ============================================================
# 4. Convenience: build a full permutation-group sectorized system
# ============================================================

def build_system_from_perms(elements, gen_perms):
    """Build a sectorized system from permutation group data.

    The canonical pipeline for constructing R1/R2/D input from a finite
    permutation group:
      1. Build regular representation
      2. Compute class-sum + symmetrized-generator center operators
      3. Joint diagonalization -> sector projectors -> sector bases
      4. Skew-log generators

    Args:
        elements: list of all group elements (permutation tuples).
        gen_perms: list of generator permutations (subset of elements).

    Returns:
        dict with keys: Vs, Xs, elements, gen_perms, rho_fn, projs,
                        center_ops, sectors_raw, dims, n_sec
    """
    from rime.spectral_utils import joint_diag_sectors, build_projectors

    n_total = len(elements)
    idx = {p: i for i, p in enumerate(elements)}

    def rho_fn(p):
        m = np.zeros((n_total, n_total), dtype=complex)
        for i, pe in enumerate(elements):
            r = tuple(p[pe[k]] for k in range(len(p)))
            m[idx[r], i] = 1.0
        return m

    center_ops = build_center_operators(elements, gen_perms, rho_fn)
    sectors_raw = joint_diag_sectors(center_ops, tol=1e-8)
    projs = build_projectors(sectors_raw, n_total)
    Vs = sector_bases_from_projectors(projs)

    rho_gens = [rho_fn(p) for p in gen_perms]
    Xs = skew_log_generators(rho_gens)

    return {
        'Vs': Vs,
        'Xs': Xs,
        'elements': elements,
        'gen_perms': gen_perms,
        'rho_fn': rho_fn,
        'projs': projs,
        'center_ops': center_ops,
        'sectors_raw': sectors_raw,
        'dims': sector_dimensions(Vs),
        'n_sec': len(Vs),
    }
