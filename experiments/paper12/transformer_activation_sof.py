"""Paper XII diagnostic: transformer activation SOF.

Claim status:
    - Diagnostic case study for Paper XII.
    - Demonstrates SOF realization in an AI/transformer-style system.
    - Not a theorem about trained LLMs and not an explainability theory.

The finite space is token space.  Sectors are activation-pattern clusters from
a tiny transformer-like block.  Observables are token-to-token influence
operators induced by attention and FFN activation similarity.

This is the Paper XII diagnostic pipeline:

    system -> stable information decomposition -> SOF audit -> report
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
from rime.accessibility import AccessibilityEngine  # noqa: E402


def sector_bases_from_token_groups(groups: list[list[int]], n_tokens: int) -> list[np.ndarray]:
    eye = np.eye(n_tokens, dtype=complex)
    return [eye[:, group] for group in groups if group]


def topk_rows(M: np.ndarray, k: int = 2) -> np.ndarray:
    """Keep top-k entries per row and zero the rest."""

    out = np.zeros_like(M)
    for i in range(M.shape[0]):
        idx = np.argsort(-np.abs(M[i]))[:k]
        out[i, idx] = M[i, idx]
    return out


def build_tiny_transformer(seed: int = 42) -> dict:
    rng = np.random.RandomState(seed)
    d_model, d_ff, n_tokens = 32, 64, 8

    W_Q = rng.randn(d_model, d_model) * 0.1
    W_K = rng.randn(d_model, d_model) * 0.1
    W_V = rng.randn(d_model, d_model) * 0.1
    W_1 = rng.randn(d_ff, d_model) * 0.1
    W_2 = rng.randn(d_model, d_ff) * 0.1
    X = rng.randn(d_model, n_tokens)

    Q = W_Q @ X
    K = W_K @ X
    V = W_V @ X
    scores = Q.T @ K / np.sqrt(d_model)
    attn = np.exp(scores - scores.max(axis=1, keepdims=True))
    attn /= attn.sum(axis=1, keepdims=True)

    attn_out = V @ attn.T
    residual = X + attn_out
    residual = (residual - residual.mean(axis=0, keepdims=True)) / (
        residual.std(axis=0, keepdims=True) + 1e-5
    )

    hidden_pre = W_1 @ residual
    hidden_act = np.maximum(0.0, hidden_pre)
    output = residual + W_2 @ hidden_act

    return {
        "d_model": d_model,
        "d_ff": d_ff,
        "n_tokens": n_tokens,
        "attention": attn,
        "hidden_act": hidden_act,
        "output": output,
    }


def activation_sectors(hidden_act: np.ndarray) -> tuple[list[np.ndarray], list[str]]:
    """Cluster tokens by coarse FFN activation count quantiles."""

    n_tokens = hidden_act.shape[1]
    active_counts = np.sum(hidden_act > 0, axis=0)
    q1, q2 = np.quantile(active_counts, [1 / 3, 2 / 3])

    low = [idx for idx, value in enumerate(active_counts) if value <= q1]
    mid = [idx for idx, value in enumerate(active_counts) if q1 < value <= q2]
    high = [idx for idx, value in enumerate(active_counts) if value > q2]
    groups = [low, mid, high]
    labels = [
        f"low activation count, tokens={low}",
        f"middle activation count, tokens={mid}",
        f"high activation count, tokens={high}",
    ]
    Vs = sector_bases_from_token_groups(groups, n_tokens)
    labels = [label for group, label in zip(groups, labels) if group]
    return Vs, labels


def token_observables(attention: np.ndarray, hidden_act: np.ndarray) -> list[np.ndarray]:
    """Return token-space observables from attention and FFN activation geometry."""

    attn_op = topk_rows(attention, k=2)
    ffn_similarity = hidden_act.T @ hidden_act
    scale = np.max(np.abs(ffn_similarity))
    if scale > 1e-12:
        ffn_similarity = ffn_similarity / scale
    ffn_op = topk_rows(ffn_similarity, k=2)

    # Center the diagonals so self-loops do not dominate the audit.
    np.fill_diagonal(attn_op, 0.0)
    np.fill_diagonal(ffn_op, 0.0)
    return [attn_op.astype(complex), ffn_op.astype(complex)]


def audit(seed: int = 42) -> dict:
    model = build_tiny_transformer(seed=seed)
    Vs, labels = activation_sectors(model["hidden_act"])
    Xs = token_observables(model["attention"], model["hidden_act"])
    engine = AccessibilityEngine(Vs, Xs, tol=1e-8, max_depth=3)
    R1, R2, _ = engine.support()
    D, _ = engine.depth()
    return {
        "model": model,
        "labels": labels,
        "support_graph": np.any(R1, axis=0),
        "bridge_graph": np.any(R2, axis=0),
        "depth_matrix": D,
        **engine.audit(),
    }


def sofreport(result: dict) -> dict:
    support = result["support_graph"]
    depth = result["depth_matrix"]
    repaired = [
        {"source": i, "target": j, "depth": int(depth[i, j])}
        for i in range(result["n_sec"])
        for j in range(result["n_sec"])
        if i != j and not support[i, j] and depth[i, j] < 3
    ]
    return {
        "sofrs_version": "1.0",
        "report_id": "transformer_activation",
        "system": "tiny transformer-like block",
        "claim_status": "diagnostic",
        "claim_note": "synthetic transformer activation-sector case study",
        "sectorization": {
            "origin": "FFN activation-count quantiles",
            "space": "token space",
            "sector_count": result["n_sec"],
            "sector_dimensions": result["sector_dims"],
            "labels": result["labels"],
            "strict_sof_realization": True,
        },
        "observable_family": {
            "attention": "row-top-2 token attention operator",
            "activation": "row-top-2 FFN activation-similarity operator",
        },
        "support_matrix": {
            "kind": "aggregated_R1",
            "matrix": support.astype(int).tolist(),
            "offdiag_density_pct": result["R1_pct"],
        },
        "bridge_matrix": {
            "kind": "aggregated_R2",
            "matrix": result["bridge_graph"].astype(int).tolist(),
            "offdiag_density_pct": result["R2_pct"],
        },
        "repair_matrix": {
            "kind": "Lie-depth repair in the finite synthetic realization",
            "depth_matrix": depth.astype(int).tolist(),
            "repaired_pairs": repaired,
            "repaired_count": result["D_repaired"],
        },
        "wall_record": {
            "status": "not_applicable",
            "reason": "no deformation path supplied",
        },
        "failure_modes": [
            "synthetic untrained block",
            "activation-count sectors are diagnostic rather than canonical",
            "not a theorem about trained transformers or language models",
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "transformer.sofreport"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def main() -> None:
    result = audit()
    model = result["model"]

    print("=" * 72)
    print("  Paper XII: Transformer Activation SOF Diagnostic")
    print("=" * 72)
    print(
        f"Model: tiny transformer-like block, d_model={model['d_model']}, "
        f"d_ff={model['d_ff']}, tokens={model['n_tokens']}"
    )
    print(f"Sectors from FFN activation-count decomposition: {result['n_sec']}")
    for idx, (dim, label) in enumerate(zip(result["sector_dims"], result["labels"])):
        print(f"  Sector {idx}: dim={dim}, {label}")
    print()
    print("SOF accessibility report:")
    print(f"  observables: attention top-k operator + FFN activation-similarity operator")
    print(f"  R1 offdiag density: {result['R1_pct']:.1f}%")
    print(f"  R2 offdiag density: {result['R2_pct']:.1f}%")
    print(f"  frozen_R1:          {result['frozen_R1']}")
    print(f"  D_repaired:         {result['D_repaired']}")
    print(f"  D_max:              {result['D_max']}")
    print()
    print("Interpretation:")
    print("  - activation counts provide a stable information decomposition of token space;")
    print("  - attention and FFN geometry become token-space observable operators;")
    print("  - the SOF report exposes cross-sector token influence rather than raw weights alone;")
    print("  - this is a diagnostic case study, not a theorem about all transformers.")
    print(f"SOFRS v1.0: {write_sofreport(sofreport(result))}")
    print("Done.")


if __name__ == "__main__":
    main()
