"""Regression tests for AccessibilityEngine metric conventions."""

from pathlib import Path
import sys

import numpy as np
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rime.accessibility import (
    AccessibilityEngine,
    UNREACHED_DEPTH,
    audit_lie_closure,
    audit_matrix_product,
    check_accessibility_inputs,
    compute_R2,
    compute_depth_census,
    compute_length_two_support,
    compute_lie_accessibility_audit,
    compute_lie_filtration,
    compute_routed_depth_matrix,
    compute_routed_support,
    compute_word_depth_matrix,
    image_kernel_distance,
)


def _assert_raises(exc_type, fn):
    try:
        fn()
    except exc_type as exc:
        return exc
    raise AssertionError(f"expected {exc_type.__name__}")


def test_diagonal_support_not_counted_as_accessibility_pair():
    Vs = [np.eye(2, dtype=complex)[:, [0]], np.eye(2, dtype=complex)[:, [1]]]
    X_diag = 1j * np.diag([1.0, -1.0])

    engine = AccessibilityEngine(Vs, [X_diag], max_depth=3)
    audit = engine.audit()
    cutoff = engine.cutoff_summary()

    assert audit["R1_tensor_count"] == 2
    assert audit["R1_count"] == 0
    assert audit["R1_tensor_pct"] == 50.0
    assert audit["R1_offdiag_pct"] == 0.0
    assert cutoff["unsupported_direct_pairs"] == 2
    assert cutoff["unreached_lie_pairs"] == 2
    assert cutoff["lie_emergent_pairs"] == 0


def test_offdiagonal_support_counts_as_accessibility_pair():
    Vs = [np.eye(2, dtype=complex)[:, [0]], np.eye(2, dtype=complex)[:, [1]]]
    X_flip = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)

    engine = AccessibilityEngine(Vs, [X_flip], max_depth=3)
    audit = engine.audit()
    cutoff = engine.cutoff_summary()

    assert audit["R1_tensor_count"] == 2
    assert audit["R1_count"] == 2
    assert audit["R1_tensor_pct"] == 50.0
    assert audit["R1_offdiag_pct"] == 100.0
    assert cutoff["unsupported_direct_pairs"] == 0
    assert cutoff["unreached_lie_pairs"] == 0
    assert cutoff["lie_emergent_pairs"] == 0


def test_invalid_sector_basis_fails_before_computation():
    bad_basis = np.array([[1.0], [1.0]], dtype=complex)
    X = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)

    exc = _assert_raises(ValueError, lambda: AccessibilityEngine([bad_basis], [X]))
    assert "not orthonormal" in str(exc)


def test_incomplete_and_non_skew_realizations_report_boundaries():
    retained = [np.eye(2, dtype=complex)[:, [0]]]
    X_hermitian = np.diag([1.0, -1.0]).astype(complex)

    engine = AccessibilityEngine(retained, [X_hermitian], max_depth=2)
    report = engine.check_inputs()

    assert report["valid"]
    assert report["coverage_rank"] == 1
    assert any("incomplete retained subspace" in item for item in report["warnings"])
    assert any("not all skew-Hermitian" in item for item in report["warnings"])

    _assert_raises(
        ValueError,
        lambda: engine.assert_valid(require_complete=True),
    )
    _assert_raises(
        ValueError,
        lambda: engine.assert_valid(require_skew_hermitian=True),
    )


def test_retained_subspace_leakage_and_result_invariants_are_checkable():
    retained = [np.eye(2, dtype=complex)[:, [0]]]
    X_flip = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)

    engine = AccessibilityEngine(retained, [X_flip], max_depth=2)
    input_report = engine.check_inputs()
    assert input_report["retained_subspace_leakage_max"] > 0
    assert any("undeclared complement" in item for item in input_report["warnings"])
    _assert_raises(
        ValueError,
        lambda: engine.assert_valid(require_invariant_subspace=True),
    )

    invariant_report = engine.check_invariants()
    assert invariant_report["valid"]
    assert engine.assert_consistent()["valid"]


def test_module_check_reports_shape_and_threshold_errors_without_crashing():
    report = check_accessibility_inputs(
        [np.eye(2, dtype=complex)[:, [0]]],
        [np.eye(3, dtype=complex)],
        tol="not-a-number",
    )
    assert not report["valid"]
    assert any("tol must" in item for item in report["errors"])
    assert any("expected (2, 2)" in item for item in report["errors"])


def test_single_lie_level_excludes_commutators_without_false_failure():
    Vs = [np.eye(2, dtype=complex)[:, [0]], np.eye(2, dtype=complex)[:, [1]]]
    X1 = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    X2 = 1j * np.diag([1.0, -1.0])

    engine = AccessibilityEngine(Vs, [X1, X2], max_depth=1)
    D, per_depth = engine.depth()
    report = engine.check_invariants()

    assert len(per_depth) == 1
    assert np.all(D[~np.eye(2, dtype=bool)] == 0)
    assert report["valid"]
    assert any("max_depth=1" in item for item in report["warnings"])


def test_routed_support_is_distinct_from_full_word_support():
    identity = np.eye(4, dtype=complex)
    sectors = [identity[:, [index]] for index in range(4)]
    observable = np.zeros((4, 4), dtype=complex)
    observable[1, 0] = 1.0
    observable[2, 0] = 1.0
    observable[3, 1] = 1.0
    observable[3, 2] = -1.0

    routed = compute_routed_support(sectors, [observable], depth=2)
    word = compute_length_two_support(sectors, [observable])
    depth = compute_routed_depth_matrix(sectors, [observable], max_depth=2)
    commutator, pairs = compute_R2(sectors, [observable])

    assert routed[3, 0]
    assert not word[3, 0]
    assert depth[3, 0] == 2
    assert depth[0, 3] == UNREACHED_DEPTH
    assert commutator.shape == (0, 4, 4)
    assert pairs == []


def test_image_kernel_incidence_and_rank_protection_are_typed():
    A = np.array([[1.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    incidence = audit_matrix_product(A, B)
    assert incidence["category"] == "unprotected-zero"
    assert incidence["factors_nonzero"]
    assert not incidence["product_nonzero"]
    assert incidence["image_kernel_distance"] < 1e-12

    left = audit_matrix_product(np.eye(2), B)
    assert left["left_protected"]
    assert left["product_nonzero"]
    assert left["protection_consistent"]

    right = audit_matrix_product(A, np.eye(2))
    assert right["right_protected"]
    assert right["product_nonzero"]
    assert right["protection_consistent"]


def test_lie_closure_certificate_requires_generator_closure():
    X = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    Z = 1j * np.diag([1.0, -1.0])
    filtration = compute_lie_filtration([X, Z], max_depth=4)
    basis = [vector for layer in filtration for vector in layer]
    certificate = audit_lie_closure([X, Z], basis)

    assert certificate["dimension"] == 3
    assert certificate["contains_generators"]
    assert certificate["closed_under_generators"]
    assert certificate["saturated"]
    assert certificate["claim_status"] == "computational_certificate"


def test_typed_lie_audit_preserves_all_cutoff_depths():
    identity = np.eye(2, dtype=complex)
    sectors = [identity[:, [0]], identity[:, [1]]]
    flip = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)

    audit = compute_lie_accessibility_audit(
        sectors, [flip], max_depth=2
    )

    assert set(audit) >= {
        "R1_Lie",
        "R2_Lie",
        "D_Lie_cutoff",
        "lie_depth_census",
        "tested_max_depth_index",
    }
    assert audit["lie_depth_census"]["by_depth"] == {0: 2}
    assert audit["lie_depth_census"]["unreached"] == 0
    assert audit["tested_max_depth_index"] == 1


def test_removed_untyped_kappa_helpers_are_absent():
    import rime.accessibility as accessibility

    assert not hasattr(accessibility, "compute_kappa_depth_matrix")
    assert not hasattr(accessibility, "compute_kappa_01")
    assert not hasattr(accessibility, "compute_transport_tensor")


def test_frozen_keyword_remains_a_deprecated_compatibility_alias():
    identity = np.eye(2, dtype=complex)
    sectors = [identity[:, [0]], identity[:, [1]]]
    diagonal = np.diag([1.0, -1.0]).astype(complex)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        depth = compute_word_depth_matrix(
            sectors, [diagonal], max_depth=1, frozen=777
        )
    assert np.all(depth[~np.eye(2, dtype=bool)] == 777)
    assert any(item.category is DeprecationWarning for item in caught)


def test_certificate_helpers_reject_invalid_numeric_policies():
    _assert_raises(
        ValueError,
        lambda: compute_depth_census(np.array([[0, -1], [999, 0]])),
    )
    _assert_raises(
        ValueError,
        lambda: image_kernel_distance(np.eye(1), np.eye(1), rank_tol=np.nan),
    )


if __name__ == "__main__":
    test_diagonal_support_not_counted_as_accessibility_pair()
    test_offdiagonal_support_counts_as_accessibility_pair()
    test_invalid_sector_basis_fails_before_computation()
    test_incomplete_and_non_skew_realizations_report_boundaries()
    test_retained_subspace_leakage_and_result_invariants_are_checkable()
    test_module_check_reports_shape_and_threshold_errors_without_crashing()
    test_single_lie_level_excludes_commutators_without_false_failure()
    test_routed_support_is_distinct_from_full_word_support()
    test_image_kernel_incidence_and_rank_protection_are_typed()
    test_lie_closure_certificate_requires_generator_closure()
    test_typed_lie_audit_preserves_all_cutoff_depths()
    test_removed_untyped_kappa_helpers_are_absent()
    test_frozen_keyword_remains_a_deprecated_compatibility_alias()
    test_certificate_helpers_reject_invalid_numeric_policies()
    print("test_accessibility_engine.py: OK")
