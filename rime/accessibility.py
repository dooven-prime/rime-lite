"""Accessibility support, bridge, and depth diagnostics.

Input contract
--------------
``Vs`` is a sequence of sector bases, not projector matrices. Each ``Vs[i]``
has shape ``(ambient_dim, sector_dim)`` with orthonormal columns, and distinct
sector bases are mutually orthogonal. ``Xs`` is a non-empty sequence of square
observable matrices on the same ambient space.

A complete sectorization is not required by default because retained-subspace
and diagnostic realizations are useful. When the declared sectors are
incomplete, however, products and commutators may propagate through the
undeclared complement. Use ``require_complete=True`` or
``require_invariant_subspace=True`` when that distinction matters.

Skew-Hermitian observables are required for the strict compact-Lie
interpretation. General matrices are accepted for cross-species diagnostics,
but the resulting Lie-depth output is then only a matrix-commutator diagnostic.

Interpretation boundaries
-------------------------
* ``compute_R2`` uses commutators. ``compute_length_two_support`` uses words.
  They measure different transport mechanisms and are not interchangeable.
* Lie depth starts at 0: generators have depth 0, first commutators depth 1.
  Word depth starts at 1: one observable has word depth 1.
* ``999`` means not reached within the tested filtration cutoff. It is not a
  proof of global impossibility.
* ``tol`` is an absolute support threshold. Rescaling observables can therefore
  change binary support and must be declared in reproducible reports.
* Reports are relative to the declared sectorization and observable family.

``AccessibilityEngine`` validates and snapshots its inputs. The lower-level
functions assume the same contract; callers using them directly should invoke
``assert_accessibility_inputs`` first.
"""
from itertools import combinations
import warnings

import numpy as np

UNREACHED_DEPTH = 999
# Compatibility alias for versioned artifacts that still serialize "frozen".
FROZEN_DEPTH = UNREACHED_DEPTH


# ============================================================
# Internal helpers
# ============================================================

def _validation_error_message(report):
    details = "\n".join(f"  - {message}" for message in report["errors"])
    return f"Invalid accessibility inputs:\n{details}"


def _positive_finite_float(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) and result > 0 else None


def _materialize_sequence(value):
    if isinstance(value, np.ndarray):
        return value
    try:
        return list(value)
    except TypeError:
        return value


def check_accessibility_inputs(
        Vs,
        Xs,
        *,
        tol=1e-8,
        validation_tol=1e-7,
        require_complete=False,
        require_skew_hermitian=False,
        require_invariant_subspace=False):
    """Validate an accessibility realization without raising.

    The returned dictionary is JSON-friendly and separates hard ``errors``
    from interpretive ``warnings``. Completeness, skew-Hermiticity, and
    invariance of an incomplete retained subspace are optional strict checks.

    Returns:
        A report containing ``valid``, ``errors``, ``warnings``, dimensions,
        normalized basis/overlap errors, coverage information, observable
        norms, skew-Hermitian errors, and complement-leakage diagnostics.
    """
    errors = []
    warnings = []
    tol_value = _positive_finite_float(tol)
    validation_tol_value = _positive_finite_float(validation_tol)
    report = {
        "valid": False,
        "errors": errors,
        "warnings": warnings,
        "tol": tol_value,
        "validation_tol": validation_tol_value,
        "require_complete": bool(require_complete),
        "require_skew_hermitian": bool(require_skew_hermitian),
        "require_invariant_subspace": bool(require_invariant_subspace),
    }

    if tol_value is None:
        errors.append("tol must be a finite positive scalar")
    if validation_tol_value is None:
        errors.append("validation_tol must be a finite positive scalar")

    support_tol = tol_value if tol_value is not None else 0.0
    structure_tol = (
        validation_tol_value if validation_tol_value is not None else 1e-7
    )

    if isinstance(Vs, np.ndarray):
        errors.append("Vs must be a sequence of basis matrices, not one ndarray")
        sector_values = []
    else:
        try:
            sector_values = list(Vs)
        except TypeError:
            errors.append("Vs must be an iterable of basis matrices")
            sector_values = []

    if isinstance(Xs, np.ndarray):
        errors.append("Xs must be a sequence of observable matrices, not one ndarray")
        observable_values = []
    else:
        try:
            observable_values = list(Xs)
        except TypeError:
            errors.append("Xs must be an iterable of observable matrices")
            observable_values = []

    if not sector_values:
        errors.append("at least one sector basis is required")
    if not observable_values:
        errors.append("at least one observable matrix is required")

    valid_sectors = []
    ambient_dim = None
    sector_dims = []
    orthonormality_errors = []
    for index, value in enumerate(sector_values):
        try:
            basis = np.asarray(value)
        except (TypeError, ValueError):
            errors.append(f"Vs[{index}] cannot be converted to a numeric matrix")
            continue
        if basis.ndim != 2:
            errors.append(f"Vs[{index}] must be two-dimensional")
            continue
        if basis.shape[0] == 0 or basis.shape[1] == 0:
            errors.append(f"Vs[{index}] must have non-zero ambient and sector dimensions")
            continue
        if ambient_dim is None:
            ambient_dim = int(basis.shape[0])
        elif basis.shape[0] != ambient_dim:
            errors.append(
                f"Vs[{index}] has ambient dimension {basis.shape[0]}, "
                f"expected {ambient_dim}"
            )
            continue
        try:
            finite = bool(np.all(np.isfinite(basis)))
        except TypeError:
            finite = False
        if not finite:
            errors.append(f"Vs[{index}] contains non-finite or non-numeric values")
            continue

        sector_dim = int(basis.shape[1])
        gram = basis.conj().T @ basis
        gram_error = float(
            np.linalg.norm(gram - np.eye(sector_dim), "fro")
            / max(1.0, np.sqrt(sector_dim))
        )
        if gram_error > structure_tol:
            errors.append(
                f"Vs[{index}] columns are not orthonormal "
                f"(normalized error {gram_error:.3e})"
            )
        valid_sectors.append(basis)
        sector_dims.append(sector_dim)
        orthonormality_errors.append(gram_error)

    overlap_error_max = 0.0
    for i, left in enumerate(valid_sectors):
        for j in range(i + 1, len(valid_sectors)):
            right = valid_sectors[j]
            overlap_error = float(
                np.linalg.norm(left.conj().T @ right, "fro")
                / max(1.0, np.sqrt(left.shape[1] * right.shape[1]))
            )
            overlap_error_max = max(overlap_error_max, overlap_error)
            if overlap_error > structure_tol:
                errors.append(
                    f"Vs[{i}] and Vs[{j}] are not mutually orthogonal "
                    f"(normalized overlap {overlap_error:.3e})"
                )

    coverage_rank = 0
    coverage_error = None
    coverage_fraction = None
    sector_projector = None
    if ambient_dim is not None and valid_sectors:
        combined = np.hstack(valid_sectors)
        coverage_rank = int(np.linalg.matrix_rank(combined, tol=structure_tol))
        sector_projector = sum(
            (basis @ basis.conj().T for basis in valid_sectors),
            np.zeros((ambient_dim, ambient_dim), dtype=complex),
        )
        coverage_error = float(
            np.linalg.norm(sector_projector - np.eye(ambient_dim), "fro")
            / max(1.0, np.sqrt(ambient_dim))
        )
        coverage_fraction = float(coverage_rank / ambient_dim)
        complete = coverage_rank == ambient_dim and coverage_error <= structure_tol
        if not complete:
            message = (
                f"declared sectors span rank {coverage_rank}/{ambient_dim}; "
                "results are relative to an incomplete retained subspace"
            )
            if require_complete:
                errors.append(message)
            else:
                warnings.append(message)

    valid_observables = []
    observable_norms = []
    skew_errors = []
    zero_observables = []
    for index, value in enumerate(observable_values):
        try:
            observable = np.asarray(value)
        except (TypeError, ValueError):
            errors.append(f"Xs[{index}] cannot be converted to a numeric matrix")
            continue
        if observable.ndim != 2:
            errors.append(f"Xs[{index}] must be two-dimensional")
            continue
        if observable.shape[0] != observable.shape[1]:
            errors.append(f"Xs[{index}] must be square, got {observable.shape}")
            continue
        if ambient_dim is not None and observable.shape != (ambient_dim, ambient_dim):
            errors.append(
                f"Xs[{index}] has shape {observable.shape}, "
                f"expected ({ambient_dim}, {ambient_dim})"
            )
            continue
        try:
            finite = bool(np.all(np.isfinite(observable)))
        except TypeError:
            finite = False
        if not finite:
            errors.append(f"Xs[{index}] contains non-finite or non-numeric values")
            continue

        norm = float(np.linalg.norm(observable, "fro"))
        skew_error = float(
            np.linalg.norm(observable + observable.conj().T, "fro")
            / max(1.0, norm)
        )
        if norm <= support_tol:
            zero_observables.append(index)
        if skew_error > structure_tol and require_skew_hermitian:
            errors.append(
                f"Xs[{index}] is not skew-Hermitian "
                f"(normalized error {skew_error:.3e})"
            )
        valid_observables.append(observable)
        observable_norms.append(norm)
        skew_errors.append(skew_error)

    non_skew = [
        index for index, error in enumerate(skew_errors)
        if error > structure_tol
    ]
    if non_skew and not require_skew_hermitian:
        warnings.append(
            "observables are not all skew-Hermitian; Lie-depth values are "
            "general matrix-commutator diagnostics, not a strict compact-Lie audit"
        )
    if zero_observables:
        warnings.append(
            f"observable indices {zero_observables} have Frobenius norm <= tol"
        )

    leakage_error_max = 0.0
    if (ambient_dim is not None and sector_projector is not None
            and valid_observables and coverage_rank < ambient_dim):
        complement = np.eye(ambient_dim) - sector_projector
        for observable in valid_observables:
            norm = max(1.0, float(np.linalg.norm(observable, "fro")))
            leakage = max(
                np.linalg.norm(complement @ observable @ sector_projector, "fro"),
                np.linalg.norm(sector_projector @ observable @ complement, "fro"),
            ) / norm
            leakage_error_max = max(leakage_error_max, float(leakage))
        if leakage_error_max > structure_tol:
            message = (
                "the declared retained subspace is not observable-invariant "
                f"(normalized leakage {leakage_error_max:.3e}); products and "
                "commutators may traverse the undeclared complement"
            )
            if require_invariant_subspace:
                errors.append(message)
            else:
                warnings.append(message)

    report.update({
        "ambient_dim": ambient_dim,
        "n_sec": len(sector_values),
        "n_gen": len(observable_values),
        "sector_dims": sector_dims,
        "orthonormality_error_max": (
            max(orthonormality_errors) if orthonormality_errors else None
        ),
        "sector_overlap_error_max": overlap_error_max,
        "coverage_rank": coverage_rank,
        "coverage_fraction": coverage_fraction,
        "coverage_error": coverage_error,
        "observable_norms": observable_norms,
        "skew_hermitian_error_max": max(skew_errors) if skew_errors else None,
        "zero_observable_indices": zero_observables,
        "retained_subspace_leakage_max": leakage_error_max,
    })
    report["valid"] = not errors
    return report


def assert_accessibility_inputs(Vs, Xs, **kwargs):
    """Validate accessibility inputs and raise ``ValueError`` on failure."""
    report = check_accessibility_inputs(Vs, Xs, **kwargs)
    if not report["valid"]:
        raise ValueError(_validation_error_message(report))
    return report


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


def _routed_products_from_source(Vs, Xs, source, depth):
    """Enumerate reduced products for every labelled route from one source."""
    source_dim = Vs[source].shape[1]
    routes = [(source, np.eye(source_dim, dtype=complex))]
    for _ in range(depth):
        next_routes = []
        for intermediate, product in routes:
            for target, target_basis in enumerate(Vs):
                for observable in Xs:
                    block = (
                        target_basis.conj().T
                        @ observable
                        @ Vs[intermediate]
                    )
                    routed = block @ product
                    if np.count_nonzero(routed):
                        next_routes.append((target, routed))
        routes = next_routes
    return routes


def compute_routed_support(Vs, Xs, depth=2, tol=1e-8):
    """Compute aggregate support of fixed-route projected products ``C_d``.

    A pair ``(i, j)`` is supported when at least one observable-label tuple and
    one intermediate-sector tuple gives a routed product with Frobenius norm
    above ``tol``. This is not full-word support: different routes are not
    summed. Diagonal entries are omitted from the accessibility relation.
    """
    if not isinstance(depth, (int, np.integer)) or depth < 1:
        raise ValueError("depth must be an integer >= 1")

    n_sec = len(Vs)
    support = np.zeros((n_sec, n_sec), dtype=bool)
    for source in range(n_sec):
        for target, product in _routed_products_from_source(
                Vs, Xs, source, int(depth)):
            if target != source and np.linalg.norm(product, "fro") > tol:
                support[target, source] = True
    return support


def compute_routed_depth_matrix(
        Vs, Xs, max_depth=4, tol=1e-8, unreached=UNREACHED_DEPTH):
    """Compute cutoff-relative routed-composition depth ``D_route``.

    Depth one is direct support. An entry equal to ``unreached`` means only
    that no routed product was found through ``max_depth``.
    """
    if not isinstance(max_depth, (int, np.integer)) or max_depth < 1:
        raise ValueError("max_depth must be an integer >= 1")

    n_sec = len(Vs)
    depth_matrix = np.full((n_sec, n_sec), unreached, dtype=int)
    np.fill_diagonal(depth_matrix, 0)
    for depth in range(1, int(max_depth) + 1):
        support = compute_routed_support(Vs, Xs, depth=depth, tol=tol)
        newly_reached = support & (depth_matrix == unreached)
        depth_matrix[newly_reached] = depth
    return depth_matrix


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


def compute_word_depth_matrix(
        Vs,
        Xs,
        max_depth=4,
        tol=1e-8,
        unreached=UNREACHED_DEPTH,
        *,
        frozen=None):
    """Compute first accessibility depth using words in the observables.

    Depth 1 uses generators, depth 2 uses products of two generators, etc.
    This is useful for transport/PDE/control diagnostics. It is distinct from
    compute_lie_depth_matrix, which uses the Lie filtration.
    """
    if not isinstance(max_depth, (int, np.integer)) or max_depth < 1:
        raise ValueError("max_depth must be an integer >= 1")
    if frozen is not None:
        warnings.warn(
            "the frozen keyword is deprecated; use unreached",
            DeprecationWarning,
            stacklevel=2,
        )
        unreached = frozen

    n_sec = len(Vs)
    dim = Xs[0].shape[0]
    D = np.full((n_sec, n_sec), unreached, dtype=int)
    np.fill_diagonal(D, 0)

    words = [np.eye(dim, dtype=Xs[0].dtype)]
    for depth in range(1, max_depth + 1):
        words = [X @ W for X in Xs for W in words]
        for i in range(n_sec):
            for j in range(n_sec):
                if i == j or D[i, j] != unreached:
                    continue
                if any(sector_block_norm(Vs, W, i, j) > tol for W in words):
                    D[i, j] = depth
    return D


def plateau_fraction(D, depth, unreached=UNREACHED_DEPTH, *, frozen=None):
    """Fraction of off-diagonal sector pairs reachable by a given depth."""
    if frozen is not None:
        warnings.warn(
            "the frozen keyword is deprecated; use unreached",
            DeprecationWarning,
            stacklevel=2,
        )
        unreached = frozen
    n_sec = D.shape[0]
    total = n_sec * (n_sec - 1)
    if total == 0:
        return 0.0
    reached = sum(
        1 for i in range(n_sec) for j in range(n_sec)
        if i != j and D[i, j] != unreached and D[i, j] <= depth
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
        max_depth: number of Lie levels to compute. Returned depth indices are
            ``0 .. max_depth-1``.
        tol: Gram-Schmidt norm threshold.

    Returns:
        list of lists: per_depth[d] = list of vectorized basis matrices.
    """
    if not isinstance(max_depth, (int, np.integer)) or max_depth < 1:
        raise ValueError("max_depth must be an integer >= 1")

    n_total = Xs[0].shape[0]
    per_depth = []

    # Depth 0: generators
    basis_vecs = [X.flatten() for X in Xs]
    basis_vecs = _gram_schmidt(basis_vecs, tol)
    per_depth.append(basis_vecs[:])

    if max_depth == 1:
        return per_depth

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


def audit_lie_closure(Xs, basis, tol=1e-8):
    """Audit whether a numerical span is closed under generator brackets.

    ``basis`` may contain flattened vectors or square matrices. Closure under
    ``[X_g, L_a]`` for every declared generator and span basis element, together
    with containment of the generators, certifies saturation of the generated
    Lie span at the declared numerical tolerance. The result remains a
    computational certificate, not an exact Lie-algebra theorem.
    """
    if not Xs:
        raise ValueError("at least one generator is required")
    if not basis:
        raise ValueError("at least one basis element is required")
    tol_value = _positive_finite_float(tol)
    if tol_value is None:
        raise ValueError("tol must be a finite positive scalar")
    tol = tol_value

    ambient_dim = np.asarray(Xs[0]).shape[0]
    vectors = []
    for index, value in enumerate(basis):
        array = np.asarray(value)
        if array.shape == (ambient_dim, ambient_dim):
            vectors.append(array.reshape(-1))
        elif array.ndim == 1 and array.size == ambient_dim * ambient_dim:
            vectors.append(array)
        else:
            raise ValueError(
                f"basis[{index}] must be a square matrix or flattened matrix"
            )

    columns = np.column_stack(vectors)
    u_basis, singular_basis, _ = np.linalg.svd(columns, full_matrices=False)
    basis_rank = int(np.sum(singular_basis > tol))
    if basis_rank == 0:
        raise ValueError("basis is numerically zero at the declared tolerance")
    span_basis = u_basis[:, :basis_rank]

    def residual(vector):
        return vector - span_basis @ (span_basis.conj().T @ vector)

    generator_residuals = [
        float(np.linalg.norm(residual(np.asarray(X).reshape(-1))))
        for X in Xs
    ]
    commutator_columns = []
    closure_residuals = []
    for vector in vectors:
        element = vector.reshape(ambient_dim, ambient_dim)
        for generator in Xs:
            commutator = generator @ element - element @ generator
            flat = commutator.reshape(-1)
            commutator_columns.append(flat)
            closure_residuals.append(float(np.linalg.norm(residual(flat))))

    augmented = np.column_stack([*vectors, *commutator_columns])
    augmented_singular = np.linalg.svd(augmented, compute_uv=False)
    retained = augmented_singular[augmented_singular > tol]
    discarded = augmented_singular[augmented_singular <= tol]
    augmented_rank = int(retained.size)
    max_generator_residual = max(generator_residuals, default=0.0)
    max_closure_residual = max(closure_residuals, default=0.0)
    gram_error = float(
        np.linalg.norm(
            columns.conj().T @ columns - np.eye(columns.shape[1]), "fro"
        )
    )

    return {
        "declared_basis_count": len(vectors),
        "dimension": basis_rank,
        "augmented_rank": augmented_rank,
        "rank_threshold": float(tol),
        "minimum_retained_singular_value": (
            float(np.min(retained)) if retained.size else 0.0
        ),
        "maximum_discarded_singular_value": (
            float(np.max(discarded)) if discarded.size else 0.0
        ),
        "basis_gram_error": gram_error,
        "maximum_generator_span_residual": max_generator_residual,
        "maximum_generator_closure_residual": max_closure_residual,
        "contains_generators": max_generator_residual <= tol,
        "closed_under_generators": max_closure_residual <= tol,
        "saturated": (
            augmented_rank == basis_rank
            and max_generator_residual <= tol
            and max_closure_residual <= tol
        ),
        "claim_status": "computational_certificate",
    }


def compute_lie_depth_matrix(Vs, Xs, max_depth=4, tol=1e-8):
    """Compute accessibility depth matrix D via Lie filtration.

    D[i, j] = first depth d where some Lie basis element connects sector i to j.
    D[i, i] = 0 (diagonal).
    D[i, j] = 999 if unreached through the declared cutoff.

    Args:
        Vs: list of sector bases.
        Xs: list of generator matrices.
        max_depth: number of Lie levels to probe. Returned depth indices are
            ``0 .. max_depth-1``.
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
                D[i, j] = UNREACHED_DEPTH  # Not reached within tested depth.

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


def image_kernel_distance(A, B, rank_tol=1e-10):
    """Return normalized distance from ``im(B)`` to ``ker(A)``.

    The value is

    ``||(I - P_ker(A)) U_B||_F / sqrt(rank(B))``,

    where the columns of ``U_B`` are an orthonormal basis for ``im(B)``. It is
    zero for the zero map ``B``. This is a numerical subspace diagnostic, not
    an exact-incidence certificate unless the input arithmetic is exact.
    """
    A = np.asarray(A)
    B = np.asarray(B)
    if A.ndim != 2 or B.ndim != 2 or A.shape[1] != B.shape[0]:
        raise ValueError("A and B must be composable two-dimensional matrices")
    if not np.all(np.isfinite(A)) or not np.all(np.isfinite(B)):
        raise ValueError("A and B must contain only finite values")
    rank_tol_value = _positive_finite_float(rank_tol)
    if rank_tol_value is None:
        raise ValueError("rank_tol must be a finite positive scalar")
    rank_tol = rank_tol_value

    u_b, singular_b, _ = np.linalg.svd(B, full_matrices=False)
    rank_b = int(np.sum(singular_b > rank_tol))
    if rank_b == 0:
        return 0.0

    _, singular_a, vh_a = np.linalg.svd(A, full_matrices=False)
    rank_a = int(np.sum(singular_a > rank_tol))
    if rank_a == 0:
        return 0.0

    image_b = u_b[:, :rank_b]
    row_space_a = vh_a[:rank_a, :].conj().T
    residual = row_space_a.conj().T @ image_b
    return float(np.linalg.norm(residual, "fro") / np.sqrt(rank_b))


def audit_matrix_product(A, B, tol=1e-8, rank_tol=None):
    """Audit image--kernel incidence and rectangular rank protection.

    For ``A: C^n -> C^m`` and ``B: C^p -> C^n``, left protection means
    ``rank(A) = n`` and right protection means ``rank(B) = n``. Maximal rank
    relative to a rectangular factor's own dimensions is not sufficient.
    """
    A = np.asarray(A)
    B = np.asarray(B)
    if A.ndim != 2 or B.ndim != 2 or A.shape[1] != B.shape[0]:
        raise ValueError("A and B must be composable two-dimensional matrices")
    if not np.all(np.isfinite(A)) or not np.all(np.isfinite(B)):
        raise ValueError("A and B must contain only finite values")
    if rank_tol is None:
        rank_tol = tol
    tol_value = _positive_finite_float(tol)
    rank_tol_value = _positive_finite_float(rank_tol)
    if tol_value is None or rank_tol_value is None:
        raise ValueError("tol and rank_tol must be finite positive scalars")
    tol = tol_value
    rank_tol = rank_tol_value

    middle_dim = A.shape[1]
    singular_a = np.linalg.svd(A, compute_uv=False)
    singular_b = np.linalg.svd(B, compute_uv=False)
    rank_a = int(np.sum(singular_a > rank_tol))
    rank_b = int(np.sum(singular_b > rank_tol))
    norm_a = float(np.linalg.norm(A, "fro"))
    norm_b = float(np.linalg.norm(B, "fro"))
    product = A @ B
    product_norm = float(np.linalg.norm(product, "fro"))
    denominator = norm_a * norm_b
    left_protected = rank_a == middle_dim
    right_protected = rank_b == middle_dim

    if left_protected and right_protected:
        category = "both-protected"
    elif left_protected:
        category = "left-only"
    elif right_protected:
        category = "right-only"
    elif product_norm > tol:
        category = "unprotected-nonzero"
    else:
        category = "unprotected-zero"

    factors_nonzero = norm_a > tol and norm_b > tol
    protected = left_protected or right_protected
    return {
        "shape_A": tuple(int(value) for value in A.shape),
        "shape_B": tuple(int(value) for value in B.shape),
        "middle_dimension": int(middle_dim),
        "rank_A": rank_a,
        "rank_B": rank_b,
        "minimum_nonzero_singular_A": (
            float(singular_a[rank_a - 1]) if rank_a else 0.0
        ),
        "minimum_nonzero_singular_B": (
            float(singular_b[rank_b - 1]) if rank_b else 0.0
        ),
        "norm_A": norm_a,
        "norm_B": norm_b,
        "product_norm": product_norm,
        "relative_product_norm": product_norm / denominator if denominator else 0.0,
        "image_kernel_distance": image_kernel_distance(A, B, rank_tol),
        "left_protected": left_protected,
        "right_protected": right_protected,
        "protected": protected,
        "factors_nonzero": factors_nonzero,
        "product_nonzero": product_norm > tol,
        "protection_consistent": not (
            factors_nonzero and protected and product_norm <= tol
        ),
        "category": category,
    }


def rank_protection_audit(bridges, tol=1e-8):
    """Add incidence and rank-protection fields to routed-product records.

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

        audit = audit_matrix_product(A, B, tol=tol)
        dim_ok = d_k <= min(d_i, d_j)

        b['rank_A'] = audit['rank_A']
        b['rank_B'] = audit['rank_B']
        b['dim_ok'] = dim_ok
        b['full_col_rank'] = audit['left_protected']
        b['full_row_rank'] = audit['right_protected']
        b['left_protected'] = audit['left_protected']
        b['right_protected'] = audit['right_protected']
        b['both_protected'] = (
            audit['left_protected'] and audit['right_protected']
        )
        b['rank_protected'] = audit['protected']
        b['structural'] = audit['protected']  # compatibility field
        b['product_zero'] = not audit['product_nonzero']
        b['relative_product_norm'] = audit['relative_product_norm']
        b['image_kernel_distance'] = audit['image_kernel_distance']
        b['protection_consistent'] = audit['protection_consistent']
        b['incidence_category'] = audit['category']

    return bridges


def matrix_nondeg_audit(bridges, tol=1e-8):
    """Deprecated alias for :func:`rank_protection_audit`."""
    warnings.warn(
        "matrix_nondeg_audit() is deprecated; use rank_protection_audit()",
        DeprecationWarning,
        stacklevel=2,
    )
    return rank_protection_audit(bridges, tol=tol)


# ============================================================
# Convenience
# ============================================================

def compute_depth_census(D, unreached=UNREACHED_DEPTH):
    """Count off-diagonal pairs at every recorded depth and at the cutoff."""
    matrix = np.asarray(D)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("D must be a square depth matrix")
    try:
        finite = bool(np.all(np.isfinite(matrix)))
        unreached_code = int(unreached)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("D and unreached must use finite integer codes") from None
    if not finite or unreached_code != unreached:
        raise ValueError("D must contain only finite depth codes")
    if not np.all(matrix == np.floor(matrix)):
        raise ValueError("D must contain integer depth codes")
    if not np.all(np.diag(matrix) == 0):
        raise ValueError("D diagonal must be zero")
    offdiag = ~np.eye(matrix.shape[0], dtype=bool)
    invalid = (matrix < 0) & (matrix != unreached_code) & offdiag
    if np.any(invalid):
        raise ValueError("off-diagonal depths must be nonnegative or unreached")
    finite_depths = sorted(
        int(value)
        for value in np.unique(matrix[offdiag])
        if value != unreached_code
    )
    return {
        "by_depth": {
            depth: int(np.sum((matrix == depth) & offdiag))
            for depth in finite_depths
        },
        "unreached": int(np.sum((matrix == unreached_code) & offdiag)),
        "unreached_value": unreached_code,
    }


def compute_signature_from_D(D):
    """Deprecated fixed-width view of a cutoff Lie-depth matrix.

    A0 = direct edges (excluding diagonal), A1 = commutator,
    A2 = nested commutator, Aunreached = cutoff-unreached.

    Warns if the matrix contains entries with D >= 3 that are not unreached,
    since these are not counted in the returned tuple.
    """
    warnings.warn(
        "compute_signature_from_D() drops finite depths >= 3; use "
        "compute_depth_census()",
        DeprecationWarning,
        stacklevel=2,
    )
    n_sec = D.shape[0]
    A0 = int(np.sum(D == 0)) - n_sec
    A1 = int(np.sum(D == 1))
    A2 = int(np.sum(D == 2))
    aunreached = int(np.sum(D == UNREACHED_DEPTH))
    other = int(np.sum((D >= 3) & (D != UNREACHED_DEPTH)))
    if other > 0:
        warnings.warn(
            f"Found {other} entries with D >= 3 (not unreached). "
            f"These are NOT reflected in (A0,A1,A2,Aunreached)."
        )
    return (A0, A1, A2, aunreached)


def compute_lie_accessibility_audit(Vs, Xs, max_depth=4, tol=1e-8):
    """Compute typed direct, commutator, and cutoff Lie-depth data.

    Args:
        Vs: list of sector bases.
        Xs: list of generator matrices.
        max_depth: number of Lie filtration levels.
        tol: norm/rank threshold.

    Returns:
        A dictionary whose keys explicitly distinguish ``R1_Lie``,
        ``R2_Lie``, and ``D_Lie_cutoff``. The depth census retains every
        finite depth and a separate cutoff-unreached count.
    """
    sector_values = _materialize_sequence(Vs)
    observable_values = _materialize_sequence(Xs)
    assert_accessibility_inputs(sector_values, observable_values, tol=tol)
    R1 = compute_R1(sector_values, observable_values, tol)
    R2, R2_pairs = compute_R2(sector_values, observable_values, tol)
    R2_gen = compute_R2_per_generator(R2, len(observable_values))
    D, per_depth, cum_bases = compute_lie_depth_matrix(
        sector_values, observable_values, max_depth, tol
    )
    census = compute_depth_census(D)

    return {
        'R1_Lie': R1,
        'R2_Lie': R2,
        'R2_pairs': R2_pairs,
        'R2_per_generator': R2_gen,
        'D_Lie_cutoff': D,
        'lie_depth_census': census,
        'per_depth_basis': per_depth,
        'cumulative_basis': cum_bases,
        'n_sectors': len(sector_values),
        'n_generators': len(observable_values),
        'tested_max_depth_index': int(max_depth) - 1,
        'unreached_value': UNREACHED_DEPTH,
    }


def accessibility_signature(Vs, Xs, max_depth=4, tol=1e-8):
    """Deprecated compatibility wrapper with untyped historical keys."""
    warnings.warn(
        "accessibility_signature() uses untyped legacy keys; use "
        "compute_lie_accessibility_audit()",
        DeprecationWarning,
        stacklevel=2,
    )
    typed = compute_lie_accessibility_audit(
        Vs, Xs, max_depth=max_depth, tol=tol
    )
    census = typed['lie_depth_census']
    by_depth = census['by_depth']
    return {
        'R1': typed['R1_Lie'],
        'R2': typed['R2_Lie'],
        'R2_pairs': typed['R2_pairs'],
        'R2_gen': typed['R2_per_generator'],
        'D': typed['D_Lie_cutoff'],
        'sig': (
            by_depth.get(0, 0),
            by_depth.get(1, 0),
            by_depth.get(2, 0),
            census['unreached'],
        ),
        'per_depth': typed['per_depth_basis'],
        'cum_bases': typed['cumulative_basis'],
        'n_sec': typed['n_sectors'],
        'n_gens': typed['n_generators'],
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
        input_report = engine.check_inputs()
        engine.assert_valid(require_complete=True)  # optional strict profile
        summary = engine.audit()           # full audit
        d_matrix, layers = engine.depth()   # D and filtration layers
        r1, r2, pairs = engine.support()    # generator and commutator support
        cutoff = engine.cutoff_summary()    # cutoff-relative pair counts
        engine.assert_consistent()           # R1/R2/D internal checks

    The engine copies its inputs into read-only arrays so cached results cannot
    silently become stale after caller-side mutation.
    """

    def __init__(
            self,
            Vs,
            Xs,
            tol=1e-8,
            max_depth=4,
            seed=42,
            *,
            validation_tol=1e-7,
            require_complete=False,
            require_skew_hermitian=False,
            require_invariant_subspace=False):
        """Initialize engine with sectorized observable framework.

        Args:
            Vs: list of sector bases, each (dim, d_k).
            Xs: list of (dim, dim) observable matrices. Set
                ``require_skew_hermitian=True`` for the strict Lie convention.
            tol: Frobenius norm threshold for "nonzero".
            max_depth: number of Lie levels to probe. Depth indices are
                ``0 .. max_depth-1``.
            seed: reserved reproducibility metadata. The current deterministic
                filtration does not consume randomness.
            validation_tol: normalized tolerance for basis and structure checks.
            require_complete: reject sector bases that do not span the ambient
                space.
            require_skew_hermitian: reject observables without the strict
                skew-Hermitian generator convention.
            require_invariant_subspace: when sectors are incomplete, reject
                observables that leak into or out of the undeclared complement.
        """
        if not isinstance(max_depth, (int, np.integer)) or max_depth < 1:
            raise ValueError("max_depth must be an integer >= 1")

        sector_values = _materialize_sequence(Vs)
        observable_values = _materialize_sequence(Xs)
        input_report = assert_accessibility_inputs(
            sector_values,
            observable_values,
            tol=tol,
            validation_tol=validation_tol,
            require_complete=require_complete,
            require_skew_hermitian=require_skew_hermitian,
            require_invariant_subspace=require_invariant_subspace,
        )

        self.Vs = [np.array(V, copy=True) for V in sector_values]
        self.Xs = [np.array(X, copy=True) for X in observable_values]
        for array in self.Vs + self.Xs:
            array.setflags(write=False)

        self.tol = float(tol)
        self.validation_tol = float(validation_tol)
        self.max_depth = int(max_depth)
        self.seed = seed
        self.require_complete = bool(require_complete)
        self.require_skew_hermitian = bool(require_skew_hermitian)
        self.require_invariant_subspace = bool(require_invariant_subspace)
        self._input_report = input_report
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

    # ---- validation and interpretation checks ----

    def check_inputs(
            self,
            *,
            require_complete=None,
            require_skew_hermitian=None,
            require_invariant_subspace=None):
        """Return a fresh validation report for the engine snapshot."""
        return check_accessibility_inputs(
            self.Vs,
            self.Xs,
            tol=self.tol,
            validation_tol=self.validation_tol,
            require_complete=(
                self.require_complete
                if require_complete is None else require_complete
            ),
            require_skew_hermitian=(
                self.require_skew_hermitian
                if require_skew_hermitian is None else require_skew_hermitian
            ),
            require_invariant_subspace=(
                self.require_invariant_subspace
                if require_invariant_subspace is None else require_invariant_subspace
            ),
        )

    def assert_valid(self, **kwargs):
        """Raise ``ValueError`` if the stored realization violates its contract."""
        report = self.check_inputs(**kwargs)
        if not report["valid"]:
            raise ValueError(_validation_error_message(report))
        return report

    def check_invariants(self):
        """Check consistency among cached R1, R2, and Lie-depth shadows.

        This does not prove that ``max_depth`` is sufficient. It checks only
        internal consistency at the declared threshold and filtration cutoff.
        """
        errors = []
        warnings = []
        R1 = self._get_R1()
        R2_arr, _ = self._get_R2()
        D, _, _ = self._get_D()
        ns = self.n_sec
        offdiag = ~np.eye(ns, dtype=bool)

        if D.shape != (ns, ns):
            errors.append(f"D has shape {D.shape}, expected ({ns}, {ns})")
        if not np.all(np.diag(D) == 0):
            errors.append("D diagonal must be zero")

        allowed_depths = set(range(self.max_depth)) | {UNREACHED_DEPTH}
        unexpected = sorted(set(int(value) for value in D.flat) - allowed_depths)
        if unexpected:
            errors.append(f"D contains unexpected depth values: {unexpected}")

        direct_graph = np.any(R1, axis=0)
        direct_mismatch = int(np.sum((direct_graph != (D == 0)) & offdiag))
        if direct_mismatch:
            errors.append(
                f"R1 aggregate and D depth-0 support disagree on "
                f"{direct_mismatch} off-diagonal pairs"
            )

        if len(R2_arr) and self.max_depth >= 2:
            commutator_graph = np.any(R2_arr, axis=0)
            r2_depth_mismatch = int(np.sum(
                commutator_graph & (D > 1) & offdiag
            ))
            if r2_depth_mismatch:
                errors.append(
                    f"R2 support is absent from D<=1 on "
                    f"{r2_depth_mismatch} off-diagonal pairs"
                )
        elif len(R2_arr) and np.any(R2_arr[:, offdiag]):
            warnings.append(
                "R2 support was computed, but max_depth=1 excludes the "
                "commutator level from D"
            )

        frozen_count = int(np.sum((D == UNREACHED_DEPTH) & offdiag))
        if frozen_count:
            warnings.append(
                f"{frozen_count} pairs are unreached through Lie depth "
                f"{self.max_depth - 1}; this is cutoff-relative, not a global "
                "impossibility result"
            )

        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "direct_depth_mismatch_count": direct_mismatch,
            "frozen_pair_count": frozen_count,
            "tested_max_depth_index": self.max_depth - 1,
        }

    def assert_consistent(self):
        """Raise ``RuntimeError`` when R1/R2/D shadows are inconsistent."""
        report = self.check_invariants()
        if not report["valid"]:
            details = "\n".join(
                f"  - {message}" for message in report["errors"]
            )
            raise RuntimeError(f"Inconsistent accessibility results:\n{details}")
        return report

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
        """Return generator R1 and commutator R2 tensors plus pair indices."""
        return self._get_R1(), *self._get_R2()

    def depth(self):
        """Return cutoff-relative Lie-depth matrix and per-depth bases."""
        D, per_depth, _ = self._get_D()
        return D, per_depth

    def cutoff_summary(self):
        """Return typed cutoff-relative direct and Lie pair counts."""
        R1 = self._get_R1()
        D, _, _ = self._get_D()
        ns = self.n_sec
        offdiag = ~np.eye(ns, dtype=bool)
        R1_graph = np.zeros((ns, ns), dtype=bool)
        for g in range(self.n_gen):
            R1_graph |= R1[g]
        unsupported_direct = ns * (ns - 1) - int(np.sum(R1_graph & offdiag))
        unreached_lie = sum(
            1 for i in range(ns) for j in range(ns)
            if i != j and D[i, j] == UNREACHED_DEPTH
        )
        lie_emergent = sum(
            1 for i in range(ns) for j in range(ns)
            if i != j and not R1_graph[i, j] and D[i, j] != UNREACHED_DEPTH
        )
        return {
            'unsupported_direct_pairs': unsupported_direct,
            'unreached_lie_pairs': unreached_lie,
            'lie_emergent_pairs': lie_emergent,
        }

    def frozen_pairs(self):
        """Deprecated compatibility view of :meth:`cutoff_summary`."""
        warnings.warn(
            "frozen_pairs() uses retired untyped names; use cutoff_summary()",
            DeprecationWarning,
            stacklevel=2,
        )
        summary = self.cutoff_summary()
        return {
            'frozen_R1': summary['unsupported_direct_pairs'],
            'frozen_D': summary['unreached_lie_pairs'],
            'D_repaired': summary['lie_emergent_pairs'],
        }

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
            R1_tensor_pct/R2_tensor_pct. Cutoff-unreached counts are always
            off-diagonal sector-pair counts. The ``frozen_*`` keys are legacy
            serialization aliases only.
        """
        R1 = self._get_R1()
        R2_arr, R2_pairs = self._get_R2()
        D, per_depth, _ = self._get_D()
        cutoff = self.cutoff_summary()
        legacy_cutoff = {
            'frozen_R1': cutoff['unsupported_direct_pairs'],
            'frozen_D': cutoff['unreached_lie_pairs'],
            'D_repaired': cutoff['lie_emergent_pairs'],
        }
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
            **cutoff,
            **legacy_cutoff,
        }

    def __repr__(self):
        return (f"AccessibilityEngine({self.n_sec} sectors, {self.n_gen} gens, "
                f"dims={self.sector_dims})")


# Also expose at module level
__all__ = [
    'UNREACHED_DEPTH', 'FROZEN_DEPTH',
    'check_accessibility_inputs', 'assert_accessibility_inputs',
    'sector_block_norm', 'projector_block_norm', 'offdiag_count',
    'compute_direct_support', 'compute_routed_support',
    'compute_routed_depth_matrix', 'compute_length_two_support',
    'compute_word_depth_matrix', 'plateau_fraction', 'compute_depth_census',
    'compute_R1', 'compute_R2', 'compute_R2_per_generator',
    'compute_lie_filtration', 'audit_lie_closure',
    'compute_lie_depth_matrix', 'image_kernel_distance',
    'audit_matrix_product', 'rank_protection_audit',
    'single_term_bridge_audit', 'matrix_nondeg_audit',
    'compute_lie_accessibility_audit', 'accessibility_signature',
    'AccessibilityEngine',
]
