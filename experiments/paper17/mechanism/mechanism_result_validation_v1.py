#!/usr/bin/env python3
"""Independent exact rederivation and result validation for MTS-1.

The producer records evidence. This module reconstructs the registered pair
universe from source-addressed cache records, anchors each successor residual
to the historical Paper XVII observation bytes, and only then derives the
finite-census classification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping, Protocol

import gmpy2
import numpy as np


MTS_ROOT = Path(__file__).resolve().parent
PAPER17_ROOT = MTS_ROOT.parent
DYNAMIC_ROOT = PAPER17_ROOT
REPO_ROOT = MTS_ROOT.parents[2]
sys.path.insert(0, str(DYNAMIC_ROOT))

import finite_history_binary as paper17_binary  # noqa: E402
from exact_state_payload_v1 import (  # noqa: E402
    decode_microstate_payload_v1,
    paper17_legacy_state_sha256_v1,
)
from exact_transition_payloads_v1 import (  # noqa: E402
    FATES,
    decode_clipped_drive_payload_v1,
    decode_clipping_fate_payload_v1,
    decode_raw_drive_payload_v1,
)
from mechanism_records_v1 import (  # noqa: E402
    canonical_json_bytes,
    validate_pair_transition_record,
    validate_source_transition_record,
)
from nontrivial_contrast_v1 import (  # noqa: E402
    classify_finite_census,
    cohort_specs_from_registry,
)
from optimized_exact_common import exact_observation  # noqa: E402
from source_addressed_mechanism_producer_v1 import (  # noqa: E402
    COARSE_DIMENSION,
    CURRENT_TIMES,
    DECAY,
    ALPHA,
    HistoricalRecord,
    Paper17Sidecar,
    SourceSpec,
    load_execution_authority,
    load_source_specs,
)


CLASSIFICATION_SCHEMA = "rime.exploratory.male-cns.mts-mechanism-classification.v1"
RECEIPT_SCHEMA = "rime.exploratory.male-cns.mts-mechanism-validation-receipt.v1"
ZERO = gmpy2.mpq(0)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_relative_path(value: object, label: str) -> PurePosixPath:
    require(isinstance(value, str) and value != "", f"{label} must be a path")
    require("\\" not in value and ":" not in value, f"{label} is not portable")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, f"{label} escapes its root")
    return path


def _artifact(path: Path, role: str, root: Path) -> dict[str, Any]:
    return {
        "role": role,
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _write_json(path: Path, value: object) -> dict[str, Any]:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.exists(), f"refusing to replace validation artifact: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def _rational_json(value: object) -> dict[str, str]:
    rational = gmpy2.mpq(value)
    return {
        "numerator": str(gmpy2.numer(rational)),
        "denominator": str(gmpy2.denom(rational)),
    }


def _sparse_json(values: Mapping[int, object]) -> dict[str, Any]:
    entries = []
    for coordinate in sorted(values):
        value = gmpy2.mpq(values[coordinate])
        if value:
            entries.append({"coordinate": int(coordinate), **_rational_json(value)})
    return {"dimension": COARSE_DIMENSION, "entries": entries}


def _decode_sparse_json(value: Mapping[str, Any]) -> dict[int, gmpy2.mpq]:
    require(value.get("dimension") == COARSE_DIMENSION, "coarse vector dimension drift")
    result: dict[int, gmpy2.mpq] = {}
    previous = -1
    for entry in value.get("entries", []):
        coordinate = int(entry["coordinate"])
        require(previous < coordinate < COARSE_DIMENSION, "coarse vector order drift")
        rational = gmpy2.mpq(int(entry["numerator"]), int(entry["denominator"]))
        require(bool(rational), "explicit zero in coarse vector")
        result[coordinate] = rational
        previous = coordinate
    return result


def _subtract(
    left: Mapping[int, object], right: Mapping[int, object]
) -> dict[int, gmpy2.mpq]:
    result: dict[int, gmpy2.mpq] = {}
    for coordinate in sorted(set(left) | set(right)):
        value = gmpy2.mpq(left.get(coordinate, ZERO)) - gmpy2.mpq(
            right.get(coordinate, ZERO)
        )
        if value:
            result[int(coordinate)] = value
    return result


def _add_scaled(
    left: Mapping[int, object],
    left_factor: object,
    right: Mapping[int, object],
    right_factor: object,
) -> dict[int, gmpy2.mpq]:
    result: dict[int, gmpy2.mpq] = {}
    for coordinate in sorted(set(left) | set(right)):
        value = gmpy2.mpq(left_factor) * gmpy2.mpq(left.get(coordinate, ZERO))
        value += gmpy2.mpq(right_factor) * gmpy2.mpq(
            right.get(coordinate, ZERO)
        )
        if value:
            result[int(coordinate)] = value
    return result


def _scale(values: Mapping[int, object], factor: object) -> dict[int, gmpy2.mpq]:
    return {
        int(coordinate): gmpy2.mpq(factor) * gmpy2.mpq(value)
        for coordinate, value in values.items()
        if value
    }


def _geometry(
    left: Mapping[int, object], right: Mapping[int, object]
) -> dict[str, Any]:
    left_support = set(left)
    right_support = set(right)
    union = left_support | right_support
    l1 = sum(
        (
            abs(
                gmpy2.mpq(left.get(coordinate, ZERO))
                - gmpy2.mpq(right.get(coordinate, ZERO))
            )
            for coordinate in union
        ),
        gmpy2.mpq(0),
    )
    return {
        "support_intersection_count": len(left_support & right_support),
        "support_union_count": len(union),
        "support_symmetric_difference_count": len(left_support ^ right_support),
        "exact_l1_difference": _rational_json(l1),
    }


def _fate_table(left: Mapping[int, str], right: Mapping[int, str]) -> dict[str, Any]:
    counts = {(a, b): 0 for a in FATES for b in FATES}
    for coordinate in sorted(set(left) | set(right)):
        counts[(left.get(coordinate, "LOWER"), right.get(coordinate, "LOWER"))] += 1
    return {
        "row_semantics": "source_a_fate",
        "column_semantics": "source_b_fate",
        "touched_target_union_count": sum(counts.values()),
        "cells": [
            {"source_a_fate": a, "source_b_fate": b, "count": counts[(a, b)]}
            for a in FATES
            for b in FATES
        ],
    }


def _cache_record_ref(
    result_root: Path, source_id: int, current_time: int, role: str
) -> dict[str, Any]:
    relative = f"source-cache/{source_id}/{current_time}.json"
    path = result_root / relative
    require(path.is_file(), f"missing source cache record: {source_id}/{current_time}")
    return {"role": role, "path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _payload_bytes(result_root: Path, record: Mapping[str, Any], key: str) -> bytes:
    ref = record["payloads"][key]
    relative = _safe_relative_path(ref["path"], f"payloads.{key}.path")
    path = result_root / Path(*relative.parts)
    require(path.is_file(), f"missing source payload: {ref['path']}")
    payload = path.read_bytes()
    require(len(payload) == ref["bytes"], f"source payload byte count mismatch: {key}")
    require(sha256_bytes(payload) == ref["sha256"], f"source payload digest mismatch: {key}")
    return payload


class HistoricalSource(Protocol):
    def records_for_source(self, source_id: int) -> dict[int, HistoricalRecord]: ...


Observer = Callable[[Mapping[int, gmpy2.mpq]], dict[int, gmpy2.mpq]]


class CachedHistoricalSource:
    """Cache selected sidecar members without changing their byte identity."""

    def __init__(self, source: HistoricalSource) -> None:
        self.source = source
        self._records: dict[int, dict[int, HistoricalRecord]] = {}

    def records_for_source(self, source_id: int) -> dict[int, HistoricalRecord]:
        if source_id not in self._records:
            self._records[source_id] = self.source.records_for_source(source_id)
        return self._records[source_id]


@dataclass(frozen=True)
class ValidatedSourceCache:
    record: dict[str, Any]
    state: dict[int, gmpy2.mpq]
    raw_drive: dict[int, gmpy2.mpq]
    clipped_drive: dict[int, gmpy2.mpq]
    clipping_fates: dict[int, str]
    observations: dict[str, dict[int, gmpy2.mpq]]


def validate_source_cache_record(
    result_root: Path,
    record: dict[str, Any],
    historical: HistoricalSource,
    observe: Observer,
) -> ValidatedSourceCache:
    """Validate one cache record from canonical payloads and historical bytes."""

    validate_source_transition_record(record)
    state_payload = _payload_bytes(result_root, record, "x_t")
    raw_payload = _payload_bytes(result_root, record, "u_t")
    clipped_payload = _payload_bytes(result_root, record, "clip_u_t")
    fate_payload = _payload_bytes(result_root, record, "clipping_fate")
    state = decode_microstate_payload_v1(state_payload)
    raw_drive = decode_raw_drive_payload_v1(raw_payload)
    clipped_drive = decode_clipped_drive_payload_v1(clipped_payload)
    fates = decode_clipping_fate_payload_v1(fate_payload)
    require(record["payloads"]["x_t"]["entry_count"] == len(state), "state entry count drift")
    require(record["payloads"]["u_t"]["entry_count"] == len(raw_drive), "raw-drive entry count drift")
    require(record["payloads"]["clip_u_t"]["entry_count"] == len(clipped_drive), "clipped-drive entry count drift")
    require(record["payloads"]["clipping_fate"]["entry_count"] == len(fates), "fate entry count drift")
    require(set(raw_drive) <= set(fates), "raw-drive support is not covered by touched-target fates")
    expected_clipped: dict[int, gmpy2.mpq] = {}
    for coordinate, fate in fates.items():
        raw = raw_drive.get(coordinate, ZERO)
        expected_fate = "LOWER" if raw <= 0 else "UPPER" if raw >= 1 else "INTERIOR"
        require(fate == expected_fate, "clipping fate disagrees with exact raw drive")
        clipped = ZERO if raw <= 0 else gmpy2.mpq(1) if raw >= 1 else raw
        if clipped:
            expected_clipped[coordinate] = clipped
    require(clipped_drive == expected_clipped, "clipped-drive payload disagrees with exact clipping")

    observations = {
        "O_x_t": observe(state),
        "O_u_t": observe(raw_drive),
        "O_clip_u_t": observe(clipped_drive),
    }
    for key, value in observations.items():
        require(
            _decode_sparse_json(record["observations"][key]) == value,
            f"source cache {key} was not rederived from exact payload",
        )
    source_id = int(record["source_id"])
    current_time = int(record["current_time"])
    historical_record = historical.records_for_source(source_id)[current_time]
    replayed_observation = paper17_binary.encode_observation_payload(
        COARSE_DIMENSION, observations["O_x_t"]
    )
    require(
        replayed_observation == historical_record.observation_payload,
        "source cache current observation differs from Paper XVII historical bytes",
    )
    require(
        paper17_legacy_state_sha256_v1(state) == historical_record.legacy_state_sha256,
        "source cache microscopic state differs from Paper XVII ancestry hash",
    )
    return ValidatedSourceCache(
        record=record,
        state=state,
        raw_drive=raw_drive,
        clipped_drive=clipped_drive,
        clipping_fates=fates,
        observations=observations,
    )


def _historical_observation(
    historical: HistoricalSource, source_id: int, time: int
) -> dict[int, gmpy2.mpq]:
    payload = historical.records_for_source(source_id)[time].observation_payload
    dimension, observation = paper17_binary.decode_observation_payload(payload)
    require(dimension == COARSE_DIMENSION, "historical successor dimension drift")
    require(
        paper17_binary.encode_observation_payload(dimension, observation) == payload,
        "historical successor observation payload is not canonical",
    )
    return observation


def rederive_pair_record(
    result_root: Path,
    cache_a: ValidatedSourceCache,
    cache_b: ValidatedSourceCache,
    historical: HistoricalSource,
) -> tuple[dict[str, Any], dict[str, bool]]:
    """Rederive one pair record and independently anchor its successor."""

    record_a = cache_a.record
    record_b = cache_b.record
    source_a = int(record_a["source_id"])
    source_b = int(record_b["source_id"])
    require(source_a < source_b, "validator pair orientation requires source_a < source_b")
    require(record_a["current_time"] == record_b["current_time"], "pair current-time mismatch")
    require(record_a["cohort_id"] == record_b["cohort_id"], "cross-cohort pair is forbidden")
    require(record_a["source_role"] == record_b["source_role"], "cross-role pair is forbidden")
    current_time = int(record_a["current_time"])
    current = _subtract(cache_a.observations["O_x_t"], cache_b.observations["O_x_t"])
    r_raw = _subtract(cache_a.observations["O_u_t"], cache_b.observations["O_u_t"])
    r_clip = _subtract(
        cache_a.observations["O_clip_u_t"], cache_b.observations["O_clip_u_t"]
    )
    r_corr = _subtract(r_clip, r_raw)
    predicted_successor = _add_scaled(current, DECAY, r_clip, ALPHA)
    historical_successor = _subtract(
        _historical_observation(historical, source_a, current_time + 1),
        _historical_observation(historical, source_b, current_time + 1),
    )
    require(
        predicted_successor == historical_successor,
        "cache-side transition prediction disagrees with historical successor observation bytes",
    )
    current_equal = not current
    if current_equal:
        require(
            r_clip == _scale(historical_successor, 5),
            "historically anchored fiber reduction r_clip=5*delta_z_next failed",
        )
    role = str(record_a["source_role"])
    defining = (role == "TRANSIENT_OBSTRUCTION" and current_time == 1) or (
        role == "PERSISTENT_SAFE" and current_time in (2, 3)
    )
    expected = {
        "schema": "rime.exploratory.male-cns.mts-pair-transition-record.v1",
        "pair_role": role,
        "cohort_id": record_a["cohort_id"],
        "source_a": source_a,
        "source_b": source_b,
        "current_time": current_time,
        "next_time": current_time + 1,
        "transition": f"{current_time}_TO_{current_time + 1}",
        "defining_transition": defining,
        "orientation": {
            "source_a": "min(source_id_1,source_id_2)",
            "source_b": "max(source_id_1,source_id_2)",
            "signed_difference": "value(source_a)-value(source_b)",
            "fate_table_rows": "source_a_fate",
            "fate_table_columns": "source_b_fate",
        },
        "source_cache_records": {
            "source_a": _cache_record_ref(
                result_root, source_a, current_time, "SOURCE_TRANSITION_CACHE_RECORD_A"
            ),
            "source_b": _cache_record_ref(
                result_root, source_b, current_time, "SOURCE_TRANSITION_CACHE_RECORD_B"
            ),
        },
        "current_observation_equal": current_equal,
        "successor_observation_equal": not historical_successor,
        "state_geometry": _geometry(cache_a.state, cache_b.state),
        "raw_drive_geometry": _geometry(cache_a.raw_drive, cache_b.raw_drive),
        "residuals": {
            "current_observation": _sparse_json(current),
            "successor_observation": _sparse_json(historical_successor),
            "r_raw": _sparse_json(r_raw),
            "r_clip": _sparse_json(r_clip),
            "r_corr": _sparse_json(r_corr),
        },
        "clipping_fate_table": _fate_table(cache_a.clipping_fates, cache_b.clipping_fates),
        "residual_quadrant": ("RAW_ZERO" if not r_raw else "RAW_NONZERO")
        + "__"
        + ("CLIP_ZERO" if not r_clip else "CLIP_NONZERO"),
        "identity_checks": {
            "r_corr_identity": "PASS",
            "pair_successor_equation": "PASS",
            "fiber_reduction": "PASS"
            if current_equal
            else "NOT_APPLICABLE_CURRENT_OBSERVATION_UNEQUAL",
        },
    }
    validate_pair_transition_record(expected)
    return expected, {
        "historical_successor_payload_anchor": True,
        "predicted_equals_historical_successor": True,
        "historical_fiber_reduction_checked": current_equal,
    }


class RegisteredObserver:
    def __init__(self, cache_dir: Path) -> None:
        self.sector_codes = np.load(cache_dir / "sector_codes.npy", mmap_mode="r", allow_pickle=False)
        self.sector_sizes = np.load(cache_dir / "sector_sizes.npy", mmap_mode="r", allow_pickle=False)
        require(
            isinstance(self.sector_codes, np.memmap)
            and isinstance(self.sector_sizes, np.memmap)
            and not self.sector_codes.flags.writeable
            and not self.sector_sizes.flags.writeable,
            "registered observation arrays are not read-only mmap",
        )

    def __call__(self, values: Mapping[int, gmpy2.mpq]) -> dict[int, gmpy2.mpq]:
        observation, _ = exact_observation(
            dict(values), self.sector_codes, self.sector_sizes, COARSE_DIMENSION
        )
        return observation


def _verify_inventory(result_root: Path) -> dict[str, Any]:
    inventory_path = result_root / "inventory.json"
    require(inventory_path.is_file(), "missing MTS-1 result inventory")
    inventory = json.loads(inventory_path.read_text(encoding="ascii"))
    require(
        inventory.get("schema")
        == "rime.exploratory.male-cns.mts-source-addressed-result-inventory.v1",
        "result inventory schema mismatch",
    )
    require(inventory.get("classification_performed") is False, "producer performed classification")
    require(inventory.get("pair_operator_recomputation") is False, "pair stage recomputed operator")
    artifacts = inventory.get("ordered_artifacts")
    require(isinstance(artifacts, list), "ordered result artifacts missing")
    require(len(artifacts) == 2481, "ordered result artifact count drift")
    artifact_paths = [entry["path"] for entry in artifacts]
    require(len(artifact_paths) == len(set(artifact_paths)), "duplicate ordered result artifact path")
    require("inventory.json" not in artifact_paths, "producer inventory is self-bound")
    for entry in artifacts:
        relative = _safe_relative_path(entry["path"], "ordered artifact path")
        path = result_root / Path(*relative.parts)
        require(path.is_file(), f"missing ordered result artifact: {entry['path']}")
        require(path.stat().st_size == entry["bytes"], "ordered artifact byte count mismatch")
        require(sha256_file(path) == entry["sha256"], "ordered artifact digest mismatch")
    require(
        sha256_bytes(canonical_json_bytes(artifacts))
        == inventory["ordered_artifact_closure_sha256"],
        "ordered result closure digest mismatch",
    )
    require(
        inventory.get("source_count") == 153
        and inventory.get("source_transition_cache_record_count") == 459
        and inventory.get("pair_count") == 2325
        and inventory.get("pair_transition_record_count") == 6975,
        "result inventory count drift",
    )
    pair_shards = inventory.get("pair_shards")
    require(isinstance(pair_shards, list) and len(pair_shards) == 33, "pair shard surface drift")
    require(
        len({(entry["cohort_id"], entry["transition"]) for entry in pair_shards}) == 33
        and sum(entry["record_count"] for entry in pair_shards) == 6975,
        "pair shard address or record-count drift",
    )
    ordered_by_path = {entry["path"]: entry for entry in artifacts}
    for shard in pair_shards:
        require(
            shard["path"] in ordered_by_path
            and all(shard[key] == ordered_by_path[shard["path"]][key] for key in ("role", "bytes", "sha256")),
            "pair shard is not bound by the ordered result closure",
        )
    return inventory


def _pair_shard_entry(
    inventory: Mapping[str, Any], cohort_id: str, transition: str
) -> Mapping[str, Any]:
    matches = [
        entry
        for entry in inventory["pair_shards"]
        if entry["cohort_id"] == cohort_id and entry["transition"] == transition
    ]
    require(len(matches) == 1, f"pair shard address is not unique: {cohort_id}/{transition}")
    return matches[0]


def validate_complete_result(
    result_root: Path,
    authority_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Exhaustively validate one complete MTS-1 result without writing outputs."""

    authority, paths = load_execution_authority(authority_path)
    expected_result = (REPO_ROOT / authority["result_root"]).resolve()
    require(result_root.resolve() == expected_result, "result root differs from execution authority")
    inventory = _verify_inventory(result_root)
    registry = json.loads(paths["COHORT_REGISTRY"].read_text(encoding="utf-8"))
    specs, cohorts = load_source_specs(paths["COHORT_REGISTRY"])
    cohort_specs = cohort_specs_from_registry(registry)
    cache_dir = paths["OPTIMIZED_CACHE_MANIFEST"].parent
    observer = RegisteredObserver(cache_dir)
    all_rederived: list[dict[str, Any]] = []
    historical_anchor_count = 0
    historically_reduced_fiber_count = 0

    with Paper17Sidecar(
        paths["PAPER17_EXACT_SIDECAR"], paths["PAPER17_SIDECAR_INVENTORY"]
    ) as sidecar:
        historical = CachedHistoricalSource(sidecar)
        for cohort in sorted(cohorts, key=lambda item: item["cohort_id"]):
            cohort_sources = cohort["source_ids"]
            for current_time in CURRENT_TIMES:
                validated: dict[int, ValidatedSourceCache] = {}
                for source_id in cohort_sources:
                    path = result_root / f"source-cache/{source_id}/{current_time}.json"
                    require(path.is_file(), f"missing source cache record: {source_id}/{current_time}")
                    source_record_bytes = path.read_bytes()
                    record = json.loads(source_record_bytes)
                    require(
                        source_record_bytes == canonical_json_bytes(record),
                        "source cache record is not canonical JSON",
                    )
                    validated[source_id] = validate_source_cache_record(
                        result_root, record, historical, observer
                    )
                transition = f"{current_time}_TO_{current_time + 1}"
                shard_entry = _pair_shard_entry(inventory, cohort["cohort_id"], transition)
                shard_path = result_root / Path(
                    *_safe_relative_path(shard_entry["path"], "pair shard path").parts
                )
                lines = shard_path.read_bytes().splitlines(keepends=True)
                expected_pairs = list(combinations(cohort_sources, 2))
                require(len(lines) == len(expected_pairs), "pair shard record count mismatch")
                for line, (source_a, source_b) in zip(lines, expected_pairs, strict=True):
                    require(line.endswith(b"\n"), "pair shard contains a noncanonical final line")
                    actual = json.loads(line)
                    expected, anchors = rederive_pair_record(
                        result_root,
                        validated[source_a],
                        validated[source_b],
                        historical,
                    )
                    require(
                        line == canonical_json_bytes(expected),
                        "producer pair record differs from exhaustive validator rederivation",
                    )
                    require(actual == expected, "producer pair JSON differs after canonical parsing")
                    historical_anchor_count += int(anchors["historical_successor_payload_anchor"])
                    historically_reduced_fiber_count += int(
                        anchors["historical_fiber_reduction_checked"]
                    )
                    all_rederived.append(expected)

    require(len(all_rederived) == 6975, "exhaustive pair rederivation count drift")
    classification = classify_finite_census(all_rederived, cohort_specs)
    require(classification["comparison_cell_count"] == 15, "comparison cell count drift")
    result = {
        "schema": CLASSIFICATION_SCHEMA,
        "status": "PASS",
        "outcome": classification["outcome"],
        "scientific_outcome_derived_by": "EXHAUSTIVE_RESULT_VALIDATOR",
        "producer_classification_performed": False,
        "source_transition_cache_record_count": 459,
        "pair_transition_record_count": len(all_rederived),
        "historical_successor_payload_anchor_count": historical_anchor_count,
        "historically_anchored_fiber_reduction_count": historically_reduced_fiber_count,
        "historical_successor_equation": "delta_z_next_historical=(4/5)delta_z_t+(1/5)r_clip",
        "current_equal_reduction": "r_clip=5*delta_z_next_historical",
        "classification": classification,
        "claim_boundary": {
            "identity_layer_replay_is_mechanism_finding": False,
            "quadrant_labels_are_mechanism_labels": False,
            "statistical_inference": "NONE",
            "causal_attribution": "NONE",
            "external_world_input": "NONE",
        },
    }
    audit = {
        "ordered_artifact_closure_sha256": inventory["ordered_artifact_closure_sha256"],
        "historical_successor_payload_anchor_count": historical_anchor_count,
        "historically_anchored_fiber_reduction_count": historically_reduced_fiber_count,
        "complete_pair_universe_rederived": True,
        "all_pair_records_byte_equal_rederivation": True,
        "all_primary_predicate_signatures_rederived": True,
        "all_comparison_cells_rederived": True,
        "normalized_histograms_compared_by_integer_cross_multiplication": True,
    }
    return result, audit


def write_validation_outputs(
    result_root: Path,
    authority_path: Path,
    classification_output: Path,
    receipt_output: Path,
) -> dict[str, Any]:
    owned_results = (MTS_ROOT / "results").resolve()
    require(result_root.resolve().is_relative_to(owned_results), "result root is not MTS-1-owned")
    validation_root = (result_root / "validation").resolve()
    require(
        classification_output.resolve().is_relative_to(validation_root)
        and receipt_output.resolve().is_relative_to(validation_root),
        "validator outputs must remain under the result-owned validation directory",
    )
    require(classification_output.resolve() != receipt_output.resolve(), "classification and receipt paths coincide")
    result, audit = validate_complete_result(result_root, authority_path)
    result_meta = _write_json(classification_output, result)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "validation_mode": "LOCAL_EXHAUSTIVE_EXACT_REDERIVATION",
        "independent_validation": False,
        "producer_replayed": False,
        "scientific_outcome_written_by_producer": False,
        "result_root": result_root.relative_to(REPO_ROOT).as_posix(),
        "classification": {
            "path": classification_output.relative_to(REPO_ROOT).as_posix(),
            **result_meta,
        },
        "execution_authority": _artifact(authority_path, "EXECUTION_AUTHORITY", REPO_ROOT),
        "result_inventory": _artifact(result_root / "inventory.json", "RESULT_INVENTORY", REPO_ROOT),
        "validator": _artifact(Path(__file__).resolve(), "EXHAUSTIVE_RESULT_VALIDATOR", REPO_ROOT),
        "verified": audit,
    }
    _write_json(receipt_output, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--classification-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()
    receipt = write_validation_outputs(
        args.result_root.resolve(),
        args.authority.resolve(),
        args.classification_output.resolve(),
        args.receipt_output.resolve(),
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
