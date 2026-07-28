"""Finite-dimensional numerical algebra certificate helpers."""

from __future__ import annotations

import numpy as np


def _positive_finite_float(value, name):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a finite positive scalar") from None
    if not np.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be a finite positive scalar")
    return result


def audit_finite_dimensional_star_algebra(generators, basis, tol=1e-10):
    """Audit a declared finite-dimensional unital ``*``-algebra span.

    The audit checks that the span contains the declared generators and the
    identity and is closed under multiplication and adjoint. A singular Gram
    matrix for the supplied spanning list is allowed: it means only that the
    list is redundant. Semisimplicity is supported by the finite-dimensional
    unital complex ``*``-algebra theorem, never by a Gram determinant.

    The result is a floating-point computational certificate at ``tol``. It is
    not an exact proof that the input span is a ``C*``-algebra.
    """
    tol = _positive_finite_float(tol, "tol")
    generators = [np.asarray(value) for value in generators]
    basis = [np.asarray(value) for value in basis]
    if not generators:
        raise ValueError("at least one generator is required")
    if not basis:
        raise ValueError("at least one spanning matrix is required")

    ambient_dim = generators[0].shape[0]
    expected_shape = (ambient_dim, ambient_dim)
    for label, values in (("generators", generators), ("basis", basis)):
        for index, value in enumerate(values):
            if value.ndim != 2 or value.shape != expected_shape:
                raise ValueError(
                    f"{label}[{index}] must have shape {expected_shape}"
                )
            if not np.all(np.isfinite(value)):
                raise ValueError(f"{label}[{index}] contains non-finite values")

    columns = np.column_stack([value.reshape(-1) for value in basis])
    gram = columns.conj().T @ columns
    gram_residual = float(
        np.linalg.norm(gram - np.eye(len(basis)), "fro")
    )
    if gram_residual <= tol:
        span_dimension = len(basis)
        span_basis = columns
    else:
        u, singular_values, _ = np.linalg.svd(columns, full_matrices=False)
        span_dimension = int(np.sum(singular_values > tol))
        span_basis = u[:, :span_dimension]
    if span_dimension == 0:
        raise ValueError("the declared spanning list is numerically zero")
    span_matrices = [
        span_basis[:, index].reshape(expected_shape)
        for index in range(span_dimension)
    ]

    def residual(matrix):
        vector = np.asarray(matrix).reshape(-1)
        projected = span_basis @ (span_basis.conj().T @ vector)
        return float(np.linalg.norm(vector - projected))

    generator_residual = max(residual(value) for value in generators)
    identity_residual = residual(np.eye(ambient_dim, dtype=complex))
    adjoint_residual = max(
        residual(value.conj().T) for value in span_matrices
    )
    product_residual = max(
        residual(left @ right)
        for left in span_matrices
        for right in span_matrices
    )
    contains_generators = generator_residual <= tol
    contains_identity = identity_residual <= tol
    closed_under_adjoint = adjoint_residual <= tol
    closed_under_multiplication = product_residual <= tol
    registered_unital_star_algebra = (
        contains_generators
        and contains_identity
        and closed_under_adjoint
        and closed_under_multiplication
    )

    return {
        "ambient_dimension": ambient_dim,
        "declared_basis_count": len(basis),
        "span_dimension": span_dimension,
        "basis_linearly_independent": span_dimension == len(basis),
        "declared_basis_gram_residual": gram_residual,
        "maximum_generator_span_residual": generator_residual,
        "identity_span_residual": identity_residual,
        "maximum_adjoint_closure_residual": adjoint_residual,
        "maximum_product_closure_residual": product_residual,
        "contains_generators": contains_generators,
        "contains_identity": contains_identity,
        "closed_under_adjoint": closed_under_adjoint,
        "closed_under_multiplication": closed_under_multiplication,
        "registered_unital_star_algebra": registered_unital_star_algebra,
        "semisimplicity_supported": registered_unital_star_algebra,
        "semisimplicity_basis": (
            "finite_dimensional_unital_complex_star_algebra_theorem"
        ),
        "claim_status": "computational_certificate",
        "tolerance": tol,
    }


__all__ = ["audit_finite_dimensional_star_algebra"]
