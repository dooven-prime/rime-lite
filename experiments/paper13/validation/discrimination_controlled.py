"""Appendix-level discrimination and coupling controls for Paper XIII."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rime.accessibility import (
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
)


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
TOL = 1e-8
FROZEN = 999


def one_hot_sectors(dim: int) -> list[np.ndarray]:
    eye = np.eye(dim, dtype=complex)
    return [eye[:, [index]] for index in range(dim)]


def _offdiag_count(matrix: np.ndarray) -> int:
    mask = ~np.eye(matrix.shape[0], dtype=bool)
    return int(np.count_nonzero(matrix & mask))


def check_support_bridge_coupling() -> bool:
    sectors = one_hot_sectors(4)
    reference = np.zeros((4, 4), dtype=complex)
    reference[1, 0], reference[0, 1] = 0.5, -0.5
    reference[2, 1], reference[1, 2] = 0.5, -0.5
    reference[3, 2], reference[2, 3] = 0.5, -0.5
    target = reference.copy()
    target[2, 1] = target[1, 2] = 0.0

    r1_ref = compute_direct_support(sectors, [reference], tol=TOL)
    r1_target = compute_direct_support(sectors, [target], tol=TOL)
    r2_ref = compute_length_two_support(sectors, [reference], tol=TOL)
    r2_target = compute_length_two_support(sectors, [target], tol=TOL)
    support_delta = _offdiag_count(r1_target) - _offdiag_count(r1_ref)
    bridge_delta = _offdiag_count(r2_target) - _offdiag_count(r2_ref)
    return support_delta < 0 and bridge_delta < 0


def check_shortcut_couples_support_and_depth() -> bool:
    sectors = one_hot_sectors(3)
    reference = np.zeros((3, 3), dtype=complex)
    reference[1, 0], reference[0, 1] = 0.5, -0.5
    reference[2, 1], reference[1, 2] = 0.5, -0.5
    target = reference.copy()
    target[2, 0], target[0, 2] = 0.25, -0.25

    r1_ref = compute_direct_support(sectors, [reference], tol=TOL)
    r1_target = compute_direct_support(sectors, [target], tol=TOL)
    d_ref = compute_word_depth_matrix(
        sectors, [reference], max_depth=3, tol=TOL, frozen=FROZEN
    )
    d_target = compute_word_depth_matrix(
        sectors, [target], max_depth=3, tol=TOL, frozen=FROZEN
    )
    support_gain = _offdiag_count(r1_target) > _offdiag_count(r1_ref)
    depth_reduction = d_ref[2, 0] == 2 and d_target[2, 0] == 1
    return support_gain and depth_reduction


def _load(stem: str) -> dict:
    return json.loads((RESULTS / f"{stem}.sofaudit").read_text(encoding="utf-8"))


def _signature_has_change(artifact: dict) -> bool:
    signature = artifact["signature"]
    scalar_paths = (
        ("support_mismatch", "total_mismatch"),
        ("bridge_word_mismatch", "total_mismatch"),
        ("bridge_lie_mismatch", "total_mismatch"),
        ("depth_distortion", "total_mismatch"),
        ("constraint_violations", "count"),
        ("action_response_failure", "total_large_deltas"),
    )
    for group, field in scalar_paths:
        value = signature.get(group)
        if isinstance(value, dict) and int(value.get(field, 0)) > 0:
            return True
    frozen = signature.get("frozen_disagreement", {})
    return any(
        abs(int(frozen.get(name, {}).get("delta", 0))) > 0
        for name in ("frozen_R1", "frozen_D_word", "frozen_D_lie")
    )


def check_legitimate_transformations() -> bool:
    artifacts = [
        _load("before_after_compiler"),
        _load("before_after_traffic"),
        _load("before_after_gridworld"),
    ]
    return all(
        _signature_has_change(artifact)
        and artifact["contract_evaluation"]["residual_violation_count"] == 0
        for artifact in artifacts
    )


def check_channel_specific_f4() -> bool:
    artifacts = [_load("compiler_f4"), _load("gridworld_f4")]
    return all(
        artifact["signature"]["support_mismatch"]["total_mismatch"] == 0
        and artifact["signature"]["bridge_word_mismatch"]["total_mismatch"] == 0
        and artifact["signature"]["bridge_lie_mismatch"]["total_mismatch"] > 0
        for artifact in artifacts
    )


def run_checks() -> dict[str, bool]:
    return {
        "support_bridge_coupling": check_support_bridge_coupling(),
        "shortcut_support_depth_coupling": check_shortcut_couples_support_and_depth(),
        "legitimate_change_zero_residual": check_legitimate_transformations(),
        "channel_specific_f4": check_channel_specific_f4(),
    }


def main() -> None:
    checks = run_checks()
    print("Paper XIII appendix discrimination controls")
    for name, passed in checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    print("Boundary: these controls validate signatures; they are not classification theorems.")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
