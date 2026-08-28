#!/usr/bin/env python3
"""Run the waiting--capacity profile over existing automaton records."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import _bootstrap  # noqa: F401
from fiber_incidence_controls import waiting_capacity_tradeoff_certificate
from registry import file_digest, payload_digest


def _records(paths: list[Path]):
    for path in paths:
        shards = sorted(path.glob("shard_*.json")) if path.is_dir() else [path]
        for shard in shards:
            payload = json.loads(shard.read_text(encoding="utf-8"))
            for record in payload.get("records", []):
                yield shard, record


def build_audit(paths: list[Path]) -> dict:
    rows: list[dict] = []
    source_digests: dict[str, str] = {}
    for source, record in _records(paths):
        source_key = source.as_posix()
        source_digests[source_key] = file_digest(source)
        transition = tuple(tuple(letter) for letter in record["transition"])
        result = waiting_capacity_tradeoff_certificate(transition)
        depth = result["shortest_reset_depth"]
        bound = result["declared_capacity_profile"]["pin_frankl_capacity_bound"]["bound"]
        envelope = result["exact_tradeoff_envelope"]
        phi_statewise = envelope["phi_statewise_initial"]
        statewise_fraction = (
            None if phi_statewise is None
            else Fraction(phi_statewise["numerator"], phi_statewise["denominator"])
        )
        rows.append({
            "id": record.get("id", record.get("family")),
            "family": record.get("family"),
            "source": source_key,
            "state_count": len(transition[0]),
            "synchronizing": depth is not None,
            "reset_depth": depth,
            "H": result["high_capacity_ranks_H"],
            "U": result["unit_capacity_ranks_U"],
            "Omega_epsilon_kappa": result["Omega_epsilon_kappa"],
            "phi_kappa": envelope["phi_kappa_initial"],
            "phi_statewise": phi_statewise,
            "statewise_branch_tail_profile": envelope[
                "statewise_branch_tail_profile"
            ],
            "combined_statewise_bound": envelope[
                "combined_statewise_bound_initial"
            ],
            "global_finite_bound_status": envelope[
                "global_finite_bound_status"
            ],
            "statewise_bound_slack": (
                None if depth is None or statewise_fraction is None else {
                    "numerator": (statewise_fraction - depth).numerator,
                    "denominator": (statewise_fraction - depth).denominator,
                }
            ),
            "capacity_profile_bound": bound,
            "capacity_bound_slack": result["bound_slack"],
            "minimum_rank_candidate_slack": (
                None if depth is None else
                (len(transition[0]) - 1)
                * min(len(set(letter)) for letter in transition)
                - depth
            ),
        })
    families: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        families[row.get("family") or row["source"]].append(row)
    summaries = []
    for family, cohort in sorted(families.items()):
        sync = [row for row in cohort if row["synchronizing"]]
        summaries.append({
            "family": family,
            "row_count": len(cohort),
            "synchronizing_count": len(sync),
            "unit_capacity_rank_union": sorted({rank for row in sync for rank in row["U"]}),
            "high_capacity_rank_union": sorted({rank for row in sync for rank in row["H"]}),
            "max_reset_depth": max((row["reset_depth"] for row in sync), default=None),
            "max_phi_kappa": max(
                (Fraction(row["phi_kappa"]["numerator"], row["phi_kappa"]["denominator"])
                 for row in sync),
                default=None,
            ),
            "max_phi_statewise": max(
                (
                    Fraction(
                        row["phi_statewise"]["numerator"],
                        row["phi_statewise"]["denominator"],
                    )
                    for row in sync
                    if row["phi_statewise"] is not None
                ),
                default=None,
            ),
            "minimum_statewise_bound_slack": min(
                (
                    Fraction(
                        row["statewise_bound_slack"]["numerator"],
                        row["statewise_bound_slack"]["denominator"],
                    )
                    for row in sync
                    if row["statewise_bound_slack"] is not None
                ),
                default=None,
            ),
            "minimum_capacity_bound_slack": min(
                (
                    Fraction(row["capacity_bound_slack"]["numerator"], row["capacity_bound_slack"]["denominator"])
                    for row in sync
                    if row["capacity_bound_slack"] is not None
                ),
                default=None,
            ),
        })
    # Convert exact summary fractions to JSON objects without losing exactness.
    for summary in summaries:
        for key in (
            "max_phi_kappa",
            "max_phi_statewise",
            "minimum_capacity_bound_slack",
            "minimum_statewise_bound_slack",
        ):
            value = summary[key]
            summary[key] = None if value is None else {
                "numerator": value.numerator,
                "denominator": value.denominator,
            }
    payload = {
        "schema": "rime.synchronizing-automata.waiting-capacity-tradeoff-audit.v1",
        "carrier": "waiting_capacity_tradeoff",
        "source_artifacts": [
            {"path": path, "raw_blob_sha256": digest}
            for path, digest in sorted(source_digests.items())
        ],
        "rows": rows,
        "summaries": summaries,
        "claim_boundary": {
            "tradeoff": "Exact finite theorem",
            "capacity_profile_bound": "Theorem under declared lower profile",
            "family_pattern": "Computational Observation",
            "cerny_or_linear_rank_bound": "Open",
        },
    }
    payload["content_sha256"] = payload_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    payload = build_audit(args.paths)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"rows": len(payload["rows"]), "summaries": len(payload["summaries"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
