#!/usr/bin/env python
"""Run selected fixed-frame and endogenous incidence censuses."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from incidence_profiles import incidence_census, named_family, write_json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--families",
        default="full,drop_axis0_ht,axes02_qt",
        help="comma-separated named families",
    )
    parser.add_argument(
        "--protocols",
        default="fixed_full,endogenous",
        help="comma-separated protocols: fixed_full,endogenous",
    )
    parser.add_argument("--output", type=Path, default=Path("results/named"))
    parser.add_argument("--no-carrier-classification", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    summary = []
    for family_name in filter(None, args.families.split(",")):
        family = named_family(family_name)
        for protocol in filter(None, args.protocols.split(",")):
            print(f"running {family_name} / {protocol}", flush=True)
            started = time.perf_counter()
            profile = incidence_census(
                family,
                protocol,
                include_carrier_classification=not args.no_carrier_classification,
            )
            elapsed = time.perf_counter() - started
            profile["provenance"]["elapsed_seconds"] = elapsed
            destination = args.output / f"{family_name}__{protocol}.json"
            write_json(destination, profile)
            row = {
                "family": family_name,
                "protocol": protocol,
                "elapsed_seconds": elapsed,
                **profile["counts"],
            }
            summary.append(row)
            print(
                f"  routes={row['total_supported_routes']} "
                f"zero={row['unprotected_zero']} protected={row['protected_routes']} "
                f"elapsed={elapsed:.1f}s",
                flush=True,
            )
    write_json(args.output / "summary.json", summary)


if __name__ == "__main__":
    main()
