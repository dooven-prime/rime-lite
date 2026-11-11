"""Construct the fixed typed requests using the released syntax constructors."""

import importlib
import json
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("cases.json")


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    with tempfile.TemporaryDirectory(prefix="rgt-case-build-") as temporary:
        with zipfile.ZipFile(ROOT / "experiments/paper40/source/q2-source-v1.zip") as archive:
            archive.extractall(temporary)
        sys.path.insert(0, temporary)
        controls = importlib.import_module("q2_examples").controls()
        rows = []
        for case_id, name, status, words in (
            ("R", "forget_origin", "FAIL_READ", ["dpd", "pdpd"]),
            ("G", "forget_partition", "FAIL_GUARD", ["d", "dpppdp"]),
            ("T", "parity_only", "FAIL_SUCCESSOR", ["d", "dp"]),
            ("P", "packet_only", "PASS_EXACT", None),
        ):
            request = controls[name]
            n = len(request["environment"]["defect"])
            request["environment"]["defect"] = [0, 0] + list(range(2, n))
            if case_id == "R":
                request["program"]["commands"] = []
            rows.append({"id": case_id, "name": name, "request": request,
                         "expected_status": status, "display_histories": words})
    OUT.write_text(json.dumps({"schema": "rime.rgt-formal-cases.v1", "cases": rows}, indent=2) + "\n",
                   encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
