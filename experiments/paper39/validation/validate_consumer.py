"""Read-only finite replay. Reuses the audit runner; not an independent validator."""

import argparse
import json
from pathlib import Path
import re
import sys

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from audit_scope import BOUNDARY, RESULT, cases
from consumer_audit import build_report
from contract import primitive, require


def check_record(report):
    require(set(report) == {"schema", "boundary", "cases", "totals", "examples"}, "result schema drift")
    require(report["schema"] == "rime.paper39.consumer-audit.v1"
            and report["boundary"] == BOUNDARY, "result boundary drift")
    catalogue = list(cases())
    require(len(catalogue) == 464 and len(report["cases"]) == 464, "fixed case range narrowed")
    expected_totals = {}
    for case, row in zip(catalogue, report["cases"]):
        require(set(row) == {"id", "environment", "max_word_length", "counts",
                             "full_trace_sha256", "atom_renaming"}, "case fields drift")
        require(row["id"] == case["id"] and row["environment"] == primitive(case["environment"])
                and row["max_word_length"] == case["max_word_length"], "case input/range drift")
        counts = row["counts"]
        required = {"histories", "registration_queries", "registered_invocations",
                    "command_queries", "legal_commands", "max_absorptions"}
        require(required <= set(counts) <= required | {"absorb_commands", "carry_with_unrelated_fusion"}
                and all(type(value) is int and value >= 0 for value in counts.values()), "invalid counters")
        histories = 2 ** (case["max_word_length"] + 1) - 1
        queries = histories * (2 ** len(case["environment"].seed) - 1)
        require(counts["histories"] == histories and counts["registration_queries"] == queries
                and counts["command_queries"] == 4 * queries
                and counts["legal_commands"] == 2 * counts["registered_invocations"], "coverage counts drift")
        require(re.fullmatch(r"[0-9a-f]{64}", row["full_trace_sha256"]) is not None
                and row["atom_renaming"] == "PASS", "invalid trace or renaming status")
        for key, value in counts.items():
            expected_totals[key] = (max(expected_totals.get(key, 0), value) if key == "max_absorptions"
                                    else expected_totals.get(key, 0) + value)
    require(report["totals"] == expected_totals, "total counters drift")
    require(set(report["examples"]) == {"origin_non_descent", "seven_state", "renamed_final"},
            "worked examples missing")
    require([row["word"] for row in report["examples"]["seven_state"]]
            == ["dppd", "dppdppd", "dppdppdpppppd"], "worked continuation changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="check fixed scope only; skip replay")
    args = parser.parse_args()
    report = json.loads((ROOT / RESULT).read_text(encoding="utf-8"))
    check_record(report)
    if args.static:
        print("PASS: fixed record coverage; finite replay explicitly skipped")
    else:
        replay = build_report(progress=True)
        require(report == replay, "retained result differs from current bounded replay")
        print("PASS: exact complete-trace replay, registration, commands, UFE fold, and worked examples")


if __name__ == "__main__":
    main()
