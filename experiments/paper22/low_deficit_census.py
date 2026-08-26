#!/usr/bin/env python3
"""Enumerate only low-deficit survivor subsets for larger prime fields.

For a survivor subset S, every routed transition replaces S by an image and
possibly a restriction, so |S| cannot increase.  Therefore the deficit
k = p - |S| is monotone nondecreasing.  A BFS truncated at k <= K is exact for
all states in those layers; paths that leave the truncation cannot return.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "experiments" / "paper22" / "results" / "low_deficit_census_p23_p29_p31_k7_v1.json"
LABELS = ("S", "R", "R_inv")


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_digest(payload: dict[str, Any]) -> str:
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode()).hexdigest()


def inverse_mod(value: int, prime: int) -> int:
    return pow(value % prime, prime - 2, prime)


def eval_label(prime: int, label: str, point: int) -> int:
    infinity = prime
    if label == "S":
        if point == infinity:
            return 0
        if point == 0:
            return infinity
        return (-inverse_mod(point, prime)) % prime
    if label == "R":
        if point == infinity:
            return 0
        if point == prime - 1:
            return infinity
        return (-inverse_mod(point + 1, prime)) % prime
    if label == "R_inv":
        if point == infinity:
            return prime - 1
        if point == 0:
            return infinity
        return (-1 - inverse_mod(point, prime)) % prime
    raise ValueError(label)


def finite_image(prime: int, label: str, mask: int, infinity_hit: bool) -> tuple[int, bool]:
    image = 0
    hit = infinity_hit
    while mask:
        bit = mask & -mask
        point = bit.bit_length() - 1
        target = eval_label(prime, label, point)
        if target == prime:
            hit = True
        else:
            image |= 1 << target
        mask ^= bit
    return image, hit


def census(prime: int, max_deficit: int) -> dict[str, Any]:
    full = (1 << prime) - 1
    # Sector 1 states are finite-point masks.  The sector-0 branch cannot
    # return to a low-deficit sector-1 state once p > max_deficit + 1.
    states = {full}
    queue: deque[int] = deque([full])
    transitions = 0
    while queue:
        mask = queue.popleft()
        for label in LABELS:
            image, _ = finite_image(prime, label, mask, False)
            transitions += 1
            deficit = prime - image.bit_count()
            if deficit <= max_deficit and image not in states:
                states.add(image)
                queue.append(image)
    layers = Counter(prime - mask.bit_count() for mask in states)
    return {
        "prime": prime,
        "max_deficit": max_deficit,
        "reachable_sector_1_state_count": len(states),
        "explored_label_transitions": transitions,
        "deficit_layer_counts": {str(k): layers[k] for k in sorted(layers)},
        "truncation_exactness": (
            "exact for every sector-1 state with deficit <= max_deficit; "
            "states outside the truncation cannot return because survivor-set "
            "cardinality is nonincreasing"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primes", nargs="+", type=int, default=[23, 29])
    parser.add_argument("--max-deficit", type=int, default=7)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if any(prime < 2 for prime in args.primes):
        raise SystemExit("primes must be >= 2")
    payload = {
        "schema": "paper.route-profiles.low-deficit-census.v1",
        "artifact_role": "COMPUTATIONAL_OBSERVATION_LOW_DEFICIT_LARGE_PRIME_CENSUS",
        "claim_status": "computational_observation",
        "primes": args.primes,
        "max_deficit": args.max_deficit,
        "records": [census(prime, args.max_deficit) for prime in args.primes],
        "boundary": [
            "no full automaton state count is claimed",
            "no eventual stabilization theorem is claimed",
            "the truncation argument relies on survivor-set cardinality monotonicity",
        ],
    }
    payload["content_sha256"] = content_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    for record in payload["records"]:
        print(record["prime"], record["reachable_sector_1_state_count"], record["deficit_layer_counts"])
    print(f"PASS {payload['schema']}: {args.primes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
