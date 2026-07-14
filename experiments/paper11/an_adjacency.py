"""Paper XI branch-aware A_n adjacency falsification audit.

The audit does not infer A2 adjacency from sorted eigenvalue indices. It:

1. analyzes each invariant Rubik block separately;
2. continues eigenbranches by eigenvector-overlap assignment;
3. rejects persistent degeneracies and endpoint-only closures;
4. requires two isolated pair-collision candidates at separated parameter
   values involving all three branches of an endpoint triple.

Passing this audit would provide an A2 -> A1 + A1 candidate, not a versal
unfolding theorem. Failing it leaves the adjacency claim unsupported.
"""

from __future__ import annotations

import json
import os
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.cubie import BLOCK_RANGES  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


BETA = 0.314159
N_STEPS = 96
ENDPOINT_TOL = 1e-7
START_SEPARATION_TOL = 1e-3
COLLISION_TOL = 2e-4
MAX_NEAR_SAMPLES = 4
MIN_ALPHA_SEPARATION = 0.02
MAX_TRIPLES_PER_BLOCK = 20
EPSILONS = [0.02, 0.05, 0.10, 0.20]
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def qt_ht_indices(n_generators: int) -> tuple[list[int], list[int]]:
    qt_indices = [index for index in range(n_generators) if index % 3 != 2]
    ht_indices = [index for index in range(n_generators) if index % 3 == 2]
    return qt_indices, ht_indices


def block_generators() -> tuple[dict[str, list[np.ndarray]], list[int], list[int]]:
    operator = CubieSpectralOperator()
    generators = [np.asarray(rho, dtype=complex) for rho in operator.rho_matrices()]
    qt_indices, ht_indices = qt_ht_indices(len(generators))
    blocks = {}
    for name, (start, end) in BLOCK_RANGES.items():
        blocks[name] = [generator[start:end, start:end] for generator in generators]
    return blocks, qt_indices, ht_indices


def probe_matrix(
    generators: list[np.ndarray],
    qt_indices: list[int],
    ht_indices: list[int],
    alpha: float,
    epsilon: float,
) -> np.ndarray:
    weights = np.ones(len(generators), dtype=float)
    first, second = qt_indices[0], qt_indices[1]
    weights[first] = alpha * (1.0 + epsilon)
    weights[second] = alpha * (1.0 - epsilon)
    qt = sum(weights[index] * generators[index] for index in qt_indices) / sum(
        weights[index] for index in qt_indices
    )
    ht = sum(weights[index] * generators[index] for index in ht_indices) / sum(
        weights[index] for index in ht_indices
    )
    matrix = qt + BETA * ht
    return (matrix + matrix.conj().T) / 2.0


def align_vectors(reference: np.ndarray, candidate: np.ndarray) -> np.ndarray:
    overlaps = np.abs(reference.conj().T @ candidate) ** 2
    rows, cols = linear_sum_assignment(-overlaps)
    ordering = np.empty(reference.shape[1], dtype=int)
    ordering[rows] = cols
    return ordering


def track_branches(
    matrices: list[np.ndarray],
    initial_reference: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    values = []
    first_values, first_vectors = np.linalg.eigh(matrices[0])
    descending = np.argsort(first_values)[::-1]
    first_values = first_values[descending]
    first_vectors = first_vectors[:, descending]
    if initial_reference is not None:
        ordering = align_vectors(initial_reference, first_vectors)
        first_values = first_values[ordering]
        first_vectors = first_vectors[:, ordering]

    values.append(first_values)
    previous_vectors = first_vectors
    for matrix in matrices[1:]:
        current_values, current_vectors = np.linalg.eigh(matrix)
        descending = np.argsort(current_values)[::-1]
        current_values = current_values[descending]
        current_vectors = current_vectors[:, descending]
        ordering = align_vectors(previous_vectors, current_vectors)
        current_values = current_values[ordering]
        current_vectors = current_vectors[:, ordering]
        values.append(current_values)
        previous_vectors = current_vectors
    return np.asarray(values), first_vectors


def endpoint_clusters(branch_values: np.ndarray) -> list[list[int]]:
    endpoint = branch_values[-1]
    ordered = sorted(range(endpoint.size), key=lambda index: endpoint[index], reverse=True)
    clusters: list[list[int]] = []
    for branch in ordered:
        if not clusters:
            clusters.append([branch])
            continue
        anchor = clusters[-1][0]
        if abs(endpoint[branch] - endpoint[anchor]) <= ENDPOINT_TOL:
            clusters[-1].append(branch)
        else:
            clusters.append([branch])
    return [cluster for cluster in clusters if len(cluster) >= 3]


def candidate_triples(branch_values: np.ndarray) -> list[tuple[int, int, int]]:
    candidates = []
    start = branch_values[0]
    for cluster in endpoint_clusters(branch_values):
        for triple in combinations(cluster, 3):
            start_gaps = [abs(start[left] - start[right]) for left, right in combinations(triple, 2)]
            if min(start_gaps) <= START_SEPARATION_TOL:
                continue
            candidates.append(tuple(sorted(triple)))
    candidates.sort(
        key=lambda triple: min(
            abs(start[left] - start[right]) for left, right in combinations(triple, 2)
        ),
        reverse=True,
    )
    return candidates[:MAX_TRIPLES_PER_BLOCK]


def isolated_pair_events(
    branch_values: np.ndarray,
    alphas: np.ndarray,
    triple: tuple[int, int, int],
) -> list[dict]:
    events = []
    for left, right in combinations(triple, 2):
        gaps = np.abs(branch_values[:, left] - branch_values[:, right])
        minimum_index = int(np.argmin(gaps))
        minimum_gap = float(gaps[minimum_index])
        near_samples = int(np.sum(gaps <= COLLISION_TOL))
        interior = 0 < minimum_index < len(alphas) - 1
        isolated = minimum_gap <= COLLISION_TOL and near_samples <= MAX_NEAR_SAMPLES and interior
        if isolated:
            events.append(
                {
                    "pair": [left, right],
                    "alpha": float(alphas[minimum_index]),
                    "minimum_gap": minimum_gap,
                    "near_samples": near_samples,
                }
            )
    return events


def has_split_adjacency(events: list[dict], triple: tuple[int, int, int]) -> bool:
    for first, second in combinations(events, 2):
        if abs(first["alpha"] - second["alpha"]) < MIN_ALPHA_SEPARATION:
            continue
        involved = set(first["pair"]) | set(second["pair"])
        if involved == set(triple):
            return True
    return False


def audit_block(
    name: str,
    generators: list[np.ndarray],
    qt_indices: list[int],
    ht_indices: list[int],
) -> dict:
    alphas = np.linspace(0.02, 1.0, N_STEPS)
    diagonal_matrices = [
        probe_matrix(generators, qt_indices, ht_indices, float(alpha), 0.0)
        for alpha in alphas
    ]
    diagonal_values, initial_vectors = track_branches(diagonal_matrices)
    triples = candidate_triples(diagonal_values)
    tests = []

    for epsilon in EPSILONS:
        perturbed_matrices = [
            probe_matrix(generators, qt_indices, ht_indices, float(alpha), epsilon)
            for alpha in alphas
        ]
        perturbed_values, _vectors = track_branches(
            perturbed_matrices,
            initial_reference=initial_vectors,
        )
        for triple in triples:
            events = isolated_pair_events(perturbed_values, alphas, triple)
            tests.append(
                {
                    "epsilon": epsilon,
                    "triple": list(triple),
                    "isolated_pair_events": events,
                    "split_candidate": has_split_adjacency(events, triple),
                }
            )

    split_tests = [test for test in tests if test["split_candidate"]]
    return {
        "block": name,
        "dimension": generators[0].shape[0],
        "endpoint_clusters": [len(cluster) for cluster in endpoint_clusters(diagonal_values)],
        "tested_triples": len(triples),
        "tests": tests,
        "split_candidate_count": len(split_tests),
        "split_candidates": split_tests,
    }


def markdown_report(result: dict) -> str:
    lines = [
        "# Paper XI Branch-Aware A_n Adjacency Audit",
        "",
        "The audit is block-restricted and follows eigenbranches by eigenvector overlap.",
        "",
        "| Block | Dimension | Endpoint cluster sizes | Tested triples | Split candidates |",
        "|---|---:|---|---:|---:|",
    ]
    for block in result["blocks"]:
        lines.append(
            f"| {block['block']} | {block['dimension']} | {block['endpoint_clusters']} | "
            f"{block['tested_triples']} | {block['split_candidate_count']} |"
        )
    lines.extend(
        [
            "",
            f"**Conclusion:** {result['conclusion']}",
            "",
            "A split candidate would still require local normal-form and versality analysis before an A2 claim.",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict:
    blocks, qt_indices, ht_indices = block_generators()
    block_results = [
        audit_block(name, generators, qt_indices, ht_indices)
        for name, generators in blocks.items()
    ]
    total_splits = sum(block["split_candidate_count"] for block in block_results)
    conclusion = (
        "branch-aware split candidates were detected; adjacency remains candidate evidence"
        if total_splits
        else "no branch-aware A2-to-two-A1 split candidate was detected on the tested slices"
    )
    result = {
        "parameters": {
            "beta": BETA,
            "n_steps": N_STEPS,
            "epsilons": EPSILONS,
            "endpoint_tolerance": ENDPOINT_TOL,
            "collision_tolerance": COLLISION_TOL,
            "minimum_alpha_separation": MIN_ALPHA_SEPARATION,
        },
        "blocks": block_results,
        "total_split_candidates": total_splits,
        "conclusion": conclusion,
        "claim_boundary": (
            "This is a branch-aware falsification audit, not an ADE classification "
            "or versal-unfolding theorem."
        ),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "an_adjacency.json"
    md_path = RESULTS_DIR / "an_adjacency.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(markdown_report(result), encoding="utf-8")

    print("Paper XI branch-aware A_n adjacency audit")
    for block in block_results:
        print(
            f"  {block['block']}: dim={block['dimension']}, "
            f"clusters={block['endpoint_clusters']}, triples={block['tested_triples']}, "
            f"split_candidates={block['split_candidate_count']}"
        )
    print(f"  conclusion: {conclusion}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return result


if __name__ == "__main__":
    run()
