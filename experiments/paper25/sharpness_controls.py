"""Generate exact finite controls for the diagnostic sharpness theorems."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = HERE / "results" / "diagnostic_sharpness_v1.json"
MANUSCRIPT = (
    ROOT
    / "papers"
    / "paper25"
    / "Paper XXV.md"
)
SOURCE_PATHS = (
    Path("experiments/paper25/sharpness_controls.py"),
    Path("papers/paper25/Paper XXV.md"),
)


def mm(left: list[list[F]], right: list[list[F]]) -> list[list[F]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), F(0))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def sub(left: list[list[F]], right: list[list[F]]) -> list[list[F]]:
    return [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def transpose(matrix: list[list[F]]) -> list[list[F]]:
    return [list(row) for row in zip(*matrix)]


def frobenius_squared(matrix: list[list[F]]) -> F:
    return sum((entry * entry for row in matrix for entry in row), F(0))


def diagonal(size: int, support: set[int]) -> list[list[F]]:
    return [[F(int(i == j and i in support)) for j in range(size)] for i in range(size)]


def scale(value: F, matrix: list[list[F]]) -> list[list[F]]:
    return [[value * entry for entry in row] for row in matrix]


def outer(left: list[F], right: list[F]) -> list[list[F]]:
    return [[a * b for b in right] for a in left]


def encoded(value: F) -> str:
    return f"{value.numerator}/{value.denominator}"


def content_digest(payload: dict) -> str:
    unsigned = deepcopy(payload)
    unsigned.pop("content_sha256", None)
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _axis_controls() -> dict:
    epsilon = F(7, 5)
    operator_actual_sq = epsilon * epsilon

    cosine, sine, magnitude = F(4, 5), F(3, 5), F(7, 4)
    q_left = diagonal(4, {0})
    q_left_prime = [
        [cosine * cosine, cosine * sine, F(0), F(0)],
        [cosine * sine, sine * sine, F(0), F(0)],
        [F(0), F(0), F(0), F(0)],
        [F(0), F(0), F(0), F(0)],
    ]
    q_right = diagonal(4, {2, 3})
    y = [
        [F(0), F(0), magnitude, F(0)],
        [F(0), F(0), F(0), magnitude],
        [F(0), F(0), F(0), F(0)],
        [F(0), F(0), F(0), F(0)],
    ]
    delta = sub(q_left_prime, q_left)
    left_difference = mm(mm(delta, y), q_right)
    delta_sq = frobenius_squared(delta)
    left_actual_sq = frobenius_squared(left_difference)
    assert delta_sq == F(18, 25)
    assert left_actual_sq == magnitude * magnitude * delta_sq

    right_difference = transpose(left_difference)
    assert frobenius_squared(right_difference) == magnitude * magnitude * delta_sq
    return {
        "operator_axis": {
            "epsilon_frobenius": encoded(epsilon),
            "actual_difference_squared": encoded(operator_actual_sq),
            "global_bound_squared": encoded(operator_actual_sq),
            "equality": True,
        },
        "left_projector_axis": {
            "operator_norm": encoded(magnitude),
            "projector_delta_squared": encoded(delta_sq),
            "actual_difference_squared": encoded(left_actual_sq),
            "global_bound_squared": encoded(magnitude * magnitude * delta_sq),
            "equality": True,
        },
        "right_projector_axis": {
            "operator_norm": encoded(magnitude),
            "projector_delta_squared": encoded(delta_sq),
            "actual_difference_squared": encoded(frobenius_squared(right_difference)),
            "global_bound_squared": encoded(magnitude * magnitude * delta_sq),
            "equality": True,
        },
    }


def _localization_controls() -> list[dict]:
    epsilon = F(5, 3)
    rows = []
    for alpha, complement in ((F(0), F(1)), (F(3, 5), F(4, 5)), (F(1), F(0))):
        # E = epsilon |alpha e_1 + complement e_3><e_2|.
        global_sq = epsilon * epsilon * (alpha * alpha + complement * complement)
        local_sq = epsilon * epsilon * alpha * alpha
        assert global_sq == epsilon * epsilon
        rows.append(
            {
                "alpha": encoded(alpha),
                "operator_norm_squared": encoded(global_sq),
                "frobenius_norm_squared": encoded(global_sq),
                "localized_error_squared": encoded(local_sq),
                "localized_to_global_ratio_squared": encoded(alpha * alpha),
            }
        )
    return rows


def _information_lattice_controls() -> dict:
    directions = (
        (F(0), F(1)),
        (F(3, 5), F(4, 5)),
        (F(4, 5), F(3, 5)),
        (F(1), F(0)),
    )
    grid = []
    for alpha, alpha_complement in directions:
        for beta, beta_complement in directions:
            perturbation = outer(
                [alpha, alpha_complement],
                [beta, beta_complement],
            )
            assert frobenius_squared(perturbation) == 1
            local = alpha * beta
            grid.append(
                {
                    "left_coordinate": encoded(alpha),
                    "right_coordinate": encoded(beta),
                    "global_operator_norm": "1/1",
                    "global_frobenius_norm": "1/1",
                    "left_semilocal_norm": encoded(alpha),
                    "right_semilocal_norm": encoded(beta),
                    "local_norm": encoded(local),
                    "U_G": "1/1",
                    "U_L": encoded(alpha),
                    "U_R": encoded(beta),
                    "U_LR": encoded(min(alpha, beta)),
                    "U_loc": encoded(local),
                }
            )

    return {
        "hasse_edges": [
            ["I_G", "I_L"],
            ["I_G", "I_R"],
            ["I_L", "I_LR"],
            ["I_R", "I_LR"],
            ["I_LR", "I_loc"],
        ],
        "rank_one_rational_grid": grid,
        "semilocal_incomparability": {
            "E_11": {"global_2": "1/1", "global_F": "1/1", "left": "1/1", "right": "1/1", "local": "1/1"},
            "E_12": {"global_2": "1/1", "global_F": "1/1", "left": "1/1", "right": "0/1", "local": "0/1"},
            "E_21": {"global_2": "1/1", "global_F": "1/1", "left": "0/1", "right": "1/1", "local": "0/1"},
        },
        "bilateral_semilocal_nonidentifiability": {
            "identity": {"global_2": "1/1", "global_F_squared": "2/1", "left": "1/1", "right": "1/1", "local": "1/1"},
            "swap": {"global_2": "1/1", "global_F_squared": "2/1", "left": "1/1", "right": "1/1", "local": "0/1"},
        },
    }


def _margin_controls() -> dict:
    n, budget, threshold = F(1), F(1), F(1)
    inactive, active = F(0), F(2)
    assert n - budget <= threshold < n + budget
    assert abs(inactive - n) <= budget and inactive <= threshold
    assert abs(active - n) <= budget and active > threshold
    return {
        "reference_norm": encoded(n),
        "error_budget": encoded(budget),
        "threshold": encoded(threshold),
        "policy_status": "UNRESOLVED",
        "inactive_realization": {
            "perturbed_norm": encoded(inactive),
            "error_norm": encoded(abs(inactive - n)),
            "status": "INACTIVE",
        },
        "active_realization": {
            "perturbed_norm": encoded(active),
            "error_norm": encoded(abs(active - n)),
            "status": "ACTIVE",
        },
    }


def _joint_control() -> dict:
    cosine, sine, epsilon = F(4, 5), F(3, 5), F(1, 2)
    e1 = [F(1), F(0), F(0), F(0)]
    e2 = [F(0), F(1), F(0), F(0)]
    u = [cosine, F(0), sine, F(0)]
    v = [F(0), cosine, F(0), sine]
    q_i, q_i_prime = outer(e1, e1), outer(u, u)
    q_j, q_j_prime = outer(e2, e2), outer(v, v)
    operator = outer(e1, e2)
    delta_i, delta_j = sub(q_i_prime, q_i), sub(q_j_prime, q_j)
    final_reference = mm(mm(q_i_prime, operator), q_j_prime)
    initial_reference = mm(mm(q_i, operator), q_j)
    carrier_error = sub(final_reference, initial_reference)
    carrier_parallel = mm(mm(q_i_prime, carrier_error), q_j_prime)
    left_term = mm(mm(delta_i, operator), q_j_prime)
    right_term = mm(mm(q_i, operator), delta_j)
    additive_completion = scale(epsilon, outer(u, v))
    completed_error = sub(carrier_error, scale(F(-1), additive_completion))

    carrier_error_sq = frobenius_squared(carrier_error)
    exact_supremum_sq = frobenius_squared(completed_error)
    left_norm = cosine * sine
    right_norm = sine
    localized_sum = left_norm + right_norm + epsilon
    assert frobenius_squared(carrier_parallel) == 0
    assert frobenius_squared(delta_i) == F(2) * sine**2
    assert frobenius_squared(delta_j) == F(2) * sine**2
    assert frobenius_squared(left_term) == left_norm**2
    assert frobenius_squared(right_term) == right_norm**2
    assert carrier_error_sq == F(369, 625)
    assert exact_supremum_sq == F(2101, 2500)
    assert exact_supremum_sq < localized_sum**2
    # b_glob > b_loc follows from 2 sqrt(2) > 1+c; squaring is exact here.
    assert F(8) > (F(1) + cosine) ** 2
    return {
        "cosine": encoded(cosine),
        "sine": encoded(sine),
        "epsilon_frobenius": encoded(epsilon),
        "left_projector_delta_squared": encoded(F(2) * sine**2),
        "right_projector_delta_squared": encoded(F(2) * sine**2),
        "carrier_error_parallel_squared": "0/1",
        "carrier_error_perpendicular_squared": encoded(carrier_error_sq),
        "left_localized_term_squared": encoded(frobenius_squared(left_term)),
        "right_localized_term_squared": encoded(frobenius_squared(right_term)),
        "exact_additive_supremum_squared": encoded(exact_supremum_sq),
        "localized_three_term_sum": encoded(localized_sum),
        "localized_sum_squared": encoded(localized_sum**2),
        "global_sum": "6*sqrt(2)/5+1/2",
        "strictly_below_localized_sum": True,
        "strictly_below_global_sum": True,
    }


def _localized_equality_control() -> dict:
    e1 = [F(1), F(0), F(0)]
    e2 = [F(0), F(1), F(0)]
    e3 = [F(0), F(0), F(1)]
    q_i, q_i_prime = outer(e1, e1), outer(e2, e2)
    q_j = outer(e3, e3)
    operator = outer(e2, e3)
    error = outer(e2, e3)
    left = mm(mm(sub(q_i_prime, q_i), operator), q_j)
    middle = mm(mm(q_i_prime, error), q_j)
    right = [[F(0) for _ in range(3)] for _ in range(3)]
    actual = sub(sub(left, scale(F(-1), middle)), scale(F(-1), right))
    assert frobenius_squared(left) == 1
    assert frobenius_squared(middle) == 1
    assert frobenius_squared(right) == 0
    assert frobenius_squared(actual) == 4
    return {
        "dimension": 3,
        "left_term_squared": "1/1",
        "additive_term_squared": "1/1",
        "right_term_squared": "0/1",
        "actual_difference_squared": "4/1",
        "localized_bound": "2/1",
        "equality": True,
        "active_term_count": 2,
    }


def build_payload() -> dict:
    payload = {
        "schema": "rime.paper25.diagnostic-sharpness-certificate.v1",
        "artifact_id": "PAPER25-DIAGNOSTIC-SHARPNESS-V1",
        "evidence_layer": "EXACT_INTEGER_FRACTION_CERTIFICATE",
        "claim_status": "EXACT_FINITE_CERTIFICATE",
        "paper_evidence_status": "REGISTERED_THEOREM_SUPPORT_NOT_PROOF",
        "arithmetic": "fractions.Fraction exact rational arithmetic",
        "frozen_protocol": {
            "integer_backend": "Python int",
            "rational_backend": "fractions.Fraction",
            "floating_point": False,
            "norms": {
                "primary": "exact Frobenius norm via squared entries",
                "operator_norm": "exact witness identities; squared values recorded",
            },
            "threshold_policy": {
                "reference_norm": "1/1",
                "error_radius": "1/1",
                "threshold": "1/1",
                "unresolved": "n-b <= tau < n+b",
            },
            "zero_policy": {
                "exact_zero": "literal Fraction(0)",
                "near_zero": "not applicable; no tolerance substitution",
            },
            "numerical_environment": {
                "python": "3.13.0",
                "encoding": "UTF-8",
                "line_endings": "LF",
            },
        },
        "claim_surface": [
            "Theorem 3.3",
            "Theorem 3.4",
            "Definition 3.6",
            "Theorem 3.7",
            "Theorem 3.8",
            "Corollary 3.9",
            "Theorem 3.10",
            "Theorem 4.2",
        ],
        "one_axis_sharpness": _axis_controls(),
        "fixed_global_data_localization_family": _localization_controls(),
        "carrier_information_lattice": _information_lattice_controls(),
        "three_axis_joint_strictness": _joint_control(),
        "localized_triangle_equality": _localized_equality_control(),
        "unresolved_two_sided_realization": _margin_controls(),
        "source_artifacts": [
            {
                "path": path.as_posix(),
                "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            }
            for path in SOURCE_PATHS
        ],
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"WROTE {RESULT}")


if __name__ == "__main__":
    main()
