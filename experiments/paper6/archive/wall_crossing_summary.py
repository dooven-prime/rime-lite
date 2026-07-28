"""Paper VI support script: compact accessibility wall-crossing table.

Status: computational theorem-support table for the Paper VI accessibility
layer.

The script condenses the synchronized Type III/IV demonstrations to the table
used by the manuscript:

    wall type | system | R1 preserved | R2/D change | escape fraction

The script is self-contained. Longer exploratory demos and Type IV searches
belong in ``experiments/paper6/archive``.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Callable

import numpy as np


sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from rime.accessibility import accessibility_signature  # noqa: E402
from rime.rep_utils import build_system_from_perms, symmetric_group  # noqa: E402


np.random.seed(42)

OUT_DIR = os.path.join(REPO_ROOT, "data")
LOG_PATH = os.path.join(OUT_DIR, "_paper6_wall_crossing_summary.txt")
TOL = 1e-8


@dataclass(frozen=True)
class SummaryRow:
    wall_type: str
    system: str
    r1_preserved: bool
    r2_d_change: bool
    escape_fraction: float


@dataclass(frozen=True)
class SupportCase:
    wall_type: str
    label: str
    system: str
    build: Callable[[], tuple[list[np.ndarray], list[np.ndarray]]]
    gap_pairs: tuple[tuple[int, int], ...]


def is_even_perm(p: tuple[int, ...]) -> bool:
    """Return whether a permutation is even."""
    inversions = 0
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                inversions += 1
    return inversions % 2 == 0


def build_s4_type3() -> tuple[list[np.ndarray], list[np.ndarray]]:
    gen_perms = [
        (1, 0, 2, 3),
        (2, 0, 1, 3),
        (1, 2, 3, 0),
    ]
    system = build_system_from_perms(symmetric_group(4), gen_perms)
    return system["Vs"], system["Xs"]


def build_a5_type3() -> tuple[list[np.ndarray], list[np.ndarray]]:
    gen_perms = [
        (0, 2, 4, 3, 1),
        (1, 3, 2, 0, 4),
        (3, 0, 2, 1, 4),
    ]
    a5 = [p for p in symmetric_group(5) if is_even_perm(p)]
    system = build_system_from_perms(a5, gen_perms)
    return system["Vs"], system["Xs"]


def build_synthetic_type3() -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Build the constructed Type III cancellation model."""
    x_g = np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0, 0.0],
        ],
        dtype=complex,
    )
    x_h = np.array(
        [
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [-1.0, 0.0, 0.0, 0.0],
            [0.0, -1.0, 0.0, 0.0],
        ],
        dtype=complex,
    )
    x_c = np.zeros((4, 4), dtype=complex)
    x_c[0, 1] = 1.0
    x_c[1, 0] = -1.0
    x_c[2, 3] = 1.0
    x_c[3, 2] = -1.0

    vs = [
        np.array([[1.0], [0.0], [0.0], [0.0]], dtype=complex),
        np.array(
            [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 0.0]],
            dtype=complex,
        ),
        np.array([[0.0], [0.0], [0.0], [1.0]], dtype=complex),
    ]
    return vs, [x_g, x_h, x_c]


def build_synthetic_type4() -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Build the constructed Type IV AB=0 incidence model."""
    x_g = np.zeros((6, 6), dtype=complex)
    x_g[0, 2] = 1.0
    x_g[2, 0] = -1.0

    x_h = np.zeros((6, 6), dtype=complex)
    x_h[3, 4] = 1.0
    x_h[4, 3] = -1.0

    vs = [
        np.array(
            [[1, 0], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0]],
            dtype=complex,
        ),
        np.array(
            [[0, 0], [0, 0], [1, 0], [0, 1], [0, 0], [0, 0]],
            dtype=complex,
        ),
        np.array(
            [[0, 0], [0, 0], [0, 0], [0, 0], [1, 0], [0, 1]],
            dtype=complex,
        ),
    ]
    return vs, [x_g, x_h]


def decompose_to_blocks(vs: list[np.ndarray], x: np.ndarray) -> dict:
    """Decompose a matrix into sector blocks."""
    blocks = {}
    for i, vi in enumerate(vs):
        for j, vj in enumerate(vs):
            blocks[(i, j)] = vi.conj().T @ x @ vj
    return blocks


def reconstruct_from_blocks(
    vs: list[np.ndarray],
    blocks: dict,
    n_total: int,
) -> np.ndarray:
    """Reconstruct a full matrix from sector blocks."""
    x = np.zeros((n_total, n_total), dtype=complex)
    for (i, j), block in blocks.items():
        if block is not None:
            x += vs[i] @ block @ vs[j].conj().T
    return x


def r1_preserving_perturbation(
    vs: list[np.ndarray],
    xs_0: list[np.ndarray],
    rng: np.random.RandomState,
) -> list[dict]:
    """Generate normalized block perturbations without changing R1 support."""
    n_sec = len(vs)
    perturbations = []

    for x in xs_0:
        blocks_0 = decompose_to_blocks(vs, x)
        pert = {}
        for i in range(n_sec):
            for j in range(i, n_sec):
                block = blocks_0[(i, j)]
                if np.linalg.norm(block, "fro") > TOL:
                    d_i, d_j = block.shape
                    z = rng.normal(0, 1, (d_i, d_j))
                    z = z + 1j * rng.normal(0, 1, (d_i, d_j))
                    pert[(i, j)] = z
                    if i != j:
                        pert[(j, i)] = -z.conj().T
                else:
                    pert[(i, j)] = None
                    pert[(j, i)] = None

        total = sum(
            np.linalg.norm(delta, "fro") ** 2
            for delta in pert.values()
            if delta is not None
        )
        if total > 0:
            scale = 1.0 / np.sqrt(total)
            for key, delta in pert.items():
                if delta is not None:
                    pert[key] = scale * delta
        perturbations.append(pert)

    return perturbations


def apply_block_perturbation(
    vs: list[np.ndarray],
    xs_0: list[np.ndarray],
    perturbations: list[dict],
    strength: float,
) -> list[np.ndarray]:
    """Apply an R1-preserving perturbation to all generators."""
    n_total = xs_0[0].shape[0]
    xs_t = []
    for g, x in enumerate(xs_0):
        blocks_0 = decompose_to_blocks(vs, x)
        blocks_t = {}
        for key, block in blocks_0.items():
            delta = perturbations[g].get(key)
            blocks_t[key] = block if delta is None else block + strength * delta
        xs_t.append(reconstruct_from_blocks(vs, blocks_t, n_total))
    return xs_t


def protocol_b_escape_fraction(
    vs: list[np.ndarray],
    xs_0: list[np.ndarray],
    eps: float,
    n_trials: int,
    gap_pairs: tuple[tuple[int, int], ...],
) -> tuple[float, bool]:
    """Return escape fraction and whether R1 stayed fixed in all trials."""
    result_0 = accessibility_signature(vs, xs_0, max_depth=4, tol=TOL)
    n_wall = 0
    n_r1_changed = 0

    for trial in range(n_trials):
        rng = np.random.RandomState(trial * 7919 + 137)
        perturbations = r1_preserving_perturbation(vs, xs_0, rng)
        xs_t = apply_block_perturbation(vs, xs_0, perturbations, eps)
        result_t = accessibility_signature(vs, xs_t, max_depth=4, tol=TOL)

        if all(int(result_t["D"][pair]) >= 2 for pair in gap_pairs):
            n_wall += 1
        if int(np.sum(result_t["R1"] != result_0["R1"])) > 0:
            n_r1_changed += 1

    escape_fraction = (n_trials - n_wall) / n_trials
    return escape_fraction, n_r1_changed == 0


SUPPORT_CASES = [
    SupportCase(
        wall_type="Type III",
        label="S4-3gen-B",
        system="real S4 regular representation",
        build=build_s4_type3,
        gap_pairs=((3, 4), (4, 3)),
    ),
    SupportCase(
        wall_type="Type III",
        label="A5-3gen",
        system="real A5 regular representation",
        build=build_a5_type3,
        gap_pairs=((5, 6), (6, 5), (7, 8), (8, 7)),
    ),
    SupportCase(
        wall_type="Type III",
        label="Synthetic-Type-III",
        system="constructed 4x4 cancellation model",
        build=build_synthetic_type3,
        gap_pairs=((0, 2),),
    ),
    SupportCase(
        wall_type="Type IV",
        label="Synthetic-Type-IV",
        system="constructed AB=0 incidence model",
        build=build_synthetic_type4,
        gap_pairs=((0, 2), (2, 0)),
    ),
]


def summarize_case(case: SupportCase, trials: int, eps: float) -> SummaryRow:
    vs, xs = case.build()
    escape_fraction, r1_preserved = protocol_b_escape_fraction(
        vs,
        xs,
        eps,
        trials,
        case.gap_pairs,
    )
    return SummaryRow(
        wall_type=case.wall_type,
        system=f"{case.label} ({case.system})",
        r1_preserved=r1_preserved,
        r2_d_change=escape_fraction > 0,
        escape_fraction=escape_fraction,
    )


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


def format_table(rows: list[SummaryRow]) -> list[str]:
    lines = [
        "| Wall type | System | R1 preserved | R2/D change | Escape fraction |",
        "|---|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row.wall_type} | "
            f"{row.system} | "
            f"{format_bool(row.r1_preserved)} | "
            f"{format_bool(row.r2_d_change)} | "
            f"{row.escape_fraction:.1%} |"
        )
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the compact Paper VI Type III/IV support table."
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=32,
        help="number of random block-space trials per system in default mode",
    )
    parser.add_argument(
        "--eps",
        type=float,
        default=1.0,
        help="perturbation strength used for the default escape fraction",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = [summarize_case(case, args.trials, args.eps) for case in SUPPORT_CASES]

    assert all(row.r1_preserved for row in rows)
    assert all(row.r2_d_change for row in rows)

    table = format_table(rows)
    for line in table:
        print(line)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(table))
        f.write("\n")

    print(f"\n[snapshot: {LOG_PATH}]")


if __name__ == "__main__":
    main()
