"""API contract tests for numerical spectral registration gates."""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import rime.spectral_utils as spectral_utils
from rime.spectral_utils import (
    build_projectors,
    joint_diag_sectors,
    ordered_compression_sectors,
    sector_bases_from_projectors,
)


def _assert_raises(exc_type, fn):
    try:
        fn()
    except exc_type as exc:
        return exc
    raise AssertionError(f"expected {exc_type.__name__}")


def test_joint_registration_requires_commuting_hermitian_inputs():
    nonnormal = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=complex)
    _assert_raises(ValueError, lambda: joint_diag_sectors([nonnormal]))

    x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    z = np.diag([1.0, -1.0]).astype(complex)
    _assert_raises(ValueError, lambda: joint_diag_sectors([x, z]))


def test_valid_joint_registration_produces_orthogonal_projectors():
    q = np.diag([0.0, 0.0, 1.0]).astype(complex)
    h = np.diag([0.0, 1.0, 1.0]).astype(complex)
    sectors = joint_diag_sectors([q, h])
    projectors = build_projectors(sectors, dim_total=3)
    bases = sector_bases_from_projectors(projectors)

    assert len(sectors) == 3
    assert sorted(basis.shape[1] for basis in bases) == [1, 1, 1]
    assert np.linalg.norm(sum(projectors) - np.eye(3), "fro") < 1e-12


def test_ordered_compression_is_explicitly_not_joint_diagonalization():
    x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    z = np.diag([1.0, -1.0]).astype(complex)
    sectors = ordered_compression_sectors([x, z])
    projectors = build_projectors(sectors, dim_total=2)

    assert len(sectors) == 2
    assert np.linalg.norm(sum(projectors) - np.eye(2), "fro") < 1e-12
    _assert_raises(ValueError, lambda: joint_diag_sectors([x, z]))


def test_projector_registration_rejects_nonprojectors():
    candidate = np.diag([1.0, 0.25]).astype(complex)
    _assert_raises(
        ValueError,
        lambda: sector_bases_from_projectors([candidate]),
    )


def test_registration_rejects_invalid_threshold_policies():
    identity = np.eye(2, dtype=complex)
    _assert_raises(
        ValueError,
        lambda: ordered_compression_sectors([identity], tol=np.nan),
    )
    _assert_raises(
        ValueError,
        lambda: joint_diag_sectors([identity], validation_tol="bad"),
    )


def test_first_version_t7_helpers_are_not_in_the_active_api():
    for name in (
        "compute_transport_kappa",
        "count_t7_pairs",
        "find_t7_pairs",
        "analyze_t7",
    ):
        assert not hasattr(spectral_utils, name)


if __name__ == "__main__":
    test_joint_registration_requires_commuting_hermitian_inputs()
    test_valid_joint_registration_produces_orthogonal_projectors()
    test_ordered_compression_is_explicitly_not_joint_diagonalization()
    test_projector_registration_rejects_nonprojectors()
    test_registration_rejects_invalid_threshold_policies()
    test_first_version_t7_helpers_are_not_in_the_active_api()
    print("test_spectral_utils_api.py: OK")
