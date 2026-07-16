"""Paper XII diagnostic: transformer batch/sector aggregation sweep.

Claim status:
    - Diagnostic robustness check for Paper XII transformer-style SOFs.
    - Shows that enlarging token groups preserves the qualitative repair/freeze
      pattern in a fixed sparse sector graph.
    - Synthetic token-partition model, not a theorem about trained LLMs.

Canonical row:
    5 sectors x 50 tokens, dim=300
    frozen_R1 = 14, D_repaired = 6, frozen_D = 8
    sector 4 is permanently frozen from sectors 0--3

The model uses token-bin sectors.  Sectors 0--3 form a sparse chain, so
non-adjacent pairs inside that component are repaired by Lie depth.  The final
sector is isolated, producing permanent frozen pairs.
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


def token_bin_sectors(n_sectors: int, tokens_per_sector: int, ambient_dim: int) -> list[np.ndarray]:
    eye = np.eye(ambient_dim, dtype=complex)
    sectors = []
    for idx in range(n_sectors):
        start = idx * tokens_per_sector
        stop = start + tokens_per_sector
        sectors.append(eye[:, start:stop])
    return sectors


def chain_generators(sectors: list[np.ndarray], active_sectors: int) -> list[np.ndarray]:
    generators = []
    for idx in range(active_sectors - 1):
        X = np.outer(sectors[idx][:, 0], sectors[idx + 1][:, 0])
        generators.append(((X - X.T) / 2.0).astype(complex))
    return generators


def audit_config(n_sectors: int, tokens_per_sector: int, ambient_dim: int) -> dict:
    sectors = token_bin_sectors(n_sectors, tokens_per_sector, ambient_dim)
    active_sectors = n_sectors - 1
    generators = chain_generators(sectors, active_sectors=active_sectors)
    engine = AccessibilityEngine(sectors, generators, tol=1e-8, max_depth=4)
    audit = engine.audit()
    frozen = engine.frozen_pairs()
    R1, R2, _ = engine.support()
    D, _ = engine.depth()
    isolated_sector = n_sectors - 1

    return {
        "n_sectors": n_sectors,
        "tokens_per_sector": tokens_per_sector,
        "ambient_dim": ambient_dim,
        "isolated_sector": isolated_sector,
        "ordered_pairs": n_sectors * (n_sectors - 1),
        "support_graph": np.any(R1, axis=0),
        "bridge_graph": np.any(R2, axis=0),
        "D": D,
        **audit,
        **frozen,
    }


def run() -> list[dict]:
    configs = [
        (4, 50, 240),
        (5, 50, 300),
        (6, 50, 360),
    ]
    return [audit_config(*config) for config in configs]


def sofreport(rows: list[dict]) -> dict:
    canonical = next(row for row in rows if row["n_sectors"] == 5)
    return {
        "sofrs_version": "1.0",
        "report_id": "transformer_batch_sweep",
        "system": "synthetic token-bin transformer sector sweep",
        "claim_status": "diagnostic",
        "claim_note": "sector-count robustness diagnostic",
        "sectorization": {
            "origin": "equal-size token bins",
            "configurations": [
                {
                    "sector_count": row["n_sectors"],
                    "tokens_per_sector": row["tokens_per_sector"],
                    "ambient_dim": row["ambient_dim"],
                    "isolated_sector": row["isolated_sector"],
                }
                for row in rows
            ],
            "realization_status": "constructed finite realization",
        },
        "observable_family": {
            "chain_generators": "nearest-neighbor sparse skew generators over active token sectors"
        },
        "support_matrix": {
            "kind": "aggregated_R1_by_configuration",
            "configurations": [
                {
                    "sector_count": row["n_sectors"],
                    "matrix": row["support_graph"].astype(int).tolist(),
                    "offdiag_density_pct": row["R1_pct"],
                    "frozen_R1": row["frozen_R1"],
                }
                for row in rows
            ],
        },
        "bridge_matrix": {
            "kind": "aggregated_R2_by_configuration",
            "configurations": [
                {
                    "sector_count": row["n_sectors"],
                    "matrix": row["bridge_graph"].astype(int).tolist(),
                    "offdiag_density_pct": row["R2_pct"],
                }
                for row in rows
            ],
        },
        "repair_matrix": {
            "kind": "Lie-depth repair by configuration",
            "configurations": [
                {
                    "sector_count": row["n_sectors"],
                    "depth_matrix": row["D"].astype(int).tolist(),
                    "D_repaired": row["D_repaired"],
                    "frozen_D": row["frozen_D"],
                    "D_max": row["D_max"],
                }
                for row in rows
            ],
            "canonical_five_sector_row": {
                "frozen_R1": canonical["frozen_R1"],
                "D_repaired": canonical["D_repaired"],
                "frozen_D": canonical["frozen_D"],
                "isolated_sector": canonical["isolated_sector"],
            },
        },
        "wall_record": {
            "status": "not_computed",
            "reason": "discrete sector-count robustness sweep, not a parameterized wall map",
            "trajectory_summary": {
                "sector_counts": [row["n_sectors"] for row in rows],
                "frozen_R1": [row["frozen_R1"] for row in rows],
                "D_repaired": [row["D_repaired"] for row in rows],
                "frozen_D": [row["frozen_D"] for row in rows],
            },
        },
        "failure_modes": [
            "synthetic token-bin model rather than a trained language model",
            "the isolated final sector is constructed by design",
            "changing sector count is a robustness sweep, not a continuous deformation",
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "transformer_batch.sofreport"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def print_depth_matrix(D: np.ndarray) -> None:
    for i in range(D.shape[0]):
        row = " ".join(f"{D[i, j]:>3d}" if i != j else "  -" for j in range(D.shape[1]))
        print(f"      {i}: [{row}]")


def print_report(rows: list[dict]) -> None:
    print("=" * 86)
    print("  Paper XII: Transformer Batch/Sector Aggregation Sweep")
    print("=" * 86)
    print("  Sectors are token bins; sectors 0..n-2 form a chain; the last sector is isolated.")
    print("  Claim status: synthetic robustness diagnostic, not an LLM theorem.")

    for row in rows:
        print()
        print(
            f"  {row['n_sectors']} sectors x {row['tokens_per_sector']} tokens "
            f"(dim={row['ambient_dim']}, ordered_pairs={row['ordered_pairs']}):"
        )
        print(
            f"    R1={row['R1_pct']:.1f}%, R2={row['R2_pct']:.1f}%, "
            f"Dmax={row['D_max']}, Drep={row['D_repaired']}, "
            f"frzR1={row['frozen_R1']}, frzD={row['frozen_D']}"
        )
        print(f"    permanently frozen sector: {row['isolated_sector']}")
        print("    D matrix:")
        print_depth_matrix(row["D"])

    canonical = next(row for row in rows if row["n_sectors"] == 5)
    print()
    print("  Canonical 5-sector row:")
    print(
        f"    frozen_R1={canonical['frozen_R1']}, "
        f"D_repaired={canonical['D_repaired']}, "
        f"frozen_D={canonical['frozen_D']}, "
        f"isolated sector={canonical['isolated_sector']}"
    )
    print()
    print("  Interpretation:")
    print("    enlarging the token partition increases the number of sector pairs;")
    print("    it does not change the qualitative chain-repair plus isolated-freeze pattern;")
    print("    the batch sweep is a diagnostic stress test, not a new theory layer.")
    print("Done.")


def main() -> None:
    rows = run()
    print_report(rows)
    print(f"SOFRS v1.0: {write_sofreport(sofreport(rows))}")


if __name__ == "__main__":
    main()
