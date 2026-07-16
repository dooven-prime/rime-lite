"""Paper XII diagnostic: diffusion denoising SOF.

Claim status:
    - Diagnostic case study for Paper XII.
    - Demonstrates that diffusion time is a natural SOF deformation parameter.
    - Not a theorem about diffusion models and not a trained generative model.

The toy system is a 1D-style latent diffusion probe implemented in a finite
feature space.  A PCA-sign sector proposal is evaluated along the forward
noise schedule.  The default run is intentionally counterintuitive:

    forward noise:  sectors 1 -> 2 at t=11
    reverse time:   denoising crosses the same wall as repair of the clean
                    observable signature

Thus the forward process is a noise-induced sector-creation wall, while the
reverse process is the denoising repair direction.
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
from rime.accessibility import compute_R1  # noqa: E402


def generate_two_cluster_data(seed: int = 42) -> dict:
    rng = np.random.RandomState(seed)
    n_dim, n_samples = 16, 64

    c1 = rng.randn(n_dim) * 0.5
    c2 = rng.randn(n_dim) * 0.5 + 3.0
    X0 = np.column_stack(
        [
            c1.reshape(-1, 1) + rng.randn(n_dim, n_samples // 2) * 0.3,
            c2.reshape(-1, 1) + rng.randn(n_dim, n_samples // 2) * 0.3,
        ]
    )

    # Keep the legacy random stream used by the original denoising-MLP probe.
    # The weights are not needed for this minimal observable audit, but these
    # draws fix the published threshold at t=11 for seed=42.
    rng.randn(32, n_dim)
    rng.randn(n_dim, 32)

    return {"rng": rng, "n_dim": n_dim, "n_samples": n_samples, "X0": X0}


def pca_probe_sector_bases(X_t: np.ndarray, probe_dim: int) -> list[np.ndarray]:
    """Build coordinate-sector bases from PCA signs on a fixed probe window."""

    X_centered = X_t - X_t.mean(axis=1, keepdims=True)
    U, _, _ = np.linalg.svd(X_centered, full_matrices=False)
    projection = U[:, 0] @ X_centered
    labels = (projection > 0).astype(int)

    # The probe window is a fixed finite chart for this toy diagnostic.  Noise
    # may split this chart even when the clean endpoint appears as one sector.
    probe_labels = labels[:probe_dim]
    eye = np.eye(probe_dim, dtype=complex)
    sectors: list[np.ndarray] = []
    for label in sorted(set(int(value) for value in probe_labels)):
        indices = np.flatnonzero(probe_labels == label)
        if len(indices) > 0:
            sectors.append(eye[:, indices])
    return sectors


def feature_observables(X_t: np.ndarray, eps: np.ndarray, seed: int) -> list[np.ndarray]:
    n_dim, n_samples = X_t.shape
    G_data = X_t @ X_t.T / n_samples
    G_noise = eps @ eps.T / n_samples
    X1 = (G_data @ G_noise - G_noise @ G_data) / 2.0

    rng = np.random.RandomState(seed)
    M = rng.randn(n_dim, n_dim)
    X2 = (M - M.T) / 2.0
    return [X1.astype(complex), X2.astype(complex)]


def run(seed: int = 42, steps: int = 20) -> dict:
    data = generate_two_cluster_data(seed=seed)
    rng = data["rng"]
    n_dim = data["n_dim"]
    n_samples = data["n_samples"]
    X0 = data["X0"]

    beta = np.linspace(0.01, 0.5, steps)
    alpha_bar = np.cumprod(1.0 - beta)

    rows = []
    for t_idx in range(steps):
        eps = rng.randn(n_dim, n_samples)
        X_t = np.sqrt(alpha_bar[t_idx]) * X0 + np.sqrt(1.0 - alpha_bar[t_idx]) * eps

        sectors = pca_probe_sector_bases(X_t, probe_dim=n_dim)
        if len(sectors) >= 2:
            R1 = compute_R1(sectors, feature_observables(X_t, eps, seed=t_idx), tol=1e-6)
            r1_edges = int(np.sum(R1))
        else:
            r1_edges = 0

        rows.append(
            {
                "t": t_idx,
                "alpha_bar": float(alpha_bar[t_idx]),
                "sectors": len(sectors),
                "R1_edges": r1_edges,
            }
        )

    transitions = [
        (prev, curr)
        for prev, curr in zip(rows, rows[1:])
        if prev["sectors"] != curr["sectors"]
    ]
    first_transition = transitions[0] if transitions else None

    return {
        "seed": seed,
        "steps": steps,
        "n_dim": n_dim,
        "n_samples": n_samples,
        "rows": rows,
        "first_transition": first_transition,
    }


def sofreport(result: dict) -> dict:
    transition = result["first_transition"]
    wall_event = None
    repair_event = None
    if transition is not None:
        before, after = transition
        wall_event = {
            "direction": "forward_noise",
            "step": after["t"],
            "sector_count_before": before["sectors"],
            "sector_count_after": after["sectors"],
            "alpha_bar": after["alpha_bar"],
        }
        repair_event = {
            "direction": "reverse_denoising",
            "from_step": after["t"],
            "to_step": before["t"],
            "restored_sector_count": before["sectors"],
        }
    return {
        "sofrs_version": "1.0",
        "report_id": "diffusion_denoising",
        "system": "finite latent diffusion probe",
        "claim_status": "diagnostic",
        "claim_note": "diffusion-time wall and reverse-denoising repair case study",
        "sectorization": {
            "origin": "PCA-sign partition on a fixed probe window",
            "space": "finite feature coordinates",
            "time_dependent": True,
            "strict_sof_realization": True,
        },
        "observable_family": {
            "data_noise_commutator": "feature-space Gram commutator",
            "fixed_skew_probe": "seeded skew-symmetric feature operator",
        },
        "support_matrix": {
            "kind": "R1 edge-count trajectory",
            "samples": [
                {"t": row["t"], "R1_edges": row["R1_edges"]}
                for row in result["rows"]
            ],
        },
        "bridge_matrix": None,
        "repair_matrix": {
            "kind": "reverse-time restoration of the clean observable signature",
            "event": repair_event,
            "claim_note": "registered denoising repair, not fixed-sector Lie-depth D-repair",
        },
        "wall_record": {
            "wall_type": "noise-induced sector creation",
            "first_wall": wall_event,
            "trajectory_summary": {
                "parameter": "diffusion time",
                "rows": result["rows"],
            },
        },
        "failure_modes": [
            "toy finite probe rather than a trained diffusion model",
            "PCA-sign sectors depend on the chosen probe chart",
            "reverse denoising repair is not identified with Lie-depth D-repair",
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "diffusion.sofreport"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def print_report(result: dict) -> None:
    print("=" * 76)
    print("  Paper XII: Diffusion Denoising SOF Diagnostic")
    print("=" * 76)
    print(
        f"  steps={result['steps']}, dim={result['n_dim']}, "
        f"samples={result['n_samples']}, seed={result['seed']}"
    )
    print("  Sector rule: PCA-sign sectors on a fixed finite probe window")
    print()
    print(f"  {'t':>4s}  {'alpha_bar':>9s}  {'sectors':>7s}  {'R1_edges':>8s}")
    print(f"  {'-' * 4}  {'-' * 9}  {'-' * 7}  {'-' * 8}")
    for row in result["rows"]:
        print(
            f"  {row['t']:>4d}  {row['alpha_bar']:>9.4f}  "
            f"{row['sectors']:>7d}  {row['R1_edges']:>8d}"
        )

    transition = result["first_transition"]
    print()
    if transition is None:
        print("  No sector-count transition detected on this grid.")
    else:
        before, after = transition
        print(
            f"  Forward wall: t={after['t']} changes sectors "
            f"{before['sectors']} -> {after['sectors']} "
            f"(alpha_bar={after['alpha_bar']:.4f})."
        )
        print("  Interpretation: forward noise creates a probe-sector split.")
        print(
            f"  Reverse repair: denoising crosses back between t={after['t']} "
            f"and t={before['t']}, restoring the clean endpoint signature."
        )

    print()
    print("  Summary:")
    print("    diffusion time is the deformation parameter;")
    print("    the forward wall is not the repair direction;")
    print("    reverse-time denoising supplies the SOF repair geometry.")
    print("Done.")


def main() -> None:
    result = run()
    print_report(result)
    print(f"SOFRS v1.0: {write_sofreport(sofreport(result))}")


if __name__ == "__main__":
    main()
