#!/usr/bin/env python3
"""Canonical exact sparse-state payloads for MTS-1.

The Paper XVII hash is retained only as a compatibility gate.  New MTS-1
state identities use a domain-tagged binary payload with explicit dimension,
coordinate order, and reduced rational encoding.
"""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Iterator, Mapping

import gmpy2


SCHEMA = "rime.exploratory.male-cns.mts-microstate-payload.v1"
DOMAIN_TAG = b"RIME-MTS-MICROSTATE-V1\x00"
FORMAT_VERSION = 1
REGISTERED_DIMENSION = 211_577
POSITIVE_SIGN = 1
NEGATIVE_SIGN = 2
_HEADER = struct.Struct(">HQQ")
_ENTRY_HEADER = struct.Struct(">QBII")


def _uint_bytes(value: int) -> bytes:
    if value <= 0:
        raise ValueError("unsigned integer magnitude must be positive")
    return value.to_bytes((value.bit_length() + 7) // 8, "big")


def _rational_parts(value: object) -> tuple[int, int]:
    if isinstance(value, bool) or not (
        type(value) is int or isinstance(value, (gmpy2.mpz, gmpy2.mpq))
    ):
        raise TypeError(
            "exact state scalars must be Python int, gmpy2.mpz, or gmpy2.mpq"
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
            f"MTS-1 payload dimension must equal {REGISTERED_DIMENSION}"
        )


def _canonical_entries(values: Mapping[int, object]) -> list[tuple[int, int, int]]:
    entries: list[tuple[int, int, int]] = []
    for coordinate, value in values.items():
        if not isinstance(coordinate, int) or isinstance(coordinate, bool):
            raise TypeError("state coordinates must be integers")
        if coordinate < 0 or coordinate >= REGISTERED_DIMENSION:
            raise ValueError(
                f"state coordinate outside [0,{REGISTERED_DIMENSION}): {coordinate}"
            )
        numerator, denominator = _rational_parts(value)
        if numerator:
            entries.append((coordinate, numerator, denominator))
    entries.sort(key=lambda entry: entry[0])
    return entries


def iter_microstate_payload_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> Iterator[bytes]:
    """Yield canonical payload chunks in their exact semantic byte order."""

    _require_registered_dimension(dimension)
    entries = _canonical_entries(values)
    yield DOMAIN_TAG
    yield _HEADER.pack(FORMAT_VERSION, REGISTERED_DIMENSION, len(entries))
    for coordinate, numerator, denominator in entries:
        sign = POSITIVE_SIGN if numerator > 0 else NEGATIVE_SIGN
        numerator_bytes = _uint_bytes(abs(numerator))
        denominator_bytes = _uint_bytes(denominator)
        yield _ENTRY_HEADER.pack(
            coordinate, sign, len(numerator_bytes), len(denominator_bytes)
        )
        yield numerator_bytes
        yield denominator_bytes


def encode_microstate_payload_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> bytes:
    """Return the canonical, uncompressed MTS-1 microscopic-state payload."""

    return b"".join(iter_microstate_payload_v1(values, dimension=dimension))


def microstate_payload_sha256_v1(
    values: Mapping[int, object], *, dimension: int = REGISTERED_DIMENSION
) -> str:
    """Hash the canonical payload; the digest does not replace payload equality."""

    digest = hashlib.sha256()
    for chunk in iter_microstate_payload_v1(values, dimension=dimension):
        digest.update(chunk)
    return digest.hexdigest()


def decode_microstate_payload_v1(payload: bytes | bytearray | memoryview) -> dict[int, gmpy2.mpq]:
    """Strictly decode and validate one canonical MTS-1 microscopic state."""

    if not isinstance(payload, (bytes, bytearray, memoryview)):
        raise TypeError("payload must be bytes-like")
    data = bytes(payload)
    minimum = len(DOMAIN_TAG) + _HEADER.size
    if len(data) < minimum:
        raise ValueError("truncated MTS-1 microscopic-state payload")
    if not data.startswith(DOMAIN_TAG):
        raise ValueError("MTS-1 microscopic-state domain tag mismatch")
    offset = len(DOMAIN_TAG)
    version, dimension, nonzero_count = _HEADER.unpack_from(data, offset)
    offset += _HEADER.size
    if version != FORMAT_VERSION:
        raise ValueError(f"unsupported MTS-1 microscopic-state version: {version}")
    if dimension != REGISTERED_DIMENSION:
        raise ValueError(f"MTS-1 microscopic-state dimension mismatch: {dimension}")
    if nonzero_count > REGISTERED_DIMENSION:
        raise ValueError("declared nonzero count exceeds registered dimension")

    state: dict[int, gmpy2.mpq] = {}
    previous_coordinate = -1
    for _ in range(nonzero_count):
        if offset + _ENTRY_HEADER.size > len(data):
            raise ValueError("truncated MTS-1 microscopic-state entry header")
        coordinate, sign, numerator_length, denominator_length = _ENTRY_HEADER.unpack_from(
            data, offset
        )
        offset += _ENTRY_HEADER.size
        if coordinate >= REGISTERED_DIMENSION:
            raise ValueError("microscopic-state coordinate outside registered dimension")
        if coordinate <= previous_coordinate:
            raise ValueError("microscopic-state coordinates are not strictly increasing")
        if sign not in (POSITIVE_SIGN, NEGATIVE_SIGN):
            raise ValueError("invalid microscopic-state numerator sign code")
        if numerator_length == 0 or denominator_length == 0:
            raise ValueError("zero-length integer magnitude is forbidden")
        stop = offset + numerator_length + denominator_length
        if stop > len(data):
            raise ValueError("truncated MTS-1 microscopic-state integer magnitude")
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
        state[int(coordinate)] = gmpy2.mpq(numerator, denominator)
        previous_coordinate = int(coordinate)
    if offset != len(data):
        raise ValueError("trailing bytes after MTS-1 microscopic-state payload")
    return state


def paper17_legacy_state_sha256_v1(values: Mapping[int, object]) -> str:
    """Reproduce Paper XVII's sparse ASCII state hash for ancestry checks only."""

    digest = hashlib.sha256()
    for coordinate in sorted(values):
        if not isinstance(coordinate, int) or isinstance(coordinate, bool):
            raise TypeError("state coordinates must be integers")
        numerator, denominator = _rational_parts(values[coordinate])
        if numerator == 0:
            raise ValueError("Paper XVII sparse state payloads must omit zero entries")
        digest.update(
            f"{coordinate}\t{numerator}\t{denominator}\n".encode("ascii")
        )
    return digest.hexdigest()
