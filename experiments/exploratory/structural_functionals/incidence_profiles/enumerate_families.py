#!/usr/bin/env python
"""Build or execute the symmetry-reduced axis-balanced family index."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from incidence_profiles import (
    axis_balanced_families,
    incidence_census,
    source_artifact,
    write_json,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--family-index",
        type=Path,
        default=Path("results/axis_balanced_family_index.json"),
    )
    parser.add_argument("--run", action="store_true", help="run censuses after writing the family index")
    parser.add_argument("--protocol", choices=("fixed_full", "endogenous"), default="fixed_full")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing profile files after an implementation change",
    )
    args = parser.parse_args()

    family_index = axis_balanced_families()
    write_json(
        args.family_index,
        {
            "schema": "rime.axis-balanced-family-index.v1",
            "claim_status": "Computational Certificate",
            "certificate_kind": "exact_finite_combinatorial",
            "family_count": len(family_index),
            "families": family_index,
            "provenance": {
                "source_artifacts": [
                    source_artifact(Path(__file__)),
                    source_artifact(Path(__file__).with_name("incidence_profiles.py")),
                ]
            },
        },
    )
    print(
        f"indexed {len(family_index)} rotation-orbit representatives "
        f"in {args.family_index}"
    )
    if not args.run:
        return

    selected = family_index[args.start : args.stop]
    default_directories = {
        "fixed_full": Path("results/axis_balanced_fixed"),
        "endogenous": Path("results/axis_balanced_endogenous"),
    }
    output_directory = args.output or default_directories[args.protocol]
    for record in selected:
        output = output_directory / f"{record['orbit_id']}__{args.protocol}.json"
        if output.exists() and not args.overwrite:
            print(f"skip existing {output}")
            continue
        print(f"running {record['orbit_id']} ({record['operator_count']} operators)", flush=True)
        started = time.perf_counter()
        profile = incidence_census(record["generator_keys"], args.protocol)
        profile["family"]["orbit_id"] = record["orbit_id"]
        profile["provenance"]["elapsed_seconds"] = time.perf_counter() - started
        write_json(output, profile)


if __name__ == "__main__":
    main()
