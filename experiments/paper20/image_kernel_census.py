#!/usr/bin/env python3
"""Audit the twelve Rubik shared-carrier null pairs at routed depth two."""

from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_SOURCE = HERE / "results" / "rubik_228_depth2.json"
DEFAULT_OUTPUT = HERE / "results" / "image_kernel" / "rubik_depth2_shared_carrier_v1.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper20.adapters import rubik_engine  # noqa: E402
from experiments.paper20.census import content_digest, source_reference  # noqa: E402


SCHEMA = "rime.carrier-accessibility.rubik-depth2-image-kernel.v1"
ARTIFACT_ID = "RUBIK-DEPTH2-SHARED-CARRIER-IMAGE-KERNEL-V1"
CATEGORY_KEYS = (
    "both_factors_zero",
    "prefix_zero_only",
    "suffix_zero_only",
    "nontrivial_image_kernel_annihilation",
    "active_product",
)


def _transitive_closure(adjacency: np.ndarray) -> np.ndarray:
    closure = np.asarray(adjacency, dtype=bool).copy()
    for middle in range(closure.shape[0]):
        closure |= closure[:, middle, None] & closure[middle, None, :]
    return closure


def _classify(prefix: np.ndarray, suffix: np.ndarray, tolerance: float) -> tuple[str, float, float]:
    prefix_norm = float(np.linalg.norm(prefix, "fro"))
    suffix_norm = float(np.linalg.norm(suffix, "fro"))
    product_norm = float(np.linalg.norm(suffix @ prefix, "fro"))
    prefix_zero = prefix_norm <= tolerance
    suffix_zero = suffix_norm <= tolerance
    if prefix_zero and suffix_zero:
        category = "both_factors_zero"
    elif prefix_zero:
        category = "prefix_zero_only"
    elif suffix_zero:
        category = "suffix_zero_only"
    elif product_norm <= tolerance:
        category = "nontrivial_image_kernel_annihilation"
    else:
        category = "active_product"
    return category, product_norm, min(prefix_norm, suffix_norm)


def _empty_counts() -> dict[str, int]:
    return {key: 0 for key in CATEGORY_KEYS}


def _shared_null_pairs(source: dict) -> list[tuple[int, int, list[int]]]:
    profiles = source["result"]["carrier_profiles"]
    supports = {item["sector"]: set(item["carrier_support"]) for item in profiles}
    rows = []
    for key, depth in source["result"]["minimum_active_depth_within_bound"].items():
        source_sector, target_sector = map(int, key.split("->"))
        shared = sorted(supports[source_sector] & supports[target_sector])
        if depth is None and shared:
            rows.append((source_sector, target_sector, shared))
    return sorted(rows)


def build_payload(source_path: Path = DEFAULT_SOURCE) -> dict:
    source_path = source_path.resolve()
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("model") != "rubik" or source.get("max_depth_enumerated") != 2:
        raise ValueError("image-kernel audit requires the retained Rubik depth-2 census")
    engine = rubik_engine()
    tolerance = engine.tolerance
    pairs = _shared_null_pairs(source)
    if len(pairs) != 12:
        raise AssertionError("shared-carrier null-pair registry changed")

    pair_rows = []
    aggregate = _empty_counts()
    aggregate_carrier = _empty_counts()
    global_max_product = 0.0
    global_max_min_factor = 0.0
    for source_sector, target_sector, shared_carriers in pairs:
        counts = _empty_counts()
        carrier_counts = {str(carrier): _empty_counts() for carrier in shared_carriers}
        max_product_norm = 0.0
        max_min_factor_norm = 0.0
        carrier_maxima = {
            str(carrier): {"max_product_norm": 0.0, "max_min_factor_norm": 0.0}
            for carrier in shared_carriers
        }
        for intermediate, first_transport, second_transport in product(
            range(engine.sector_count),
            range(len(engine.transports)),
            range(len(engine.transports)),
        ):
            prefix = engine.reduced_transport_block(
                first_transport, intermediate, source_sector
            )
            suffix = engine.reduced_transport_block(
                second_transport, target_sector, intermediate
            )
            category, product_norm, min_factor_norm = _classify(
                prefix, suffix, tolerance
            )
            counts[category] += 1
            max_product_norm = max(max_product_norm, product_norm)
            max_min_factor_norm = max(max_min_factor_norm, min_factor_norm)
            for carrier in shared_carriers:
                carrier_prefix = engine.carrier_reduced_transport_block(
                    carrier, first_transport, intermediate, source_sector
                )
                carrier_suffix = engine.carrier_reduced_transport_block(
                    carrier, second_transport, target_sector, intermediate
                )
                carrier_category, carrier_product, carrier_min_factor = _classify(
                    carrier_prefix, carrier_suffix, tolerance
                )
                carrier_counts[str(carrier)][carrier_category] += 1
                maxima = carrier_maxima[str(carrier)]
                maxima["max_product_norm"] = max(maxima["max_product_norm"], carrier_product)
                maxima["max_min_factor_norm"] = max(
                    maxima["max_min_factor_norm"], carrier_min_factor
                )
        route_count = engine.sector_count * len(engine.transports) ** 2
        if sum(counts.values()) != route_count:
            raise AssertionError("route category partition is incomplete")
        for key in CATEGORY_KEYS:
            aggregate[key] += counts[key]
            aggregate_carrier[key] += sum(row[key] for row in carrier_counts.values())
        global_max_product = max(global_max_product, max_product_norm)
        global_max_min_factor = max(global_max_min_factor, max_min_factor_norm)
        pair_rows.append(
            {
                "source_sector": source_sector,
                "target_sector": target_sector,
                "display_pair": f"S{source_sector + 1}->S{target_sector + 1}",
                "shared_carriers": shared_carriers,
                "route_count": route_count,
                "route_categories": counts,
                "carrier_route_categories": carrier_counts,
                "carrier_numerical_maxima": carrier_maxima,
                "max_product_norm": max_product_norm,
                "max_min_factor_norm": max_min_factor_norm,
                "depth_two_status": "BOUNDED_FACTOR_ZERO_OBSERVATION",
            }
        )

    adjacency = engine.direct_support() > engine.support_tolerance
    closure = _transitive_closure(adjacency)
    isolated = [
        sector
        for sector in range(engine.sector_count)
        if set(np.flatnonzero(adjacency[:, sector])) == {sector}
        and set(np.flatnonzero(adjacency[sector, :])) == {sector}
    ]
    all_absent = all(not closure[target, source] for source, target, _ in pairs)
    source_artifacts = [
        source_reference(HERE / "engine.py"),
        source_reference(HERE / "adapters.py"),
        source_reference(Path(__file__).resolve()),
        source_reference(source_path),
    ]
    for reference in source.get("source_artifacts", []):
        if reference["uri"] not in {item["uri"] for item in source_artifacts}:
            source_artifacts.append(reference)
    payload = {
        "schema_version": SCHEMA,
        "artifact_id": ARTIFACT_ID,
        "model": "rubik",
        "dimension": engine.dimension,
        "sector_count": engine.sector_count,
        "transport_count": len(engine.transports),
        "audited_depth": 2,
        "cut_after_transport": 1,
        "route_count_per_pair": engine.sector_count * len(engine.transports) ** 2,
        "tolerance": tolerance,
        "support_tolerance": engine.support_tolerance,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "arithmetic": "complex128_with_declared_thresholds",
        },
        "claim_status": "mixed_evidence_bundle",
        "claim_status_by_component": {
            "finite_route_space_enumeration": "Computational Certificate",
            "factor_and_product_norms": "Computational Observation",
            "exact_projected_factor_zero": "Not Established",
            "exact_all_depth_zero": "Not Established",
        },
        "evidence_layers": {
            "enumeration_certificate": {
                "status": "EXACT_FINITE_ENUMERATION_CERTIFICATE",
                "scope": (
                    "Exhaustive index coverage for the twelve pairs selected by the "
                    "frozen bounded numerical source census."
                ),
                "selection_basis": "BOUNDED_NUMERICAL_SOURCE_CENSUS",
                "pair_count": len(pairs),
                "route_count_per_pair_formula": "9 * 18^2 = 2916",
                "route_audit_count_formula": "12 * 2916 = 34992",
                "shared_carrier_route_audit_count": sum(
                    row["route_count"] * len(row["shared_carriers"])
                    for row in pair_rows
                ),
                "does_not_certify": "Exact zero or nonzero status of any projected matrix.",
            },
            "numerical_observation": {
                "status": "BOUNDED_NUMERICAL_OBSERVATION",
                "coefficient_backend": "complex128",
                "activity_tolerance": tolerance,
                "support_tolerance": engine.support_tolerance,
                "scope": "Factor norms and product norms at routed depth two.",
            },
            "exact_zero_status": {
                "status": "NOT_ESTABLISHED",
                "projected_factor_zero": "NOT_ESTABLISHED",
                "nontrivial_image_kernel_absence": "NOT_ESTABLISHED_AS_EXACT",
                "all_depth_zero": "NOT_ESTABLISHED",
            },
        },
        "claim_boundary": (
            "Finite route-index coverage is certified exactly, while factor/product "
            "zero classifications are bounded complex128 observations. Thresholded "
            "direct-support isolation is not an exact all-depth zero theorem."
        ),
        "source_census": {
            "artifact": source_reference(source_path),
            "content_sha256": source["content_sha256"],
        },
        "source_artifacts": source_artifacts,
        "selection": {
            "rule": "minimum_active_depth_within_bound is null and endpoint carrier supports overlap",
            "pair_count": len(pairs),
            "pairs": [[source, target] for source, target, _ in pairs],
        },
        "thresholded_support_graph": {
            "isolated_self_loop_sectors": isolated,
            "all_selected_pairs_absent_from_transitive_closure": all_absent,
            "status": "NUMERICAL_SUPPORT_REGISTRATION_ONLY",
        },
        "pair_audits": pair_rows,
        "aggregate": {
            "pair_count": len(pairs),
            "route_audit_count": sum(row["route_count"] for row in pair_rows),
            "shared_carrier_route_audit_count": sum(
                row["route_count"] * len(row["shared_carriers"]) for row in pair_rows
            ),
            "route_categories": aggregate,
            "shared_carrier_route_categories": aggregate_carrier,
            "max_product_norm": global_max_product,
            "max_min_factor_norm": global_max_min_factor,
            "nontrivial_image_kernel_annihilation_count": aggregate[
                "nontrivial_image_kernel_annihilation"
            ],
            "conclusion": "ALL_DEPTH_TWO_ROUTES_FACTOR_ZERO_WITHIN_TOLERANCE",
            "all_depth_exact_status": "NOT_ESTABLISHED",
        },
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(args.source)
    output = args.out if args.out.is_absolute() else ROOT / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "artifact_id": payload["artifact_id"],
                "route_audit_count": payload["aggregate"]["route_audit_count"],
                "content_sha256": payload["content_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
