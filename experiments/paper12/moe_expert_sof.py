"""Paper XII diagnostic: Mixture-of-Experts routing SOF Report.

Claim status:
    - White-box routing diagnostic for a synthetic top-2 MoE layer.
    - Token groups with the same expert pair form natural sectors.
    - The routing-overlap kernel is a token-space observable; its word-depth
      closure is a routing analogue, not Lie-depth D.

With four experts, there are six possible expert pairs. The default 32-token
sample realizes all six. Direct routing support is not complete, but its
two-step closure repairs every missing pair, leaving no terminally frozen
sector pair. Larger expert pools, fewer tokens, or top-1 routing are natural
sparse-boundary probes.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import (  # noqa: E402
    compute_direct_support,
    compute_word_depth_matrix,
    offdiag_count,
)


N_EXPERTS = 4
N_TOKENS = 32
D_MODEL = 64
TOP_K = 2
FROZEN = 999


def route_tokens(seed: int = 42) -> tuple[np.ndarray, dict[tuple[int, ...], list[int]]]:
    rng = np.random.RandomState(seed)
    router = rng.randn(N_EXPERTS, D_MODEL) * 0.1
    tokens = rng.randn(D_MODEL, N_TOKENS)
    logits = router @ tokens
    top_experts = np.argsort(-logits, axis=0)[:TOP_K]

    groups: dict[tuple[int, ...], list[int]] = {}
    for token in range(N_TOKENS):
        expert_pair = tuple(sorted(int(expert) for expert in top_experts[:, token]))
        groups.setdefault(expert_pair, []).append(token)
    return top_experts, groups


def token_sectors(groups: dict[tuple[int, ...], list[int]]) -> tuple[list[np.ndarray], list[tuple[int, ...]]]:
    eye = np.eye(N_TOKENS, dtype=complex)
    labels = sorted(groups)
    sectors = [eye[:, groups[label]] for label in labels]
    return sectors, labels


def routing_kernel(top_experts: np.ndarray) -> np.ndarray:
    incidence = np.zeros((N_EXPERTS, N_TOKENS), dtype=float)
    for token in range(N_TOKENS):
        incidence[top_experts[:, token], token] = 1.0
    kernel = incidence.T @ incidence
    np.fill_diagonal(kernel, 0.0)
    return kernel.astype(complex)


def audit() -> dict:
    top_experts, groups = route_tokens()
    sectors, labels = token_sectors(groups)
    kernel = routing_kernel(top_experts)
    support = compute_direct_support(sectors, [kernel])
    D = compute_word_depth_matrix(sectors, [kernel], max_depth=3, frozen=FROZEN)

    repaired = [
        (i, j)
        for i in range(len(sectors))
        for j in range(len(sectors))
        if i != j and not support[i, j] and D[i, j] != FROZEN
    ]
    frozen = [
        (i, j)
        for i in range(len(sectors))
        for j in range(len(sectors))
        if i != j and D[i, j] == FROZEN
    ]
    return {
        "groups": groups,
        "labels": labels,
        "support": support,
        "D": D,
        "support_edges": offdiag_count(support),
        "repaired": repaired,
        "frozen": frozen,
    }


def sofreport(result: dict) -> dict:
    labels = result["labels"]
    return {
        "sofrs_version": "1.0",
        "report_id": "moe_expert_routing",
        "system": "synthetic four-expert top-2 MoE router",
        "claim_status": "diagnostic",
        "claim_note": "closure-complete routing control with no terminally frozen sector pairs",
        "sectorization": {
            "origin": "identical top-2 expert routes",
            "space": "token space",
            "sector_count": len(labels),
            "labels": [list(label) for label in labels],
            "sector_dimensions": [len(result["groups"][label]) for label in labels],
            "strict_sof_realization": True,
        },
        "observable_family": {
            "routing_overlap": "token-space expert-incidence Gram kernel"
        },
        "support_matrix": {
            "kind": "direct routing overlap",
            "matrix": result["support"].astype(int).tolist(),
            "ordered_support_edges": result["support_edges"],
        },
        "bridge_matrix": {
            "kind": "routing word-depth closure",
            "depth_matrix": result["D"].astype(int).tolist(),
            "claim_note": "routing analogue, not Lie-depth D",
        },
        "repair_matrix": {
            "repaired_pairs": [list(pair) for pair in result["repaired"]],
            "repaired_count": len(result["repaired"]),
        },
        "wall_record": {
            "status": "not_applicable",
            "reason": "no routing deformation supplied",
        },
        "failure_modes": [
            "the four-expert top-2 sample has no terminally frozen pair after two-step closure",
            "synthetic router is not a production MoE audit",
            "routing word depth is not Lie-depth D",
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "moe.sofreport"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def print_report(result: dict) -> None:
    labels = result["labels"]
    n_sectors = len(labels)
    possible = n_sectors * (n_sectors - 1)

    print("=" * 84)
    print("  Paper XII: MoE Expert-Routing SOF Report")
    print("=" * 84)
    print(f"  Experts={N_EXPERTS}, top_k={TOP_K}, tokens={N_TOKENS}")
    print("  Sectorization: tokens grouped by identical expert-pair routes")
    print("  Observable Family: token-space routing-overlap kernel")
    print()
    print(f"  Natural routing sectors: {n_sectors}/6 possible expert pairs")
    for label in labels:
        print(f"    experts={label}: tokens={len(result['groups'][label])}")
    print()
    print(
        f"  Support Matrix: {result['support_edges']}/{possible} "
        f"ordered sector pairs ({100 * result['support_edges'] / possible:.1f}%)"
    )
    print(f"  Two-step routing repairs: {len(result['repaired'])}")
    print(f"  Frozen routing-sector pairs: {len(result['frozen'])}")
    print(f"  Maximum finite word depth: {max(result['D'][result['D'] < FROZEN])}")
    print()
    print("  Expert-pair coverage:")
    for left in range(N_EXPERTS):
        for right in range(left + 1, N_EXPERTS):
            pair = (left, right)
            print(f"    {pair}: {'observed' if pair in result['groups'] else 'missing'}")
    print()
    print("  Interpretation:")
    print("    MoE routing naturally induces information sectorization")
    print("    two-step closure repairs all missing direct-support pairs")
    print("    sparse expert pools require more experts, fewer tokens, or top-1 routing")
    print("    word-depth repair here is a routing analogue, not Lie-depth D-repair")
    print(f"SOFRS v1.0: {write_sofreport(sofreport(result))}")
    print("Done.")


if __name__ == "__main__":
    print_report(audit())
