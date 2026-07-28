"""Paper VII v2: rank protection and projected-composition audit.

The audited local object is

    A = Q_i X_g Q_k,  B = Q_k X_h Q_j,  AB = Q_i X_g Q_k X_h Q_j.

For A: C^{d_k} -> C^{d_i} and B: C^{d_j} -> C^{d_k},
left protection means rank(A) = d_k and right protection means
rank(B) = d_k.  Maximum possible rectangular rank is not enough.

All reported classes are numerical observations at declared SVD and product
thresholds.  The exact rank-protection theorem is proved in the manuscript.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rime.cubieoperator import CubieSpectralOperator


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
JSON_PATH = RESULTS_DIR / "projected_composition_audit.json"
TEXT_PATH = RESULTS_DIR / "projected_composition_audit.txt"

SUPPORT_ATOL = 1e-8
RANK_ATOL = 1e-12
RANK_RTOL = 1e-9
PRODUCT_ATOL = 1e-12
PRODUCT_RTOL = 1e-10
RANDOM_SEEDS = [42, 43, 44, 45, 46]


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def svd_rank(matrix: np.ndarray) -> tuple[int, float, np.ndarray]:
    singular = np.linalg.svd(matrix, compute_uv=False)
    scale = float(singular[0]) if singular.size else 0.0
    cutoff = max(RANK_ATOL, RANK_RTOL * scale)
    rank = int(np.count_nonzero(singular > cutoff))
    return rank, cutoff, singular


def product_threshold(norm_a: float, norm_b: float) -> float:
    return PRODUCT_ATOL + PRODUCT_RTOL * norm_a * norm_b


def classify_pair(A: np.ndarray, B: np.ndarray) -> dict:
    di, dk = A.shape
    dk_b, dj = B.shape
    if dk_b != dk:
        raise ValueError(f"incompatible factors: {A.shape} and {B.shape}")

    norm_a = float(np.linalg.norm(A, "fro"))
    norm_b = float(np.linalg.norm(B, "fro"))
    rank_a, cutoff_a, singular_a = svd_rank(A)
    rank_b, cutoff_b, singular_b = svd_rank(B)
    left = rank_a == dk
    right = rank_b == dk

    product = A @ B
    norm_product = float(np.linalg.norm(product, "fro"))
    threshold = product_threshold(norm_a, norm_b)
    product_nonzero = norm_product > threshold

    if left and right:
        protection = "both_protected"
    elif left:
        protection = "left_only"
    elif right:
        protection = "right_only"
    elif product_nonzero:
        protection = "unprotected_nonzero"
    else:
        protection = "unprotected_zero"

    lower_left = (
        float(singular_a[dk - 1]) * norm_b if left and dk > 0 else None
    )
    lower_right = (
        float(singular_b[dk - 1]) * norm_a if right and dk > 0 else None
    )

    if (left or right) and not product_nonzero:
        raise AssertionError(
            "numerically rank-protected factors were classified with zero product"
        )

    scale = norm_a * norm_b
    _, _, vh_a = np.linalg.svd(A, full_matrices=True)
    u_b, _, _ = np.linalg.svd(B, full_matrices=True)
    image_basis = u_b[:, :rank_b]
    kernel_basis = vh_a.conj().T[:, rank_a:]
    image_kernel_action = (
        float(np.linalg.norm(A @ image_basis, "fro")) if rank_b else 0.0
    )
    if rank_b:
        if kernel_basis.shape[1]:
            outside_kernel = image_basis - kernel_basis @ (
                kernel_basis.conj().T @ image_basis
            )
            image_kernel_distance = float(
                np.linalg.norm(outside_kernel, "fro")
            )
        else:
            image_kernel_distance = float(np.sqrt(rank_b))
    else:
        image_kernel_distance = 0.0
    return {
        "di": di,
        "dk": dk,
        "dj": dj,
        "rank_a": rank_a,
        "rank_b": rank_b,
        "rank_cutoff_a": cutoff_a,
        "rank_cutoff_b": cutoff_b,
        "sigma_min_positive_a": (
            float(singular_a[rank_a - 1]) if rank_a else 0.0
        ),
        "sigma_min_positive_b": (
            float(singular_b[rank_b - 1]) if rank_b else 0.0
        ),
        "left_protected": left,
        "right_protected": right,
        "protection_class": protection,
        "norm_a": norm_a,
        "norm_b": norm_b,
        "norm_product": norm_product,
        "relative_product_norm": norm_product / scale if scale else 0.0,
        "image_kernel_action_norm": image_kernel_action,
        "image_kernel_distance": image_kernel_distance,
        "product_threshold": threshold,
        "product_nonzero": product_nonzero,
        "left_lower_bound": lower_left,
        "right_lower_bound": lower_right,
    }


def precompute_blocks(Vs: list[np.ndarray], Xs: list[np.ndarray]) -> list:
    return [
        [[Vi.conj().T @ X @ Vj for Vj in Vs] for Vi in Vs]
        for X in Xs
    ]


def audit_routes(
    name: str,
    Vs: list[np.ndarray],
    Xs: list[np.ndarray],
) -> dict:
    dims = [int(V.shape[1]) for V in Vs]
    blocks = precompute_blocks(Vs, Xs)
    counts: Counter[str] = Counter()
    zero_witnesses = []
    protected_margin_ratios = []

    for i in range(len(Vs)):
        for k in range(len(Vs)):
            if i == k:
                continue
            for j in range(len(Vs)):
                if k == j:
                    continue
                for g in range(len(Xs)):
                    A = blocks[g][i][k]
                    if np.linalg.norm(A, "fro") <= SUPPORT_ATOL:
                        continue
                    for h in range(len(Xs)):
                        B = blocks[h][k][j]
                        if np.linalg.norm(B, "fro") <= SUPPORT_ATOL:
                            continue
                        record = classify_pair(A, B)
                        counts["total"] += 1
                        counts[record["protection_class"]] += 1
                        if record["left_protected"]:
                            counts["left_protected"] += 1
                        if record["right_protected"]:
                            counts["right_protected"] += 1
                        if record["product_nonzero"]:
                            counts["product_nonzero"] += 1
                        else:
                            counts["product_zero"] += 1

                        bounds = [
                            value
                            for value in (
                                record["left_lower_bound"],
                                record["right_lower_bound"],
                            )
                            if value is not None and value > 0
                        ]
                        if bounds:
                            protected_margin_ratios.append(
                                record["norm_product"] / max(bounds)
                            )

                        if not record["product_nonzero"]:
                            zero_witnesses.append(
                                {
                                    "i": i,
                                    "k": k,
                                    "j": j,
                                    "g": g,
                                    "h": h,
                                    **record,
                                }
                            )

    return {
        "name": name,
        "ambient_dimension": int(Vs[0].shape[0]),
        "sector_dimensions": dims,
        "operator_count": len(Xs),
        "counts": dict(sorted(counts.items())),
        "minimum_protected_margin_ratio": (
            float(min(protected_margin_ratios))
            if protected_margin_ratios
            else None
        ),
        "zero_witnesses": zero_witnesses,
    }


def make_rubik() -> tuple[list[np.ndarray], list[np.ndarray], dict]:
    op = CubieSpectralOperator()
    decomp = op.center_decomposition()
    Vs = [np.asarray(V, dtype=complex) for V in decomp["sector_bases"]]
    move_keys = [tuple(map(int, key)) for key in op.rho_moves.keys()]
    Xs = []
    for rho in op.rho_matrices():
        rho = np.asarray(rho, dtype=complex)
        Xs.append((rho - rho.conj().T) / 2.0)
    norms = [float(np.linalg.norm(X, "fro")) for X in Xs]
    zero_indices = [
        index for index, norm in enumerate(norms) if norm <= SUPPORT_ATOL
    ]
    half_turn_indices = [
        index for index, key in enumerate(move_keys) if key[2] == 2
    ]
    if zero_indices != half_turn_indices:
        raise AssertionError(
            "anti-Hermitian zero operators do not match the half turns"
        )
    registration = {
        "definition": "X_g=(rho(g)-rho(g)^*)/2",
        "operator_count": len(Xs),
        "nonzero_operator_count": len(Xs) - len(zero_indices),
        "zero_operator_count": len(zero_indices),
        "zero_operator_indices": zero_indices,
        "half_turn_indices": half_turn_indices,
        "half_turn_move_keys": [list(move_keys[index]) for index in zero_indices],
        "maximum_zero_operator_norm": max(
            (norms[index] for index in zero_indices), default=0.0
        ),
        "minimum_nonzero_operator_norm": min(
            norm for norm in norms if norm > SUPPORT_ATOL
        ),
    }
    return Vs, Xs, registration


def make_random(
    seed: int,
    *,
    dim: int = 12,
    n_sectors: int = 4,
    n_operators: int = 3,
    deficient_fraction: float = 0.0,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    rng = np.random.default_rng(seed)
    unitary, _ = np.linalg.qr(
        rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    )
    sizes = [
        dim // n_sectors + (1 if i < dim % n_sectors else 0)
        for i in range(n_sectors)
    ]
    offsets = np.cumsum([0] + sizes)
    Vs = [unitary[:, offsets[i] : offsets[i + 1]] for i in range(n_sectors)]

    Xs = []
    for _ in range(n_operators):
        block_matrix = np.zeros((dim, dim), dtype=complex)
        for i in range(n_sectors):
            for j in range(i + 1, n_sectors):
                di, dj = sizes[i], sizes[j]
                block = (
                    rng.standard_normal((di, dj))
                    + 1j * rng.standard_normal((di, dj))
                ) / np.sqrt(di * dj)
                if (
                    rng.random() < deficient_fraction
                    and min(di, dj) >= 2
                ):
                    u, singular, vh = np.linalg.svd(block, full_matrices=False)
                    target_rank = max(1, min(di, dj) // 2)
                    block = (
                        (u[:, :target_rank] * singular[:target_rank])
                        @ vh[:target_rank, :]
                    )
                a, b = offsets[i], offsets[j]
                block_matrix[a : a + di, b : b + dj] = block
                block_matrix[b : b + dj, a : a + di] = -block.conj().T
        Xs.append(unitary @ block_matrix @ unitary.conj().T)
    return Vs, Xs


def exact_examples() -> list[dict]:
    examples = {
        "both_protected": (
            np.eye(2),
            np.array([[1, 2], [3, 4]], dtype=float),
        ),
        "left_only": (
            np.array([[1, 0], [0, 1], [1, 1]], dtype=float),
            np.array([[1], [2]], dtype=float),
        ),
        "right_only": (
            np.array([[1, 2]], dtype=float),
            np.array([[1, 0, 1], [0, 1, 1]], dtype=float),
        ),
        "unprotected_nonzero": (
            np.array([[1, 0], [0, 0]], dtype=float),
            np.array([[1, 0], [0, 0]], dtype=float),
        ),
        "unprotected_zero": (
            np.array([[1, 0], [0, 0]], dtype=float),
            np.array([[0, 0], [1, 0]], dtype=float),
        ),
    }
    records = []
    for expected, (A, B) in examples.items():
        record = classify_pair(A.astype(complex), B.astype(complex))
        if record["protection_class"] != expected:
            raise AssertionError(
                f"{expected}: got {record['protection_class']}"
            )
        records.append(
            {
                "name": expected,
                "a": A.astype(int).tolist(),
                "b": B.astype(int).tolist(),
                **record,
            }
        )
    return records


def perturbation_audit() -> list[dict]:
    rows = []
    for d in (2, 3, 4):
        rng = np.random.default_rng(42)
        A = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
        A[:, -1] = 0
        B = np.zeros((d, d), dtype=complex)
        B[-1, :] = (
            rng.standard_normal(d) + 1j * rng.standard_normal(d)
        )
        if np.linalg.norm(A @ B, "fro") != 0:
            raise AssertionError("constructed incidence pair is not exact zero")
        for epsilon in (1e-6, 1e-4, 1e-2):
            broken = 0
            for _ in range(100):
                noise = (
                    rng.standard_normal((d, d))
                    + 1j * rng.standard_normal((d, d))
                )
                noise /= np.linalg.norm(noise, "fro")
                if np.linalg.norm((A + epsilon * noise) @ B, "fro") > 1e-10:
                    broken += 1
            rows.append(
                {
                    "dimension": d,
                    "epsilon": epsilon,
                    "broken": broken,
                    "trials": 100,
                }
            )
    return rows


def random_pair_sanity() -> list[dict]:
    rows = []
    for d in (2, 3, 4, 5):
        rng = np.random.default_rng(42)
        trials = 100_000
        relative_norms = np.empty(trials, dtype=float)
        for _ in range(trials):
            A = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
            B = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
            norm_a = np.linalg.norm(A, "fro")
            norm_b = np.linalg.norm(B, "fro")
            relative_norms[_] = np.linalg.norm(A @ B, "fro") / (
                norm_a * norm_b
            )
        rows.append(
            {
                "dimension": d,
                "trials": trials,
                "minimum_relative_product_norm": float(relative_norms.min()),
                "relative_product_norm_quantiles": {
                    "q_0.001": float(np.quantile(relative_norms, 0.001)),
                    "q_0.01": float(np.quantile(relative_norms, 0.01)),
                    "q_0.5": float(np.quantile(relative_norms, 0.5)),
                },
                "threshold_sweep_hits": {
                    "1e-8": int(np.count_nonzero(relative_norms <= 1e-8)),
                    "1e-10": int(np.count_nonzero(relative_norms <= 1e-10)),
                    "1e-12": int(np.count_nonzero(relative_norms <= 1e-12)),
                },
            }
        )
    return rows


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rubik_vs, rubik_xs, rubik_registration = make_rubik()
    rubik_record = audit_routes("rubik", rubik_vs, rubik_xs)
    rubik_record["operator_registration"] = rubik_registration
    systems = [rubik_record]
    for seed in RANDOM_SEEDS:
        Vs, Xs = make_random(seed)
        systems.append(audit_routes(f"random_seed_{seed}", Vs, Xs))
    for seed in RANDOM_SEEDS:
        Vs, Xs = make_random(seed, deficient_fraction=0.8)
        systems.append(
            audit_routes(f"rank_deficient_seed_{seed}", Vs, Xs)
        )

    payload = {
        "schema": "paper7.projected-composition-audit.v2",
        "claim_scope": (
            "finite numerical routed-product observations; not a word, "
            "commutator, Lie-depth, or generic-completion certificate"
        ),
        "thresholds": {
            "support_atol": SUPPORT_ATOL,
            "rank_atol": RANK_ATOL,
            "rank_rtol": RANK_RTOL,
            "product_atol": PRODUCT_ATOL,
            "product_rtol": PRODUCT_RTOL,
            "norm": "Frobenius",
            "image_kernel_distance": (
                "||(I-P_ker(A)) U_B||_F for an orthonormal basis U_B of im(B)"
            ),
            "image_kernel_distance_normalized": False,
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "script_sha256": source_sha256(Path(__file__)),
        },
        "exact_integer_examples": exact_examples(),
        "perturbation_audit": perturbation_audit(),
        "random_pair_sanity": random_pair_sanity(),
        "systems": systems,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "Paper VII v2 projected-composition audit",
        "=" * 72,
        f"support_atol={SUPPORT_ATOL:g}",
        f"rank cutoff=max({RANK_ATOL:g}, {RANK_RTOL:g}*sigma_max)",
        (
            f"product cutoff={PRODUCT_ATOL:g} + "
            f"{PRODUCT_RTOL:g}*||A||_F*||B||_F"
        ),
        "",
        (
            "rubik operator registration: "
            f"{rubik_registration['nonzero_operator_count']} nonzero, "
            f"{rubik_registration['zero_operator_count']} half-turn zeros"
        ),
        "",
    ]
    for system in systems:
        counts = system["counts"]
        lines.append(
            f"{system['name']}: total={counts.get('total', 0)}, "
            f"both={counts.get('both_protected', 0)}, "
            f"left-only={counts.get('left_only', 0)}, "
            f"right-only={counts.get('right_only', 0)}, "
            f"unprotected-nonzero={counts.get('unprotected_nonzero', 0)}, "
            f"unprotected-zero={counts.get('unprotected_zero', 0)}"
        )
    lines.extend(
        [
            "",
            "The audit classifies routed products only.",
            "It does not promote routes to full words, commutators, or Lie depth.",
        ]
    )
    TEXT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nJSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
