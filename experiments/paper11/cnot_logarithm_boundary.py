"""Paper XI diagnostic: CNOT path admissibility and logarithm control.

The affine path ``I + s(U_CNOT - I)`` is singular at ``s=1/2``.  This
producer records that failure and compares it with the unitary path

    P_plus + exp(i*pi*s) P_minus,

where ``P_minus = (I - U_CNOT) / 2``.  The unitary path has the explicit
continuous logarithm ``i*pi*s*P_minus``.  The comparison withdraws the old
interior repair threshold; it does not emit a wall certificate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

try:
    import cirq
except ImportError as exc:  # pragma: no cover - user-facing dependency error
    raise SystemExit(
        "Missing optional dependency 'cirq'. Run this script inside the project "
        "venv or install cirq in the active interpreter."
    ) from exc

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine  # noqa: E402


TOL = 1e-6
MAX_DEPTH = 4


def sector_bases(n_qubits: int) -> list[np.ndarray]:
    dim = 2**n_qubits
    eye = np.eye(dim, dtype=complex)
    return [eye[:, [idx]] for idx in range(dim)]


def embed_first_qubits(matrix: np.ndarray, n_qubits: int, arity: int) -> np.ndarray:
    if n_qubits < arity:
        raise ValueError(f"n_qubits must be at least {arity}")
    trailing = np.eye(2 ** (n_qubits - arity), dtype=complex)
    return np.kron(matrix, trailing)


def cnot_projectors(n_qubits: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cnot = embed_first_qubits(cirq.unitary(cirq.CNOT), n_qubits, arity=2)
    eye = np.eye(cnot.shape[0], dtype=complex)
    p_minus = (eye - cnot) / 2.0
    p_plus = eye - p_minus

    residuals = {
        "involution": np.linalg.norm(cnot @ cnot - eye, ord="fro"),
        "minus_projector": np.linalg.norm(p_minus @ p_minus - p_minus, ord="fro"),
        "plus_projector": np.linalg.norm(p_plus @ p_plus - p_plus, ord="fro"),
        "orthogonality": np.linalg.norm(p_plus @ p_minus, ord="fro"),
    }
    if max(residuals.values()) > TOL:
        raise RuntimeError(f"CNOT projector identities failed: {residuals}")
    return cnot, p_plus, p_minus


def fixed_generators(n_qubits: int) -> list[np.ndarray]:
    """Return explicit anti-Hermitian logarithms for fixed H and S gates."""
    h = cirq.unitary(cirq.H)
    h_minus = (np.eye(2, dtype=complex) - h) / 2.0
    log_h = 1j * np.pi * h_minus
    log_s = np.diag([0.0j, 0.5j * np.pi]).astype(complex)
    return [
        embed_first_qubits(log_h, n_qubits, arity=1),
        embed_first_qubits(log_s, n_qubits, arity=1),
    ]


def affine_path(
    strength: float,
    p_plus: np.ndarray,
    p_minus: np.ndarray,
) -> np.ndarray:
    return p_plus + (1.0 - 2.0 * strength) * p_minus


def affine_sample_logarithm(
    strength: float,
    p_plus: np.ndarray,
    p_minus: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, str]:
    """Return a finite samplewise log and its skew part away from s=1/2.

    On the right component this uses the scalar convention ``Arg(-x)=pi``.
    It is a valid logarithm at each sample but is not a continuous branch
    through the excluded singular point.
    """
    eigenvalue = 1.0 - 2.0 * strength
    if np.isclose(eigenvalue, 0.0, atol=TOL, rtol=0.0):
        raise ValueError("the affine CNOT path has no finite logarithm at s=1/2")
    branch_phase = np.pi if eigenvalue < 0.0 else 0.0
    scalar_log = np.log(abs(eigenvalue)) + 1j * branch_phase
    full_log = scalar_log * p_minus
    skew_log = (full_log - full_log.conj().T) / 2.0
    branch = "right_component_arg_pi" if eigenvalue < 0.0 else "left_component_real"
    return full_log, skew_log, branch


def unitary_path(
    strength: float,
    p_plus: np.ndarray,
    p_minus: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    continuous_log = 1j * np.pi * strength * p_minus
    matrix = p_plus + np.exp(1j * np.pi * strength) * p_minus
    return matrix, continuous_log


def audit_generators(
    generators: list[np.ndarray],
    n_qubits: int,
) -> dict:
    sectors = sector_bases(n_qubits)
    engine = AccessibilityEngine(
        sectors,
        generators,
        tol=TOL,
        max_depth=MAX_DEPTH,
        require_complete=True,
        require_skew_hermitian=True,
    )
    engine.assert_consistent()
    cutoff = engine.cutoff_summary()
    declared_pairs = len(sectors) * (len(sectors) - 1)
    direct_supported_pairs = declared_pairs - cutoff["unsupported_direct_pairs"]
    return {
        "cutoff": MAX_DEPTH,
        "declared_pairs": declared_pairs,
        "direct_supported_pairs": direct_supported_pairs,
        "direct_unsupported_pairs": cutoff["unsupported_direct_pairs"],
        "lie_unreached_at_cutoff_pairs": cutoff["unreached_lie_pairs"],
        "lie_reached_without_direct_support_pairs": cutoff["lie_emergent_pairs"],
        "direct_supported_pair_fraction": (
            direct_supported_pairs / declared_pairs if declared_pairs else 0.0
        ),
    }


def matrix_diagnostics(matrix: np.ndarray) -> dict:
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    determinant = np.linalg.det(matrix)
    eye = np.eye(matrix.shape[0], dtype=complex)
    return {
        "matrix_rank": int(np.linalg.matrix_rank(matrix, tol=TOL)),
        "matrix_dimension": matrix.shape[0],
        "determinant_real": float(np.real(determinant)),
        "determinant_imag": float(np.imag(determinant)),
        "minimum_singular_value": float(np.min(singular_values)),
        "unitarity_residual_fro": float(
            np.linalg.norm(matrix.conj().T @ matrix - eye, ord="fro")
        ),
    }


def affine_row(
    strength: float,
    n_qubits: int,
    p_plus: np.ndarray,
    p_minus: np.ndarray,
) -> dict:
    matrix = affine_path(strength, p_plus, p_minus)
    base = {"strength": strength, **matrix_diagnostics(matrix)}
    if base["matrix_rank"] < base["matrix_dimension"]:
        return {
            **base,
            "logarithm_status": "undefined_singular_matrix",
            "samplewise_branch": None,
            "logarithm_reconstruction_residual_fro": None,
            "cutoff": MAX_DEPTH,
            "declared_pairs": (2**n_qubits) * (2**n_qubits - 1),
            "direct_supported_pairs": None,
            "direct_unsupported_pairs": None,
            "lie_unreached_at_cutoff_pairs": None,
            "lie_reached_without_direct_support_pairs": None,
            "direct_supported_pair_fraction": None,
        }

    full_log, skew_log, branch = affine_sample_logarithm(
        strength,
        p_plus,
        p_minus,
    )
    reconstructed = expm(full_log)
    return {
        **base,
        "logarithm_status": "finite_samplewise_logarithm",
        "samplewise_branch": branch,
        "logarithm_reconstruction_residual_fro": float(
            np.linalg.norm(reconstructed - matrix, ord="fro")
        ),
        **audit_generators(fixed_generators(n_qubits) + [skew_log], n_qubits),
    }


def unitary_row(
    strength: float,
    n_qubits: int,
    p_plus: np.ndarray,
    p_minus: np.ndarray,
) -> dict:
    matrix, continuous_log = unitary_path(strength, p_plus, p_minus)
    reconstructed = expm(continuous_log)
    return {
        "strength": strength,
        **matrix_diagnostics(matrix),
        "logarithm_status": "explicit_continuous_branch",
        "continuous_log_norm_fro": float(np.linalg.norm(continuous_log, ord="fro")),
        "logarithm_reconstruction_residual_fro": float(
            np.linalg.norm(reconstructed - matrix, ord="fro")
        ),
        **audit_generators(
            fixed_generators(n_qubits) + [continuous_log],
            n_qubits,
        ),
    }


def support_signature(row: dict) -> tuple[int, int, int, int]:
    return (
        row["direct_supported_pairs"],
        row["direct_unsupported_pairs"],
        row["lie_unreached_at_cutoff_pairs"],
        row["lie_reached_without_direct_support_pairs"],
    )


def run(grid: int = 21, n_qubits: int = 2) -> dict:
    if grid < 3 or grid % 2 == 0:
        raise ValueError("grid must be odd and at least 3 so that s=0.5 is sampled")
    strengths = np.linspace(0.0, 1.0, grid)
    cnot, p_plus, p_minus = cnot_projectors(n_qubits)
    affine_rows = [
        affine_row(float(strength), n_qubits, p_plus, p_minus)
        for strength in strengths
    ]
    unitary_rows = [
        unitary_row(float(strength), n_qubits, p_plus, p_minus)
        for strength in strengths
    ]

    singular_rows = [
        row for row in affine_rows
        if row["logarithm_status"] == "undefined_singular_matrix"
    ]
    if len(singular_rows) != 1 or not np.isclose(singular_rows[0]["strength"], 0.5):
        raise RuntimeError("the affine audit must contain the unique s=0.5 singular sample")
    singular_index = next(
        index for index, row in enumerate(affine_rows)
        if row["logarithm_status"] == "undefined_singular_matrix"
    )
    left = affine_rows[singular_index - 1]
    right = affine_rows[singular_index + 1]

    positive_rows = [row for row in unitary_rows if row["strength"] > 0.0]
    positive_signatures = {support_signature(row) for row in positive_rows}
    if len(positive_signatures) != 1:
        raise RuntimeError("unitary-path support summary changed at positive sampled parameters")
    if np.linalg.norm(unitary_rows[-1]["strength"] * 1j * np.pi * p_minus) == 0.0:
        raise RuntimeError("unitary endpoint logarithm unexpectedly vanished")
    endpoint_residual = np.linalg.norm(unitary_path(1.0, p_plus, p_minus)[0] - cnot)
    if endpoint_residual > TOL:
        raise RuntimeError("unitary control does not terminate at CNOT")

    positive_signature = positive_rows[0]
    return {
        "record_version": "paper11-cnot-path-admissibility-v1.0",
        "claim_status": "Computational Observation",
        "record_role": "trajectory_diagnostic",
        "wall_admission": "not_admitted",
        "diagnostic_kind": "affine_logarithm_failure_with_unitary_path_control",
        "producer": "experiments/paper11/cnot_logarithm_boundary.py",
        "curation_assignment": {
            "rulebook_version": "paper11-curation-tags-v1.0",
            "assignment_source": "derived",
            "tags": ["NONSMOOTH_DISCRETE"],
            "override_reason": (
                "the affine path has a logarithm-domain singularity; the unitary "
                "control has no positive-parameter support transition"
            ),
        },
        "grid": grid,
        "sample_spacing": float(strengths[1] - strengths[0]),
        "n_qubits": n_qubits,
        "fixed_lie_generators": {
            "generators": ["analytic_log(H)", "analytic_log(S)"],
            "registration": "fixed anti-Hermitian generators on the first qubit",
        },
        "affine_path": {
            "formula": "P_plus + (1 - 2*s) P_minus",
            "matrix_interpolation": "I + s * (U_CNOT - I)",
            "logarithm_rule": (
                "log(abs(1-2*s))*P_minus with +i*pi*P_minus on the right component"
            ),
            "logarithm_reconstruction_method": "scipy.linalg.expm(samplewise_logarithm)",
            "continuous_logarithm_branch_certified": False,
            "logarithm_domain": "[0,0.5) union (0.5,1]",
            "maximum_logarithm_reconstruction_residual_fro": float(
                max(
                    row["logarithm_reconstruction_residual_fro"]
                    for row in affine_rows
                    if row["logarithm_reconstruction_residual_fro"] is not None
                )
            ),
            "rows": affine_rows,
            "singularity": {
                "strength": 0.5,
                "matrix_rank": singular_rows[0]["matrix_rank"],
                "matrix_dimension": singular_rows[0]["matrix_dimension"],
                "determinant_real": singular_rows[0]["determinant_real"],
                "reason": (
                    "the eigenvalue 1-2*s vanishes on the CNOT -1 eigenspace"
                ),
                "finite_matrix_logarithm_exists": False,
            },
            "sampled_side_comparison": {
                "comparison_semantics": "separate legal samples; not a wall bracket",
                "left_sample": left,
                "right_sample": right,
                "sampled_pair_count_difference": (
                    right["lie_reached_without_direct_support_pairs"]
                    - left["lie_reached_without_direct_support_pairs"]
                ),
            },
        },
        "unitary_control": {
            "formula": "P_plus + exp(i*pi*s) P_minus",
            "continuous_logarithm": "L(s) = i*pi*s*P_minus",
            "logarithm_reconstruction_method": "scipy.linalg.expm(continuous_logarithm)",
            "continuous_logarithm_branch_certified": True,
            "path_domain": "[0,1]",
            "endpoint_residual_fro": float(endpoint_residual),
            "maximum_unitarity_residual_fro": float(
                max(row["unitarity_residual_fro"] for row in unitary_rows)
            ),
            "maximum_logarithm_reconstruction_residual_fro": float(
                max(row["logarithm_reconstruction_residual_fro"] for row in unitary_rows)
            ),
            "rows": unitary_rows,
            "positive_parameter_signature": {
                key: positive_signature[key]
                for key in (
                    "direct_supported_pairs",
                    "direct_unsupported_pairs",
                    "lie_unreached_at_cutoff_pairs",
                    "lie_reached_without_direct_support_pairs",
                )
            },
            "all_positive_sampled_parameters_have_same_signature": True,
            "sampled_endpoint_activation_at_s_zero": (
                support_signature(unitary_rows[0]) != support_signature(positive_rows[0])
            ),
            "sampled_internal_support_transition_detected": False,
        },
        "retired_provenance": {
            "withdrawn_claim": "first detected repair at 0.55 with bracket (0.50,0.55]",
            "reason": (
                "the affine path crosses a singular logarithm-domain boundary, "
                "while the admissible unitary control is constant on sampled s>0"
            ),
        },
        "regularity": "unknown",
        "comparison_relation": "path_dependent_affine_failure_with_unitary_control",
        "claim_boundary": (
            "the affine-side difference is a logarithm-domain diagnostic and the "
            "unitary path is a control; neither is admitted here as an interior wall, "
            "repair threshold, or universal CNOT mechanism"
        ),
    }


def print_report(result: dict) -> None:
    print("=" * 88)
    print("  Paper XI - CNOT Path Admissibility Diagnostic")
    print("=" * 88)
    print("  Affine path: singular at s=0.50; no finite logarithm there")
    print("  Unitary control: P_plus + exp(i*pi*s) P_minus")
    print("  Continuous log: i*pi*s*P_minus")
    print("  Claim status: Computational Observation; no wall admission")
    print()
    print(
        f"  {'s':>5s}  {'affine':>9s}  {'affine Hall':>12s}  "
        f"{'unitary Hall':>12s}  {'unitary residual':>16s}"
    )
    print("  " + "-" * 72)
    affine_rows = result["affine_path"]["rows"]
    unitary_rows = result["unitary_control"]["rows"]
    for affine, unitary in zip(affine_rows, unitary_rows):
        affine_hall = affine["lie_reached_without_direct_support_pairs"]
        affine_label = "undefined" if affine_hall is None else f"{affine_hall}/12"
        print(
            f"  {affine['strength']:5.2f}  "
            f"{affine['logarithm_status'][:9]:>9s}  "
            f"{affine_label:>12s}  "
            f"{unitary['lie_reached_without_direct_support_pairs']:>9d}/12  "
            f"{unitary['unitarity_residual_fro']:16.3e}"
        )
    print()
    print("  Result: the former interior s=0.55 repair threshold is withdrawn.")
    print("          The unitary control has one sampled signature for every s>0.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=int, default=21, help="odd sample count")
    parser.add_argument("--qubits", type=int, default=2, help="number of qubits")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run(grid=args.grid, n_qubits=args.qubits)
    print_report(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
