#!/usr/bin/env python3
"""Rebuild the Paper XXVII theorem-facing artifact chain."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "experiments" / "paper27"
RESULTS = PACKAGE / "results"


def run(*arguments: str) -> None:
    command = [sys.executable, *arguments]
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def result(name: str) -> str:
    return str(RESULTS / name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rebuild-n6-base",
        action="store_true",
        help="rebuild the n=6 base enumeration before derived artifacts",
    )
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    if args.rebuild_n6_base:
        run(
            str(PACKAGE / "audit_n6_rank4_activated_entry_exhaustiveness.py"),
            "--workers",
            str(args.workers),
            "--out",
            result("single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json"),
        )

    run(
        str(PACKAGE / "analyze_n6_entry_section_image.py"),
        "--out",
        result("single_defect_n6_entry_section_image_v1.json"),
    )
    run(
        str(PACKAGE / "analyze_n6_type_ii_only_section.py"),
        "--out",
        result("single_defect_n6_type_ii_only_section_v1.json"),
    )
    channel = result("single_defect_n7_extremal_carrier_input_v1.json")
    moved = result("single_defect_n7_extremal_moved_slot_menu_v1.json")
    germs = result("single_defect_n7_extremal_edge_germs_v1.json")
    complement = result("single_defect_n7_extremal_direct_complement_v1.json")
    failure = result("single_defect_n7_extremal_failure_equations_v1.json")

    run(str(PACKAGE / "analyze_n7_extremal_moved_slot_menu.py"), channel, "--out", moved)
    run(str(PACKAGE / "analyze_n7_extremal_edge_germs.py"), moved, "--out", germs)
    run(
        str(PACKAGE / "analyze_n7_extremal_direct_complement.py"),
        germs,
        "--out",
        complement,
    )
    run(
        str(PACKAGE / "analyze_n7_extremal_failure_equations.py"),
        complement,
        "--out",
        failure,
    )
    run(
        str(PACKAGE / "analyze_n7_extremal_negative_cell_exhaustion.py"),
        failure,
        "--out",
        result("single_defect_n7_extremal_negative_cell_exhaustion_v1.json"),
    )


if __name__ == "__main__":
    main()
