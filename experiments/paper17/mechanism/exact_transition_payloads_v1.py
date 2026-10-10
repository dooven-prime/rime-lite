#!/usr/bin/env python3
"""Canonical exact raw-drive, clipped-drive, and clipping-fate payloads."""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Iterator, Mapping

import gmpy2


FORMAT_VERSION = 1
REGISTERED_DIMENSION = 211_577
RAW_DRIVE_SCHEMA = "rime.exploratory.male-cns.mts-raw-drive-payload.v1"
CLIPPED_DRIVE_SCHEMA = "rime.exploratory.male-cns.mts-clipped-drive-payload.v1"
CLIPPING_FATE_SCHEMA = "rime.exploratory.male-cns.mts-clipping-fate-payload.v1"
RAW_DRIVE_DOMAIN_TAG = b"RIME-MTS-RAW-DRIVE-V1\x00"
CLIPPED_DRIVE_DOMAIN_TAG = b"RIME-MTS-CLIPPED-DRIVE-V1\x00"
CLIPPING_FATE_DOMAIN_TAG = b"RIME-MTS-CLIPPING-FATE-V1\x00"
POSITIVE_SIGN = 1
NEGATIVE_SIGN = 2
LOWER = "LOWER"
INTERIOR = "INTERIOR"
UPPER = "UPPER"
FATES = (LOWER, INTERIOR, UPPER)
FATE_CODES = {LOWER: 1, INTERIOR: 2, UPPER: 3}
FATE_LABELS = {code: label for label, code in FATE_CODES.items()}
_HEADER = struct.Struct(">HQQ")
_RATIONAL_ENTRY_HEADER = struct.Struct(">QBII")
_FATE_ENTRY = struct.Struct(">QB")


def _uint_bytes(value: int) -> bytes:
    if value <= 0:
        raise ValueError("unsigned integer magnitude must be positive")
    return value.to_bytes((value.bit_length() + 7) // 8, "big")


def _rational_parts(value: object) -> tuple[int, int]:
    if isinstance(value, bool) or not (
        type(value) is int or isinstance(value, (gmpy2.mpz, gmpy2.mpq))
    ):
        raise TypeError(
            "exact transition scalars must be Python int, gmpy2.mpz, or gmpy2.mpq"
        )
    rational = gmpy2.mpq(value)
    numerator = int(gmpy2.numer(rational))
    denominator = int(gmpy2.denom(rational))
    if denominator <= 0:
        raise ValueError("canonical rational denominator must be positive")
    if gmpy2.gcd(abs(numerator), denominator) != 1:
        raise ValueError("canonical rational must be reduced")
    return numerator, denominator


def _require_registered_dimension(dimension: int) -> None:
    if type(dimension) is not int or dimension != REGISTERED_DIMENSION:
        raise ValueError(
            f"MTS-1 transition payload dimension must equal {REGISTERED_DIMENSION}"
        )


def _coordinate(value: object) -> int:
    if type(value) is not int:
        raise TypeError("transition payload coordinates must be Python integers")
    if value < 0 or value >= REGISTERED_DIMENSION:
        raise ValueError(
            f"transition payload coordinate outside [0,{REGISTERED_DIMENSION}): {value}"
        )
    return value


def _canonical_rational_entries(
    values: Mapping[int, object], *, clipped: bool
) -> list[tuple[int, int, int]]:
    if not isinstance(values, Mapping):
        raise TypeError("transition payload values must be a mapping")
    entries: list[tuple[int, int, int]] = []
    for coordinate_value, value in values.items():
        coordinate = _coordinate(coordinate_value)
        numerator, denominator = _rational_parts(value)
        if clipped and (numerator < 0 or numerator > denominator):
            raise ValueError("clipped-drive values must lie in the exact interval [0,1]")
        if numerator:
            entries.append((coordinate, numerator, denominator))
    entries.sort(key=lambda entry: entry[0])
    return entries


def _iter_rational_payload(
    values: Mapping[int, object],
    *,
    dimension: int,
    domain_tag: bytes,
    clipped: bool,
) -> Iterator[bytes]:
    _require_registered_dimension(dimension)
    entries = _canonical_rational_entries(values, clipped=clipped)
    yield domain_tag
    yield _HEADER.pack(FORMAT_VERSION, REGISTERED_DIMENSION, len(entries))
    for coordinate, numerator, denominator in entries:
        sign = POSITIVE_SIGN if numerator > 0 else NEGATIVE_SIGN
        numerator_bytes = _uint_bytes(abs(numerator))
        denominator_bytes = _uint_bytes(denominator)
        yield _RATIONAL_ENTRY_HEADER.pack(
            coordinate, sign, len(numerator_bytes), len(denominator_bytes)
        )
        yield numerator_bytes
        yield denominator_bytes


def iter_raw_drive_payload_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> Iterator[bytes]:
    """Yield canonical raw-drive payload chunks."""

    yield from _iter_rational_payload(
        values,
        dimension=dimension,
        domain_tag=RAW_DRIVE_DOMAIN_TAG,
        clipped=False,
    )


def encode_raw_drive_payload_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> bytes:
    return b"".join(iter_raw_drive_payload_v1(values, dimension=dimension))


def raw_drive_payload_sha256_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> str:
    digest = hashlib.sha256()
    for chunk in iter_raw_drive_payload_v1(values, dimension=dimension):
        digest.update(chunk)
    return digest.hexdigest()


def iter_clipped_drive_payload_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> Iterator[bytes]:
    """Yield canonical clipped-drive payload chunks."""

    yield from _iter_rational_payload(
        values,
        dimension=dimension,
        domain_tag=CLIPPED_DRIVE_DOMAIN_TAG,
        clipped=True,
    )


def encode_clipped_drive_payload_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> bytes:
    return b"".join(iter_clipped_drive_payload_v1(values, dimension=dimension))


def clipped_drive_payload_sha256_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> str:
    digest = hashlib.sha256()
    for chunk in iter_clipped_drive_payload_v1(values, dimension=dimension):
        digest.update(chunk)
    return digest.hexdigest()


def _decode_rational_payload(
    payload: bytes | bytearray | memoryview,
    *,
    domain_tag: bytes,
    label: str,
    clipped: bool,
) -> dict[int, gmpy2.mpq]:
    if not isinstance(payload, (bytes, bytearray, memoryview)):
        raise TypeError("payload must be bytes-like")
    data = bytes(payload)
    minimum = len(domain_tag) + _HEADER.size
    if len(data) < minimum:
        raise ValueError(f"truncated MTS-1 {label} payload")
    if not data.startswith(domain_tag):
        raise ValueError(f"MTS-1 {label} domain tag mismatch")
    offset = len(domain_tag)
    version, dimension, entry_count = _HEADER.unpack_from(data, offset)
    offset += _HEADER.size
    if version != FORMAT_VERSION:
        raise ValueError(f"unsupported MTS-1 {label} version: {version}")
    if dimension != REGISTERED_DIMENSION:
        raise ValueError(f"MTS-1 {label} dimension mismatch: {dimension}")
    if entry_count > REGISTERED_DIMENSION:
        raise ValueError(f"declared {label} entry count exceeds registered dimension")

    values: dict[int, gmpy2.mpq] = {}
    previous_coordinate = -1
    for _ in range(entry_count):
        if offset + _RATIONAL_ENTRY_HEADER.size > len(data):
            raise ValueError(f"truncated MTS-1 {label} entry header")
        coordinate, sign, numerator_length, denominator_length = (
            _RATIONAL_ENTRY_HEADER.unpack_from(data, offset)
        )
        offset += _RATIONAL_ENTRY_HEADER.size
        if coordinate >= REGISTERED_DIMENSION:
            raise ValueError(f"{label} coordinate outside registered dimension")
        if coordinate <= previous_coordinate:
            raise ValueError(f"{label} coordinates are not strictly increasing")
        if sign not in (POSITIVE_SIGN, NEGATIVE_SIGN):
            raise ValueError(f"invalid {label} numerator sign code")
        if numerator_length == 0 or denominator_length == 0:
            raise ValueError("zero-length integer magnitude is forbidden")
        stop = offset + numerator_length + denominator_length
        if stop > len(data):
            raise ValueError(f"truncated MTS-1 {label} integer magnitude")
        numerator_bytes = data[offset : offset + numerator_length]
        offset += numerator_length
        denominator_bytes = data[offset : offset + denominator_length]
        offset += denominator_length
        if numerator_bytes[0] == 0 or denominator_bytes[0] == 0:
            raise ValueError("integer magnitudes must use minimal big-endian encoding")
        numerator_magnitude = int.from_bytes(numerator_bytes, "big")
        denominator = int.from_bytes(denominator_bytes, "big")
        if numerator_magnitude == 0:
            raise ValueError("zero numerator must be omitted from sparse payload")
        if denominator == 0:
            raise ValueError("rational denominator must be positive")
        if gmpy2.gcd(numerator_magnitude, denominator) != 1:
            raise ValueError("rational payload entry is not reduced")
        numerator = numerator_magnitude if sign == POSITIVE_SIGN else -numerator_magnitude
        if clipped and (numerator < 0 or numerator > denominator):
            raise ValueError("clipped-drive payload value lies outside [0,1]")
        values[int(coordinate)] = gmpy2.mpq(numerator, denominator)
        previous_coordinate = int(coordinate)
    if offset != len(data):
        raise ValueError(f"trailing bytes after MTS-1 {label} payload")
    return values


def decode_raw_drive_payload_v1(
    payload: bytes | bytearray | memoryview,
) -> dict[int, gmpy2.mpq]:
    return _decode_rational_payload(
        payload,
        domain_tag=RAW_DRIVE_DOMAIN_TAG,
        label="raw-drive",
        clipped=False,
    )


def decode_clipped_drive_payload_v1(
    payload: bytes | bytearray | memoryview,
) -> dict[int, gmpy2.mpq]:
    return _decode_rational_payload(
        payload,
        domain_tag=CLIPPED_DRIVE_DOMAIN_TAG,
        label="clipped-drive",
        clipped=True,
    )


def _canonical_fate_entries(fates: Mapping[int, str]) -> list[tuple[int, int]]:
    if not isinstance(fates, Mapping):
        raise TypeError("clipping fates must be a mapping")
    entries: list[tuple[int, int]] = []
    for coordinate_value, fate in fates.items():
        coordinate = _coordinate(coordinate_value)
        if type(fate) is not str or fate not in FATE_CODES:
            raise ValueError(f"unregistered clipping fate: {fate!r}")
        entries.append((coordinate, FATE_CODES[fate]))
    entries.sort(key=lambda entry: entry[0])
    return entries


def iter_clipping_fate_payload_v1(
    fates: Mapping[int, str], *, dimension: int = REGISTERED_DIMENSION
) -> Iterator[bytes]:
    """Yield touched-target clipping fates in canonical coordinate order."""

    _require_registered_dimension(dimension)
    entries = _canonical_fate_entries(fates)
    yield CLIPPING_FATE_DOMAIN_TAG
    yield _HEADER.pack(FORMAT_VERSION, REGISTERED_DIMENSION, len(entries))
    for coordinate, fate_code in entries:
        yield _FATE_ENTRY.pack(coordinate, fate_code)


def encode_clipping_fate_payload_v1(
    fates: Mapping[int, str], *, dimension: int = REGISTERED_DIMENSION
) -> bytes:
    return b"".join(iter_clipping_fate_payload_v1(fates, dimension=dimension))


def clipping_fate_payload_sha256_v1(
    fates: Mapping[int, str], *, dimension: int = REGISTERED_DIMENSION
) -> str:
    digest = hashlib.sha256()
    for chunk in iter_clipping_fate_payload_v1(fates, dimension=dimension):
        digest.update(chunk)
    return digest.hexdigest()


def decode_clipping_fate_payload_v1(
    payload: bytes | bytearray | memoryview,
) -> dict[int, str]:
    if not isinstance(payload, (bytes, bytearray, memoryview)):
        raise TypeError("payload must be bytes-like")
    data = bytes(payload)
    minimum = len(CLIPPING_FATE_DOMAIN_TAG) + _HEADER.size
    if len(data) < minimum:
        raise ValueError("truncated MTS-1 clipping-fate payload")
    if not data.startswith(CLIPPING_FATE_DOMAIN_TAG):
        raise ValueError("MTS-1 clipping-fate domain tag mismatch")
    offset = len(CLIPPING_FATE_DOMAIN_TAG)
    version, dimension, entry_count = _HEADER.unpack_from(data, offset)
    offset += _HEADER.size
    if version != FORMAT_VERSION:
        raise ValueError(f"unsupported MTS-1 clipping-fate version: {version}")
    if dimension != REGISTERED_DIMENSION:
        raise ValueError(f"MTS-1 clipping-fate dimension mismatch: {dimension}")
    if entry_count > REGISTERED_DIMENSION:
        raise ValueError("declared clipping-fate count exceeds registered dimension")
    expected_size = offset + entry_count * _FATE_ENTRY.size
    if expected_size != len(data):
        if expected_size > len(data):
            raise ValueError("truncated MTS-1 clipping-fate entry")
        raise ValueError("trailing bytes after MTS-1 clipping-fate payload")

    fates: dict[int, str] = {}
    previous_coordinate = -1
    for _ in range(entry_count):
        coordinate, fate_code = _FATE_ENTRY.unpack_from(data, offset)
        offset += _FATE_ENTRY.size
        if coordinate >= REGISTERED_DIMENSION:
            raise ValueError("clipping-fate coordinate outside registered dimension")
        if coordinate <= previous_coordinate:
            raise ValueError("clipping-fate coordinates are not strictly increasing")
        if fate_code not in FATE_LABELS:
            raise ValueError("invalid clipping-fate code")
        fates[int(coordinate)] = FATE_LABELS[fate_code]
        previous_coordinate = int(coordinate)
    return fates
