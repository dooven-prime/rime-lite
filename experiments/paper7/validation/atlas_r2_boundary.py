"""Paper VII v2: finite full-array low-order Lie atlas audit.

This audit groups systems only when their complete generator-indexed R1^Lie
and complete commutator-indexed R2^Lie arrays agree.  It then compares the
complete cutoff D_Lie arrays, not only D_max or a frozen count.

Agreement in this finite atlas is a computational observation.  It is not a
promotion theorem from low-order support to exact Lie depth.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import hashlib
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rime.accessibility import AccessibilityEngine


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
JSON_PATH = RESULTS_DIR / "full_array_lie_atlas.json"
TEXT_PATH = RESULTS_DIR / "full_array_lie_atlas.txt"

SYSTEM_COUNT = 80
SECTOR_DIMENSION = 2
SECTOR_COUNT = 4
OPERATOR_COUNT = 3
MAX_DEPTH = 12
TOLERANCES = (1e-9, 1e-8, 1e-7)


MASK_FAMILIES = (
    (
        ((0, 1), (1, 2)),
        ((2, 3),),
        ((0, 3),),
    ),
    (
        ((0, 1), (2, 3)),
        ((1, 2),),
        ((0, 3),),
    ),
    (
        ((0, 1),),
        ((1, 2),),
        ((2, 3),),
    ),
    (
        ((0, 1), (1, 2), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3),),
    ),
)


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_sha256(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    header = f"{contiguous.dtype}|{contiguous.shape}|".encode("ascii")
    return hashlib.sha256(header + contiguous.tobytes()).hexdigest()


def build_system(seed: int) -> tuple[list[np.ndarray], list[np.ndarray], int]:
    rng = np.random.default_rng(seed)
    dim = SECTOR_DIMENSION * SECTOR_COUNT
    identity = np.eye(dim, dtype=complex)
    Vs = [
        identity[
            :,
            i * SECTOR_DIMENSION : (i + 1) * SECTOR_DIMENSION,
        ]
        for i in range(SECTOR_COUNT)
    ]

    family_index = seed % len(MASK_FAMILIES)
    family = MASK_FAMILIES[family_index]
    Xs = []
    for edges in family:
        X = np.zeros((dim, dim), dtype=complex)
        for i, j in edges:
            block = (
                rng.standard_normal((SECTOR_DIMENSION, SECTOR_DIMENSION))
                + 1j
                * rng.standard_normal((SECTOR_DIMENSION, SECTOR_DIMENSION))
            )
            si = slice(i * SECTOR_DIMENSION, (i + 1) * SECTOR_DIMENSION)
            sj = slice(j * SECTOR_DIMENSION, (j + 1) * SECTOR_DIMENSION)
            X[si, sj] = block
            X[sj, si] = -block.conj().T
        Xs.append(X)
    return Vs, Xs, family_index


def closure_certificate(
    Xs: list[np.ndarray],
    per_depth: list[list[np.ndarray]],
    tolerance: float,
) -> dict:
    """Audit closure of the cumulative numerical Lie basis under generators."""
    cumulative_dimensions = np.cumsum(
        [len(layer) for layer in per_depth], dtype=int
    ).tolist()
    first_empty_round = next(
        (index for index, layer in enumerate(per_depth) if not layer),
        None,
    )
    vectors = [vector for layer in per_depth for vector in layer]
    basis_matrix = np.column_stack(vectors)
    retained = np.linalg.svd(basis_matrix, compute_uv=False)
    orthonormal_basis, _ = np.linalg.qr(basis_matrix, mode="reduced")

    residual_vectors = []
    absolute_residuals = []
    relative_residuals = []
    ambient_dimension = Xs[0].shape[0]
    for X in Xs:
        for vector in vectors:
            matrix = vector.reshape(ambient_dimension, ambient_dimension)
            commutator = (X @ matrix - matrix @ X).reshape(-1)
            residual = commutator - orthonormal_basis @ (
                orthonormal_basis.conj().T @ commutator
            )
            residual_norm = float(np.linalg.norm(residual))
            commutator_norm = float(np.linalg.norm(commutator))
            residual_vectors.append(residual)
            absolute_residuals.append(residual_norm)
            relative_residuals.append(
                residual_norm / commutator_norm if commutator_norm else 0.0
            )

    residual_matrix = np.column_stack(residual_vectors)
    discarded = np.linalg.svd(residual_matrix, compute_uv=False)
    max_absolute = max(absolute_residuals, default=0.0)
    return {
        "basis_dimension": len(vectors),
        "cumulative_dimensions": cumulative_dimensions,
        "first_empty_round": first_empty_round,
        "generator_basis_commutators_checked": len(residual_vectors),
        "max_closure_residual": max_absolute,
        "max_relative_closure_residual": max(
            relative_residuals, default=0.0
        ),
        "smallest_retained_singular_value": float(retained[-1]),
        "largest_discarded_singular_value": float(discarded[0]),
        "rank_tolerance": tolerance,
        "closure_below_tolerance": (
            first_empty_round is not None and max_absolute <= tolerance
        ),
    }


def audit_at_tolerance(
    Vs: list[np.ndarray],
    Xs: list[np.ndarray],
    tolerance: float,
) -> dict:
    engine = AccessibilityEngine(
        Vs,
        Xs,
        tol=tolerance,
        max_depth=MAX_DEPTH,
        require_complete=True,
        require_skew_hermitian=True,
    )
    R1, R2, pairs = engine.support()
    D, per_depth = engine.depth()
    engine.assert_consistent()
    n = Xs[0].shape[0]
    layer_support = []
    cumulative_support = np.zeros((len(Vs), len(Vs)), dtype=bool)
    cumulative_layers = []
    for layer in per_depth:
        support = np.zeros((len(Vs), len(Vs)), dtype=bool)
        for vector in layer:
            matrix = vector.reshape(n, n)
            for i, Vi in enumerate(Vs):
                for j, Vj in enumerate(Vs):
                    if np.linalg.norm(Vi.conj().T @ matrix @ Vj, "fro") > tolerance:
                        support[i, j] = True
        layer_support.append(support)
        cumulative_support = cumulative_support | support
        cumulative_layers.append(cumulative_support.copy())
    closure = closure_certificate(Xs, per_depth, tolerance)
    return {
        "R1": R1,
        "R2": R2,
        "D": D,
        "commutator_pairs": pairs,
        "per_depth_dimensions": [len(layer) for layer in per_depth],
        "layer_support": np.asarray(layer_support, dtype=bool),
        "cumulative_support": np.asarray(cumulative_layers, dtype=bool),
        "closure": closure,
    }


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    systems = []
    raw = []

    for seed in range(SYSTEM_COUNT):
        Vs, Xs, family_index = build_system(seed)
        audits = {
            tolerance: audit_at_tolerance(Vs, Xs, tolerance)
            for tolerance in TOLERANCES
        }
        reference = audits[1e-8]
        stable = all(
            np.array_equal(audit["R1"], reference["R1"])
            and np.array_equal(audit["R2"], reference["R2"])
            and np.array_equal(audit["D"], reference["D"])
            and np.array_equal(
                audit["layer_support"], reference["layer_support"]
            )
            and np.array_equal(
                audit["cumulative_support"],
                reference["cumulative_support"],
            )
            for audit in audits.values()
        )
        record = {
            "seed": seed,
            "mask_family": family_index,
            "r1_sha256": array_sha256(reference["R1"]),
            "r2_sha256": array_sha256(reference["R2"]),
            "d_sha256": array_sha256(reference["D"]),
            "layer_support_sha256": array_sha256(
                reference["layer_support"]
            ),
            "cumulative_support_sha256": array_sha256(
                reference["cumulative_support"]
            ),
            "per_depth_dimensions": reference["per_depth_dimensions"],
            "cumulative_dimensions": reference["closure"][
                "cumulative_dimensions"
            ],
            "r1_array": reference["R1"].astype(int).tolist(),
            "r2_array": reference["R2"].astype(int).tolist(),
            "d_matrix": reference["D"].tolist(),
            "layer_support": reference["layer_support"].astype(int).tolist(),
            "cumulative_support": (
                reference["cumulative_support"].astype(int).tolist()
            ),
            "closure_certificate": reference["closure"],
            "threshold_stable": stable,
        }
        systems.append(record)
        raw.append(reference)

    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, record in enumerate(systems):
        groups[(record["r1_sha256"], record["r2_sha256"])].append(index)

    group_records = []
    disagreement_count = 0
    for (r1_hash, r2_hash), indices in sorted(groups.items()):
        reference_d = raw[indices[0]]["D"]
        full_d_equal = all(
            np.array_equal(raw[index]["D"], reference_d)
            for index in indices[1:]
        )
        reference_layer_support = raw[indices[0]]["layer_support"]
        reference_cumulative_support = raw[indices[0]]["cumulative_support"]
        full_layer_support_equal = all(
            np.array_equal(
                raw[index]["layer_support"], reference_layer_support
            )
            and np.array_equal(
                raw[index]["cumulative_support"],
                reference_cumulative_support,
            )
            for index in indices[1:]
        )
        if not full_d_equal:
            disagreement_count += 1
        group_records.append(
            {
                "r1_sha256": r1_hash,
                "r2_sha256": r2_hash,
                "member_seeds": [systems[index]["seed"] for index in indices],
                "member_count": len(indices),
                "full_d_arrays_equal": full_d_equal,
                "full_layer_support_arrays_equal": full_layer_support_equal,
                "d_sha256_values": sorted(
                    {systems[index]["d_sha256"] for index in indices}
                ),
                "per_depth_dimension_values": sorted(
                    {
                        tuple(systems[index]["per_depth_dimensions"])
                        for index in indices
                    }
                ),
                "cumulative_dimension_values": sorted(
                    {
                        tuple(systems[index]["cumulative_dimensions"])
                        for index in indices
                    }
                ),
                "mask_family_values": sorted(
                    {systems[index]["mask_family"] for index in indices}
                ),
                "first_empty_round_values": sorted(
                    {
                        systems[index]["closure_certificate"][
                            "first_empty_round"
                        ]
                        for index in indices
                    }
                ),
                "minimum_retained_singular_value": min(
                    systems[index]["closure_certificate"][
                        "smallest_retained_singular_value"
                    ]
                    for index in indices
                ),
                "maximum_discarded_singular_value": max(
                    systems[index]["closure_certificate"][
                        "largest_discarded_singular_value"
                    ]
                    for index in indices
                ),
                "maximum_closure_residual": max(
                    systems[index]["closure_certificate"][
                        "max_closure_residual"
                    ]
                    for index in indices
                ),
                "maximum_relative_closure_residual": max(
                    systems[index]["closure_certificate"][
                        "max_relative_closure_residual"
                    ]
                    for index in indices
                ),
                "rank_tolerance_values": sorted(
                    {
                        systems[index]["closure_certificate"][
                            "rank_tolerance"
                        ]
                        for index in indices
                    }
                ),
                "all_members_saturated": all(
                    systems[index]["closure_certificate"][
                        "closure_below_tolerance"
                    ]
                    for index in indices
                ),
            }
        )

    payload = {
        "schema": "paper7.full-array-lie-atlas.v2",
        "claim_scope": (
            "finite cutoff-relative array comparison; no low-order-to-depth "
            "promotion theorem"
        ),
        "system_count": SYSTEM_COUNT,
        "max_depth_levels": MAX_DEPTH,
        "depth_indices": list(range(MAX_DEPTH)),
        "unreached_encoding": 999,
        "tolerances": list(TOLERANCES),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "script_sha256": source_sha256(Path(__file__)),
        },
        "all_systems_threshold_stable": all(
            record["threshold_stable"] for record in systems
        ),
        "all_systems_closure_certified": all(
            record["closure_certificate"]["closure_below_tolerance"]
            for record in systems
        ),
        "low_order_hash_class_count": len(group_records),
        "multi_member_class_count": sum(
            record["member_count"] > 1 for record in group_records
        ),
        "full_d_disagreement_class_count": disagreement_count,
        "full_layer_support_disagreement_class_count": sum(
            not record["full_layer_support_arrays_equal"]
            for record in group_records
        ),
        "groups": group_records,
        "systems": systems,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "Paper VII v2 full-array finite Lie atlas",
        "=" * 72,
        f"systems={SYSTEM_COUNT}",
        f"low-order hash classes={len(group_records)}",
        (
            "multi-member classes="
            f"{sum(record['member_count'] > 1 for record in group_records)}"
        ),
        f"full-D disagreement classes={disagreement_count}",
        (
            "all systems threshold-stable="
            f"{payload['all_systems_threshold_stable']}"
        ),
        (
            "all systems closure-certified="
            f"{payload['all_systems_closure_certified']}"
        ),
        "",
        "This is a cutoff-relative finite observation, not a completion theorem.",
    ]
    TEXT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    print(f"\nJSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
