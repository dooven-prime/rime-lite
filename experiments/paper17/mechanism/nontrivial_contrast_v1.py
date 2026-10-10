#!/usr/bin/env python3
"""Frozen exact predicates and finite-census classification for MTS-1."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from typing import Any, Iterable

from mechanism_records_v1 import FATES, validate_pair_transition_record


TRANSITIONS = ("1_TO_2", "2_TO_3", "3_TO_4")
PAIR_ROLES = ("TRANSIENT_OBSTRUCTION", "PERSISTENT_SAFE")
PRIMARY_PREDICATE_ORDER = (
    "CLIPPING_CREATES_COARSE_RESIDUAL",
    "CLIPPING_ELIMINATES_COARSE_RAW_RESIDUAL",
    "CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL",
    "RAW_RESIDUAL_PERSISTS_UNCHANGED",
    "RAW_DRIVE_DIFFERENCE_COARSE_ANNIHILATED",
    "MICROSCOPIC_DIFFERENCE_RAW_DRIVE_IDENTICAL",
    "FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION",
)
DESCRIPTIVE_ONLY_PREDICATES = (
    "REGISTERED_SAFE_FORGETTING_GEOMETRY",
)
PREDICATE_DEFINITIONS = {
    "CLIPPING_CREATES_COARSE_RESIDUAL": (
        "r_raw==0 AND r_clip!=0 AND r_corr==r_clip"
    ),
    "CLIPPING_ELIMINATES_COARSE_RAW_RESIDUAL": (
        "r_raw!=0 AND r_clip==0 AND r_corr==-r_raw"
    ),
    "CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL": (
        "r_raw!=0 AND r_clip!=0 AND r_corr!=0"
    ),
    "RAW_RESIDUAL_PERSISTS_UNCHANGED": (
        "r_raw!=0 AND r_clip==r_raw AND r_corr==0"
    ),
    "RAW_DRIVE_DIFFERENCE_COARSE_ANNIHILATED": (
        "raw_drive_exact_l1_difference!=0 AND r_raw==0"
    ),
    "MICROSCOPIC_DIFFERENCE_RAW_DRIVE_IDENTICAL": (
        "microscopic_state_exact_l1_difference!=0 AND raw_drive_exact_l1_difference==0"
    ),
    "FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION": (
        "off_diagonal_clipping_fate_count!=0 AND r_corr!=0"
    ),
    "REGISTERED_SAFE_FORGETTING_GEOMETRY": (
        "(microscopic_state_exact_l1_difference!=0 OR raw_drive_exact_l1_difference!=0) AND r_clip==0"
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _fraction(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def _sparse_vector(value: dict[str, Any]) -> dict[int, Fraction]:
    return {
        entry["coordinate"]: Fraction(
            int(entry["numerator"]), int(entry["denominator"])
        )
        for entry in value["entries"]
    }


def _negate(value: dict[int, Fraction]) -> dict[int, Fraction]:
    return {coordinate: -entry for coordinate, entry in value.items() if entry}


def evaluate_pair_predicates(record: dict[str, Any]) -> dict[str, bool]:
    """Evaluate the closed predicate family on one validated pair record."""

    validate_pair_transition_record(record)
    state_difference_nonzero = _fraction(
        record["state_geometry"]["exact_l1_difference"]
    ) != 0
    raw_drive_difference_nonzero = _fraction(
        record["raw_drive_geometry"]["exact_l1_difference"]
    ) != 0
    residuals = {
        key: _sparse_vector(value) for key, value in record["residuals"].items()
    }
    r_raw = residuals["r_raw"]
    r_clip = residuals["r_clip"]
    r_corr = residuals["r_corr"]
    off_diagonal_fate_count = sum(
        cell["count"]
        for cell in record["clipping_fate_table"]["cells"]
        if cell["source_a_fate"] != cell["source_b_fate"]
    )
    predicates = {
        "CLIPPING_CREATES_COARSE_RESIDUAL": (
            not r_raw and bool(r_clip) and r_corr == r_clip
        ),
        "CLIPPING_ELIMINATES_COARSE_RAW_RESIDUAL": (
            bool(r_raw) and not r_clip and r_corr == _negate(r_raw)
        ),
        "CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL": (
            bool(r_raw) and bool(r_clip) and bool(r_corr)
        ),
        "RAW_RESIDUAL_PERSISTS_UNCHANGED": (
            bool(r_raw) and r_clip == r_raw and not r_corr
        ),
        "RAW_DRIVE_DIFFERENCE_COARSE_ANNIHILATED": (
            raw_drive_difference_nonzero and not r_raw
        ),
        "MICROSCOPIC_DIFFERENCE_RAW_DRIVE_IDENTICAL": (
            state_difference_nonzero and not raw_drive_difference_nonzero
        ),
        "FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION": (
            off_diagonal_fate_count != 0 and bool(r_corr)
        ),
        "REGISTERED_SAFE_FORGETTING_GEOMETRY": (
            (state_difference_nonzero or raw_drive_difference_nonzero)
            and not r_clip
        ),
    }
    require(
        set(predicates) == set(PRIMARY_PREDICATE_ORDER) | set(DESCRIPTIVE_ONLY_PREDICATES),
        "predicate implementation and frozen registry disagree",
    )
    return predicates


def primary_signature(predicates: dict[str, bool]) -> str:
    return "".join("1" if predicates[name] else "0" for name in PRIMARY_PREDICATE_ORDER)


def cohort_specs_from_registry(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}
    for registry_key, pair_role in (
        ("transient_obstruction", "TRANSIENT_OBSTRUCTION"),
        ("persistent_safe", "PERSISTENT_SAFE"),
    ):
        for cohort in registry[registry_key]["cohorts"]:
            labels = cohort["initial_sector_labels"]
            require(len(labels) == 1, "MTS-1 cohorts must have one initial sector label")
            cohort_id = cohort["cohort_id"]
            require(cohort_id not in specs, "duplicate cohort id")
            unordered_pairs = [
                [source_a, source_b]
                for source_a, source_b in combinations(
                    sorted(cohort["source_ids"]), 2
                )
            ]
            require(
                len(unordered_pairs) == cohort["unordered_pair_count"],
                "cohort source membership and pair count disagree",
            )
            specs[cohort_id] = {
                "pair_role": pair_role,
                "initial_sector_label": labels[0],
                "unordered_pair_count": cohort["unordered_pair_count"],
                "unordered_pairs": unordered_pairs,
            }
    return specs


def _normalized_histograms_equal(
    left: Counter[str], left_total: int, right: Counter[str], right_total: int
) -> bool:
    require(left_total > 0 and right_total > 0, "empty cohort histogram")
    return all(
        left.get(signature, 0) * right_total
        == right.get(signature, 0) * left_total
        for signature in set(left) | set(right)
    )


def classify_finite_census(
    records: Iterable[dict[str, Any]], cohort_specs: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Classify one complete finite census without thresholds or pooling."""

    histograms: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    predicate_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    observed_pairs: dict[tuple[str, str], set[tuple[int, int]]] = defaultdict(set)
    observed_transitions: dict[
        tuple[str, str, int, int], set[str]
    ] = defaultdict(set)
    record_count = 0
    for record in records:
        validate_pair_transition_record(record)
        cohort_id = record["cohort_id"]
        require(cohort_id in cohort_specs, f"unregistered cohort: {cohort_id}")
        spec = cohort_specs[cohort_id]
        require(record["pair_role"] == spec["pair_role"], "pair role disagrees with cohort")
        identity = (
            record["pair_role"],
            cohort_id,
            record["source_a"],
            record["source_b"],
        )
        require(
            record["transition"] not in observed_transitions[identity],
            "duplicate pair transition record",
        )
        observed_transitions[identity].add(record["transition"])
        observed_pairs[(record["pair_role"], cohort_id)].add(
            (record["source_a"], record["source_b"])
        )
        predicates = evaluate_pair_predicates(record)
        key = (cohort_id, record["transition"])
        histograms[key][primary_signature(predicates)] += 1
        for name in PRIMARY_PREDICATE_ORDER:
            if predicates[name]:
                predicate_counts[key][name] += 1
        record_count += 1

    expected_record_count = 0
    for cohort_id, spec in cohort_specs.items():
        pair_role = spec["pair_role"]
        expected_pairs = spec["unordered_pair_count"]
        expected_record_count += expected_pairs * len(TRANSITIONS)
        require(
            observed_pairs[(pair_role, cohort_id)]
            == {tuple(pair) for pair in spec["unordered_pairs"]},
            f"pair membership disagrees with registered cohort for {cohort_id}",
        )
        for source_a, source_b in observed_pairs[(pair_role, cohort_id)]:
            require(
                observed_transitions[(pair_role, cohort_id, source_a, source_b)]
                == set(TRANSITIONS),
                f"transition grid incomplete for {cohort_id}:{source_a},{source_b}",
            )
        for transition in TRANSITIONS:
            require(
                sum(histograms[(cohort_id, transition)].values()) == expected_pairs,
                f"histogram count incomplete for {cohort_id}:{transition}",
            )
    require(record_count == expected_record_count, "finite census record count mismatch")

    comparison_cells: list[dict[str, Any]] = []
    transient_ids = [
        cohort_id
        for cohort_id, spec in cohort_specs.items()
        if spec["pair_role"] == "TRANSIENT_OBSTRUCTION"
    ]
    persistent_ids = [
        cohort_id
        for cohort_id, spec in cohort_specs.items()
        if spec["pair_role"] == "PERSISTENT_SAFE"
    ]
    for transition in TRANSITIONS:
        for transient_id in sorted(transient_ids):
            for persistent_id in sorted(persistent_ids):
                transient_spec = cohort_specs[transient_id]
                persistent_spec = cohort_specs[persistent_id]
                if transient_spec["initial_sector_label"] != persistent_spec["initial_sector_label"]:
                    continue
                transient_total = transient_spec["unordered_pair_count"]
                persistent_total = persistent_spec["unordered_pair_count"]
                transient_hist = histograms[(transient_id, transition)]
                persistent_hist = histograms[(persistent_id, transition)]
                comparison_cells.append(
                    {
                        "transition": transition,
                        "initial_sector_label": transient_spec["initial_sector_label"],
                        "transient_cohort_id": transient_id,
                        "persistent_cohort_id": persistent_id,
                        "transient_pair_count": transient_total,
                        "persistent_pair_count": persistent_total,
                        "normalized_signature_histograms_equal": _normalized_histograms_equal(
                            transient_hist,
                            transient_total,
                            persistent_hist,
                            persistent_total,
                        ),
                    }
                )
    require(comparison_cells, "no shared-stratum comparison cells")

    exact_separators: list[dict[str, str]] = []
    for transition in TRANSITIONS:
        transition_cells = [
            cell for cell in comparison_cells if cell["transition"] == transition
        ]
        require(transition_cells, f"no shared-stratum cells for {transition}")
        for predicate in PRIMARY_PREDICATE_ORDER:
            for direction in (
                "TRANSIENT_ALL__PERSISTENT_NONE",
                "PERSISTENT_ALL__TRANSIENT_NONE",
            ):
                separates = True
                for cell in transition_cells:
                    transient_count = predicate_counts[
                        (cell["transient_cohort_id"], transition)
                    ][predicate]
                    persistent_count = predicate_counts[
                        (cell["persistent_cohort_id"], transition)
                    ][predicate]
                    if direction == "TRANSIENT_ALL__PERSISTENT_NONE":
                        separates = separates and (
                            transient_count == cell["transient_pair_count"]
                            and persistent_count == 0
                        )
                    else:
                        separates = separates and (
                            persistent_count == cell["persistent_pair_count"]
                            and transient_count == 0
                        )
                if separates:
                    exact_separators.append(
                        {
                            "transition": transition,
                            "predicate": predicate,
                            "direction": direction,
                        }
                    )

    differing_cells = [
        cell for cell in comparison_cells
        if not cell["normalized_signature_histograms_equal"]
    ]
    if exact_separators:
        outcome = "EXACT_TRANSITION_LAYER_LOCALIZATION"
    elif differing_cells:
        outcome = "PARTIAL_REGISTERED_FEATURE_CONTRAST"
    else:
        outcome = "NO_CONTRAST_IN_DECLARED_FEATURE_FAMILIES"
    return {
        "status": "PASS",
        "outcome": outcome,
        "complete_finite_census": True,
        "record_count": record_count,
        "expected_record_count": expected_record_count,
        "primary_predicate_order": list(PRIMARY_PREDICATE_ORDER),
        "comparison_cell_count": len(comparison_cells),
        "differing_comparison_cell_count": len(differing_cells),
        "exact_separators": exact_separators,
        "comparison_cells": comparison_cells,
        "statistical_inference": "NONE",
        "thresholds": "NONE",
        "time_pooling": False,
        "cohort_pooling": False,
    }


def classify_finite_census_or_unresolved(
    records: Iterable[dict[str, Any]], cohort_specs: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Fail closed to the registered unresolved state."""

    try:
        return classify_finite_census(records, cohort_specs)
    except (KeyError, TypeError, ValueError) as error:
        return {
            "status": "UNRESOLVED",
            "outcome": "UNRESOLVED",
            "reason": str(error),
            "complete_finite_census": False,
            "statistical_inference": "NONE",
            "thresholds": "NONE",
            "time_pooling": False,
            "cohort_pooling": False,
        }
