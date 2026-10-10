#!/usr/bin/env python3
"""Canonical binary records for exact finite-history observations."""

from __future__ import annotations

import hashlib
import io
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Iterator

import gmpy2


MAGIC = b"RIMEDC01"
VERSION = 1
FILE_HEADER = struct.Struct(">8sHI")
RECORD_LENGTH = struct.Struct(">I")
ENTRY_PREFIX = struct.Struct(">IbI")
DENOMINATOR_LENGTH = struct.Struct(">I")
MAX_RECORD_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class CanonicalRecord:
    source_id: int
    time: int
    dimension: int
    observation: dict[int, gmpy2.mpq]
    observation_payload: bytes
    observation_offset: int
    observation_length: int


def _unsigned_bytes(value: int) -> bytes:
    if value < 0:
        raise ValueError("unsigned magnitude is negative")
    width = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(width, "big")


def encode_observation_payload(
    dimension: int, observation: dict[int, gmpy2.mpq]
) -> bytes:
    if dimension <= 0:
        raise ValueError("observation dimension must be positive")
    output = io.BytesIO()
    nonzero = [(int(key), value) for key, value in observation.items() if value]
    nonzero.sort(key=lambda item: item[0])
    if len({key for key, _ in nonzero}) != len(nonzero):
        raise ValueError("duplicate observation coordinate")
    output.write(struct.pack(">II", dimension, len(nonzero)))
    for coordinate, value in nonzero:
        if not 0 <= coordinate < dimension:
            raise ValueError("observation coordinate is outside dimension")
        if not isinstance(value, gmpy2.mpq):
            raise TypeError("observation values must be gmpy2.mpq")
        numerator = int(gmpy2.numer(value))
        denominator = int(gmpy2.denom(value))
        if denominator <= 0 or math.gcd(abs(numerator), denominator) != 1:
            raise ValueError("observation rational is not reduced with positive denominator")
        if numerator == 0:
            raise ValueError("zero observation coordinate was not omitted")
        sign = 1 if numerator > 0 else -1
        numerator_bytes = _unsigned_bytes(abs(numerator))
        denominator_bytes = _unsigned_bytes(denominator)
        output.write(ENTRY_PREFIX.pack(coordinate, sign, len(numerator_bytes)))
        output.write(numerator_bytes)
        output.write(DENOMINATOR_LENGTH.pack(len(denominator_bytes)))
        output.write(denominator_bytes)
    return output.getvalue()


def encode_record(
    source_id: int,
    time: int,
    dimension: int,
    observation: dict[int, gmpy2.mpq],
) -> bytes:
    if source_id < 0 or time < 0:
        raise ValueError("source and time must be nonnegative")
    observation_payload = encode_observation_payload(dimension, observation)
    payload = struct.pack(">QI", source_id, time) + observation_payload
    if len(payload) > MAX_RECORD_BYTES:
        raise OverflowError("canonical observation record exceeds registered byte cap")
    return payload


def write_shard(
    path: Path,
    records: Iterable[tuple[int, int, int, dict[int, gmpy2.mpq]]],
) -> dict[str, int | str]:
    encoded = [encode_record(*record) for record in records]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    digest = hashlib.sha256()
    with temporary.open("wb") as handle:
        header = FILE_HEADER.pack(MAGIC, VERSION, len(encoded))
        handle.write(header)
        digest.update(header)
        for payload in encoded:
            prefix = RECORD_LENGTH.pack(len(payload))
            handle.write(prefix)
            handle.write(payload)
            digest.update(prefix)
            digest.update(payload)
        handle.flush()
    temporary.replace(path)
    return {
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
        "record_count": len(encoded),
    }


def _read_exact(handle: BinaryIO, length: int) -> bytes:
    payload = handle.read(length)
    if len(payload) != length:
        raise ValueError("truncated canonical binary record")
    return payload


def decode_observation_payload(payload: bytes) -> tuple[int, dict[int, gmpy2.mpq]]:
    handle = io.BytesIO(payload)
    dimension, count = struct.unpack(">II", _read_exact(handle, 8))
    if dimension <= 0 or count > dimension:
        raise ValueError("invalid observation header")
    observation: dict[int, gmpy2.mpq] = {}
    previous = -1
    for _ in range(count):
        coordinate, sign, numerator_length = ENTRY_PREFIX.unpack(
            _read_exact(handle, ENTRY_PREFIX.size)
        )
        if coordinate <= previous or coordinate >= dimension:
            raise ValueError("observation coordinates are not strictly ordered")
        if sign not in (-1, 1) or numerator_length <= 0:
            raise ValueError("invalid signed numerator encoding")
        numerator = int.from_bytes(_read_exact(handle, numerator_length), "big")
        denominator_length = DENOMINATOR_LENGTH.unpack(
            _read_exact(handle, DENOMINATOR_LENGTH.size)
        )[0]
        if numerator == 0 or denominator_length <= 0:
            raise ValueError("noncanonical rational magnitude")
        denominator = int.from_bytes(
            _read_exact(handle, denominator_length), "big"
        )
        if denominator <= 0 or math.gcd(numerator, denominator) != 1:
            raise ValueError("nonreduced rational encoding")
        observation[coordinate] = gmpy2.mpq(sign * numerator, denominator)
        previous = coordinate
    if handle.read(1):
        raise ValueError("trailing bytes in observation payload")
    return dimension, observation


def iter_shard(path: Path) -> Iterator[CanonicalRecord]:
    with path.open("rb") as handle:
        magic, version, record_count = FILE_HEADER.unpack(
            _read_exact(handle, FILE_HEADER.size)
        )
        if magic != MAGIC or version != VERSION:
            raise ValueError("canonical binary header mismatch")
        for _ in range(record_count):
            payload_length = RECORD_LENGTH.unpack(
                _read_exact(handle, RECORD_LENGTH.size)
            )[0]
            if payload_length > MAX_RECORD_BYTES or payload_length < 20:
                raise ValueError("canonical record length is invalid")
            payload_offset = handle.tell()
            payload = _read_exact(handle, payload_length)
            source_id, time = struct.unpack(">QI", payload[:12])
            observation_payload = payload[12:]
            dimension, observation = decode_observation_payload(observation_payload)
            yield CanonicalRecord(
                source_id=source_id,
                time=time,
                dimension=dimension,
                observation=observation,
                observation_payload=observation_payload,
                observation_offset=payload_offset + 12,
                observation_length=len(observation_payload),
            )
        if handle.read(1):
            raise ValueError("trailing bytes after canonical shard records")


def read_payload_slice(path: Path, offset: int, length: int) -> bytes:
    with path.open("rb") as handle:
        handle.seek(offset)
        return _read_exact(handle, length)
