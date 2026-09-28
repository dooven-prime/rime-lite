#!/usr/bin/env python3
"""Hostile round-trip tests for canonical exact-observation records."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

import gmpy2


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from finite_history_binary import iter_shard, read_payload_slice, write_shard


def main() -> int:
    records = [
        (7, 0, 4, {0: gmpy2.mpq(1, 3), 3: gmpy2.mpq(-5, 7)}),
        (7, 1, 4, {2: gmpy2.mpq(11, 13)}),
    ]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "toy.bin"
        metadata = write_shard(path, records)
        decoded = list(iter_shard(path))
        assert metadata["record_count"] == len(decoded) == 2
        assert decoded[0].source_id == 7 and decoded[0].time == 0
        assert decoded[0].observation == records[0][3]
        assert decoded[1].observation == records[1][3]
        assert read_payload_slice(
            path, decoded[0].observation_offset, decoded[0].observation_length
        ) == decoded[0].observation_payload

        bad = Path(directory) / "bad.bin"
        bad.write_bytes(path.read_bytes()[:-1])
        try:
            list(iter_shard(bad))
        except ValueError:
            pass
        else:
            raise AssertionError("corrupt rational payload was accepted")

    print("FINITE_HISTORY_BINARY_TEST_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
