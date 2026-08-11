"""Inherited word/Lie identities and Paper XIII aligned F4 observations."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import numpy as np

from rime.accessibility import compute_length_two_support


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "archive" / "results"


def one_hot_sectors(dim: int) -> list[np.ndarray]:
    eye = np.eye(dim, dtype=complex)
    return [eye[:, [index]] for index in range(dim)]


def block_norm(
    sectors: list[np.ndarray], matrix: np.ndarray, i: int, j: int
) -> float:
    return float(np.linalg.norm(sectors[i].conj().T @ matrix @ sectors[j], "fro"))


def aggregate_lie_support(
    sectors: list[np.ndarray], observables: list[np.ndarray], tol: float
) -> np.ndarray:
    support = np.zeros((len(sectors), len(sectors)), dtype=bool)
    for a in range(len(observables)):
        for b in range(a + 1, len(observables)):
            commutator = observables[a] @ observables[b] - observables[b] @ observables[a]
            for i, j in product(range(len(sectors)), repeat=2):
                if i != j and block_norm(sectors, commutator, i, j) > tol:
                    support[i, j] = True
    return support


def check_exact_support_lemma(seed: int = 13, trials: int = 50) -> bool:
    """Verify the quantitative block inequality behind exact support inclusion."""

    rng = np.random.default_rng(seed)
    for _ in range(trials):
        dim = int(rng.integers(3, 8))
        sectors = one_hot_sectors(dim)
        a = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
        b = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
        ab = a @ b
        ba = b @ a
        commutator = ab - ba
        for i, j in product(range(dim), repeat=2):
            if i == j:
                continue
            comm_norm = block_norm(sectors, commutator, i, j)
            word_bound = block_norm(sectors, ab, i, j) + block_norm(sectors, ba, i, j)
            if comm_norm > word_bound + 1e-10:
                return False
    return True


def check_threshold_caveat(tol: float = 1e-4) -> bool:
    """Construct word blocks below tol whose commutator block exceeds tol."""

    sectors = one_hot_sectors(3)
    scale = np.sqrt(0.75 * tol)
    a = np.zeros((3, 3), dtype=complex)
    b = np.zeros((3, 3), dtype=complex)
    a[2, 1] = scale
    a[1, 0] = -scale
    b[2, 1] = scale
    b[1, 0] = scale

    word = compute_length_two_support(sectors, [a, b], tol=tol)
    lie = aggregate_lie_support(sectors, [a, b], tol=tol)
    return not bool(word[2, 0]) and bool(lie[2, 0])


def check_strict_word_only_witness(tol: float = 1e-10) -> bool:
    """Single-generator chain: X^2 reaches 0->2 while [X,X] is zero."""

    sectors = one_hot_sectors(3)
    x = np.zeros((3, 3), dtype=complex)
    x[1, 0] = 0.5
    x[0, 1] = -0.5
    x[2, 1] = 0.5
    x[1, 2] = -0.5

    word = compute_length_two_support(sectors, [x], tol=tol)
    lie = aggregate_lie_support(sectors, [x], tol=tol)
    return bool(word[2, 0]) and not bool(lie[2, 0])


def _artifact_counts(stem: str) -> tuple[int, int, int]:
    artifact = json.loads((RESULTS / f"{stem}.sofaudit").read_text(encoding="utf-8"))
    signature = artifact["signature"]
    return (
        int(signature["support_mismatch"]["total_mismatch"]),
        int(signature["bridge_word_mismatch"]["total_mismatch"]),
        int(signature["bridge_lie_mismatch"]["total_mismatch"]),
    )


def check_domain_f4_controls() -> bool:
    """Assert the released Compiler/GridWorld channel-specific controls."""

    compiler = _artifact_counts("compiler_f4")
    gridworld = _artifact_counts("gridworld_f4")
    return compiler == (0, 0, 4) and gridworld == (0, 0, 8)


def run_checks() -> dict[str, bool]:
    return {
        "exact_support_lemma": check_exact_support_lemma(),
        "finite_threshold_caveat": check_threshold_caveat(),
        "strict_word_only_witness": check_strict_word_only_witness(),
        "domain_f4_controls": check_domain_f4_controls(),
    }


def main() -> None:
    checks = run_checks()
    print("Paper VIII identity controls and Paper XIII aligned F4 observations")
    for name, passed in checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
