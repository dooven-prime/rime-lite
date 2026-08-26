#!/usr/bin/env python3
"""Analyze fixed-deficit survivor-layer stability across sampled primes.

The input is the published Paper XXI arbitrary-depth replay.  This module
only tests finite observations; it does not infer a uniform automaton theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "experiments" / "paper21" / "results" / "arbitrary_depth_semantic_v1.json"
DEFAULT_JSON = ROOT / "experiments" / "paper22" / "results" / "stable_deficit_v1.json"
DEFAULT_MD = ROOT / "experiments" / "paper22" / "results" / "stable_deficit_v1.md"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: dict[str, Any]) -> str:
    unsigned = dict(value)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "paper.route-profiles.arbitrary-depth-semantic.v1":
        raise ValueError("unexpected source schema")
    if payload.get("content_sha256") != digest(payload):
        raise ValueError("source content digest mismatch")
    return payload


def deficit_layers(payload: dict[str, Any], extras: list[dict[str, Any]] | None = None) -> dict[int, dict[int, int]]:
    result: dict[int, dict[int, int]] = {}
    for record in payload["fixed_field_automata"]:
        prime = int(record["prime"])
        layers: dict[int, int] = {}
        for key, count in record["state_histogram"].items():
            if not key.startswith("sector_1_card_"):
                continue
            card = int(key.rsplit("_", 1)[1])
            layers[prime - card] = int(count)
        result[prime] = layers
    for record in extras or []:
        prime = int(record["prime"])
        result[prime] = {int(k): int(v) for k, v in record["deficit_layer_counts"].items()}
    return result


def longest_stable_tail(values: list[tuple[int, int]]) -> dict[str, Any]:
    """Return the longest equal-valued suffix in prime order."""
    if not values:
        return {"value": None, "primes": [], "length": 0}
    value = values[-1][1]
    index = len(values) - 1
    while index > 0 and values[index - 1][1] == value:
        index -= 1
    primes = [prime for prime, _ in values[index:]]
    return {"value": value, "primes": primes, "length": len(primes)}


def forward_stability(values: list[tuple[int, int]]) -> dict[str, Any]:
    """Find the earliest suffix with no observed variation through the end."""
    if not values:
        return {"status": "NO_DATA", "threshold_prime": None, "value": None}
    tail = longest_stable_tail(values)
    if tail["length"] >= 2:
        return {
            "status": "OBSERVED_STABLE_TAIL",
            "threshold_prime": tail["primes"][0],
            "value": tail["value"],
            "sample_count": tail["length"],
        }
    return {
        "status": "NO_STABLE_TAIL",
        "threshold_prime": None,
        "value": tail["value"],
        "sample_count": 1,
    }


def recurrence_fit(sequence: list[int], max_order: int = 4) -> list[dict[str, Any]]:
    """Search exact small integer linear recurrences on observed prefixes.

    A fit is only reported when every available equation is exact.  It is a
    diagnostic for future work, not evidence of a recurrence theorem.
    """
    fits = []
    for order in range(1, max_order + 1):
        if len(sequence) <= order:
            continue
        # Brute-force small coefficients keeps this diagnostic transparent.
        import itertools

        for coeffs in itertools.product(range(-8, 9), repeat=order):
            if all(
                sequence[index]
                == sum(coeffs[offset] * sequence[index - 1 - offset] for offset in range(order))
                for index in range(order, len(sequence))
            ):
                fits.append({"order": order, "coefficients": list(coeffs), "checked_terms": len(sequence) - order})
                break
    return fits


def build(payload: dict[str, Any], extras: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    layers = deficit_layers(payload, extras)
    primes = sorted(layers)
    max_deficit = max(max(row) for row in layers.values())
    rows = []
    for k in range(max_deficit + 1):
        values = [(prime, layers[prime][k]) for prime in primes if k in layers[prime]]
        tail = longest_stable_tail(values)
        rows.append(
            {
                "deficit": k,
                "observations": [{"prime": prime, "count": count} for prime, count in values],
                "observed_stability": forward_stability(values),
                "longest_stable_tail": tail,
            }
        )
    # Candidate sequence uses the longest currently observed stable prefix.
    stable_prefix = []
    for row in rows:
        stability = row["observed_stability"]
        if stability["status"] != "OBSERVED_STABLE_TAIL":
            break
        stable_prefix.append(stability["value"])
    return {
        "schema": "paper.route-profiles.stable-deficit-analysis.v1",
        "artifact_role": "COMPUTATIONAL_OBSERVATION_FIXED_DEFICIT_STABILITY",
        "claim_status": "computational_observation",
        "source_artifact": {
            "uri": "experiments/paper21/results/arbitrary_depth_semantic_v1.json",
            "content_sha256": payload["content_sha256"],
        },
        "additional_low_deficit_sources": [
            {"prime": int(record["prime"]), "max_deficit": int(record["max_deficit"])}
            for record in extras or []
        ],
        "sample_primes": primes,
        "deficit_layers": rows,
        "observed_stable_prefix": stable_prefix,
        "recurrence_diagnostics": recurrence_fit(stable_prefix),
        "boundary": [
            "a stable tail over sampled primes is not eventual stability",
            "the threshold may depend on deficit and the marking",
            "recurrence diagnostics are finite-sequence fits, not proofs",
            "no uniform automaton quotient is asserted",
        ],
    }


def render(payload: dict[str, Any]) -> str:
    lines = [
        "# Stable Deficit Analysis",
        "",
        "Status: computational observation from the Paper XXI v1.0 replay.",
        "",
        "## Fixed-deficit layers",
        "",
        "| k | observations by prime | stable tail | observed threshold |",
        "|---:|---|---:|---:|",
    ]
    for row in payload["deficit_layers"]:
        values = ", ".join(f"p={item['prime']}:{item['count']}" for item in row["observations"])
        stability = row["observed_stability"]
        tail = stability["value"] if stability["status"] == "OBSERVED_STABLE_TAIL" else "-"
        threshold = stability["threshold_prime"] or "-"
        lines.append(f"| {row['deficit']} | {values} | {tail} | {threshold} |")
    lines += [
        "",
        f"Observed stable prefix: `{payload['observed_stable_prefix']}`",
        "",
        "Recurrence diagnostics (finite fit only): " + json.dumps(payload["recurrence_diagnostics"], sort_keys=True),
        "",
        "Boundary: this does not prove eventual stabilization, a closed form, or a uniform automaton quotient.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--large-census", type=Path, default=None)
    args = parser.parse_args()
    extras = []
    if args.large_census is not None:
        large = json.loads(args.large_census.read_text(encoding="utf-8"))
        if large.get("schema") != "paper.route-profiles.low-deficit-census.v1":
            raise SystemExit("unexpected low-deficit census schema")
        if large.get("content_sha256") != digest(large):
            raise SystemExit("low-deficit census content digest mismatch")
        extras = large["records"]
    output = build(load(args.input), extras)
    output["content_sha256"] = digest(output)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.markdown_out.write_text(render(output), encoding="utf-8", newline="\n")
    print(f"PASS {output['schema']}: {len(output['deficit_layers'])} deficit layers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
