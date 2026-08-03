"""Build the versioned Paper X Registry-evidence result record."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import platform
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PAPER_DIR / "results"
RESULT_PATH = RESULTS_DIR / "registry_evidence_v2.json"
sys.path.insert(0, str(ROOT))

from experiments.paper10.barrier_option_sof import audit as barrier_audit  # noqa: E402
from experiments.paper10.control_pde_combinatorial_sof import audit as portability_audit  # noqa: E402
from experiments.paper9.calibrated_response import audit as response_audit  # noqa: E402
from experiments.paper10.markov_graph_sof import audit as markov_graph_audit  # noqa: E402
from experiments.paper10.ncg_spectral_triple_sof import audit as ncg_audit  # noqa: E402
from experiments.paper10.rubik_wild_type34_audit import audit as rubik_audit  # noqa: E402
from experiments.paper10.tau_quantum_graph_yang import (  # noqa: E402
    graph_edge_rewiring,
    quantum_linear_interpolation,
    yang_state_mixing,
)


SOURCE_PATHS = (
    "experiments/paper9/calibrated_response.py",
    "experiments/paper10/rubik_wild_type34_audit.py",
    "experiments/paper10/ncg_spectral_triple_sof.py",
    "experiments/paper10/control_pde_combinatorial_sof.py",
    "experiments/paper10/barrier_option_sof.py",
    "experiments/paper10/markov_graph_sof.py",
    "experiments/paper10/tau_quantum_graph_yang.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tau_payload(result) -> dict:
    return asdict(result)


def build() -> dict:
    response = response_audit()
    rubik = rubik_audit()
    ncg = ncg_audit()
    portability = portability_audit()
    barrier = barrier_audit()
    markov_graph = markov_graph_audit()
    quantum = quantum_linear_interpolation()
    graph = graph_edge_rewiring()
    yang = yang_state_mixing()

    return {
        "schema": "paper10.registry-evidence.v2",
        "claim_scope": (
            "source-addressed finite certificates and observations for Registry "
            "v2.0; no cross-carrier promotion or common dynamics theorem"
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "builder": "experiments/paper10/validation/build_results.py",
            "source_sha256": {
                relative: sha256(ROOT / relative) for relative in SOURCE_PATHS
            },
        },
        "response_control": {
            "tau_fast": response["tau_k0_grow"],
            "tau_slow": response["tau_k1_response"],
            "ratio": response["ratio"],
            "policy": "normalized displacement with common half-response threshold",
            "claim_status": "Computational Certificate",
        },
        "rubik_low_order": {
            "sector_count": rubik["n_sectors"],
            "lie_generator_count": rubik["n_generators"],
            "commutator_cancellation_count": rubik[
                "commutator_cancellation_count"
            ],
            "routed_image_kernel_incidence_count": rubik[
                "routed_image_kernel_incidence_count"
            ],
            "claim_status": "Computational Certificate",
        },
        "finite_spectral_triple": {
            "dimension": ncg["dim"],
            "sector_count": ncg["n_sectors"],
            "central_lipschitz_zero": ncg["central_lipschitz_zero"],
            "cross_block_distance": ncg["connes_distance_cross_blocks"],
            "ordered_routed_bridge_count": ncg["ordered_routed_bridge_count"],
        },
        "portability": {
            "control": {
                "kalman_ranks": portability["control"]["kalman_ranks"],
                "terminal_word_depth": portability["control"]["D_0_to_2"],
                "depth_cutoff": 3,
            },
            "pde": {
                "left_to_right_word_depth": portability["pde"][
                    "D_left_to_right"
                ],
                "depth_cutoff": 4,
            },
            "combinatorial": {
                "inter_color_edges": portability["combinatorial"][
                    "inter_color_edges"
                ],
                "same_color_conflicts": portability["combinatorial"][
                    "same_color_conflicts"
                ],
            },
        },
        "barrier_option": {
            "labelled_direct_support_count": barrier[
                "labelled_direct_support_count"
            ],
            "labelled_direct_support_possible": barrier[
                "labelled_direct_support_possible"
            ],
            "labelled_direct_support_pct": barrier[
                "labelled_direct_support_pct"
            ],
            "mean_first_hit_time": barrier["tau_hit"],
            "claim_status": "Computational Observation",
        },
        "markov_graph_static": markov_graph["realizations"],
        "proxy_boundaries": {
            "quantum": [
                {
                    "name": row["name"],
                    "status": row["status"],
                    "taus": [tau_payload(value) for value in row["taus"]],
                }
                for row in quantum
            ],
            "graph": {
                "status": graph["status"],
                "taus": [tau_payload(value) for value in graph["taus"]],
            },
            "yang_like": {
                "status": yang["status"],
                "taus": [tau_payload(value) for value in yang["taus"]],
            },
            "claim_status": "Computational Observation",
            "negative_boundary": (
                "No proxy-to-shadow, mechanism-sufficiency, or universal rate "
                "claim is inferred."
            ),
        },
    }


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = build()
    RESULT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {RESULT_PATH}")


if __name__ == "__main__":
    main()
