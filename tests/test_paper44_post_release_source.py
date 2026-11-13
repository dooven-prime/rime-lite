"""Hostile checks for the downstream Paper XLIV state-search source lock."""

from __future__ import annotations

import copy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.release.verify_paper44_state_search import (
    EXPECTED, SOURCE, audit, check_caller, check_record, check_source, tagged,
)


def must_reject(action, case: str) -> None:
    try:
        action()
    except (SyntaxError, ValueError):
        return
    raise AssertionError(f"state-search source mutation accepted: {case}")


def test_current_tag_and_materialization() -> None:
    audit()


def test_source_drift() -> None:
    must_reject(lambda: check_source(tagged(SOURCE) + b"\n# drift\n"), "source bytes")


def test_supplement_rebinding() -> None:
    altered = copy.deepcopy(EXPECTED)
    altered["omitted_source"]["sha256_at_tag"] = "0" * 64
    must_reject(lambda: check_record(altered), "supplement digest")


def test_missing_import_and_call() -> None:
    path = EXPECTED["bound_callers"]["finite-spectrum-control"]
    caller = tagged(path)
    must_reject(lambda: check_caller(
        caller.replace(b"import shortest_summary_search as search", b"import other as search"),
        path), "missing import")
    must_reject(lambda: check_caller(
        caller.replace(b"search.successor", b"search.other"), path),
        "missing successor calls")


if __name__ == "__main__":
    test_current_tag_and_materialization()
    test_source_drift()
    test_supplement_rebinding()
    test_missing_import_and_call()
    print("test_paper44_post_release_source.py: OK")
