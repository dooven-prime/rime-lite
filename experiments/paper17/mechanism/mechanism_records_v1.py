#!/usr/bin/env python3
"""Strict metadata validation for MTS-1 cache and pair records."""

from __future__ import annotations

import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import PurePosixPath
from typing import Any


NODE_DIMENSION = 211_577
COARSE_DIMENSION = 28
CURRENT_TIMES = (1, 2, 3)
FATES = ("LOWER", "INTERIOR", "UPPER")
INITIAL_SECTOR_LABELS = (
    "ascending_neuron",
    "cb_intrinsic",
    "ol_intrinsic",
    "ol_sensory",
    "visual_centrifugal",
    "vnc_intrinsic",
)
SOURCE_PAYLOAD_ORDER = ("x_t", "u_t", "clip_u_t", "clipping_fate")
SOURCE_PAYLOAD_CODECS = {
    "x_t": "RIME-MTS-MICROSTATE-V1",
    "u_t": "RIME-MTS-RAW-DRIVE-V1",
    "clip_u_t": "RIME-MTS-CLIPPED-DRIVE-V1",
    "clipping_fate": "RIME-MTS-CLIPPING-FATE-V1",
}
SOURCE_PAYLOAD_ROLES = {
    "x_t": "MICROSCOPIC_STATE",
    "u_t": "RAW_SIGNED_DRIVE",
    "clip_u_t": "CLIPPED_DRIVE",
    "clipping_fate": "TOUCHED_TARGET_CLIPPING_FATE",
}
SOURCE_DESCRIPTOR_FIELDS = (
    "known_sign_out_degree",
    "known_sign_positive_out_degree",
    "known_sign_negative_out_degree",
    "known_sign_outgoing_positive_mass",
    "known_sign_outgoing_negative_absolute_mass",
    "known_sign_outgoing_absolute_mass",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
INTEGER_RE = re.compile(r"^(?:0|-?[1-9][0-9]*)$")
POSITIVE_INTEGER_RE = re.compile(r"^[1-9][0-9]*$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _exact_keys(value: dict[str, Any], required: tuple[str, ...], label: str) -> None:
    require(isinstance(value, dict), f"{label} must be an object")
    require(set(value) == set(required), f"{label} field set mismatch")


def _nonnegative_integer(value: object, label: str) -> int:
    require(type(value) is int and value >= 0, f"{label} must be a nonnegative integer")
    return value


def _positive_integer(value: object, label: str) -> int:
    require(type(value) is int and value > 0, f"{label} must be a positive integer")
    return value


def _sha256(value: object, label: str) -> str:
    require(isinstance(value, str) and SHA256_RE.fullmatch(value) is not None, f"{label} is not SHA-256")
    return value


def _safe_path(value: object, label: str) -> str:
    require(isinstance(value, str) and value != "", f"{label} must be a nonempty path")
    require("\\" not in value and ":" not in value, f"{label} is not a portable relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, f"{label} escapes its result root")
    require(".runtime-work" not in path.parts, f"{label} uses a temporary runtime path")
    return value


def validate_artifact_ref(value: dict[str, Any], label: str) -> None:
    _exact_keys(value, ("role", "path", "bytes", "sha256"), label)
    require(isinstance(value["role"], str) and value["role"] != "", f"{label}.role is empty")
    _safe_path(value["path"], f"{label}.path")
    _nonnegative_integer(value["bytes"], f"{label}.bytes")
    _sha256(value["sha256"], f"{label}.sha256")


def validate_exact_payload_ref(value: dict[str, Any], key: str) -> None:
    _exact_keys(
        value,
        ("role", "path", "bytes", "sha256", "codec", "semantic_role", "dimension", "entry_count"),
        f"payloads.{key}",
    )
    validate_artifact_ref(
        {name: value[name] for name in ("role", "path", "bytes", "sha256")},
        f"payloads.{key}",
    )
    require(value["codec"] == SOURCE_PAYLOAD_CODECS[key], f"payloads.{key}.codec drift")
    require(value["semantic_role"] == SOURCE_PAYLOAD_ROLES[key], f"payloads.{key}.semantic_role drift")
    require(value["dimension"] == NODE_DIMENSION, f"payloads.{key}.dimension drift")
    _nonnegative_integer(value["entry_count"], f"payloads.{key}.entry_count")


def validate_rational(value: dict[str, Any], label: str, *, nonnegative: bool = False) -> Fraction:
    _exact_keys(value, ("numerator", "denominator"), label)
    numerator_text = value["numerator"]
    denominator_text = value["denominator"]
    require(isinstance(numerator_text, str) and INTEGER_RE.fullmatch(numerator_text) is not None, f"{label}.numerator is not canonical decimal")
    require(isinstance(denominator_text, str) and POSITIVE_INTEGER_RE.fullmatch(denominator_text) is not None, f"{label}.denominator is not canonical positive decimal")
    numerator = int(numerator_text)
    denominator = int(denominator_text)
    require(math.gcd(abs(numerator), denominator) == 1, f"{label} is not reduced")
    require(not nonnegative or numerator >= 0, f"{label} must be nonnegative")
    return Fraction(numerator, denominator)


def validate_sparse_vector(value: dict[str, Any], label: str, dimension: int = COARSE_DIMENSION) -> dict[int, Fraction]:
    _exact_keys(value, ("dimension", "entries"), label)
    require(value["dimension"] == dimension, f"{label}.dimension drift")
    require(isinstance(value["entries"], list), f"{label}.entries must be an array")
    result: dict[int, Fraction] = {}
    previous = -1
    for index, entry in enumerate(value["entries"]):
        _exact_keys(entry, ("coordinate", "numerator", "denominator"), f"{label}.entries[{index}]")
        coordinate = entry["coordinate"]
        require(type(coordinate) is int and previous < coordinate < dimension, f"{label} coordinates are not strictly increasing")
        rational = validate_rational(
            {"numerator": entry["numerator"], "denominator": entry["denominator"]},
            f"{label}.entries[{index}]",
        )
        require(rational != 0, f"{label} contains an explicit zero")
        result[coordinate] = rational
        previous = coordinate
    return result


def _subtract(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    output: dict[int, Fraction] = {}
    for coordinate in sorted(set(left) | set(right)):
        value = left.get(coordinate, Fraction(0)) - right.get(coordinate, Fraction(0))
        if value:
            output[coordinate] = value
    return output


def _scale(values: dict[int, Fraction], factor: int) -> dict[int, Fraction]:
    return {coordinate: factor * value for coordinate, value in values.items() if value}


def _transition(current_time: int) -> tuple[int, str]:
    require(current_time in CURRENT_TIMES, "current_time outside registered grid")
    return current_time + 1, f"{current_time}_TO_{current_time + 1}"


def _validate_role_and_cohort(source_role: str, cohort_id: str) -> None:
    require(source_role in ("TRANSIENT_OBSTRUCTION", "PERSISTENT_SAFE"), "unknown source role")
    prefix = "TO-" if source_role == "TRANSIENT_OBSTRUCTION" else "PS-"
    require(isinstance(cohort_id, str) and cohort_id.startswith(prefix), "cohort id disagrees with source role")


def validate_source_transition_record(record: dict[str, Any]) -> None:
    _exact_keys(
        record,
        (
            "schema", "source_id", "source_role", "cohort_id", "initial_sector_label",
            "current_time", "next_time", "transition", "replay_gates", "payloads",
            "observations", "clipping_fate", "source_descriptors", "ordered_payload_digest",
        ),
        "source-transition record",
    )
    require(record["schema"] == "rime.exploratory.male-cns.mts-source-transition-cache-record.v1", "source record schema mismatch")
    require(type(record["source_id"]) is int and 0 <= record["source_id"] < NODE_DIMENSION, "source_id outside node basis")
    _validate_role_and_cohort(record["source_role"], record["cohort_id"])
    require(record["initial_sector_label"] in INITIAL_SECTOR_LABELS, "unregistered initial sector label")
    next_time, transition = _transition(record["current_time"])
    require(record["next_time"] == next_time and record["transition"] == transition, "source transition label drift")

    gates = record["replay_gates"]
    _exact_keys(
        gates,
        (
            "paper17_observation_payload_sha256", "replayed_observation_payload_sha256",
            "observation_bytes_equal", "paper17_legacy_state_sha256",
            "replayed_legacy_state_sha256", "legacy_state_hash_equal",
            "canonical_state_payload_sha256", "canonical_state_payload_valid",
        ),
        "replay_gates",
    )
    for key in (
        "paper17_observation_payload_sha256", "replayed_observation_payload_sha256",
        "paper17_legacy_state_sha256", "replayed_legacy_state_sha256",
        "canonical_state_payload_sha256",
    ):
        _sha256(gates[key], f"replay_gates.{key}")
    require(gates["observation_bytes_equal"] is True, "observation replay gate failed")
    require(gates["legacy_state_hash_equal"] is True, "legacy state replay gate failed")
    require(gates["canonical_state_payload_valid"] is True, "canonical state validation gate failed")
    require(gates["paper17_observation_payload_sha256"] == gates["replayed_observation_payload_sha256"], "observation digest equality flag is inconsistent")
    require(gates["paper17_legacy_state_sha256"] == gates["replayed_legacy_state_sha256"], "legacy state hash equality flag is inconsistent")

    payloads = record["payloads"]
    _exact_keys(payloads, SOURCE_PAYLOAD_ORDER, "payloads")
    for key in SOURCE_PAYLOAD_ORDER:
        validate_exact_payload_ref(payloads[key], key)
    expected_payload_digest = sha256_bytes(canonical_json_bytes([payloads[key] for key in SOURCE_PAYLOAD_ORDER]))
    require(record["ordered_payload_digest"] == expected_payload_digest, "ordered payload digest mismatch")
    require(payloads["x_t"]["sha256"] == gates["canonical_state_payload_sha256"], "state payload and replay gate digest differ")

    observations = record["observations"]
    _exact_keys(observations, ("O_x_t", "O_u_t", "O_clip_u_t"), "observations")
    for key in observations:
        validate_sparse_vector(observations[key], f"observations.{key}")

    fate = record["clipping_fate"]
    _exact_keys(
        fate,
        ("touched_target_semantics", "lower_semantics", "interior_semantics", "upper_semantics", "touched_target_count", "counts"),
        "clipping_fate",
    )
    require(fate["touched_target_semantics"] == "TARGET_RECEIVES_AT_LEAST_ONE_PRE_SUM_EDGE_CONTRIBUTION", "touched-target semantics drift")
    require(fate["lower_semantics"] == "u<=0", "lower clipping boundary drift")
    require(fate["interior_semantics"] == "0<u<1", "interior clipping boundary drift")
    require(fate["upper_semantics"] == "u>=1", "upper clipping boundary drift")
    touched = _nonnegative_integer(fate["touched_target_count"], "clipping_fate.touched_target_count")
    _exact_keys(fate["counts"], FATES, "clipping_fate.counts")
    counts = [_nonnegative_integer(fate["counts"][key], f"clipping_fate.counts.{key}") for key in FATES]
    require(sum(counts) == touched, "clipping fate counts do not cover touched targets")
    require(payloads["clipping_fate"]["entry_count"] == touched, "fate payload entry count mismatch")

    descriptors = record["source_descriptors"]
    _exact_keys(descriptors, SOURCE_DESCRIPTOR_FIELDS, "source_descriptors")
    for key in SOURCE_DESCRIPTOR_FIELDS:
        _nonnegative_integer(descriptors[key], f"source_descriptors.{key}")
    require(
        descriptors["known_sign_positive_out_degree"] + descriptors["known_sign_negative_out_degree"]
        == descriptors["known_sign_out_degree"],
        "signed out-degree decomposition mismatch",
    )
    require(
        descriptors["known_sign_outgoing_positive_mass"] + descriptors["known_sign_outgoing_negative_absolute_mass"]
        == descriptors["known_sign_outgoing_absolute_mass"],
        "signed outgoing-mass decomposition mismatch",
    )


def _validate_geometry(value: dict[str, Any], label: str) -> None:
    _exact_keys(
        value,
        ("support_intersection_count", "support_union_count", "support_symmetric_difference_count", "exact_l1_difference"),
        label,
    )
    intersection = _nonnegative_integer(value["support_intersection_count"], f"{label}.support_intersection_count")
    union = _nonnegative_integer(value["support_union_count"], f"{label}.support_union_count")
    symmetric = _nonnegative_integer(value["support_symmetric_difference_count"], f"{label}.support_symmetric_difference_count")
    require(intersection <= union and symmetric == union - intersection, f"{label} support counts are inconsistent")
    validate_rational(value["exact_l1_difference"], f"{label}.exact_l1_difference", nonnegative=True)


def _validate_cache_ref(value: dict[str, Any], expected_role: str, label: str) -> None:
    validate_artifact_ref(value, label)
    require(value["role"] == expected_role, f"{label}.role drift")


def validate_pair_transition_record(record: dict[str, Any]) -> None:
    _exact_keys(
        record,
        (
            "schema", "pair_role", "cohort_id", "source_a", "source_b", "current_time",
            "next_time", "transition", "defining_transition", "orientation", "source_cache_records",
            "current_observation_equal", "successor_observation_equal", "state_geometry",
            "raw_drive_geometry", "residuals", "clipping_fate_table", "residual_quadrant",
            "identity_checks",
        ),
        "pair-transition record",
    )
    require(record["schema"] == "rime.exploratory.male-cns.mts-pair-transition-record.v1", "pair record schema mismatch")
    _validate_role_and_cohort(record["pair_role"], record["cohort_id"])
    source_a = record["source_a"]
    source_b = record["source_b"]
    require(type(source_a) is int and type(source_b) is int and 0 <= source_a < source_b < NODE_DIMENSION, "pair orientation is not canonical")
    next_time, transition = _transition(record["current_time"])
    require(record["next_time"] == next_time and record["transition"] == transition, "pair transition label drift")
    expected_defining = (
        record["pair_role"] == "TRANSIENT_OBSTRUCTION" and record["current_time"] == 1
    ) or (
        record["pair_role"] == "PERSISTENT_SAFE" and record["current_time"] in (2, 3)
    )
    require(record["defining_transition"] is expected_defining, "defining-transition flag drift")
    require(
        record["orientation"]
        == {
            "source_a": "min(source_id_1,source_id_2)",
            "source_b": "max(source_id_1,source_id_2)",
            "signed_difference": "value(source_a)-value(source_b)",
            "fate_table_rows": "source_a_fate",
            "fate_table_columns": "source_b_fate",
        },
        "pair orientation contract drift",
    )
    cache = record["source_cache_records"]
    _exact_keys(cache, ("source_a", "source_b"), "source_cache_records")
    _validate_cache_ref(cache["source_a"], "SOURCE_TRANSITION_CACHE_RECORD_A", "source_cache_records.source_a")
    _validate_cache_ref(cache["source_b"], "SOURCE_TRANSITION_CACHE_RECORD_B", "source_cache_records.source_b")

    require(type(record["current_observation_equal"]) is bool, "current_observation_equal must be Boolean")
    require(type(record["successor_observation_equal"]) is bool, "successor_observation_equal must be Boolean")
    if expected_defining and record["pair_role"] == "TRANSIENT_OBSTRUCTION":
        require(record["current_observation_equal"] is True and record["successor_observation_equal"] is False, "transient defining fate drift")
    if expected_defining and record["pair_role"] == "PERSISTENT_SAFE":
        require(record["current_observation_equal"] is True and record["successor_observation_equal"] is True, "persistent defining fate drift")

    _validate_geometry(record["state_geometry"], "state_geometry")
    _validate_geometry(record["raw_drive_geometry"], "raw_drive_geometry")
    residuals = record["residuals"]
    _exact_keys(residuals, ("current_observation", "successor_observation", "r_raw", "r_clip", "r_corr"), "residuals")
    decoded = {key: validate_sparse_vector(residuals[key], f"residuals.{key}") for key in residuals}
    require(decoded["r_corr"] == _subtract(decoded["r_clip"], decoded["r_raw"]), "r_corr identity failed")
    require(record["current_observation_equal"] == (not decoded["current_observation"]), "current equality flag disagrees with exact residual")
    require(record["successor_observation_equal"] == (not decoded["successor_observation"]), "successor equality flag disagrees with exact residual")

    expected_quadrant = (
        ("RAW_ZERO" if not decoded["r_raw"] else "RAW_NONZERO")
        + "__"
        + ("CLIP_ZERO" if not decoded["r_clip"] else "CLIP_NONZERO")
    )
    require(record["residual_quadrant"] == expected_quadrant, "residual quadrant disagrees with exact vectors")

    table = record["clipping_fate_table"]
    _exact_keys(table, ("row_semantics", "column_semantics", "touched_target_union_count", "cells"), "clipping_fate_table")
    require(table["row_semantics"] == "source_a_fate" and table["column_semantics"] == "source_b_fate", "fate table orientation drift")
    touched = _nonnegative_integer(table["touched_target_union_count"], "clipping_fate_table.touched_target_union_count")
    require(isinstance(table["cells"], list) and len(table["cells"]) == 9, "fate table must contain nine cells")
    expected_cells = [(left, right) for left in FATES for right in FATES]
    observed_cells: list[tuple[str, str]] = []
    cell_total = 0
    for index, cell in enumerate(table["cells"]):
        _exact_keys(cell, ("source_a_fate", "source_b_fate", "count"), f"clipping_fate_table.cells[{index}]")
        observed_cells.append((cell["source_a_fate"], cell["source_b_fate"]))
        cell_total += _nonnegative_integer(cell["count"], f"clipping_fate_table.cells[{index}].count")
    require(observed_cells == expected_cells and cell_total == touched, "fate table cells are incomplete or unordered")

    checks = record["identity_checks"]
    _exact_keys(checks, ("r_corr_identity", "pair_successor_equation", "fiber_reduction"), "identity_checks")
    require(checks["r_corr_identity"] == "PASS", "r_corr identity receipt missing")
    require(checks["pair_successor_equation"] == "PASS", "pair successor equation receipt missing")
    if record["current_observation_equal"]:
        require(checks["fiber_reduction"] == "PASS", "fiber reduction was not checked")
        require(decoded["r_clip"] == _scale(decoded["successor_observation"], 5), "r_clip=5*delta_z_next failed")
    else:
        require(checks["fiber_reduction"] == "NOT_APPLICABLE_CURRENT_OBSERVATION_UNEQUAL", "fiber reduction applicability drift")


def validate_mechanism_record(record: dict[str, Any]) -> None:
    require(isinstance(record, dict), "mechanism record must be an object")
    schema = record.get("schema")
    if schema == "rime.exploratory.male-cns.mts-source-transition-cache-record.v1":
        validate_source_transition_record(record)
        return
    if schema == "rime.exploratory.male-cns.mts-pair-transition-record.v1":
        validate_pair_transition_record(record)
        return
    raise ValueError(f"unknown mechanism record schema: {schema!r}")
