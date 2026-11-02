"""Read-only byte and bounded-replay validation for this local closure."""

from collections import defaultdict
import hashlib
import json
from pathlib import Path

import general_arc_control
import origin_control


ROOT = Path(__file__).resolve().parent
RESULT = "results/proper_arc_controls.v1.json"
BOUND_FILES = ("core.py", "general_arc_control.py", "origin_control.py",
               "validate_controls.py", RESULT)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_bytes():
    manifest = json.loads((ROOT / "control-manifest.v1.json").read_text("utf-8"))
    require(manifest.get("schema") == "proper_arc_closure.v1",
            "unexpected closure schema")
    bound = manifest.get("sha256", {})
    require(set(bound) == set(BOUND_FILES), "closure file list mismatch")
    for name in BOUND_FILES:
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        require(digest == bound[name], f"source byte drift: {name}")


def full_log_row(n):
    observed = general_arc_control.check_n(n, verbose=False)
    groups = defaultdict(list)
    for item in observed["proper_per_F"]:
        groups[item["r"]].append(item["summaries"])
    by_length = []
    for r in range(2, n):
        counts = groups[r]
        require(len(counts) == n and len(set(counts)) == 1,
                f"proper-arc uniformity failed at n={n}, r={r}")
        by_length.append({"r": r, "arc_count": n,
                          "summaries_per_arc": counts[0]})
    require(set(groups) == set(range(2, n)), "unexpected proper-arc length")
    return {"n": n, "log_states": observed["log_states"],
            "proper_by_length": by_length}


def main():
    validate_bytes()
    expected = json.loads((ROOT / RESULT).read_text("utf-8"))
    require(expected.get("schema") == "proper_arc_controls.v1" and
            expected.get("status") == "BOUNDED_CONSISTENCY_CONTROL",
            "unexpected control result schema or status")
    require(set(expected) == {"schema", "status", "full_log", "origin_words"},
            "unexpected control result fields")
    require(expected["full_log"] == [full_log_row(n) for n in range(3, 7)],
            "full-log replay differs from fixed results")
    require(expected["origin_words"] ==
            [origin_control.audit_n(n) for n in range(3, 8)],
            "origin-word replay differs from fixed results")
    print("PASS proper-arc closure: exact bytes, full logs n=3..6, "
          "origin words n=3..7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
