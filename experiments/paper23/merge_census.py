#!/usr/bin/env python3
"""Validate and merge census shards into a lightweight feature summary."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from census import digest, file_digest


def load_shard(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = payload.pop("content_sha256")
    assert payload["schema"] == "rime.synchronizing-automata.census-shard.v2"
    assert digest(payload) == expected, f"digest mismatch: {path}"
    payload["content_sha256"] = expected
    return payload


def merge(paths: list[Path]) -> dict:
    shards = [load_shard(path) for path in paths]
    assert shards, "at least one shard is required"
    scope = shards[0]["scope"]
    shard_count = shards[0]["shard"]["count"]
    assert all(shard["scope"] == scope for shard in shards)
    assert all(
        shard["carrier_contract"] == shards[0]["carrier_contract"]
        for shard in shards
    )
    assert all(shard["shard"]["count"] == shard_count for shard in shards)
    shard_indices = [shard["shard"]["index"] for shard in shards]
    assert len(shards) == shard_count, "one file is required for every shard"
    assert set(shard_indices) == set(range(shard_count)), (
        "shard indices must cover [0, shard_count) exactly"
    )
    repository_root = Path(__file__).resolve().parents[2]

    def source_path(path: Path) -> str:
        resolved = path.resolve()
        try:
            return resolved.relative_to(repository_root).as_posix()
        except ValueError:
            return resolved.as_posix()

    for shard in shards:
        producer = shard["producer"]
        for field in ("script", "registry"):
            source = repository_root / producer[field]
            assert source.is_file(), f"missing producer source: {source}"
            assert file_digest(source) == producer[f"{field}_sha256"]
    indices = [index for shard in shards for index in shard["shard"]["canonical_indices"]]
    assert len(indices) == len(set(indices)), "duplicate canonical index across shards"
    expected_indices = set(range(shards[0]["enumeration"]["isomorphism_classes"]))
    assert set(indices) == expected_indices, "shards do not cover the full census"
    rows = sorted((row for shard in shards for row in shard["feature_rows"]), key=lambda row: row["canonical_index"])
    maximum = max(row["reset_length"] for row in rows)
    extremals = [row for row in rows if row["reset_length"] == maximum]
    records_by_id = {record["id"]: record for shard in shards for record in shard["records"]}
    summary = {
        "schema": "rime.synchronizing-automata.census-summary.v2",
        "carrier_contract": shards[0]["carrier_contract"],
        "scope": scope,
        "enumeration": {**shards[0]["enumeration"], "shard_count": shard_count, "synchronizing_classes": len(rows)},
        "shards": [
            {
                "index": shard["shard"]["index"],
                "path": source_path(path),
                "file_sha256": file_digest(path),
                "content_sha256": shard["content_sha256"],
                "record_count": len(shard["records"]),
            }
            for path, shard in sorted(
                zip(paths, shards),
                key=lambda item: item[1]["shard"]["index"],
            )
        ],
        "feature_rows": rows,
        "extremal_reset_depth": {
            "value": maximum,
            "witnesses": [
                {
                    "automaton_id": row["automaton_id"],
                    "canonical_index": row["canonical_index"],
                    "transition": records_by_id[row["automaton_id"]]["transition"],
                    "shortest_reset_word": records_by_id[row["automaton_id"]]["reset"]["shortest_word"],
                    "transition_monoid_size": row["transition_monoid_size"],
                }
                for row in extremals
            ],
        },
        "producer": {
            "script": "experiments/paper23/merge_census.py",
            "script_sha256": file_digest(Path(__file__)),
        },
        "claim_boundary": "Merged finite census summary. It preserves shard digests and feature rows but is not a proof of any unbounded claim.",
    }
    summary["content_sha256"] = digest(summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("shards", nargs="+")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    paths = []
    for pattern in args.shards:
        matches = [Path(match) for match in sorted(glob.glob(pattern))]
        paths.extend(matches or [Path(pattern)])
    summary = merge(paths)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary["enumeration"], indent=2))


if __name__ == "__main__":
    main()
