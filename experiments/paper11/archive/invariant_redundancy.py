"""Legacy Paper XI configuration-diagnostic redundancy audit.

The audit deliberately excludes quantities that do not share a sampling unit:

- codimension requires an ambient geometric model;
- wall density is a cross-species taxonomy statistic;
- oscillation, plateau, and persistence require trajectories.

Only snapshot diagnostics computed on every configuration enter the correlation
and PCA tables. Static configurations are not admitted wall events, so this
cohort is excluded from the Paper XI v2 wall spectrum and typed census. The
result remains historical companion provenance, not an invariant completeness
or "orthogonal core" theorem.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from rime.accessibility import (  # noqa: E402
    AccessibilityEngine,
    UNREACHED_DEPTH,
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
    offdiag_count,
)


TOL = 1e-8
MAX_DEPTH = 4
RESULTS_DIR = Path(__file__).resolve().parent / "results"
TRAJECTORY_PATH = Path(__file__).resolve().parents[1] / "results" / "wall_trajectory.json"

METRIC_NAMES = [
    "direct_unsupported_fraction",
    "lie_unreached_fraction",
    "lie_emergent_index",
    "word_bridge_only_fraction",
    "lie_bridge_only_fraction",
    "mean_word_depth",
    "max_word_depth",
    "log10_norm_ratio",
]


def skew(matrix: np.ndarray) -> np.ndarray:
    return ((matrix - matrix.conj().T) / 2.0).astype(complex)


def sector_bases(n_sectors: int) -> list[np.ndarray]:
    eye = np.eye(n_sectors, dtype=complex)
    return [eye[:, [index]] for index in range(n_sectors)]


def snapshot_metrics(sectors: list[np.ndarray], observables: list[np.ndarray]) -> dict[str, float]:
    engine = AccessibilityEngine(sectors, observables, tol=TOL, max_depth=MAX_DEPTH)
    cutoff = engine.cutoff_summary()
    _r1, r2_lie_by_pair, _pairs = engine.support()
    r2_lie = (
        np.any(r2_lie_by_pair, axis=0)
        if r2_lie_by_pair.shape[0]
        else np.zeros((len(sectors), len(sectors)), dtype=bool)
    )
    r1_word = compute_direct_support(sectors, observables, tol=TOL)
    r2_word = compute_length_two_support(sectors, observables, tol=TOL)
    depth_word = compute_word_depth_matrix(
        sectors,
        observables,
        max_depth=MAX_DEPTH,
        tol=TOL,
        unreached=UNREACHED_DEPTH,
    )

    n_sectors = len(sectors)
    total_pairs = max(n_sectors * (n_sectors - 1), 1)
    finite_mask = (depth_word != UNREACHED_DEPTH) & (~np.eye(n_sectors, dtype=bool))
    finite_depths = depth_word[finite_mask]
    mean_depth = float(np.mean(finite_depths)) if finite_depths.size else 0.0
    max_depth = float(np.max(finite_depths)) if finite_depths.size else 0.0

    norms = [float(np.linalg.norm(observable, "fro")) for observable in observables]
    positive_norms = [value for value in norms if value > 1e-12]
    if len(positive_norms) >= 2:
        ratio = max(positive_norms) / min(positive_norms)
    else:
        ratio = 1.0

    unsupported_direct = int(cutoff["unsupported_direct_pairs"])
    lie_emergent_index = (
        int(cutoff["lie_emergent_pairs"]) / unsupported_direct
        if unsupported_direct
        else 0.0
    )
    return {
        "direct_unsupported_fraction": unsupported_direct / total_pairs,
        "lie_unreached_fraction": int(cutoff["unreached_lie_pairs"]) / total_pairs,
        "lie_emergent_index": lie_emergent_index,
        "word_bridge_only_fraction": offdiag_count(r2_word & ~r1_word) / total_pairs,
        "lie_bridge_only_fraction": offdiag_count(r2_lie & ~r1_word & ~r2_word) / total_pairs,
        "mean_word_depth": mean_depth,
        "max_word_depth": max_depth,
        "log10_norm_ratio": float(np.log10(max(ratio, 1.0))),
    }


class GridWorld:
    def __init__(self, obstacle: tuple[int, int]):
        self.size = 5
        self.obstacle = obstacle

    def index(self, row: int, col: int) -> int:
        return row * self.size + col

    def transition(self, dr: int, dc: int) -> np.ndarray:
        matrix = np.zeros((25, 25), dtype=float)
        for row in range(5):
            for col in range(5):
                source = self.index(row, col)
                if (row, col) == self.obstacle:
                    matrix[source, source] = 1.0
                    continue
                next_row, next_col = row + dr, col + dc
                valid = (
                    0 <= next_row < 5
                    and 0 <= next_col < 5
                    and (next_row, next_col) != self.obstacle
                )
                target = self.index(next_row, next_col) if valid else source
                matrix[target, source] = 1.0
        return matrix

    def observables(self) -> list[np.ndarray]:
        return [
            skew(self.transition(dr, dc))
            for dr, dc in [(-1, 0), (1, 0), (0, 1), (0, -1)]
        ]


def gridworld_configurations() -> list[tuple[str, list[np.ndarray], list[np.ndarray]]]:
    sectors = sector_bases(25)
    return [
        (f"gridworld({row},{col})", sectors, GridWorld((row, col)).observables())
        for row in range(5)
        for col in range(5)
    ]


def sir_configurations(n_steps: int = 41) -> list[tuple[str, list[np.ndarray], list[np.ndarray]]]:
    sectors = sector_bases(3)
    gamma = 0.1
    configs = []
    for beta in np.linspace(0.0, 0.5, n_steps):
        infection = np.eye(3, dtype=float)
        infection[1, 0] = beta
        infection[0, 0] = 1.0 - beta
        recovery = np.eye(3, dtype=float)
        recovery[2, 1] = gamma
        recovery[1, 1] = 1.0 - gamma
        configs.append(
            (f"sir({beta:.3f})", sectors, [skew(infection), skew(recovery)])
        )
    return configs


def random_graph_configurations(
    n_graphs: int = 50,
    n_nodes: int = 6,
    edge_probability: float = 0.4,
) -> list[tuple[str, list[np.ndarray], list[np.ndarray]]]:
    rng = np.random.default_rng(42)
    sectors = sector_bases(n_nodes)
    configs = []
    for index in range(n_graphs):
        matrix = np.eye(n_nodes, dtype=float)
        for source in range(n_nodes):
            targets = [
                target
                for target in range(n_nodes)
                if target != source and rng.random() < edge_probability
            ]
            if targets:
                matrix[source, source] = 0.0
                for target in targets:
                    matrix[target, source] = 1.0 / len(targets)
        configs.append((f"graph{index}", sectors, [skew(matrix)]))
    return configs


def random_skew_configurations(
    n_configs: int = 50,
    dimension: int = 8,
) -> list[tuple[str, list[np.ndarray], list[np.ndarray]]]:
    rng = np.random.default_rng(43)
    configs = []
    for index in range(n_configs):
        n_sectors = int(rng.integers(2, 6))
        permutation = rng.permutation(dimension)
        cuts = sorted(rng.choice(np.arange(1, dimension), n_sectors - 1, replace=False))
        sector_indices = np.split(permutation, cuts)
        eye = np.eye(dimension, dtype=complex)
        sectors = [eye[:, indices] for indices in sector_indices]
        n_generators = int(rng.integers(1, 5))
        observables = []
        for _ in range(n_generators):
            raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(
                scale=0.1, size=(dimension, dimension)
            )
            observables.append(skew(raw))
        configs.append((f"random_skew{index}", sectors, observables))
    return configs


def correlation_analysis(matrix: np.ndarray, metric_names: list[str]) -> dict:
    std = np.std(matrix, axis=0)
    retained_indices = [index for index, value in enumerate(std) if value > 1e-12]
    dropped = [metric_names[index] for index, value in enumerate(std) if value <= 1e-12]
    retained_names = [metric_names[index] for index in retained_indices]
    retained = matrix[:, retained_indices]
    correlation = np.corrcoef(retained, rowvar=False)

    standardized = (retained - np.mean(retained, axis=0)) / np.std(retained, axis=0)
    _u, singular_values, vt = np.linalg.svd(standardized, full_matrices=False)
    explained = singular_values**2 / np.sum(singular_values**2)
    cumulative = np.cumsum(explained)
    n90 = int(np.searchsorted(cumulative, 0.90) + 1)
    n95 = int(np.searchsorted(cumulative, 0.95) + 1)

    high_pairs = []
    for left in range(len(retained_names)):
        for right in range(left + 1, len(retained_names)):
            value = float(correlation[left, right])
            if abs(value) >= 0.85:
                high_pairs.append(
                    {
                        "left": retained_names[left],
                        "right": retained_names[right],
                        "correlation": value,
                    }
                )
    return {
        "retained_metrics": retained_names,
        "dropped_zero_variance_metrics": dropped,
        "correlation_matrix": correlation.tolist(),
        "high_correlation_pairs": high_pairs,
        "pca_explained": explained.tolist(),
        "pca_loadings": vt.tolist(),
        "pca_components_90": n90,
        "pca_components_95": n95,
    }


def trajectory_summary() -> dict:
    if not TRAJECTORY_PATH.is_file():
        return {"status": "missing", "path": str(TRAJECTORY_PATH)}
    payload = json.loads(TRAJECTORY_PATH.read_text(encoding="utf-8"))
    rows = []
    for name, record in payload.items():
        summary = record["summary"]
        rows.append(
            {
                "control": name,
                "pair_event_count": summary["n_pair_events"],
                "field_change_count": summary["n_field_changes"],
                "changed_pair_fraction": summary["n_changed_pairs"]
                / summary["total_pairs"],
                "event_step_count": sum(
                    count > 0 for count in summary["pair_event_counts_by_step"]
                ),
                "max_pair_event_density": max(
                    summary["pair_event_density_by_step"],
                    default=0.0,
                ),
            }
        )
    return {
        "status": "reported_separately",
        "reason": "three trajectories are insufficient for a trajectory-invariant PCA",
        "rows": rows,
    }


def markdown_report(result: dict) -> str:
    analysis = result["snapshot_analysis"]
    lines = [
        "# Legacy Paper XI Configuration Redundancy Audit",
        "",
        "**Status:** excluded from the v2 wall spectrum and typed census.",
        "",
        f"Snapshot configurations: **{result['configuration_count']}**.",
        "",
        "The matrix excludes codimension, cross-species wall density, and trajectory-only quantities.",
        "",
        "## PCA Summary",
        "",
        f"- Components for 90% variance: **{analysis['pca_components_90']}**",
        f"- Components for 95% variance: **{analysis['pca_components_95']}**",
        "- This is an empirical dimension estimate, not an invariant-basis theorem.",
        "",
        "## High-Correlation Pairs",
        "",
        "| Left | Right | Correlation |",
        "|---|---|---:|",
    ]
    if analysis["high_correlation_pairs"]:
        for item in analysis["high_correlation_pairs"]:
            lines.append(
                f"| {item['left']} | {item['right']} | {item['correlation']:+.3f} |"
            )
    else:
        lines.append("| -- | -- | no pair with abs(r) >= 0.85 |")

    lines.extend(
        [
            "",
            "## Trajectory Diagnostics",
            "",
            "Trajectory quantities are reported separately; no trajectory PCA is performed.",
            "",
            "| Control | Pair events | Field changes | Changed-pair fraction | Event steps | Max pair-event density |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in result["trajectory_analysis"].get("rows", []):
        lines.append(
            f"| {row['control']} | {row['pair_event_count']} | "
            f"{row['field_change_count']} | "
            f"{row['changed_pair_fraction']:.3f} | {row['event_step_count']} | "
            f"{row['max_pair_event_density']:.3f} |"
        )
    lines.append("")
    return "\n".join(lines)


def run() -> dict:
    configs = (
        gridworld_configurations()
        + sir_configurations()
        + random_graph_configurations()
        + random_skew_configurations()
    )
    labels = []
    rows = []
    for label, sectors, observables in configs:
        labels.append(label)
        metrics = snapshot_metrics(sectors, observables)
        rows.append([metrics[name] for name in METRIC_NAMES])

    matrix = np.asarray(rows, dtype=float)
    result = {
        "record_status": "excluded_from_v2_wall_spectrum",
        "exclusion_reason": (
            "the 166 rows are static configuration samples rather than "
            "admitted wall events or wall-locus samples"
        ),
        "configuration_count": len(configs),
        "metric_names": METRIC_NAMES,
        "configuration_labels": labels,
        "snapshot_analysis": correlation_analysis(matrix, METRIC_NAMES),
        "trajectory_analysis": trajectory_summary(),
        "claim_boundary": (
            "Legacy empirical redundancy on controlled static configurations; "
            "excluded from the v2 wall census, with no complete, minimal, "
            "orthogonal, or invariant coordinate basis claimed."
        ),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "invariant_redundancy.json"
    md_path = RESULTS_DIR / "invariant_redundancy.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(markdown_report(result), encoding="utf-8")

    analysis = result["snapshot_analysis"]
    print("Legacy Paper XI configuration redundancy audit (excluded from v2 census)")
    print(f"  configurations: {result['configuration_count']}")
    print(f"  metrics: {len(analysis['retained_metrics'])}")
    print(f"  PCA components: 90%={analysis['pca_components_90']}, 95%={analysis['pca_components_95']}")
    for item in analysis["high_correlation_pairs"]:
        print(f"  {item['left']} <-> {item['right']}: r={item['correlation']:+.3f}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return result


if __name__ == "__main__":
    run()
