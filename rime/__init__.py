"""Conservative public API for typed sectorized-operator diagnostics."""

from .algebra import audit_finite_dimensional_star_algebra
from .accessibility import (
    UNREACHED_DEPTH,
    AccessibilityEngine,
    assert_accessibility_inputs,
    audit_lie_closure,
    audit_matrix_product,
    check_accessibility_inputs,
    compute_R1,
    compute_R2,
    compute_depth_census,
    compute_direct_support,
    compute_length_two_support,
    compute_lie_accessibility_audit,
    compute_lie_depth_matrix,
    compute_lie_filtration,
    compute_routed_depth_matrix,
    compute_routed_support,
    compute_word_depth_matrix,
    image_kernel_distance,
    rank_protection_audit,
)

__version__ = "0.0.1"

__all__ = [
    "__version__",
    "audit_finite_dimensional_star_algebra",
    "UNREACHED_DEPTH",
    "AccessibilityEngine",
    "check_accessibility_inputs",
    "assert_accessibility_inputs",
    "compute_direct_support",
    "compute_routed_support",
    "compute_routed_depth_matrix",
    "compute_length_two_support",
    "compute_word_depth_matrix",
    "compute_R1",
    "compute_R2",
    "compute_lie_accessibility_audit",
    "compute_lie_filtration",
    "compute_lie_depth_matrix",
    "compute_depth_census",
    "audit_lie_closure",
    "image_kernel_distance",
    "audit_matrix_product",
    "rank_protection_audit",
]
