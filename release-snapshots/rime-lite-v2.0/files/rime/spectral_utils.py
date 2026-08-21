"""
Shared spectral utilities for experiment scripts.

Extracted from _exp_abelian_t7.py, _exp_minimal_t7.py, and others.
All functions work with raw numpy arrays — no CubieSpectralOperator dependency.

Sections:
  1. Joint diagonalization & sector classification
  2. Transport & Lie curvature (K, kappa_0, kappa_1)
  3. Support-graph and projected-composition diagnostics
  4. Group element enumeration (inverse-closed subsets, etc.)
  5. Small group representations (S_3, abelian characters, etc.)
"""
import numpy as np
from scipy.linalg import logm
from itertools import combinations


def _positive_finite_float(value, name):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a finite positive scalar") from None
    if not np.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be a finite positive scalar")
    return result


# ============================================================
# 1. Joint diagonalization & sector classification
# ============================================================

def _validate_hermitian_operators(ops, validation_tol):
    """Materialize and validate one finite Hermitian operator family."""
    ops = [np.asarray(op) for op in ops]
    if not ops:
        raise ValueError("at least one spectral operator is required")
    n = ops[0].shape[0]
    if any(op.ndim != 2 or op.shape != (n, n) for op in ops):
        raise ValueError("spectral operators must be square matrices of one size")
    for index, op in enumerate(ops):
        if not np.all(np.isfinite(op)):
            raise ValueError(f"ops[{index}] contains non-finite values")
        residual = np.linalg.norm(op - op.conj().T, "fro")
        if residual > validation_tol:
            raise ValueError(
                f"ops[{index}] is not Hermitian at validation_tol="
                f"{validation_tol}: residual={residual:.3e}"
            )
    return ops


def ordered_compression_sectors(ops, tol=1e-10, validation_tol=1e-8):
    """Build an order-dependent orthogonal sectorization from Hermitian ops.

    Each operator is compressed to every sector produced by the preceding
    operators, then the compression is diagonalized and clustered. When the
    operators do not commute, the resulting sectors are not joint
    eigenspaces and generally depend on operator order. This function records
    a numerical carrier decomposition only.
    """
    tol = _positive_finite_float(tol, "tol")
    validation_tol = _positive_finite_float(
        validation_tol, "validation_tol"
    )
    ops = _validate_hermitian_operators(ops, validation_tol)
    n = ops[0].shape[0]
    if any(op.ndim != 2 or op.shape != (n, n) for op in ops):
        raise ValueError("compression operators must be square matrices of one size")

    sectors = [(tuple([None] * len(ops)), np.eye(n))]
    for op_idx, op in enumerate(ops):
        new_sectors = []
        for evals_tuple, basis in sectors:
            dim = basis.shape[1]
            if dim <= 1:
                new_sectors.append((evals_tuple, basis))
                continue
            compressed = basis.conj().T @ op @ basis
            eigenvalues, eigenvectors = np.linalg.eigh(compressed)
            used = set()
            for i in range(dim):
                if i in used:
                    continue
                group = [
                    j for j in range(dim)
                    if abs(eigenvalues[j] - eigenvalues[i]) < tol
                ]
                used.update(group)
                registered_values = list(evals_tuple)
                registered_values[op_idx] = round(eigenvalues[i].real, 10)
                sector_basis = basis @ eigenvectors[:, group]
                new_sectors.append((tuple(registered_values), sector_basis))
        sectors = new_sectors

    sectors.sort(key=lambda item: tuple(
        -abs(value) if value is not None else 0 for value in item[0]
    ))
    return sectors


def joint_diag_sectors(ops, tol=1e-10, validation_tol=1e-8, validate=True):
    """Find simultaneous eigenspaces of commuting Hermitian operators.

    Uses iterative subspace restriction with proper eigenvector tracking:
    for each operator, diagonalize within each previously-found sector,
    split by eigenvalue, and transform eigenvectors back to the original basis.

    Args:
        ops: list of (n,n) Hermitian matrices that mutually commute.
        tol: eigenvalue grouping tolerance.
        validation_tol: absolute Hermiticity and commutator tolerance.
        validate: retained for compatibility. ``False`` is deprecated and no
            longer bypasses the commuting-Hermitian gate.

    Returns:
        List of (eigenvalue_tuple, V) where eigenvalue_tuple is a tuple
        of eigenvalues (one per op, None if unresolved) and V is an (n, d)
        matrix whose columns form an orthonormal basis for the joint eigenspace.
        Sorted by first op's eigenvalue descending, then second, etc.
    """
    tol = _positive_finite_float(tol, "tol")
    validation_tol = _positive_finite_float(
        validation_tol, "validation_tol"
    )
    if not validate:
        import warnings
        warnings.warn(
            "validate=False no longer bypasses the commuting-Hermitian gate; "
            "use ordered_compression_sectors() for noncommuting inputs",
            DeprecationWarning,
            stacklevel=2,
        )
    ops = _validate_hermitian_operators(ops, validation_tol)
    for i, left in enumerate(ops):
        for j in range(i + 1, len(ops)):
            residual = np.linalg.norm(
                left @ ops[j] - ops[j] @ left, "fro"
            )
            if residual > validation_tol:
                raise ValueError(
                    f"ops[{i}] and ops[{j}] do not commute at "
                    f"validation_tol={validation_tol}: "
                    f"residual={residual:.3e}"
                )
    return ordered_compression_sectors(
        ops, tol=tol, validation_tol=validation_tol
    )


def build_projectors(sectors, dim_total):
    """Build projector matrices from sector (evals_tuple, V) list.

    Args:
        sectors: output of joint_diag_sectors().
        dim_total: total dimension of the Hilbert space.

    Returns:
        List of (n,n) projector matrices, one per sector.
    """
    if not sectors:
        raise ValueError("at least one sector is required")
    projectors = []
    for _, V in sectors:
        if V.ndim != 2 or V.shape[0] != dim_total:
            raise ValueError("sector bases do not match dim_total")
        P = V @ V.conj().T
        projectors.append(P)
    return projectors


def classify_sectors(sectors, dim_a, dim_b=None, dim_total=None, tol=1e-10):
    """Classify each sector as pure-A ('A'), pure-B ('B'), or hybrid ('H').

    A sector is pure-A if its projector has (near)zero weight in block B;
    pure-B if (near)zero weight in block A; hybrid otherwise.

    Args:
        sectors: output of joint_diag_sectors() — list of (evals_tuple, V).
        dim_a: dimension of block A.
        dim_b: dimension of block B. If None, inferred from dim_total - dim_a.
        dim_total: total dimension. If None, inferred from V.shape[0].
        tol: threshold for considering a block weight as zero.

    Returns:
        List of str: 'A', 'B', or 'H' for each sector.
    """
    if dim_total is None:
        dim_total = sectors[0][1].shape[0]
    if dim_b is None:
        dim_b = dim_total - dim_a

    types = []
    for _, V in sectors:
        d = V.shape[1]
        # Frobenius norm squared of V projected onto block A
        w_a = np.linalg.norm(V[:dim_a, :], 'fro')**2
        # Total norm squared = d (columns are orthonormal)
        if w_a < tol * d:
            types.append('B')
        elif abs(w_a - d) < tol * d:
            types.append('A')
        else:
            types.append('H')
    return types


# ============================================================
# 2. Transport & Lie curvature
# ============================================================

def compute_transport_kappa(rhos, projectors, compute_kappa1=True):
    """Deprecated principal-log convenience for legacy kappa diagnostics.

    Standalone computation — no CubieSpectralOperator dependency.
    Used by Papers I/II/III for transport topology and Lie curvature.

    K[a,b]     = max_g ‖P_a ρ(g) P_b‖_F        (transport tensor, Paper II eq.1)
    kappa0[a,b] = max_g ‖P_a A_g P_b‖_F         (Lie depth 0, Paper III eq.2)
    kappa1[a,b] = max_{g,h} ‖P_a [A_g,A_h] P_b‖_F  (Lie depth 1, Paper III eq.3)

    where A_g = (log ρ(g) − log ρ(g)^H) / 2 are the skew-Hermitian generators.

    Args:
        rhos: list of (n,n) unitary representation matrices ρ(g).
        projectors: list of (n,n) projector matrices P_α.
        compute_kappa1: if True, also compute κ₁.

    Returns:
        (K, kappa0, kappa1) — three (n_sec, n_sec) arrays.
        kappa1 is None if compute_kappa1=False.
    """
    import warnings
    warnings.warn(
        "compute_transport_kappa() fixes SciPy's principal matrix-log branch; "
        "declare the Lie family explicitly and use "
        "compute_transport_kappa_from_Xs()",
        DeprecationWarning,
        stacklevel=2,
    )
    n_sec = len(projectors)
    K = np.zeros((n_sec, n_sec))
    kappa0 = np.zeros((n_sec, n_sec))

    # Compute skew-Hermitian Lie generators from unitary representations
    A_gs = []
    for rho_g in rhos:
        X = logm(rho_g)
        X = (X - X.conj().T) / 2
        A_gs.append(X)

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
        kappa1 = np.zeros((n_sec, n_sec))
        for a in range(n_sec):
            Pa = projectors[a]
            for b in range(n_sec):
                Pb = projectors[b]
                max_k1 = 0.0
                for g in range(len(A_gs)):
                    for h in range(len(A_gs)):
                        if g == h:
                            continue
                        comm = A_gs[g] @ A_gs[h] - A_gs[h] @ A_gs[g]
                        max_k1 = max(max_k1, np.linalg.norm(Pa @ comm @ Pb, 'fro'))
                kappa1[a, b] = max_k1
    else:
        kappa1 = None

    return K, kappa0, kappa1


def compute_transport_kappa_from_Xs(rhos, Xs, projectors, compute_kappa1=True):
    """Compute K, kappa_0, kappa_1 using pre-computed Lie generators Xs.

    Like compute_transport_kappa() but accepts Xs directly — avoids
    recomputing logm when Xs are already available (e.g., from
    rep_utils.skew_log_generators).

    Args:
        rhos: list of unitary ρ(g) matrices (for K only).
        Xs: list of skew-Hermitian Lie generators A_g.
        projectors: list of projector matrices.
        compute_kappa1: if True, also compute κ₁.

    Returns:
        (K, kappa0, kappa1)
    """
    n_sec = len(projectors)
    K = np.zeros((n_sec, n_sec))
    kappa0 = np.zeros((n_sec, n_sec))

    for a in range(n_sec):
        Pa = projectors[a]
        for b in range(n_sec):
            Pb = projectors[b]
            max_K = 0.0
            max_k0 = 0.0
            for i, rho_g in enumerate(rhos):
                max_K = max(max_K, np.linalg.norm(Pa @ rho_g @ Pb, 'fro'))
                max_k0 = max(max_k0, np.linalg.norm(Pa @ Xs[i] @ Pb, 'fro'))
            K[a, b] = max_K
            kappa0[a, b] = max_k0

    if compute_kappa1:
        kappa1 = np.zeros((n_sec, n_sec))
        for a in range(n_sec):
            Pa = projectors[a]
            for b in range(n_sec):
                Pb = projectors[b]
                max_k1 = 0.0
                for g in range(len(Xs)):
                    for h in range(len(Xs)):
                        if g == h:
                            continue
                        comm = Xs[g] @ Xs[h] - Xs[h] @ Xs[g]
                        max_k1 = max(max_k1, np.linalg.norm(Pa @ comm @ Pb, 'fro'))
                kappa1[a, b] = max_k1
    else:
        kappa1 = None

    return K, kappa0, kappa1


# ============================================================
# 3. Support-graph and projected-composition diagnostics
# ============================================================

def sector_bases_from_projectors(
        projectors, eigenvalue_cutoff=0.5, tol=1e-8, validate=True):
    """Return bases for a declared numerical orthogonal projector family.

    Validation checks Hermiticity, idempotence, and pairwise orthogonality. The
    family need not be complete; retained-subspace callers may intentionally
    omit the complement.
    """
    projectors = [np.asarray(projector) for projector in projectors]
    if not projectors:
        raise ValueError("at least one projector is required")
    ambient_dim = projectors[0].shape[0]
    if any(
            projector.ndim != 2
            or projector.shape != (ambient_dim, ambient_dim)
            for projector in projectors):
        raise ValueError("projectors must be square matrices of one ambient size")
    if validate:
        for index, projector in enumerate(projectors):
            if np.linalg.norm(projector - projector.conj().T, "fro") > tol:
                raise ValueError(f"projectors[{index}] is not Hermitian")
            if np.linalg.norm(projector @ projector - projector, "fro") > tol:
                raise ValueError(f"projectors[{index}] is not idempotent")
        for i, left in enumerate(projectors):
            for j in range(i + 1, len(projectors)):
                if np.linalg.norm(left @ projectors[j], "fro") > tol:
                    raise ValueError(
                        f"projectors[{i}] and projectors[{j}] are not orthogonal"
                    )
    bases = []
    for projector in projectors:
        hermitian = (projector + projector.conj().T) / 2
        eigenvalues, eigenvectors = np.linalg.eigh(hermitian)
        bases.append(eigenvectors[:, eigenvalues > eigenvalue_cutoff])
    return bases


def max_two_step_composition(rho_matrices, sector_bases, i, k, j):
    """Audit all projected two-step products through sector ``k``.

    Reduced sector-basis products have the same Frobenius norm and nonzero
    status as ``Q_i rho(g2) Q_k rho(g1) Q_j``.
    """
    rhos = [matrix.toarray() if hasattr(matrix, 'toarray') else np.asarray(matrix)
            for matrix in rho_matrices]
    Bi, Bk, Bj = sector_bases[i], sector_bases[k], sector_bases[j]
    left = [Bi.conj().T @ rho @ Bk for rho in rhos]
    right = [Bk.conj().T @ rho @ Bj for rho in rhos]

    left_norms = [np.linalg.norm(block, 'fro') for block in left]
    right_norms = [np.linalg.norm(block, 'fro') for block in right]
    best_norm = -1.0
    best_pair = None
    for g2, left_block in enumerate(left):
        for g1, right_block in enumerate(right):
            norm = np.linalg.norm(left_block @ right_block, 'fro')
            if norm > best_norm:
                best_norm = float(norm)
                best_pair = (g2, g1)

    return {
        'left_max': float(max(left_norms, default=0.0)),
        'right_max': float(max(right_norms, default=0.0)),
        'composition_max': best_norm,
        'composition_argmax': best_pair,
    }


def find_graph_only_two_step_pairs(K, block_sets, tol_K=0.05):
    """Find disjoint-endpoint two-step paths in the direct support graph.

    The result makes no matrix-composition claim. Each item is the zero-based
    tuple ``(i, j, candidates)``.
    """
    n = len(block_sets)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not block_sets[i].isdisjoint(block_sets[j]):
                continue
            if K[i, j] >= tol_K:
                continue
            candidates = [k for k in range(n)
                          if k != i and k != j
                          and K[i, k] > tol_K and K[k, j] > tol_K]
            if candidates:
                pairs.append((i, j, candidates))
    return pairs

def block_set(P, block_ranges, threshold=0.01):
    """Return set of block names where projector P has significant support.

    Detects multi-block membership by Frobenius norm: a block is included
    if ‖P[s:e, s:e]‖²_F > threshold × Tr(P).

    This is the correct approach for T7 cross-block detection — sectors can
    span multiple blocks (hybrid sectors), and two sectors are cross-block
    only when their block sets are *disjoint*.

    Args:
        P: (n,n) projector matrix.
        block_ranges: dict {name: (start, end)} or list of (name, slice) tuples.
        threshold: fraction of Tr(P) for significant support (default 0.01).

    Returns:
        set of block name strings.
    """
    if isinstance(block_ranges, dict):
        items = block_ranges.items()
    else:
        items = block_ranges
    trace_p = np.trace(P).real
    blocks = set()
    for bn, (s, e) in items:
        fn2 = np.linalg.norm(P[s:e, s:e], 'fro') ** 2
        if fn2 > threshold * trace_p:
            blocks.add(bn)
    return blocks


def select_canonical_intermediate(candidates, K, tol_K=0.05):
    """Select the canonical intermediate sector from a list of candidates.

    Score: transport_degree(γ) = out-degree + in-degree in K.
    When multiple length-2 witnesses exist, the highest-transport-degree
    intermediate is taken as the canonical witness.  This is a principled
    tie-breaker (preferring hub sectors over leaf sectors), not a
    hardcoded per-pair rule.

    Args:
        candidates: list of intermediate sector indices (0-based).
        K: (n,n) transport tensor.
        tol_K: threshold for "non-zero" transport edge.

    Returns:
        The candidate index with the highest transport degree.
    """
    n = K.shape[0]
    degree = np.array([sum(K[i, :] > tol_K) + sum(K[:, i] > tol_K)
                       for i in range(n)], dtype=float)
    return max(candidates, key=lambda k: degree[k])


def count_t7_pairs(K, kap0, kap1, block_sets, tol_K=0.05, tol_kappa=1e-6):
    """Legacy graph-only census formerly called T7 detection.

    This routine does not evaluate ``Q_i rho(g2) Q_k rho(g1) Q_j`` and cannot
    certify a compositional morphism. New code should combine
    ``find_graph_only_two_step_pairs`` with ``max_two_step_composition``.

    Detection pipeline (CCS §2.5):
      1. Cross-block: block_sets[i].isdisjoint(block_sets[j]) — structural,
         exact. This is the load-bearing step.
      2. K=0 and kappa_0=kappa_1=0 — numerical check on depths 0 and 1
         (logm noise ~1e-6).
      3. 2-step reachable: at least one intermediate sector γ exists with
         K[i,γ] > tol_K and K[γ,j] > tol_K.

    kappa_d=0 for all d >= 2 is NOT checked numerically. It follows from
    Lemma 1 (block-diagonal Lie closure): if block sets are disjoint, the
    Lie algebra generated by {A_g} is block-diagonal, so all nested
    commutators vanish structurally across blocks. The numerical pipeline
    establishes cross-blockness (step 1) and depth-0/1 vanishing (step 2);
    Lemma 1 then lifts depth-0/1 to all-depth vanishing.

    The returned pairs are graph-only candidates retained for compatibility.
    For canonical witness selection, use select_canonical_intermediate().

    Args:
        K: (n,n) transport tensor.
        kap0: (n,n) kappa_0 matrix.
        kap1: (n,n) kappa_1 matrix.
        block_sets: list of sets, block_set(P_i) for each sector projector.
        tol_K: threshold for "non-zero" transport (default 0.05).
        tol_kappa: threshold for "zero" kappa (default 1e-6, logm noise ~1e-6).

    Returns:
        (count, pairs) where count is int and pairs is list of (i+1, j+1) tuples.
    """
    import warnings
    warnings.warn(
        "count_t7_pairs() is deprecated; it returns graph-only legacy labels. "
        "Use find_graph_only_two_step_pairs() and evaluate routed products.",
        DeprecationWarning,
        stacklevel=2,
    )
    n = len(block_sets)
    count = 0
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not block_sets[i].isdisjoint(block_sets[j]):
                continue
            if K[i, j] < tol_K and kap0[i, j] < tol_kappa and kap1[i, j] < tol_kappa:
                candidates = [k for k in range(n)
                              if k != i and k != j
                              and K[i, k] > tol_K and K[k, j] > tol_K]
                if candidates:
                    count += 1
                    pairs.append((i + 1, j + 1))
    return count, pairs


def find_t7_pairs(K, kappa0, kappa1, sector_types, tol=1e-6):
    """DEPRECATED legacy graph-path detector.

    Old T7 detection using A/B/H sector classification (2-block model only).
    Does not handle the Rubik's cube 4-block structure correctly.
    """
    import warnings
    warnings.warn(
        'find_t7_pairs is deprecated. Use find_graph_only_two_step_pairs() '
        'and max_two_step_composition() instead.',
        DeprecationWarning, stacklevel=2)
    n = len(sector_types)
    pairs = []
    for a in range(n):
        if sector_types[a] not in ('A', 'B'):
            continue
        for b in range(a + 1, n):
            if sector_types[b] not in ('A', 'B'):
                continue
            if sector_types[a] == sector_types[b]:
                continue
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
    """DEPRECATED — one-shot T7 using old A/B/H classification.

    Use CubieSpectralOperator.center_decomposition() + count_t7_pairs() instead.
    """
    import warnings
    warnings.warn(
        'analyze_t7 is deprecated. Use CubieSpectralOperator + '
        'count_t7_pairs() with block_set() for multi-block support.',
        DeprecationWarning, stacklevel=2)
    n = rhos[0].shape[0]
    dim_a = block_slices[0][1].stop

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

# --- General block-diagonal construction ---

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

def build_s3_generators():
    """Build S₃ generators: 3 transpositions in nat⊕reg (9-dim).

    Derives both blocks from the group structure:
      nat → build_s3_natural_rep() on each transposition permutation
      reg → build_s3_regular_rep() on each transposition index

    The transpositions (12), (23), (13) are indices 1,2,3 in S3_PERMUTATIONS.
    """
    gen_indices = [1, 2, 3]  # (12), (23), (13)
    rhos_nat = [build_s3_natural_rep(S3_PERMUTATIONS[i]) for i in gen_indices]
    rhos_reg = [build_s3_regular_rep(i) for i in gen_indices]
    return build_block_diag_rho(rhos_nat, rhos_reg)

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
