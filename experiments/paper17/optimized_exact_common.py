#!/usr/bin/env python3
"""Shared exact and provenance helpers for the optimized implementation audit."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import statistics
import sys
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np
import psutil
import pyarrow
import scipy


ROOT = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def hash_operator(
    rows: np.ndarray, cols: np.ndarray, data: np.ndarray, shape: tuple[int, int]
) -> str:
    digest = hashlib.sha256()
    digest.update(np.asarray(shape, dtype=np.int64).tobytes())
    for array in (rows, cols, data):
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(np.asarray(contiguous.shape, dtype=np.int64).tobytes())
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def exact_row_abs_mass(
    rows: np.ndarray, weights: np.ndarray, node_count: int
) -> tuple[np.ndarray, int]:
    if rows.dtype != np.int64 or weights.dtype != np.int64:
        raise TypeError("exact row-mass accumulation requires int64 inputs")
    if np.any(weights < 0):
        raise ValueError("negative carrier weight in absolute-mass input")
    overflow_upper_bound = int(weights.max(initial=0)) * int(len(weights))
    if overflow_upper_bound > np.iinfo(np.int64).max:
        raise OverflowError("int64 row-mass accumulation bound is unsafe")
    row_abs = np.zeros(node_count, dtype=np.int64)
    np.add.at(row_abs, rows, weights)
    return row_abs, overflow_upper_bound


def runtime_identity() -> dict[str, str]:
    return {
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "pyarrow_version": pyarrow.__version__,
        "gmpy2_version": gmpy2.version(),
        "psutil_version": psutil.__version__,
        "cython_version": importlib.metadata.version("Cython"),
        "setuptools_version": importlib.metadata.version("setuptools"),
        "sys_executable_sha256": sha256_file(Path(sys.executable)),
    }


def process_memory() -> dict[str, int | None]:
    info = psutil.Process().memory_info()
    return {
        "rss_bytes": int(info.rss),
        "peak_working_set_bytes_if_available": (
            int(info.peak_wset) if hasattr(info, "peak_wset") else None
        ),
    }


def rational_parts(value: gmpy2.mpq) -> tuple[gmpy2.mpz, gmpy2.mpz]:
    return gmpy2.numer(value), gmpy2.denom(value)


def bit_profile(values: list[gmpy2.mpq]) -> dict[str, int | float]:
    numerator_bits: list[int] = []
    denominator_bits: list[int] = []
    for value in values:
        numerator, denominator = rational_parts(value)
        numerator_bits.append(int(abs(numerator).bit_length()))
        denominator_bits.append(int(denominator.bit_length()))
    if not values:
        return {
            "maximum_numerator_bits": 0,
            "maximum_denominator_bits": 0,
            "median_numerator_bits": 0,
            "median_denominator_bits": 0,
        }
    return {
        "maximum_numerator_bits": max(numerator_bits),
        "maximum_denominator_bits": max(denominator_bits),
        "median_numerator_bits": statistics.median(numerator_bits),
        "median_denominator_bits": statistics.median(denominator_bits),
    }


def rational_payload_hash(values: dict[int, gmpy2.mpq]) -> str:
    digest = hashlib.sha256()
    for key in sorted(values):
        numerator, denominator = rational_parts(values[key])
        digest.update(f"{key}\t{numerator}\t{denominator}\n".encode("ascii"))
    return digest.hexdigest()


def exact_observation(
    state: dict[int, gmpy2.mpq],
    sector_codes: np.ndarray,
    sector_sizes: np.ndarray,
    sector_count: int,
) -> tuple[dict[int, gmpy2.mpq], dict[str, int | float]]:
    zero = gmpy2.mpq(0)
    sums: dict[int, gmpy2.mpq] = {}
    for node, value in state.items():
        sector = int(sector_codes[node])
        sums[sector] = sums.get(sector, zero) + value
    observation = {
        sector: value / int(sector_sizes[sector])
        for sector, value in sums.items()
        if value
    }
    metrics: dict[str, int | float] = {
        "observation_support_count": len(observation),
        "observation_support_density": len(observation) / sector_count,
        "observation_payload_sha256_provenance_only": rational_payload_hash(
            observation
        ),
    }
    for key, value in bit_profile(list(observation.values())).items():
        metrics[f"observation_{key}"] = value
    return observation, metrics


def reference_exact_step(
    indptr: np.ndarray,
    indices: np.ndarray,
    numerators: np.ndarray,
    row_abs: np.ndarray,
    state: dict[int, gmpy2.mpq],
) -> tuple[dict[int, gmpy2.mpq], dict[str, int]]:
    zero = gmpy2.mpq(0)
    one = gmpy2.mpq(1)
    alpha = gmpy2.mpq(1, 5)
    decay = gmpy2.mpq(4, 5)
    drive: dict[int, gmpy2.mpq] = {}
    visited = 0
    for node, value in state.items():
        start = int(indptr[node])
        stop = int(indptr[node + 1])
        visited += stop - start
        denominator = int(row_abs[node])
        for position in range(start, stop):
            target = int(indices[position])
            coefficient = gmpy2.mpq(int(numerators[position]), denominator)
            drive[target] = drive.get(target, zero) + value * coefficient

    next_state = {node: decay * value for node, value in state.items() if value}
    clip_lower = 0
    clip_upper = 0
    clip_interior = 0
    for target, value in drive.items():
        if value <= zero:
            clip_lower += 1
            continue
        if value >= one:
            value = one
            clip_upper += 1
        else:
            clip_interior += 1
        next_state[target] = next_state.get(target, zero) + alpha * value
    next_state = {node: value for node, value in next_state.items() if value}
    return next_state, {
        "visited_edge_contribution_count": visited,
        "drive_support_count": len(drive),
        "clip_lower_count": clip_lower,
        "clip_upper_count": clip_upper,
        "clip_interior_count": clip_interior,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

