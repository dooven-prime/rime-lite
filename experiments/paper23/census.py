#!/usr/bin/env python3
"""Build one resumable shard of the small synchronizing-automata census."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from registry import (
    CARRIER_CONTRACT,
    audit_automaton,
    enumerate_isomorphism_classes,
    feature_row,
)


def digest(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_shard(n: int, alphabet: int, max_word_depth: int, shard_index: int, shard_count: int) -> dict:
    if n < 1 or alphabet < 1 or max_word_depth < 1 or shard_count < 1:
        raise ValueError(
            "states, alphabet, max-word-depth, and shard-count must be positive"
        )
    if not 0 <= shard_index < shard_count:
        raise ValueError("shard-index must lie in [0, shard-count)")
    classes = enumerate_isomorphism_classes(n, alphabet)
    records = []
    for index in range(shard_index, len(classes), shard_count):
        records.append({"id": f"dfa-n{n}-k{alphabet}-{index:05d}", "canonical_index": index, **audit_automaton(classes[index], max_word_depth)})
    synchronizing = [record for record in records if record["reset"]["is_synchronizing"]]
    feature_rows = [
        {**feature_row(record, n), "canonical_index": record["canonical_index"]}
        for record in synchronizing
    ]
    payload = {
        "schema": "rime.synchronizing-automata.census-shard.v2",
        "carrier_contract": CARRIER_CONTRACT,
        "scope": {"state_count": n, "alphabet_size": alphabet, "max_word_depth": max_word_depth, "isomorphism": "state relabelling; letter labels fixed"},
        "enumeration": {"labelled_tables": n ** (n * alphabet), "isomorphism_classes": len(classes)},
        "shard": {"index": shard_index, "count": shard_count, "canonical_indices": [record["canonical_index"] for record in records]},
        "records": records,
        "feature_rows": feature_rows,
        "producer": {
            "script": "experiments/paper23/census.py",
            "script_sha256": file_digest(Path(__file__)),
            "registry": "experiments/paper23/registry.py",
            "registry_sha256": file_digest(Path(__file__).with_name("registry.py")),
        },
        "claim_boundary": "One exact finite census shard. Its records are computational certificates for listed automata, not a general Cerny theorem.",
    }
    payload["content_sha256"] = digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=int, required=True)
    parser.add_argument("--alphabet", type=int, default=2)
    parser.add_argument("--max-word-depth", type=int, default=6)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build_shard(args.states, args.alphabet, args.max_word_depth, args.shard_index, args.shard_count)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"shard": args.shard_index, "records": len(payload["records"]), "synchronizing": len(payload["feature_rows"]), "sha256": payload["content_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
