"""Regression tests for AccessibilityEngine metric conventions."""

import numpy as np

from rime.accessibility import AccessibilityEngine


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


if __name__ == "__main__":
    test_diagonal_support_not_counted_as_accessibility_pair()
    test_offdiagonal_support_counts_as_accessibility_pair()
    print("test_accessibility_engine.py: OK")
