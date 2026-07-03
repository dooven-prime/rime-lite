"""Shared Paper VI utilities for generator-set spectral phase experiments.

The functions here intentionally stabilize the experimental vocabulary used by
the Paper VI support scripts. They report computational observations only.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from rime.cubie import CubieMove
from rime.helpers import is_in_qsqrt5, is_rational_form
from rime.spectral_utils import joint_diag_sectors


TOL_COMM = 1e-10
TOL_CLUSTER = 1e-8
RATIONAL_DENOM_MAX = 36

EXPECTED_SINGLE_DELETIONS = {
    "total": 18,
    "cq_blocked": 18,
    "a_layer_counts": {14: 6, 21: 12},
    "a_field_counts": {"mixed": 18},
}

EXPECTED_SELECTED_FAMILIES = {
    "n=18 full": {
        "cq_status": "defined",
        "cq_layers": 6,
        "cq_field": "Q",
        "a_layers": 6,
        "a_field": "Q",
    },
    "n=16 drop axis-0 HT": {
        "cq_status": "blocked",
        "cq_layers": None,
        "cq_field": "undefined",
        "a_layers": 9,
        "a_field": "mixed",
    },
    "n=15 drop negative-face HT": {
        "cq_status": "blocked",
        "cq_layers": None,
        "cq_field": "undefined",
        "a_layers": 23,
        "a_field": "mixed",
    },
    "n=14 drop axis-1 QT": {
        "cq_status": "defined",
        "cq_layers": 10,
        "cq_field": "mixed",
        "a_layers": 8,
        "a_field": "mixed",
    },
    "n=12 QT only": {
        "cq_status": "defined",
        "cq_layers": 6,
        "cq_field": "Q",
        "a_layers": 6,
        "a_field": "Q",
    },
    "n=6 HT only": {
        "cq_status": "defined",
        "cq_layers": 3,
        "cq_field": "Q",
        "a_layers": 3,
        "a_field": "Q",
    },
}

EXPECTED_AXIS0_HT_SCAN_11 = {
    "grid": 11,
    "total": 121,
    "cq_commutative": 1,
    "cq_layers": {6: 1},
    "a_layers": {6: 1, 9: 1, 10: 9, 14: 20, 15: 90},
}


def prim_data() -> tuple[list[tuple[int, int, int]], list[np.ndarray]]:
    keys = list(CubieMove.prim_moves.keys())
    rhos = [CubieMove.prim_moves[key].rho().astype(np.complex128) for key in keys]
    return keys, rhos


def move_label(key: tuple[int, int, int]) -> str:
    return CubieMove.move_label(key)


def weighted_average(mats: list[np.ndarray], weights: list[float]) -> np.ndarray:
    total = float(sum(weights))
    if total <= 1e-12:
        return np.zeros_like(mats[0], dtype=np.complex128)
    return sum(w * mat for w, mat in zip(weights, mats)) / total


def qt_ht_ops(
    keys: list[tuple[int, int, int]],
    rhos: list[np.ndarray],
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    qt = [i for i, key in enumerate(keys) if key[2] != 2]
    ht = [i for i, key in enumerate(keys) if key[2] == 2]
    qt_op = weighted_average([rhos[i] for i in qt], [float(weights[i]) for i in qt])
    ht_op = weighted_average([rhos[i] for i in ht], [float(weights[i]) for i in ht])
    return qt_op, ht_op


def commutator_norm(qt: np.ndarray, ht: np.ndarray) -> float:
    return float(np.linalg.norm(qt @ ht - ht @ qt, ord="fro"))


def commutator_matrix(
    keys: list[tuple[int, int, int]],
    rhos: list[np.ndarray],
    weights: np.ndarray,
) -> np.ndarray:
    qt, ht = qt_ht_ops(keys, rhos, weights)
    return qt @ ht - ht @ qt


def numerical_rank(mat: np.ndarray, tol: float = 1e-10) -> int:
    s = np.linalg.svd(mat, compute_uv=False)
    if len(s) == 0:
        return 0
    return int(np.sum(s > tol * max(s[0], 1.0)))


def cluster_values(values: np.ndarray, tol: float = TOL_CLUSTER) -> list[tuple[float, int]]:
    ordered = sorted((float(v.real) for v in values), reverse=True)
    if not ordered:
        return []

    clusters: list[list[float]] = []
    current = [ordered[0]]
    center = ordered[0]
    for value in ordered[1:]:
        if abs(value - center) < tol:
            current.append(value)
        else:
            clusters.append(current)
            current = [value]
            center = value
    clusters.append(current)
    return [(float(np.mean(group)), len(group)) for group in clusters]


def _is_rational(value: float) -> bool:
    return any(is_rational_form(value, denom, tol=1e-5) for denom in range(1, RATIONAL_DENOM_MAX + 1))


def classify_field(values: list[float]) -> str:
    """Classify a finite real spectrum as Q, Q(sqrt5), or mixed.

    Mixed means that rational layers and non-rational Q(sqrt5) layers occur in
    the same sampled spectrum, or that the finite small-integer detector cannot
    resolve all non-rational layers into one pure quadratic field. This
    convention matches the Paper VI experimental tables: the stable distinction
    is Q-only versus non-Q phase.
    """

    if not values:
        return "degenerate"

    rational_flags = [_is_rational(value) for value in values]
    if all(rational_flags):
        return "Q"

    non_rational = [value for value, rational in zip(values, rational_flags) if not rational]
    if all(is_in_qsqrt5(value, tol=1e-5)[0] for value in non_rational):
        return "mixed" if any(rational_flags) else "Q(sqrt5)"
    return "mixed"


def analyze_a_spectrum(rhos: list[np.ndarray], weights: np.ndarray) -> dict[str, Any]:
    positive = [i for i, weight in enumerate(weights) if weight > 1e-12]
    if not positive:
        return {"layers": 0, "field": "degenerate", "dims": []}
    a_op = weighted_average([rhos[i] for i in positive], [float(weights[i]) for i in positive])
    a_op = (a_op + a_op.conj().T) / 2
    clusters = cluster_values(np.linalg.eigvalsh(a_op))
    values = [value for value, _ in clusters]
    return {
        "layers": len(clusters),
        "field": classify_field(values),
        "dims": [dim for _, dim in clusters],
    }


def analyze_collision_quotient(
    keys: list[tuple[int, int, int]],
    rhos: list[np.ndarray],
    weights: np.ndarray,
    alpha: float = 2.0 / 3.0,
) -> dict[str, Any]:
    qt, ht = qt_ht_ops(keys, rhos, weights)
    norm = commutator_norm(qt, ht)
    if norm > TOL_COMM:
        return {
            "commutes": False,
            "comm_norm": norm,
            "sectors": None,
            "layers": None,
            "field": "undefined",
        }

    sectors = joint_diag_sectors([qt, ht], tol=TOL_CLUSTER)
    branch_values = [alpha * q + (1 - alpha) * h for (q, h), _ in sectors]
    clusters = cluster_values(np.array(branch_values), tol=TOL_CLUSTER)
    return {
        "commutes": True,
        "comm_norm": norm,
        "sectors": len(sectors),
        "layers": len(clusters),
        "field": classify_field([value for value, _ in clusters]),
    }


def deletion_weights(keys: list[tuple[int, int, int]], removed: set[tuple[int, int, int]]) -> np.ndarray:
    return np.array([0.0 if key in removed else 1.0 for key in keys], dtype=float)


def selected_family_weights(keys: list[tuple[int, int, int]]) -> list[tuple[str, np.ndarray]]:
    return [
        ("n=18 full", deletion_weights(keys, set())),
        ("n=16 drop axis-0 HT", deletion_weights(keys, {key for key in keys if key[0] == 0 and key[2] == 2})),
        (
            "n=15 drop negative-face HT",
            deletion_weights(keys, {key for key in keys if key[1] == -1 and key[2] == 2}),
        ),
        ("n=14 drop axis-1 QT", deletion_weights(keys, {key for key in keys if key[0] == 1 and key[2] != 2})),
        ("n=12 QT only", deletion_weights(keys, {key for key in keys if key[2] == 2})),
        ("n=6 HT only", deletion_weights(keys, {key for key in keys if key[2] != 2})),
    ]


def single_deletion_rows(keys: list[tuple[int, int, int]], rhos: list[np.ndarray]) -> list[dict[str, Any]]:
    rows = []
    for idx, key in enumerate(keys):
        weights = np.ones(len(keys))
        weights[idx] = 0.0
        cq = analyze_collision_quotient(keys, rhos, weights)
        a_spec = analyze_a_spectrum(rhos, weights)
        rows.append(
            {
                "label": move_label(key),
                "key": key,
                "cq_status": "defined" if cq["commutes"] else "blocked",
                "comm_norm": cq["comm_norm"],
                "a_layers": a_spec["layers"],
                "a_field": a_spec["field"],
            }
        )
    return rows


def selected_family_rows(keys: list[tuple[int, int, int]], rhos: list[np.ndarray]) -> list[dict[str, Any]]:
    rows = []
    for name, weights in selected_family_weights(keys):
        cq = analyze_collision_quotient(keys, rhos, weights)
        a_spec = analyze_a_spectrum(rhos, weights)
        rows.append(
            {
                "family": name,
                "cq_status": "defined" if cq["commutes"] else "blocked",
                "cq_layers": cq["layers"],
                "cq_field": cq["field"],
                "a_layers": a_spec["layers"],
                "a_field": a_spec["field"],
            }
        )
    return rows


def scan_axis0_ht_plane(
    keys: list[tuple[int, int, int]],
    rhos: list[np.ndarray],
    grid: int = 11,
) -> dict[str, Any]:
    axis0_ht = [i for i, key in enumerate(keys) if key[0] == 0 and key[2] == 2]
    assert len(axis0_ht) == 2

    cq_commutative = 0
    cq_layers: Counter[int] = Counter()
    a_layers: Counter[int] = Counter()

    for gi in range(grid):
        for gj in range(grid):
            weights = np.ones(len(keys))
            weights[axis0_ht[0]] = gi / (grid - 1)
            weights[axis0_ht[1]] = gj / (grid - 1)
            cq = analyze_collision_quotient(keys, rhos, weights)
            a_spec = analyze_a_spectrum(rhos, weights)
            if cq["commutes"]:
                cq_commutative += 1
                cq_layers[cq["layers"]] += 1
            a_layers[a_spec["layers"]] += 1

    return {
        "grid": grid,
        "total": grid * grid,
        "cq_commutative": cq_commutative,
        "cq_layers": dict(sorted(cq_layers.items())),
        "a_layers": dict(sorted(a_layers.items())),
    }


def summarize_single_deletions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(rows),
        "cq_blocked": sum(1 for row in rows if row["cq_status"] == "blocked"),
        "a_layer_counts": dict(sorted(Counter(row["a_layers"] for row in rows).items())),
        "a_field_counts": dict(sorted(Counter(row["a_field"] for row in rows).items())),
    }


def assert_stable_snapshot(
    single_summary: dict[str, Any],
    family_rows: list[dict[str, Any]],
    plane_summary: dict[str, Any],
) -> None:
    assert single_summary == EXPECTED_SINGLE_DELETIONS, single_summary

    observed_families = {row["family"]: {k: row[k] for k in EXPECTED_SELECTED_FAMILIES[row["family"]]} for row in family_rows}
    assert observed_families == EXPECTED_SELECTED_FAMILIES, observed_families

    assert plane_summary == EXPECTED_AXIS0_HT_SCAN_11, plane_summary
