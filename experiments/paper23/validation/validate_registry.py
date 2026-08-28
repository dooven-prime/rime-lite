#!/usr/bin/env python3
"""Validate registry invariants without promoting observations to theorems."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from _bootstrap import REPOSITORY
from registry import (
    CARRIER_CONTRACT,
    apply_word,
    audit_automaton,
    block_support_path,
    compose_maps,
    direct_support,
    feature_row,
    fiber_excess,
    file_digest,
    image_subset,
    is_congruence,
    transformation_kernel_partition,
    kernel_refines,
    positive_word_support,
    payload_digest,
    pair_collision_profile,
    rank,
    rank_preserving_escape_profile,
    routed_support,
    shortest_reset_word,
    subset_rank_carrier,
    structural_next_drop_distance,
    transition_monoid_with_words,
)
from merge_census import merge
from symbolic_search import build_payload
from families import (
    build_family_suite,
    compact_escape_certificate,
    compact_pair_collision_certificate,
)


def validate_digest(payload: dict) -> None:
    if "content_sha256" in payload:
        expected_digest = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        assert payload_digest(unsigned) == expected_digest


def validate_producer(payload: dict, repository_root: Path) -> None:
    producer = payload.get("producer", {})
    for field in ("script", "registry"):
        if field not in producer:
            continue
        source = repository_root / producer[field]
        assert source.is_file(), f"missing producer source: {source}"
        assert file_digest(source) == producer[f"{field}_sha256"]


def validate_registry_or_shard(payload: dict, repository_root: Path) -> None:
    assert payload["carrier_contract"] == CARRIER_CONTRACT
    n = payload["scope"]["state_count"]
    max_word_depth = payload["scope"]["max_word_depth"]
    expected_feature_rows = []
    for record in payload["records"]:
        transition = tuple(tuple(letter) for letter in record["transition"])
        partition = tuple(tuple(block) for block in record["partition"])
        assert len(transition) == payload["scope"]["alphabet_size"]
        assert all(len(letter) == n and all(0 <= target < n for target in letter) for letter in transition)
        exact_routed = routed_support(transition, max_word_depth, partition)
        exact_words = positive_word_support(transition, max_word_depth, partition)
        expected_record = audit_automaton(transition, max_word_depth, partition)
        for field, value in expected_record.items():
            if field == "transition":
                continue
            assert record[field] == value, (
                f"record {record['id']} field mismatch: {field}"
            )
        assert record["direct_support"] == direct_support(transition, partition)
        assert record["block_support_path"] == block_support_path(
            transition, max_word_depth, partition
        )
        assert record["routed_support"] == exact_routed
        assert record["positive_word_support"] == exact_words
        assert exact_routed == exact_words
        assert record["deterministic_route_word_agreement"] is True
        if all(len(block) == 1 for block in partition):
            assert record["deterministic_coordinate_support_collapse"] == {
                "applicable": True,
                "path_route_word_equal": True,
            }
            assert record["block_support_path"] == exact_routed == exact_words
        reset = record["reset"]
        monoid = transition_monoid_with_words(transition)
        assert record["transition_monoid_size"] == len(monoid)
        assert len(record["transition_monoid"]) == len(monoid)
        for element in record["transition_monoid"]:
            word = tuple(element["shortest_word"])
            transformation = apply_word(word, transition, range(n))
            assert list(transformation) == element["map"]
            assert element["minimal_depth"] == len(word)
            assert rank(transformation) == element["rank"]
            assert n - rank(transformation) == sum(
                len(block) - 1
                for block in transformation_kernel_partition(transformation)
            )
            assert list(image_subset(transformation)) == element["image_subset"]
            assert [
                list(block)
                for block in transformation_kernel_partition(transformation)
            ] == element["transformation_kernel_partition"]
            for letter in transition:
                product = compose_maps(transformation, letter)
                assert kernel_refines(
                    transformation_kernel_partition(transformation),
                    transformation_kernel_partition(product),
                )
                assert rank(product) <= rank(transformation)
                assert rank(transformation) - rank(product) == fiber_excess(
                    letter,
                    image_subset(transformation),
                )
        for quotient in record["sector_quotients"]:
            assert is_congruence(transition, quotient["partition"])
            uniform = quotient["fixed_congruence_uniform_bound"]
            target = quotient["fixed_congruence_target_specific_bound"]
            selected = quotient["selected_shortest_witness_composition_bound"]
            if target is not None and selected is not None:
                assert target <= selected
            if target is not None and uniform is not None:
                assert target <= uniform
            witness = quotient["target_specific_optimizing_witness"]
            if witness is not None:
                witness_word = tuple(witness["quotient_reset_word"])
                reached = tuple(sorted(set(apply_word(
                    witness_word,
                    transition,
                    range(n),
                ))))
                assert list(reached) == witness["reached_subset"]
                assert witness["bound"] == (
                    witness["quotient_reset_depth"]
                    + witness["reached_subset_internal_depth"]
                )
        assert record["pair_collision_profile"] == pair_collision_profile(
            transition
        )
        exact_reset = shortest_reset_word(transition)
        assert reset["is_synchronizing"] == (exact_reset is not None)
        if reset["is_synchronizing"]:
            word = tuple(reset["shortest_word"])
            assert rank(apply_word(word, transition, range(n))) == 1
            assert reset["shortest_length"] == len(word)
            assert len(word) == len(exact_reset)
            rank_one = next(
                hit
                for hit in record["rank_collapse"]["first_hit_depth_by_rank_threshold"]
                if hit["rank_threshold"] == 1
            )
            assert rank_one["status"] == "EXACT_FIRST_HIT"
            assert rank_one["depth"] == len(word)
            filtration = record["reset_rank_drop_filtration"]
            assert filtration[-1]["rank_after"] == 1
            assert all(step["strict_drop"] == bool(step["collision_fibers_on_current_image"]) for step in filtration)
            assert all(step["drop_size"] == step["fiber_excess"] for step in filtration)
            assert all(step["kernel_coarsening"] == step["strict_drop"] for step in filtration)
            assert all(step["kernel_unchanged"] != step["strict_drop"] for step in filtration)
            escape = record["rank_preserving_escape"]
            assert escape["bound_status"] == "EXACT_FINITE_REDUCTION"
            assert len(word) <= escape["sync_upper_bound_sum_Omega_r"]
            for layer in escape["layers"]:
                escape_by_subset = {
                    tuple(item["subset"]): item
                    for item in layer["escape_records"]
                }
                exact_distances = []
                for subset in map(tuple, layer["reachable_subsets"]):
                    exact = structural_next_drop_distance(transition, subset)
                    assert exact is not None
                    assert (
                        escape_by_subset[subset]["structural_next_drop_distance"]
                        == exact
                    )
                    escape_record = escape_by_subset[subset]
                    assert escape_record["pair_merge_upper_bound_holds"] is True
                    drop_word = tuple(escape_record["shortest_rank_drop_word"])
                    drop_target = tuple(sorted(set(apply_word(
                        drop_word,
                        transition,
                        subset,
                    ))))
                    assert list(drop_target) == escape_record[
                        "rank_drop_target_subset"
                    ]
                    assert len(drop_target) < len(subset)
                    assert escape_record[
                        "local_potential_inequality_holds"
                    ] is True
                    exact_distances.append(exact)
                assert layer["rank_layer_max_escape_distance"] == max(
                    exact_distances
                )
                assert layer["rank_layer_max_escape_distance"] <= (
                    layer["pin_frankl_compression_benchmark"]
                )
                assert layer["pin_frankl_benchmark_holds"] is True
                for collision in layer["collision_exits"]:
                    source = tuple(collision["source"])
                    letter = transition[collision["letter"]]
                    target = tuple(sorted({letter[state] for state in source}))
                    assert list(target) == collision["target"]
                    assert len(target) < len(source)
                    assert collision["fiber_excess"] == len(source) - len(target)
            assert escape["compatible_escape_budget"]["path_compatible"] is True
            assert escape["potential_certificate"][
                "local_descent_inequalities_verified"
            ] is True
            assert escape["sync_upper_bound_sum_Omega_r"] <= (
                escape["classical_compression_benchmark"]["cubic_reset_bound"]
            )
            for quotient in record["sector_quotients"]:
                bound = quotient["fixed_congruence_uniform_bound"]
                if bound is not None:
                    assert len(word) <= bound
                target_bound = quotient[
                    "fixed_congruence_target_specific_bound"
                ]
                if target_bound is not None:
                    assert len(word) <= target_bound
        else:
            rank_one = next(
                hit
                for hit in record["rank_collapse"]["first_hit_depth_by_rank_threshold"]
                if hit["rank_threshold"] == 1
            )
            assert rank_one["status"] == "UNREACHABLE_IN_SUBSET_ORBIT"
            assert record["reset_rank_drop_filtration"] is None
        if reset["is_synchronizing"]:
            row = feature_row(record, n)
            if "canonical_index" in record:
                row["canonical_index"] = record["canonical_index"]
            expected_feature_rows.append(row)
    if payload["schema"] == "rime.synchronizing-automata.v2":
        assert payload["analysis"]["feature_rows"] == expected_feature_rows
    else:
        assert payload["feature_rows"] == expected_feature_rows
    print(f"validated {len(payload['records'])} records")


def validate_summary(payload: dict, repository_root: Path) -> None:
    assert payload["carrier_contract"] == CARRIER_CONTRACT
    paths = [repository_root / item["path"] for item in payload["shards"]]
    for path, item in zip(paths, payload["shards"]):
        assert path.is_file(), f"missing shard: {path}"
        assert file_digest(path) == item["file_sha256"]
    assert merge(paths) == payload
    print(f"validated merged summary from {len(paths)} shards")


def validate_symbolic_search(payload: dict, repository_root: Path) -> None:
    assert payload["carrier_contract"] == CARRIER_CONTRACT
    paths = [repository_root / item["path"] for item in payload["inputs"]]
    for path, item in zip(paths, payload["inputs"]):
        assert path.is_file(), f"missing symbolic-search input: {path}"
        assert file_digest(path) == item["sha256"]
    assert build_payload(paths) == payload
    print(f"validated symbolic search over {payload['row_count']} rows")


def validate_family_suite(payload: dict) -> None:
    assert payload["carrier_contract"] == CARRIER_CONTRACT
    scope = payload["scope"]
    assert build_family_suite(
        scope["min_state_count"],
        scope["max_state_count"],
    ) == payload
    for record in payload["records"]:
        transition = tuple(tuple(letter) for letter in record["transition"])
        word = tuple(record["shortest_reset_word"])
        assert rank(apply_word(word, transition, range(record["state_count"]))) == 1
        assert len(word) == record["expected_family_value"]
        assert record["matches_expected_family_value"] is True
        assert record["rank_preserving_escape_certificate"] == (
            compact_escape_certificate(rank_preserving_escape_profile(transition))
        )
        assert record["pair_collision_certificate"] == (
            compact_pair_collision_certificate(pair_collision_profile(transition))
        )
        if "all_letters_idempotent" in record["cohort_tags"]:
            assert all(compose_maps(letter, letter) == letter for letter in transition)
            assert all(
                rank(letter) == record["state_count"] // 2
                for letter in transition
            )
    print(f"validated {len(payload['records'])} slow-family records")


def validate(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    repository_root = REPOSITORY
    validate_digest(payload)
    validate_producer(payload, repository_root)
    schema = payload["schema"]
    if schema in {
        "rime.synchronizing-automata.v2",
        "rime.synchronizing-automata.census-shard.v2",
    }:
        validate_registry_or_shard(payload, repository_root)
    elif schema == "rime.synchronizing-automata.census-summary.v2":
        validate_summary(payload, repository_root)
    elif schema == "rime.synchronizing-automata.symbolic-search.v2":
        validate_symbolic_search(payload, repository_root)
    elif schema == "rime.synchronizing-automata.family-suite.v1":
        validate_family_suite(payload)
    else:
        raise AssertionError(f"unsupported schema: {schema}")


def validate_coarse_partition_control() -> None:
    """Guard against identifying graph powers with routed support."""
    transition = ((0, 0, 0), (0, 0, 1))
    partition = ((1,), (0, 2))
    paths = block_support_path(transition, 2, partition)
    routed = routed_support(transition, 2, partition)
    words = positive_word_support(transition, 2, partition)
    assert paths[1] != routed[1]
    assert routed == words


def validate_exact_graph_power_depths() -> None:
    """Ensure exact Boolean powers advance by one word letter per level."""
    transition = ((1, 2, 0),)
    partition = ((0,), (1,), (2,))
    levels = block_support_path(transition, 4, partition)
    assert levels[0][1][0] == 1
    assert levels[1][2][0] == 1
    assert levels[2][0][0] == 1
    assert levels[3][1][0] == 1
    assert levels[2] != levels[3]


def validate_depth_zero_and_exact_layer_recurrence() -> None:
    singleton = ((0,),)
    singleton_record = audit_automaton(singleton, 1)
    assert singleton_record["reset"]["shortest_length"] == 0
    rank_one = singleton_record["rank_collapse"]["first_hit_depth_by_rank_threshold"][0]
    assert rank_one == {
        "rank_threshold": 1,
        "status": "EXACT_FIRST_HIT",
        "depth": 0,
    }

    swap = ((1, 0),)
    carrier = subset_rank_carrier(swap, 2)
    layers = carrier["exact_depth_reachable_image_subsets"]
    assert layers[0]["images"] == [[0, 1]]
    assert layers[1]["images"] == [[0, 1]]
    assert layers[2]["images"] == [[0, 1]]
    assert carrier["reachable_subset_orbit"] == [
        {"subset": [0, 1], "minimal_depth": 0, "shortest_word": []}
    ]
    escape = rank_preserving_escape_profile(swap)
    record = escape["layers"][0]["escape_records"][0]
    assert record["structural_next_drop_distance"] is None
    assert record["mathematical_value"] == "infinity"
    assert record["status"] == "EXACT_INFINITY_NO_REACHABLE_STRICT_DROP"


def validate_generator_presentation_separation() -> None:
    """Adding a named existing reset map changes depth, not the monoid set."""
    transition = ((0, 1, 0), (1, 2, 0))
    reset_word = shortest_reset_word(transition)
    assert reset_word is not None and len(reset_word) > 1
    reset_map = apply_word(reset_word, transition, range(3))
    augmented = transition + (reset_map,)
    assert set(transition_monoid_with_words(transition)) == set(
        transition_monoid_with_words(augmented)
    )
    augmented_reset = shortest_reset_word(augmented)
    assert augmented_reset is not None and len(augmented_reset) == 1


if __name__ == "__main__":
    validate_coarse_partition_control()
    validate_exact_graph_power_depths()
    validate_depth_zero_and_exact_layer_recurrence()
    validate_generator_presentation_separation()
    validate(Path(sys.argv[1]))
