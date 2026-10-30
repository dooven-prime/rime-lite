"""Produce the fixed bounded-control record without importing exploratory code."""

import argparse
import json
from pathlib import Path

from audit import report


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "results" / "future_event_controls.v1.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="write the paper-local bounded result record")
    args = parser.parse_args()
    payload = json.dumps(report(), indent=2, sort_keys=True) + "\n"
    if args.write:
        RESULT.write_bytes(payload.encode("utf-8"))
        print(RESULT)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
