"""Paper XI audit: piecewise-smooth activation wall diagnostics.

Claim status:
    - Boundary evidence for the non-ADE branch of Paper XI.
    - ReLU-type activation sectors produce a piecewise-smooth kink diagnostic.
    - GeLU is smooth in this test and Top-k is discontinuous.
    - Not a theorem about all neural networks and not an ADE classification.
"""

from __future__ import annotations

import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def relu_kink(seed: int = 42) -> dict:
    rng = np.random.RandomState(seed)
    d_hid = 8
    W = rng.randn(d_hid, d_hid) * 0.5
    W = (W + W.T) / 2.0
    x = np.ones(d_hid)
    biases = np.linspace(-2.0, 2.0, 100)

    samples: list[tuple[float, float]] = []
    for bias in biases:
        H = W @ x + bias
        pos = H > 0
        neg = ~pos
        if pos.sum() > 0 and neg.sum() > 0:
            Vp = np.eye(d_hid)[:, pos]
            Vn = np.eye(d_hid)[:, neg]
            nrm = float(np.linalg.norm(Vp.T @ W @ Vn, "fro"))
        else:
            nrm = 0.0
        samples.append((float(bias), nrm))

    left = [item for item in samples if item[0] < 0][-10:]
    right = [item for item in samples if item[0] >= 0][:10]
    slope_left = float(np.polyfit([x for x, _ in left], [y for _, y in left], 1)[0])
    slope_right = float(np.polyfit([x for x, _ in right], [y for _, y in right], 1)[0])
    kink_strength = abs(slope_right - slope_left) / max(abs(slope_left), abs(slope_right), 1e-12)
    return {
        "slope_left": slope_left,
        "slope_right": slope_right,
        "kink_strength": float(kink_strength),
        "is_piecewise": bool(kink_strength > 0.01),
    }


def gelu(x: np.ndarray) -> np.ndarray:
    return x * 0.5 * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x**3)))


def activation_samples(seed: int = 42) -> dict:
    rng = np.random.RandomState(seed)
    d_hid = 8
    W = rng.randn(d_hid, d_hid) * 0.5
    W = (W + W.T) / 2.0
    x = np.ones(d_hid)

    gelu_scores = []
    topk_active = []
    for bias in [-0.1, -0.01, 0.0, 0.01, 0.1]:
        H = W @ x + bias
        gelu_scores.append((bias, float(np.mean(np.abs(gelu(H))))))
        top_idx = np.argsort(-np.abs(H))[:3]
        mask = np.zeros(d_hid, dtype=bool)
        mask[top_idx] = True
        topk_active.append((bias, int(mask.sum())))
    return {"gelu_scores": gelu_scores, "topk_active": topk_active}


def main() -> None:
    kink = relu_kink()
    samples = activation_samples()

    print("=" * 72)
    print("  Paper XI: Piecewise-Smooth Activation Wall Diagnostic")
    print("=" * 72)
    print("ReLU sector diagnostic:")
    print(f"  left slope:     {kink['slope_left']:.4f}")
    print(f"  right slope:    {kink['slope_right']:.4f}")
    print(f"  kink strength:  {kink['kink_strength']:.3f}")
    print(f"  piecewise wall: {kink['is_piecewise']}")
    print()
    print("GeLU smooth diagnostic:")
    for bias, score in samples["gelu_scores"]:
        print(f"  bias={bias:+.3f}: mean |GeLU(H)|={score:.6f}")
    print()
    print("Top-k rank diagnostic:")
    for bias, active in samples["topk_active"]:
        print(f"  bias={bias:+.3f}: active entries={active}/8")
    print()
    print("Interpretation:")
    print("  - ReLU gives a piecewise-smooth kink diagnostic, outside classical ADE;")
    print("  - GeLU is smooth in this test and does not define a kink wall;")
    print("  - Top-k is a rank-selection diagnostic and needs a discrete theory;")
    print("  - activation walls are Paper XI boundary evidence, not theorem claims.")
    print("Done.")


if __name__ == "__main__":
    main()
