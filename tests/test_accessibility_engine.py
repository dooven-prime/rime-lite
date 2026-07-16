"""Regression tests for AccessibilityEngine metric conventions."""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rime.accessibility import (
    AccessibilityEngine,
    check_accessibility_inputs,
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
    frozen = engine.frozen_pairs()

    assert audit["R1_tensor_count"] == 2
    assert audit["R1_count"] == 0
    assert audit["R1_tensor_pct"] == 50.0
    assert audit["R1_offdiag_pct"] == 0.0
    assert frozen["frozen_R1"] == 2
    assert frozen["frozen_D"] == 2
    assert frozen["D_repaired"] == 0


def test_offdiagonal_support_counts_as_accessibility_pair():
    Vs = [np.eye(2, dtype=complex)[:, [0]], np.eye(2, dtype=complex)[:, [1]]]
    X_flip = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)

    engine = AccessibilityEngine(Vs, [X_flip], max_depth=3)
    audit = engine.audit()
    frozen = engine.frozen_pairs()

    assert audit["R1_tensor_count"] == 2
    assert audit["R1_count"] == 2
    assert audit["R1_tensor_pct"] == 50.0
    assert audit["R1_offdiag_pct"] == 100.0
    assert frozen["frozen_R1"] == 0
    assert frozen["frozen_D"] == 0
    assert frozen["D_repaired"] == 0


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


if __name__ == "__main__":
    test_diagonal_support_not_counted_as_accessibility_pair()
    test_offdiagonal_support_counts_as_accessibility_pair()
    test_invalid_sector_basis_fails_before_computation()
    test_incomplete_and_non_skew_realizations_report_boundaries()
    test_retained_subspace_leakage_and_result_invariants_are_checkable()
    test_module_check_reports_shape_and_threshold_errors_without_crashing()
    test_single_lie_level_excludes_commutators_without_false_failure()
    print("test_accessibility_engine.py: OK")
