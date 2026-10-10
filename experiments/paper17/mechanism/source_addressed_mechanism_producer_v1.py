#!/usr/bin/env python3
"""Produce the source-addressed MTS-1 cache and pair surface.

The CLI is fail-closed: scientific execution requires a later immutable
authority artifact. Importable helpers support synthetic hostile tests without
reading any of the 153 registered scientific sources.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import io
import json
import math
import os
import struct
import sys
import tarfile
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Mapping, Protocol

import gmpy2
import numpy as np


MTS_ROOT = Path(__file__).resolve().parent
PAPER17_ROOT = MTS_ROOT.parent
DYNAMIC_ROOT = PAPER17_ROOT
REPO_ROOT = MTS_ROOT.parents[2]
sys.path.insert(0, str(DYNAMIC_ROOT))

import finite_history_binary as paper17_binary  # noqa: E402
from exact_state_payload_v1 import (  # noqa: E402
    DOMAIN_TAG as STATE_DOMAIN_TAG,
    REGISTERED_DIMENSION,
    iter_microstate_payload_v1,
    microstate_payload_sha256_v1,
    paper17_legacy_state_sha256_v1,
)
from exact_transition_payloads_v1 import (  # noqa: E402
    CLIPPED_DRIVE_DOMAIN_TAG,
    CLIPPING_FATE_DOMAIN_TAG,
    FATES,
    RAW_DRIVE_DOMAIN_TAG,
    iter_clipped_drive_payload_v1,
    iter_clipping_fate_payload_v1,
    iter_raw_drive_payload_v1,
)
from mechanism_records_v1 import (  # noqa: E402
    canonical_json_bytes,
    validate_pair_transition_record,
    validate_source_transition_record,
)
from optimized_exact_common import exact_observation, runtime_identity  # noqa: E402


AUTHORITY_SCHEMA = "rime.exploratory.male-cns.mts-source-addressed-execution-authority.v1"
AUTHORITY_VALUE = "MTS1_SOURCE_ADDRESSED_PRODUCER_V1_ONLY"
INVENTORY_SCHEMA = "rime.exploratory.male-cns.mts-source-addressed-result-inventory.v1"
SOURCE_REPLAY_SCHEMA = "rime.exploratory.male-cns.mts-source-replay.v1"
CURRENT_TIMES = (1, 2, 3)
COARSE_DIMENSION = 28
ALPHA = gmpy2.mpq(1, 5)
DECAY = gmpy2.mpq(4, 5)
ZERO = gmpy2.mpq(0)
ONE = gmpy2.mpq(1)
_RATIONAL_HEADER = struct.Struct(">HQQ")
_RATIONAL_ENTRY = struct.Struct(">QBII")
_FATE_ENTRY = struct.Struct(">QB")
_FATE_LABELS = {1: "LOWER", 2: "INTERIOR", 3: "UPPER"}


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


def _repo_path(relative: str) -> Path:
    path = (REPO_ROOT / Path(*_safe_relative_path(relative, "repository path").parts)).resolve()
    require(path.is_relative_to(REPO_ROOT.resolve()), "repository path escapes checkout")
    return path


def _artifact(path: Path, role: str, root: Path) -> dict[str, Any]:
    return {
        "role": role,
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _verify_repo_artifact(entry: Mapping[str, Any], role: str) -> Path:
    require(entry.get("role") == role, f"authority artifact role mismatch: {role}")
    path = _repo_path(str(entry["path"]))
    require(path.is_file(), f"missing authority artifact: {role}")
    require(path.stat().st_size == int(entry["bytes"]), f"authority artifact size mismatch: {role}")
    require(sha256_file(path) == entry["sha256"], f"authority artifact digest mismatch: {role}")
    return path


def _write_json(path: Path, value: object) -> dict[str, Any]:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
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
            parts = _rational_json(value)
            entries.append({"coordinate": int(coordinate), **parts})
    return {"dimension": COARSE_DIMENSION, "entries": entries}


def _subtract(left: Mapping[int, object], right: Mapping[int, object]) -> dict[int, gmpy2.mpq]:
    result: dict[int, gmpy2.mpq] = {}
    for coordinate in sorted(set(left) | set(right)):
        value = gmpy2.mpq(left.get(coordinate, ZERO)) - gmpy2.mpq(right.get(coordinate, ZERO))
        if value:
            result[int(coordinate)] = value
    return result


def _add_scaled(
    left: Mapping[int, object], left_factor: object,
    right: Mapping[int, object], right_factor: object,
) -> dict[int, gmpy2.mpq]:
    result: dict[int, gmpy2.mpq] = {}
    for coordinate in sorted(set(left) | set(right)):
        value = gmpy2.mpq(left_factor) * gmpy2.mpq(left.get(coordinate, ZERO))
        value += gmpy2.mpq(right_factor) * gmpy2.mpq(right.get(coordinate, ZERO))
        if value:
            result[int(coordinate)] = value
    return result


@dataclass(frozen=True)
class SourceSpec:
    source_id: int
    source_role: str
    cohort_id: str
    initial_sector_label: str


@dataclass(frozen=True)
class HistoricalRecord:
    observation_payload: bytes
    legacy_state_sha256: str


@dataclass(frozen=True)
class TransitionResult:
    next_state: dict[int, gmpy2.mpq]
    raw_drive: dict[int, gmpy2.mpq]
    clipped_drive: dict[int, gmpy2.mpq]
    clipping_fates: dict[int, str]
    counts: dict[str, int]


class ExactBackend(Protocol):
    sector_count: int

    def observe(self, values: Mapping[int, gmpy2.mpq]) -> dict[int, gmpy2.mpq]: ...
    def transition(self, state: dict[int, gmpy2.mpq]) -> TransitionResult: ...
    def source_descriptors(self, source_id: int) -> dict[str, int]: ...


class HistoricalSource(Protocol):
    def records_for_source(self, source_id: int) -> dict[int, HistoricalRecord]: ...


def load_source_specs(registry_path: Path) -> tuple[list[SourceSpec], list[dict[str, Any]]]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    specs: list[SourceSpec] = []
    cohorts: list[dict[str, Any]] = []
    for section, source_role in (
        ("transient_obstruction", "TRANSIENT_OBSTRUCTION"),
        ("persistent_safe", "PERSISTENT_SAFE"),
    ):
        for cohort in registry[section]["cohorts"]:
            labels = cohort["initial_sector_labels"]
            require(len(labels) == 1, "MTS-1 source cohort must have one initial sector")
            source_ids = [int(value) for value in cohort["source_ids"]]
            require(source_ids == sorted(source_ids) and len(source_ids) == len(set(source_ids)), "cohort sources are not canonical")
            cohort_entry = {
                "cohort_id": cohort["cohort_id"],
                "source_role": source_role,
                "source_ids": source_ids,
            }
            cohorts.append(cohort_entry)
            specs.extend(
                SourceSpec(source, source_role, cohort["cohort_id"], labels[0])
                for source in source_ids
            )
    require(len(specs) == 153 and len({spec.source_id for spec in specs}) == 153, "registered source surface drift")
    return sorted(specs, key=lambda item: item.source_id), cohorts


def _decode_shard_bytes(payload: bytes) -> dict[int, tuple[bytes, dict[int, gmpy2.mpq]]]:
    handle = io.BytesIO(payload)
    header = handle.read(paper17_binary.FILE_HEADER.size)
    require(len(header) == paper17_binary.FILE_HEADER.size, "truncated Paper XVII shard")
    magic, version, count = paper17_binary.FILE_HEADER.unpack(header)
    require(magic == paper17_binary.MAGIC and version == paper17_binary.VERSION, "Paper XVII shard header mismatch")
    records: dict[int, tuple[bytes, dict[int, gmpy2.mpq]]] = {}
    for _ in range(count):
        prefix = handle.read(paper17_binary.RECORD_LENGTH.size)
        require(len(prefix) == paper17_binary.RECORD_LENGTH.size, "truncated Paper XVII record length")
        length = paper17_binary.RECORD_LENGTH.unpack(prefix)[0]
        record = handle.read(length)
        require(len(record) == length and length >= 20, "truncated Paper XVII record")
        _, time = struct.unpack(">QI", record[:12])
        observation_payload = record[12:]
        dimension, observation = paper17_binary.decode_observation_payload(observation_payload)
        require(dimension == COARSE_DIMENSION and time not in records, "Paper XVII record drift")
        records[int(time)] = (observation_payload, observation)
    require(not handle.read(1), "Paper XVII shard has trailing bytes")
    return records


class Paper17Sidecar:
    """Read selected historical observations and legacy hashes from the bound tar."""

    def __init__(self, tar_path: Path, inventory_path: Path) -> None:
        self.tar_path = tar_path
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        self.entries = {int(item["source_id"]): item for item in inventory["shards"]}
        self._tar = tarfile.open(tar_path, "r")

    def close(self) -> None:
        self._tar.close()

    def __enter__(self) -> "Paper17Sidecar":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _member_bytes(self, name: str) -> bytes:
        member = self._tar.getmember(f"finite-history-v1/{name}")
        handle = self._tar.extractfile(member)
        require(handle is not None, f"cannot read sidecar member: {name}")
        return handle.read()

    def records_for_source(self, source_id: int) -> dict[int, HistoricalRecord]:
        entry = self.entries[source_id]
        shard_bytes = self._member_bytes(entry["path"])
        require(len(shard_bytes) == int(entry["bytes"]), "historical shard byte count mismatch")
        require(sha256_bytes(shard_bytes) == entry["sha256"], "historical shard digest mismatch")
        metadata_bytes = self._member_bytes(entry["metadata_path"])
        require(sha256_bytes(metadata_bytes) == entry["metadata_sha256"], "historical metadata digest mismatch")
        metadata = json.loads(metadata_bytes)
        decoded = _decode_shard_bytes(shard_bytes)
        require(set(decoded) == set(range(5)), "historical source does not contain times 0..4")
        steps = {int(item["time"]): item for item in metadata["steps"]}
        return {
            time: HistoricalRecord(
                observation_payload=decoded[time][0],
                legacy_state_sha256=steps[time]["state_payload_sha256_provenance_only"],
            )
            for time in range(5)
        }


class RegisteredBackend:
    def __init__(self, cache_dir: Path, compiled_kernel: Path) -> None:
        names = ("indptr", "indices", "numerators", "row_abs", "sector_codes", "sector_sizes")
        self.arrays = {
            name: np.load(cache_dir / f"{name}.npy", mmap_mode="r", allow_pickle=False)
            for name in names
        }
        for name, array in self.arrays.items():
            require(isinstance(array, np.memmap) and not array.flags.writeable, f"backend array is not read-only mmap: {name}")
        labels = json.loads((cache_dir / "sector_labels.json").read_text(encoding="utf-8"))
        self.sector_count = len(labels)
        sys.path.insert(0, str(compiled_kernel.parent))
        self.kernel = importlib.import_module(compiled_kernel.stem.split(".")[0])
        require(hasattr(self.kernel, "exact_transition"), "compiled MTS-1 kernel lacks exact_transition")

    def observe(self, values: Mapping[int, gmpy2.mpq]) -> dict[int, gmpy2.mpq]:
        observation, _ = exact_observation(
            dict(values), self.arrays["sector_codes"], self.arrays["sector_sizes"], self.sector_count
        )
        return observation

    def transition(self, state: dict[int, gmpy2.mpq]) -> TransitionResult:
        result = self.kernel.exact_transition(
            self.arrays["indptr"], self.arrays["indices"], self.arrays["numerators"],
            self.arrays["row_abs"], state, ALPHA, DECAY, ZERO, ONE,
        )
        return TransitionResult(*result)

    def source_descriptors(self, source_id: int) -> dict[str, int]:
        start = int(self.arrays["indptr"][source_id])
        stop = int(self.arrays["indptr"][source_id + 1])
        weights = self.arrays["numerators"][start:stop]
        require(bool(np.all(weights != 0)), "registered CSR row contains an explicit zero")
        positive = weights[weights > 0]
        negative = weights[weights < 0]
        positive_mass = int(positive.sum(dtype=np.int64))
        negative_mass = int((-negative).sum(dtype=np.int64))
        return {
            "known_sign_out_degree": int(stop - start),
            "known_sign_positive_out_degree": int(len(positive)),
            "known_sign_negative_out_degree": int(len(negative)),
            "known_sign_outgoing_positive_mass": positive_mass,
            "known_sign_outgoing_negative_absolute_mass": negative_mass,
            "known_sign_outgoing_absolute_mass": positive_mass + negative_mass,
        }


class ResultWriter:
    def __init__(self, staging_root: Path) -> None:
        self.root = staging_root
        self.root.mkdir(parents=True, exist_ok=False)
        self.artifacts: list[dict[str, Any]] = []

    def write_payload(
        self,
        relative: str,
        chunks: Iterable[bytes],
        *,
        role: str,
        codec: str,
        semantic_role: str,
        entry_count: int,
    ) -> dict[str, Any]:
        path = self.root / Path(*_safe_relative_path(relative, "payload path").parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        digest = hashlib.sha256()
        size = 0
        with temporary.open("wb") as handle:
            for chunk in chunks:
                handle.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        temporary.replace(path)
        ref = {
            "role": role,
            "path": relative,
            "bytes": size,
            "sha256": digest.hexdigest(),
            "codec": codec,
            "semantic_role": semantic_role,
            "dimension": REGISTERED_DIMENSION,
            "entry_count": int(entry_count),
        }
        self.artifacts.append({key: ref[key] for key in ("role", "path", "bytes", "sha256")})
        return ref

    def write_json(self, relative: str, value: object, role: str) -> dict[str, Any]:
        path = self.root / Path(*_safe_relative_path(relative, "JSON path").parts)
        meta = _write_json(path, value)
        ref = {"role": role, "path": relative, **meta}
        self.artifacts.append(ref)
        return ref


def _observation_gate(
    source_id: int,
    time: int,
    state: Mapping[int, gmpy2.mpq],
    observation: Mapping[int, gmpy2.mpq],
    historical: HistoricalRecord,
) -> dict[str, Any]:
    replayed_bytes = paper17_binary.encode_observation_payload(COARSE_DIMENSION, dict(observation))
    require(replayed_bytes == historical.observation_payload, f"Paper XVII observation replay mismatch: source={source_id}, time={time}")
    legacy = paper17_legacy_state_sha256_v1(state)
    require(legacy == historical.legacy_state_sha256, f"Paper XVII state hash mismatch: source={source_id}, time={time}")
    return {
        "paper17_observation_payload_sha256": sha256_bytes(historical.observation_payload),
        "replayed_observation_payload_sha256": sha256_bytes(replayed_bytes),
        "observation_bytes_equal": True,
        "paper17_legacy_state_sha256": historical.legacy_state_sha256,
        "replayed_legacy_state_sha256": legacy,
        "legacy_state_hash_equal": True,
    }


def produce_source(
    spec: SourceSpec,
    backend: ExactBackend,
    historical_source: HistoricalSource,
    writer: ResultWriter,
) -> list[dict[str, Any]]:
    historical = historical_source.records_for_source(spec.source_id)
    require(set(historical) == set(range(5)), "historical replay surface must contain times 0..4")
    state = {spec.source_id: gmpy2.mpq(1)}
    replay_rows: list[dict[str, Any]] = []
    cache_records: list[dict[str, Any]] = []
    descriptors = backend.source_descriptors(spec.source_id)

    for current_time in range(4):
        observation = backend.observe(state)
        gate = _observation_gate(spec.source_id, current_time, state, observation, historical[current_time])
        replay_rows.append({"time": current_time, **gate})
        transition = backend.transition(state)
        require(
            transition.counts["touched_target_count"] == len(transition.clipping_fates)
            and transition.counts["raw_drive_support_count"] == len(transition.raw_drive)
            and transition.counts["clipped_drive_support_count"] == len(transition.clipped_drive),
            "exact transition support counts disagree with payloads",
        )
        require(
            transition.counts["clip_lower_count"] == sum(value == "LOWER" for value in transition.clipping_fates.values())
            and transition.counts["clip_interior_count"] == sum(value == "INTERIOR" for value in transition.clipping_fates.values())
            and transition.counts["clip_upper_count"] == sum(value == "UPPER" for value in transition.clipping_fates.values()),
            "exact transition fate counts disagree with payloads",
        )
        if current_time in CURRENT_TIMES:
            prefix = f"payloads/source-cache/{spec.source_id}/{current_time}"
            state_ref = writer.write_payload(
                f"{prefix}/x_t.bin", iter_microstate_payload_v1(state),
                role="MICROSCOPIC_STATE_PAYLOAD", codec="RIME-MTS-MICROSTATE-V1",
                semantic_role="MICROSCOPIC_STATE", entry_count=len(state),
            )
            require(state_ref["sha256"] == microstate_payload_sha256_v1(state), "state payload streaming digest drift")
            raw_ref = writer.write_payload(
                f"{prefix}/u_t.bin", iter_raw_drive_payload_v1(transition.raw_drive),
                role="RAW_SIGNED_DRIVE_PAYLOAD", codec="RIME-MTS-RAW-DRIVE-V1",
                semantic_role="RAW_SIGNED_DRIVE", entry_count=len(transition.raw_drive),
            )
            clipped_ref = writer.write_payload(
                f"{prefix}/clip_u_t.bin", iter_clipped_drive_payload_v1(transition.clipped_drive),
                role="CLIPPED_DRIVE_PAYLOAD", codec="RIME-MTS-CLIPPED-DRIVE-V1",
                semantic_role="CLIPPED_DRIVE", entry_count=len(transition.clipped_drive),
            )
            fate_ref = writer.write_payload(
                f"{prefix}/clipping_fate.bin", iter_clipping_fate_payload_v1(transition.clipping_fates),
                role="CLIPPING_FATE_PAYLOAD", codec="RIME-MTS-CLIPPING-FATE-V1",
                semantic_role="TOUCHED_TARGET_CLIPPING_FATE", entry_count=len(transition.clipping_fates),
            )
            source_gate = {
                **gate,
                "canonical_state_payload_sha256": state_ref["sha256"],
                "canonical_state_payload_valid": True,
            }
            payloads = {
                "x_t": state_ref,
                "u_t": raw_ref,
                "clip_u_t": clipped_ref,
                "clipping_fate": fate_ref,
            }
            record = {
                "schema": "rime.exploratory.male-cns.mts-source-transition-cache-record.v1",
                "source_id": spec.source_id,
                "source_role": spec.source_role,
                "cohort_id": spec.cohort_id,
                "initial_sector_label": spec.initial_sector_label,
                "current_time": current_time,
                "next_time": current_time + 1,
                "transition": f"{current_time}_TO_{current_time + 1}",
                "replay_gates": source_gate,
                "payloads": payloads,
                "observations": {
                    "O_x_t": _sparse_json(observation),
                    "O_u_t": _sparse_json(backend.observe(transition.raw_drive)),
                    "O_clip_u_t": _sparse_json(backend.observe(transition.clipped_drive)),
                },
                "clipping_fate": {
                    "touched_target_semantics": "TARGET_RECEIVES_AT_LEAST_ONE_PRE_SUM_EDGE_CONTRIBUTION",
                    "lower_semantics": "u<=0",
                    "interior_semantics": "0<u<1",
                    "upper_semantics": "u>=1",
                    "touched_target_count": len(transition.clipping_fates),
                    "counts": {
                        fate: sum(value == fate for value in transition.clipping_fates.values())
                        for fate in FATES
                    },
                },
                "source_descriptors": descriptors,
                "ordered_payload_digest": sha256_bytes(canonical_json_bytes([payloads[key] for key in ("x_t", "u_t", "clip_u_t", "clipping_fate")])),
            }
            validate_source_transition_record(record)
            cache_records.append(record)
        state = transition.next_state

    final_observation = backend.observe(state)
    final_gate = _observation_gate(spec.source_id, 4, state, final_observation, historical[4])
    replay_rows.append({"time": 4, **final_gate})
    replay = {
        "schema": SOURCE_REPLAY_SCHEMA,
        "status": "PASS",
        "source_id": spec.source_id,
        "times": replay_rows,
        "all_observation_bytes_equal": True,
        "all_legacy_state_hashes_equal": True,
    }
    writer.write_json(f"source-replay/{spec.source_id}.json", replay, "SOURCE_REPLAY_RECEIPT")
    for record in cache_records:
        writer.write_json(
            f"source-cache/{spec.source_id}/{record['current_time']}.json",
            record,
            "SOURCE_TRANSITION_CACHE_RECORD",
        )
    return cache_records


def _decode_sparse_json(value: Mapping[str, Any]) -> dict[int, gmpy2.mpq]:
    require(value["dimension"] == COARSE_DIMENSION, "coarse vector dimension drift")
    result: dict[int, gmpy2.mpq] = {}
    previous = -1
    for entry in value["entries"]:
        coordinate = int(entry["coordinate"])
        require(previous < coordinate < COARSE_DIMENSION, "coarse vector order drift")
        rational = gmpy2.mpq(int(entry["numerator"]), int(entry["denominator"]))
        require(bool(rational), "explicit zero in coarse vector")
        result[coordinate] = rational
        previous = coordinate
    return result


def _iter_rational_payload(path: Path, domain_tag: bytes) -> Iterator[tuple[int, gmpy2.mpq]]:
    with path.open("rb") as handle:
        require(handle.read(len(domain_tag)) == domain_tag, "exact payload domain tag mismatch")
        header = handle.read(_RATIONAL_HEADER.size)
        require(len(header) == _RATIONAL_HEADER.size, "truncated exact payload header")
        version, dimension, count = _RATIONAL_HEADER.unpack(header)
        require(version == 1 and dimension == REGISTERED_DIMENSION and count <= REGISTERED_DIMENSION, "exact payload header drift")
        previous = -1
        for _ in range(count):
            entry_header = handle.read(_RATIONAL_ENTRY.size)
            require(len(entry_header) == _RATIONAL_ENTRY.size, "truncated exact payload entry")
            coordinate, sign, numerator_length, denominator_length = _RATIONAL_ENTRY.unpack(entry_header)
            require(previous < coordinate < REGISTERED_DIMENSION and sign in (1, 2), "noncanonical exact payload entry")
            numerator_bytes = handle.read(numerator_length)
            denominator_bytes = handle.read(denominator_length)
            require(
                len(numerator_bytes) == numerator_length and len(denominator_bytes) == denominator_length
                and numerator_length > 0 and denominator_length > 0
                and numerator_bytes[0] != 0 and denominator_bytes[0] != 0,
                "noncanonical exact integer encoding",
            )
            numerator = int.from_bytes(numerator_bytes, "big")
            denominator = int.from_bytes(denominator_bytes, "big")
            require(numerator > 0 and denominator > 0 and math.gcd(numerator, denominator) == 1, "noncanonical exact rational")
            yield int(coordinate), gmpy2.mpq(numerator if sign == 1 else -numerator, denominator)
            previous = int(coordinate)
        require(not handle.read(1), "trailing exact payload bytes")


def _geometry(path_a: Path, path_b: Path, domain_tag: bytes) -> dict[str, Any]:
    left = iter(_iter_rational_payload(path_a, domain_tag))
    right = iter(_iter_rational_payload(path_b, domain_tag))
    a = next(left, None)
    b = next(right, None)
    intersection = union = 0
    l1 = gmpy2.mpq(0)
    while a is not None or b is not None:
        if b is None or (a is not None and a[0] < b[0]):
            union += 1
            l1 += abs(a[1])
            a = next(left, None)
        elif a is None or b[0] < a[0]:
            union += 1
            l1 += abs(b[1])
            b = next(right, None)
        else:
            intersection += 1
            union += 1
            l1 += abs(a[1] - b[1])
            a = next(left, None)
            b = next(right, None)
    return {
        "support_intersection_count": intersection,
        "support_union_count": union,
        "support_symmetric_difference_count": union - intersection,
        "exact_l1_difference": _rational_json(l1),
    }


def _iter_fates(path: Path) -> Iterator[tuple[int, str]]:
    with path.open("rb") as handle:
        require(handle.read(len(CLIPPING_FATE_DOMAIN_TAG)) == CLIPPING_FATE_DOMAIN_TAG, "fate payload domain tag mismatch")
        header = handle.read(_RATIONAL_HEADER.size)
        require(len(header) == _RATIONAL_HEADER.size, "truncated fate header")
        version, dimension, count = _RATIONAL_HEADER.unpack(header)
        require(version == 1 and dimension == REGISTERED_DIMENSION and count <= REGISTERED_DIMENSION, "fate header drift")
        previous = -1
        for _ in range(count):
            payload = handle.read(_FATE_ENTRY.size)
            require(len(payload) == _FATE_ENTRY.size, "truncated fate entry")
            coordinate, code = _FATE_ENTRY.unpack(payload)
            require(previous < coordinate < REGISTERED_DIMENSION and code in _FATE_LABELS, "noncanonical fate entry")
            yield int(coordinate), _FATE_LABELS[code]
            previous = int(coordinate)
        require(not handle.read(1), "trailing fate payload bytes")


def _fate_table(path_a: Path, path_b: Path) -> dict[str, Any]:
    left = iter(_iter_fates(path_a))
    right = iter(_iter_fates(path_b))
    a = next(left, None)
    b = next(right, None)
    counts = {(fa, fb): 0 for fa in FATES for fb in FATES}
    touched = 0
    while a is not None or b is not None:
        if b is None or (a is not None and a[0] < b[0]):
            fa, fb = a[1], "LOWER"
            a = next(left, None)
        elif a is None or b[0] < a[0]:
            fa, fb = "LOWER", b[1]
            b = next(right, None)
        else:
            fa, fb = a[1], b[1]
            a = next(left, None)
            b = next(right, None)
        counts[(fa, fb)] += 1
        touched += 1
    return {
        "row_semantics": "source_a_fate",
        "column_semantics": "source_b_fate",
        "touched_target_union_count": touched,
        "cells": [
            {"source_a_fate": fa, "source_b_fate": fb, "count": counts[(fa, fb)]}
            for fa in FATES for fb in FATES
        ],
    }


def _payload_path(result_root: Path, record: Mapping[str, Any], key: str) -> Path:
    ref = record["payloads"][key]
    path = result_root / Path(*_safe_relative_path(ref["path"], f"payloads.{key}.path").parts)
    require(path.is_file() and path.stat().st_size == ref["bytes"], f"missing payload: {key}")
    return path


def verify_source_cache_surface(result_root: Path, specs: list[SourceSpec]) -> None:
    """Validate all cache metadata and exact payload bindings once before pairing."""
    for spec in specs:
        for current_time in CURRENT_TIMES:
            record_path = result_root / f"source-cache/{spec.source_id}/{current_time}.json"
            require(record_path.is_file(), f"missing source cache record: {spec.source_id}/{current_time}")
            record = json.loads(record_path.read_text(encoding="ascii"))
            validate_source_transition_record(record)
            require(record["source_id"] == spec.source_id and record["current_time"] == current_time, "source cache address mismatch")
            for key, ref in record["payloads"].items():
                payload_path = _payload_path(result_root, record, key)
                require(sha256_file(payload_path) == ref["sha256"], f"source cache payload digest mismatch: {spec.source_id}/{current_time}/{key}")


def _cache_record_ref(result_root: Path, source_id: int, current_time: int, role: str) -> dict[str, Any]:
    relative = f"source-cache/{source_id}/{current_time}.json"
    path = result_root / relative
    require(path.is_file(), f"missing source cache record: {source_id}/{current_time}")
    return {"role": role, "path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def derive_pair_record(
    result_root: Path,
    record_a: Mapping[str, Any],
    record_b: Mapping[str, Any],
) -> dict[str, Any]:
    source_a = int(record_a["source_id"])
    source_b = int(record_b["source_id"])
    require(source_a < source_b, "pair records require source_a < source_b")
    require(record_a["current_time"] == record_b["current_time"], "pair current-time mismatch")
    require(record_a["cohort_id"] == record_b["cohort_id"], "cross-cohort pair is forbidden")
    require(record_a["source_role"] == record_b["source_role"], "cross-role pair is forbidden")
    current_time = int(record_a["current_time"])

    obs_a = {key: _decode_sparse_json(value) for key, value in record_a["observations"].items()}
    obs_b = {key: _decode_sparse_json(value) for key, value in record_b["observations"].items()}
    current = _subtract(obs_a["O_x_t"], obs_b["O_x_t"])
    r_raw = _subtract(obs_a["O_u_t"], obs_b["O_u_t"])
    r_clip = _subtract(obs_a["O_clip_u_t"], obs_b["O_clip_u_t"])
    r_corr = _subtract(r_clip, r_raw)
    successor = _add_scaled(current, DECAY, r_clip, ALPHA)
    current_equal = not current
    successor_equal = not successor
    role = str(record_a["source_role"])
    defining = (role == "TRANSIENT_OBSTRUCTION" and current_time == 1) or (
        role == "PERSISTENT_SAFE" and current_time in (2, 3)
    )

    state_a = _payload_path(result_root, record_a, "x_t")
    state_b = _payload_path(result_root, record_b, "x_t")
    raw_a = _payload_path(result_root, record_a, "u_t")
    raw_b = _payload_path(result_root, record_b, "u_t")
    fate_a = _payload_path(result_root, record_a, "clipping_fate")
    fate_b = _payload_path(result_root, record_b, "clipping_fate")
    pair = {
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
            "source_a": _cache_record_ref(result_root, source_a, current_time, "SOURCE_TRANSITION_CACHE_RECORD_A"),
            "source_b": _cache_record_ref(result_root, source_b, current_time, "SOURCE_TRANSITION_CACHE_RECORD_B"),
        },
        "current_observation_equal": current_equal,
        "successor_observation_equal": successor_equal,
        "state_geometry": _geometry(state_a, state_b, STATE_DOMAIN_TAG),
        "raw_drive_geometry": _geometry(raw_a, raw_b, RAW_DRIVE_DOMAIN_TAG),
        "residuals": {
            "current_observation": _sparse_json(current),
            "successor_observation": _sparse_json(successor),
            "r_raw": _sparse_json(r_raw),
            "r_clip": _sparse_json(r_clip),
            "r_corr": _sparse_json(r_corr),
        },
        "clipping_fate_table": _fate_table(fate_a, fate_b),
        "residual_quadrant": ("RAW_ZERO" if not r_raw else "RAW_NONZERO") + "__" + ("CLIP_ZERO" if not r_clip else "CLIP_NONZERO"),
        "identity_checks": {
            "r_corr_identity": "PASS",
            "pair_successor_equation": "PASS",
            "fiber_reduction": "PASS" if current_equal else "NOT_APPLICABLE_CURRENT_OBSERVATION_UNEQUAL",
        },
    }
    validate_pair_transition_record(pair)
    return pair


def derive_pair_surface(
    result_root: Path,
    cohorts: list[dict[str, Any]],
    writer: ResultWriter,
) -> list[dict[str, Any]]:
    shards: list[dict[str, Any]] = []
    pair_count = 0
    record_count = 0
    for cohort in sorted(cohorts, key=lambda item: item["cohort_id"]):
        for current_time in CURRENT_TIMES:
            records = {
                source: json.loads((result_root / f"source-cache/{source}/{current_time}.json").read_text(encoding="ascii"))
                for source in cohort["source_ids"]
            }
            lines = []
            for source_a, source_b in combinations(cohort["source_ids"], 2):
                pair = derive_pair_record(result_root, records[source_a], records[source_b])
                lines.append(canonical_json_bytes(pair))
                pair_count += int(current_time == 1)
                record_count += 1
            relative = f"pair-records/{cohort['cohort_id']}/{current_time}_TO_{current_time + 1}.jsonl"
            path = result_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_bytes(b"".join(lines))
            temporary.replace(path)
            ref = _artifact(path, "PAIR_TRANSITION_SHARD", result_root)
            writer.artifacts.append(ref)
            shards.append({**ref, "cohort_id": cohort["cohort_id"], "transition": f"{current_time}_TO_{current_time + 1}", "record_count": len(lines)})
    require(pair_count == 2325 and record_count == 6975, "pair surface count drift")
    return shards


def load_execution_authority(path: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    authority = json.loads(path.read_text(encoding="utf-8"))
    require(authority.get("schema") == AUTHORITY_SCHEMA, "execution authority schema mismatch")
    require(authority.get("status") == "AUTHORIZED" and authority.get("execution_authority") == AUTHORITY_VALUE, "MTS-1 producer is not authorized")
    require(authority.get("scientific_payload_generated") is False, "authority was not issued pre-execution")
    require(authority.get("runtime") == runtime_identity(), "pinned execution runtime mismatch")
    paths = {
        role: _verify_repo_artifact(authority["artifacts"][role], role)
        for role in (
            "PRODUCER_REGISTRATION", "COMPILED_TRANSITION_KERNEL", "OPTIMIZED_BACKEND_REGISTRATION",
            "OPTIMIZED_CACHE_MANIFEST", "PAPER17_EXACT_SIDECAR", "PAPER17_SIDECAR_INVENTORY",
            "COHORT_REGISTRY",
        )
    }
    producer_registration = json.loads(paths["PRODUCER_REGISTRATION"].read_text(encoding="utf-8"))
    require(
        producer_registration.get("schema") == "rime.exploratory.male-cns.mts-source-addressed-producer-registration.v1",
        "producer registration schema mismatch",
    )
    producer_entry = next(
        entry for entry in producer_registration["artifact_closure"]
        if entry["role"] == "SOURCE_ADDRESSED_PRODUCER"
    )
    require(
        producer_entry["sha256"] == sha256_file(Path(__file__).resolve()),
        "executing producer differs from authorized producer registration",
    )
    return authority, paths


def execute(authority_path: Path) -> dict[str, Any]:
    authority, paths = load_execution_authority(authority_path)
    output_relative = _safe_relative_path(authority["result_root"], "authority result_root")
    final_root = _repo_path(output_relative.as_posix())
    require(final_root.is_relative_to((MTS_ROOT / "results").resolve()), "result root must be owned by MTS-1 results")
    require(not final_root.exists(), "result root already exists; scientific replay is single-shot")
    staging = final_root.with_name(final_root.name + ".staging")
    require(not staging.exists(), "staging root already exists; resolve prior attempt before execution")
    writer = ResultWriter(staging)

    backend_registration = json.loads(paths["OPTIMIZED_BACKEND_REGISTRATION"].read_text(encoding="utf-8"))
    cache_manifest = json.loads(paths["OPTIMIZED_CACHE_MANIFEST"].read_text(encoding="utf-8"))
    require(backend_registration["runtime"] == runtime_identity(), "backend runtime mismatch")
    cache_dir = paths["OPTIMIZED_CACHE_MANIFEST"].parent
    for entry in cache_manifest["arrays"].values():
        array_path = cache_dir / entry["path"]
        require(array_path.stat().st_size == entry["bytes"] and sha256_file(array_path) == entry["sha256"], "optimized cache array mismatch")
    backend = RegisteredBackend(cache_dir, paths["COMPILED_TRANSITION_KERNEL"])
    specs, cohorts = load_source_specs(paths["COHORT_REGISTRY"])

    source_records = 0
    with Paper17Sidecar(paths["PAPER17_EXACT_SIDECAR"], paths["PAPER17_SIDECAR_INVENTORY"]) as historical:
        for spec in specs:
            source_records += len(produce_source(spec, backend, historical, writer))
    require(source_records == 459, "source-transition cache count drift")
    verify_source_cache_surface(staging, specs)
    pair_shards = derive_pair_surface(staging, cohorts, writer)
    inventory = {
        "schema": INVENTORY_SCHEMA,
        "status": "SOURCE_ADDRESSED_PRODUCTION_COMPLETE_AWAITING_EXHAUSTIVE_VALIDATION",
        "execution_authority": _artifact(authority_path, "EXECUTION_AUTHORITY", REPO_ROOT),
        "source_count": len(specs),
        "source_transition_cache_record_count": source_records,
        "pair_count": 2325,
        "pair_transition_record_count": sum(item["record_count"] for item in pair_shards),
        "pair_operator_recomputation": False,
        "pair_shards": pair_shards,
        "ordered_artifacts": writer.artifacts,
        "ordered_artifact_closure_sha256": sha256_bytes(canonical_json_bytes(writer.artifacts)),
        "classification_performed": False,
    }
    writer.write_json("inventory.json", inventory, "RESULT_INVENTORY")
    final_root.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging, final_root)
    return {
        "status": inventory["status"],
        "result_root": output_relative.as_posix(),
        "source_transition_cache_record_count": source_records,
        "pair_transition_record_count": inventory["pair_transition_record_count"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(execute(args.authority.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
