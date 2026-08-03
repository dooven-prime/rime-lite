"""Validate current Paper X experiment invariants and Registry bindings."""

from __future__ import annotations

import argparse
import json
import math

try:
    import _bootstrap
except ModuleNotFoundError:
    from . import _bootstrap

ROOT = _bootstrap.ROOT


from experiments.paper10.barrier_option_sof import audit as barrier_audit  # noqa: E402
from experiments.paper10.control_pde_combinatorial_sof import audit as portability_audit  # noqa: E402
from experiments.paper9.calibrated_response import audit as response_audit  # noqa: E402
from experiments.paper10.markov_graph_sof import audit as markov_graph_audit  # noqa: E402
from experiments.paper10.ncg_spectral_triple_sof import audit as ncg_audit  # noqa: E402
from experiments.paper10.rubik_wild_type34_audit import audit as rubik_audit  # noqa: E402
from experiments.paper10.validation.build_results import (  # noqa: E402
    RESULT_PATH,
    SOURCE_PATHS,
    sha256,
)
from experiments.paper10.validation.build_legacy_certificate_imports import (  # noqa: E402
    RESULT_PATH as LEGACY_IMPORT_PATH,
    SOURCE_PATHS as LEGACY_SOURCE_PATHS,
    V1_PATH,
)
from registry.validate_snapshot import SCHEMAS, validate_payload  # noqa: E402


REGISTRY_PATH = ROOT / "registry" / "paper10-typed-v2.0.registry.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_registry() -> None:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMAS["2.0"].read_text(encoding="utf-8"))
    errors = validate_payload(payload, schema)
    require(not errors, "Registry v2.0 validation failed:\n" + "\n".join(errors))
    require(len(payload["entries"]) == 19, "Registry v2.0 must contain 19 rows")
    summary = payload["census_certificate"]["summary"]
    require(summary["finding_count"] == 28, "Registry finding census changed")
    require(
        summary["capability_counts"]["word_carrier"] == 4,
        "Registry word-carrier census changed",
    )
    require(
        summary["capability_counts"]["lie_hall_carrier"] == 5,
        "Registry Lie/Hall-carrier census changed",
    )
    entries = {entry["id"]: entry for entry in payload["entries"]}
    for entry_id in ("markov-systems", "graph-systems"):
        entry = entries[entry_id]
        require(
            entry["capabilities"]["word_carrier"]["availability"] == "DECLARED",
            f"{entry_id} lacks its word carrier",
        )
        require(
            entry["capabilities"]["lie_hall_carrier"]["availability"]
            == "NOT_DECLARED",
            f"{entry_id} acquired an undeclared Lie/Hall carrier",
        )
        depth_channel = next(
            channel
            for channel in entry["observable_channels"]
            if channel["id"] == "channel.d-word"
        )
        require(
            depth_channel["depth_mode"] == "exact"
            and depth_channel["saturation_status"] == "exact_saturated",
            f"{entry_id} lost exact word-depth registration",
        )
    require(
        any(
            artifact["uri"]
            == "experiments/paper10/results/registry_evidence_v2.json"
            for artifact in payload["artifacts"]
        ),
        "Registry v2.0 does not bind the Paper X result record",
    )


def validate_result_record() -> None:
    record = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    require(
        record["schema"] == "paper10.registry-evidence.v2",
        "unexpected Paper X result schema",
    )
    source_hashes = record["runtime"]["source_sha256"]
    for relative in SOURCE_PATHS:
        require(
            source_hashes.get(relative) == sha256(ROOT / relative),
            f"stale Paper X result source hash: {relative}",
        )

    require(record["response_control"]["tau_fast"] == 30, "recorded fast tau changed")
    require(record["response_control"]["tau_slow"] == 1380, "recorded slow tau changed")
    require(
        record["rubik_low_order"]["commutator_cancellation_count"] == 288,
        "recorded Rubik cancellation count changed",
    )
    require(
        record["rubik_low_order"]["routed_image_kernel_incidence_count"] == 528,
        "recorded Rubik incidence count changed",
    )
    require(
        record["barrier_option"]["labelled_direct_support_count"] == 3,
        "recorded barrier support count changed",
    )
    markov_graph = record["markov_graph_static"]
    require(
        markov_graph["markov"]["findings"]["maximum_finite_word_depth"] == 2,
        "recorded Markov word depth changed",
    )
    require(
        markov_graph["graph"]["findings"]["maximum_finite_word_depth"] == 5,
        "recorded graph word depth changed",
    )
    require(
        markov_graph["graph"]["findings"]["word_two_support_count"] == 8,
        "recorded graph length-two word support changed",
    )
    require(
        all(
            item["status"] == "DEGENERATE"
            for item in record["proxy_boundaries"]["quantum"]
        ),
        "recorded quantum proxy boundary changed",
    )
    require(
        record["proxy_boundaries"]["graph"]["status"] == "DEGENERATE",
        "recorded graph proxy boundary changed",
    )
    require(
        record["proxy_boundaries"]["yang_like"]["status"] == "DEGENERATE",
        "recorded Yang-like proxy boundary changed",
    )


def validate_legacy_import_record() -> None:
    record = json.loads(LEGACY_IMPORT_PATH.read_text(encoding="utf-8"))
    require(
        record["schema"] == "paper10.legacy-certificate-imports.v2",
        "unexpected legacy-import schema",
    )
    require(
        record["source_snapshot"]["sha256"] == sha256(V1_PATH),
        "legacy-import v1 source digest is stale",
    )
    source_hashes = {
        item["path"]: item["sha256"] for item in record["source_scripts"]
    }
    for relative in LEGACY_SOURCE_PATHS:
        require(
            source_hashes.get(relative) == sha256(ROOT / relative),
            f"stale legacy-import source hash: {relative}",
        )
    records = record["records"]
    require(
        records["constructed_commutator_cancellation"]["value"]
        == "constructed positive and negative controls",
        "constructed cancellation import changed",
    )
    quantum = records["quantum_static_repair"]
    require(
        quantum["carrier_id"] == "quantum.gates.principal-log-skew.hall-v1",
        "quantum carrier registration changed",
    )
    require(
        quantum["generator_registration"]["gate_labels"] == ["H", "S", "CNOT"],
        "quantum generator list changed",
    )
    require(
        quantum["generator_registration"]["normalization"] == "none",
        "quantum generator normalization changed",
    )
    require(
        quantum["hall_filtration"]["tested_depth_indices"] == [0, 1, 2, 3],
        "quantum Hall filtration indexing changed",
    )
    require(quantum["zero_tolerance"] == 1e-6, "quantum tolerance changed")
    require(
        quantum["pair_scope"] == "off_diagonal_ordered",
        "quantum pair scope changed",
    )
    require(quantum["pauli_repair_count"] == 0, "Pauli repair import changed")
    require(
        quantum["clifford_cnot_repair_count"] == 6,
        "Clifford+CNOT repair import changed",
    )


def validate_fast_results() -> None:
    response = response_audit()
    require(response["tau_k0_grow"] == 30, "fast half-response time changed")
    require(response["tau_k1_response"] == 1380, "slow half-response time changed")
    require(response["measured_separation"], "calibrated response ordering failed")
    require(response["k1_response"][0] == 0.0, "slow displacement must start at zero")

    rubik = rubik_audit()
    require(rubik["n_sectors"] == 9, "Rubik sector count changed")
    require(rubik["n_generators"] == 18, "Rubik Lie-family size changed")
    require(
        rubik["commutator_cancellation_count"] == 288,
        "Rubik commutator-cancellation count changed",
    )
    require(
        rubik["routed_image_kernel_incidence_count"] == 528,
        "Rubik routed-incidence count changed",
    )

    ncg = ncg_audit()
    require(ncg["central_lipschitz_zero"], "central Lipschitz audit failed")
    require(
        ncg["ordered_routed_bridge_count"] == 2,
        "finite spectral-triple routed-bridge count changed",
    )

    portability = portability_audit()
    require(portability["control"]["kalman_ranks"] == [1, 2, 3], "Kalman ranks changed")

    markov_graph = markov_graph_audit()["realizations"]
    require(
        markov_graph["markov"]["findings"]["direct_support_count"] == 3,
        "Markov direct support changed",
    )
    require(
        markov_graph["markov"]["findings"]["word_two_support_count"] == 6,
        "Markov length-two word support changed",
    )
    require(
        markov_graph["graph"]["findings"]["direct_support_count"] == 10,
        "graph direct support changed",
    )
    require(
        markov_graph["graph"]["findings"]["maximum_finite_word_depth"] == 5,
        "graph exact word depth changed",
    )
    require(portability["control"]["D_0_to_2"] == 2, "control word depth changed")
    require(portability["pde"]["D_left_to_right"] == 2, "PDE word depth changed")
    require(
        portability["combinatorial"]["inter_color_edges"] == 4,
        "inter-color support count changed",
    )
    require(
        portability["combinatorial"]["same_color_conflicts"] == 2,
        "same-color conflict count changed",
    )

    barrier = barrier_audit()
    require(
        barrier["labelled_direct_support_count"] == 3
        and barrier["labelled_direct_support_possible"] == 4,
        "barrier labelled-support census changed",
    )
    require(
        math.isclose(barrier["tau_hit"], 6.5915, rel_tol=0.0, abs_tol=5e-5),
        "barrier first-hit proxy changed",
    )


def validate_slow_boundaries() -> None:
    from experiments.paper10.tau_quantum_graph_yang import (  # noqa: PLC0415
        graph_edge_rewiring,
        quantum_linear_interpolation,
        yang_state_mixing,
    )

    quantum = quantum_linear_interpolation()
    require(all(row["status"] == "DEGENERATE" for row in quantum), "quantum boundary changed")
    require(graph_edge_rewiring()["status"] == "DEGENERATE", "graph boundary changed")
    require(yang_state_mixing()["status"] == "DEGENERATE", "Yang-like boundary changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="recompute the current finite scientific fixtures",
    )
    parser.add_argument(
        "--include-slow",
        action="store_true",
        help="also recompute the slow proxy-boundary fixtures",
    )
    args = parser.parse_args()

    validate_result_record()
    validate_legacy_import_record()
    validate_registry()
    if args.recompute or args.include_slow:
        validate_fast_results()
    if args.include_slow:
        validate_slow_boundaries()

    if args.include_slow:
        scope = "artifact chain + finite recomputation + slow boundaries"
    elif args.recompute:
        scope = "artifact chain + finite recomputation"
    else:
        scope = "artifact chain"
    print(f"PASS Paper X release validation ({scope})")
    if not args.recompute:
        print("Scientific fixtures not recomputed; use --recompute to include them.")
    if not args.include_slow:
        print("Slow proxy boundaries not recomputed; use --include-slow to include them.")


if __name__ == "__main__":
    main()
