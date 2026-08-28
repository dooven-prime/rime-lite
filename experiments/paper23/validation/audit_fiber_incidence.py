#!/usr/bin/env python3
"""Audit the fiber-incidence amortized potential on existing records."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import _bootstrap  # noqa: F401
from fiber_incidence_potential import fiber_incidence_potential
from registry import file_digest, payload_digest


def _records(paths: list[Path]):
    for path in paths:
        shards = sorted(path.glob("shard_*.json")) if path.is_dir() else [path]
        for shard in shards:
            payload = json.loads(shard.read_text(encoding="utf-8"))
            for record in payload.get("records", []):
                yield shard, record


def _fraction_value(value: dict[str, int] | None) -> Fraction | None:
    if value is None:
        return None
    return Fraction(value["numerator"], value["denominator"])


def build_audit(paths: list[Path]) -> dict:
    rows: list[dict] = []
    source_digests: dict[str, str] = {}
    for source, record in _records(paths):
        source_key = source.as_posix()
        source_digests[source_key] = file_digest(source)
        transition = tuple(tuple(letter) for letter in record["transition"])
        result = fiber_incidence_potential(transition)
        phi = _fraction_value(result["initial_potential"])
        psi = result["shortest_reset_depth"]
        rows.append({
            "id": record.get("id", record.get("family")),
            "source": source_key,
            "state_count": len(transition[0]),
            "alphabet_size": len(transition),
            "synchronizing": psi is not None,
            "psi": psi,
            "phi_fiber_incidence": result["initial_potential"],
            "fiber_incidence_slack": (
                None if psi is None or phi is None
                else {"numerator": (phi - psi).numerator, "denominator": (phi - psi).denominator}
            ),
            "quadratic_slack": (
                None if psi is None
                else (len(transition[0]) - 1) ** 2 - psi
            ),
            "local_descent_verified": result["local_descent_certificate"]["all_checks_passed"],
            "theta_by_rank": result["theta_by_rank"],
        })

    cohorts: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        cohorts[row["state_count"]].append(row)
    summaries = []
    for state_count, cohort in sorted(cohorts.items()):
        sync = [row for row in cohort if row["synchronizing"]]
        slack_values = [
            _fraction_value(row["fiber_incidence_slack"])
            for row in sync
            if row["fiber_incidence_slack"] is not None
        ]
        max_phi = max(
            (_fraction_value(row["phi_fiber_incidence"]) for row in sync),
            default=None,
        )
        summaries.append({
            "state_count": state_count,
            "row_count": len(cohort),
            "synchronizing_count": len(sync),
            "max_psi": max((row["psi"] for row in sync), default=None),
            "max_phi_fiber_incidence": (
                None if max_phi is None else {
                    "numerator": max_phi.numerator,
                    "denominator": max_phi.denominator,
                }
            ),
            "minimum_fiber_incidence_slack": (
                None if not slack_values else {
                    "numerator": min(slack_values).numerator,
                    "denominator": min(slack_values).denominator,
                }
            ),
            "phi_at_or_below_quadratic_count": sum(
                _fraction_value(row["phi_fiber_incidence"]) <= (state_count - 1) ** 2
                for row in sync
            ),
            "local_descent_failures": [
                row["id"] for row in cohort if not row["local_descent_verified"]
            ],
        })
    payload = {
        "schema": "rime.synchronizing-automata.fiber-incidence-potential-audit.v1",
        "carrier": "fiber_incidence_amortized_potential",
        "source_artifacts": [
            {"path": path, "raw_blob_sha256": digest}
            for path, digest in sorted(source_digests.items())
        ],
        "rows": rows,
        "summaries": summaries,
        "claim_boundary": {
            "potential": "Exact finite theorem with fiber-excess incidence",
            "quadratic_control": "Computational Observation only",
            "candidate_status": "Not a proof of the (n-1)m conjecture",
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
    print(json.dumps({
        "rows": len(payload["rows"]),
        "summaries": len(payload["summaries"]),
        "local_descent_failures": sum(
            len(summary["local_descent_failures"])
            for summary in payload["summaries"]
        ),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
