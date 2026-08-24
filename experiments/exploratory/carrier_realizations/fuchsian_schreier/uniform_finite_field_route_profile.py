#!/usr/bin/env python3
"""Exact fixed-depth route profiles for the modular finite-field family.

This is a census/classification layer, not a universality theorem. Every
profile is relative to the declared carrier, labelled alphabet, marked
partition, word order, and routed-product semantics.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence

from core import content_digest, exact_word_layers, file_digest, is_prime
from core import modular_generators, permutation_orbits


PACKAGE_PATH = "experiments/exploratory/carrier_realizations/fuchsian_schreier"
SCHEMA = "rime.exploratory.fuchsian-schreier.uniform-finite-field-route-profile.v1"
LABELS = ("S", "R", "R_inv")


def _sector_index(sectors: Sequence[Sequence[int]]) -> dict[int, int]:
    return {
        state: index
        for index, sector in enumerate(sectors)
        for state in sector
    }


def _direct_support(named_generators, sectors):
    labels = _sector_index(sectors)
    support = []
    for _, permutation in named_generators:
        matrix = [[False for _ in sectors] for _ in sectors]
        for source, target in enumerate(permutation):
            matrix[labels[target]][labels[source]] = True
        support.append(matrix)
    return support


def route_profile_at_depth(named_generators, sectors, depth: int) -> dict:
    """Return the exact labelled route profile at one positive depth.

    Sector paths are stored source-to-target. For a word ``a1...ad`` the
    routed product is therefore ``Q_target P_ad ... P_a1 Q_source``.
    """

    if depth < 1:
        raise ValueError("route depth must be positive")
    labels = tuple(name for name, _ in named_generators)
    direct = _direct_support(named_generators, sectors)
    sector_sets = [set(sector) for sector in sectors]
    zero_routes = []
    word_profiles = []
    candidate_count = 0
    nonzero_count = 0

    for word_indices in itertools.product(range(len(labels)), repeat=depth):
        word = [labels[index] for index in word_indices]
        word_candidates = 0
        word_nonzero = 0
        word_zero_shapes = {}
        for path in itertools.product(range(len(sectors)), repeat=depth + 1):
            if not all(
                direct[word_indices[step]][path[step + 1]][path[step]]
                for step in range(depth)
            ):
                continue
            word_candidates += 1
            states = set(sector_sets[path[0]])
            for step, generator_index in enumerate(word_indices):
                target_sector = sector_sets[path[step + 1]]
                permutation = named_generators[generator_index][1]
                states = {
                    permutation[state]
                    for state in states
                    if permutation[state] in target_sector
                }
            if states:
                word_nonzero += 1
            else:
                shape = "".join(str(index) for index in path)
                word_zero_shapes[shape] = word_zero_shapes.get(shape, 0) + 1
                zero_routes.append({"word": word, "sector_path": list(path)})

        candidate_count += word_candidates
        nonzero_count += word_nonzero
        word_profiles.append(
            {
                "word": word,
                "supported_route_count": word_candidates,
                "nonzero_route_count": word_nonzero,
                "zero_route_count": word_candidates - word_nonzero,
                "zero_shape_counts": word_zero_shapes,
            }
        )

    zero_routes.sort(key=lambda item: (item["word"], item["sector_path"]))
    zero_shape_counts = {}
    for route in zero_routes:
        shape = "".join(str(index) for index in route["sector_path"])
        zero_shape_counts[shape] = zero_shape_counts.get(shape, 0) + 1

    return {
        "depth": depth,
        "supported_route_candidate_count": candidate_count,
        "nonzero_routed_product_count": nonzero_count,
        "zero_routed_product_count": candidate_count - nonzero_count,
        "zero_shape_counts": zero_shape_counts,
        "word_profiles": word_profiles,
        "zero_route_signature": content_digest(zero_routes),
    }


def _profile_key(profile: dict) -> tuple:
    return (
        profile["supported_route_candidate_count"],
        profile["nonzero_routed_product_count"],
        profile["zero_routed_product_count"],
        tuple(sorted(profile["zero_shape_counts"].items())),
        profile["zero_route_signature"],
    )


def audit_prime(prime: int, max_depth: int) -> dict:
    if not is_prime(prime):
        raise ValueError("the family parameter must be prime")
    generators = modular_generators(prime)
    named = tuple((label, generators[label]) for label in LABELS)
    sectors = permutation_orbits(generators["T"])
    word_layers = exact_word_layers(
        tuple(permutation for _, permutation in named), sectors, max_depth
    )
    profiles = []
    for depth in range(1, max_depth + 1):
        profile = route_profile_at_depth(named, sectors, depth)
        profile["positive_word_image_layer"] = word_layers[depth - 1]
        profiles.append(profile)
    return {
        "prime": prime,
        "state_count": prime + 1,
        "carrier": "P^1(F_p)",
        "alphabet": list(LABELS),
        "marked_partition": [list(sector) for sector in sectors],
        "profiles_by_depth": profiles,
    }


def stability_report(records: Sequence[dict], max_depth: int) -> dict:
    by_depth = {}
    for depth in range(1, max_depth + 1):
        groups = {}
        for record in records:
            profile = record["profiles_by_depth"][depth - 1]
            digest = content_digest(_profile_key(profile))
            groups.setdefault(digest, []).append(record["prime"])
        by_depth[str(depth)] = {
            "equivalence": [
                {"profile_digest": digest, "primes": primes}
                for digest, primes in sorted(groups.items())
            ],
            "all_sampled_primes_equal": len(groups) == 1,
        }
    return {"by_depth": by_depth}


def build_payload(primes: Iterable[int], max_depth: int) -> dict:
    primes = list(primes)
    if max_depth < 1:
        raise ValueError("max_depth must be positive")
    records = [audit_prime(prime, max_depth) for prime in primes]
    here = Path(__file__).resolve()
    files = {
        f"{PACKAGE_PATH}/core.py": file_digest(here.with_name("core.py")),
        f"{PACKAGE_PATH}/uniform_finite_field_route_profile.py": file_digest(here),
    }
    return {
        "schema": SCHEMA,
        "bundle_id": "fuchsian-schreier.uniform-finite-field-route-profile.v1",
        "artifact_role": "EXPLORATORY_FIXED_DEPTH_ROUTE_PROFILE",
        "claim_status": "Computational Certificate",
        "paper_evidence_status": "NOT_PROMOTED",
        "scope": {
            "family": "modular P^1(F_p) permutation carriers",
            "sampled_primes": primes,
            "max_route_depth": max_depth,
            "typed_contract": "(P^1(F_p), (S,R,R_inv), T-orbit partition, labelled ordered routes, Q_target P_ad ... P_a1 Q_source)",
            "profile_contents": [
                "Boolean-supported candidate count",
                "nonzero and zero routed-product counts",
                "sector-path zero histogram",
                "per-word local counts",
                "exact zero-route-set digest",
                "exact positive-word image layer",
            ],
        },
        "implementation": {
            "language": "Python",
            "arithmetic": "exact finite permutations and Python integers",
            "files": files,
            "implementation_sha256": content_digest(files),
        },
        "records": records,
        "stability": stability_report(records, max_depth),
        "interpretation": {
            "positive": "This classifies exact fixed-depth profiles for the sampled finite-field family.",
            "negative": [
                "It is not an all-prime theorem.",
                "It is not an abstract presentation invariant.",
                "It does not establish RG, Hecke, modular-form, or asymptotic universality.",
                "Equality of a fixed-depth profile does not imply equality of the full generated semigroup.",
            ],
            "low_cardinality_control": "p=2 is retained as an explicit low-cardinality control and is not silently merged with the odd-prime family.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--primes", type=int, nargs="+", default=[2, 3, 5, 7, 11, 13]
    )
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.primes, args.max_depth)
    payload["content_sha256"] = content_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "bundle_id": payload["bundle_id"],
                "content_sha256": payload["content_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
