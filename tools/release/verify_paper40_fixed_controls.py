"""Audit the fixed controls in the immutable Paper XL v1.0 release tag.

This is a post-release consistency check, not part of the tagged closure or
independent validation of the consumer theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile


TAG = "paper40-v1.0"
TAG_OBJECT = "2847653c7273b1e3d1d60baa725eba751c36e49d"
CONTENT_COMMIT = "6df0b4aa9357aa67522aa2e47436674aab1bad5f"
RUNTIME_SOURCE_SHA256 = "8fc2fa3d3ab599236d0b952a430fa2a9028dbdf2f363c03adf19b0c1678e5e25"
UPSTREAM_COMMIT = "b032b47ec47f28c8b2f65844abbe30dc3b38fef8"
UPSTREAM_DIGESTS = {
    "contract.py": "001ce3824a4cde7c2e1e37ba1cebabbdeed49e1e3b57d5664dcdf609d3e909a1",
    "forest.py": "ab2d6913f29bb4008f80d9f6d48db7e5b246fe75382ef0b2df2b2f2639d66336",
    "log_consumer.py": "f0c6786ecdfbd54209487db725340469c4816cae574e55b966d7323955dd2640",
}

EXPECTED_SCOPE = [
    {"n": 2, "defect": [0, 0], "selected": [0, 1], "saturated_forest_states": 6,
     "saturated_log_states": 6, "registered_forests": 4, "registered_summaries": 4},
    {"n": 3, "defect": [0, 2, 0], "selected": [0, 1, 2], "saturated_forest_states": 39,
     "saturated_log_states": 39, "registered_forests": 18, "registered_summaries": 18},
    {"n": 4, "defect": [0, 0, 1, 2], "selected": [0, 1], "saturated_forest_states": 276,
     "saturated_log_states": 292, "registered_forests": 84, "registered_summaries": 72},
]

# Each row fixes name, kernel status/distribution/dimension, operator result,
# and semantic result. These values are independent of the retained JSON.
EXPECTED_CASES = [
    ("gamma_n2", "PASS_EXACT", {"1": 4}, 0, 4, 4, None, None, None),
    ("unordered_parent_binding", "FAIL_READ", {"2": 2}, 2, None, None, "d", "pd", None),
    ("gamma_n3", "PASS_EXACT", {"1": 18}, 0, 18, 18, None, None, None),
    ("packet_only_consumer", "PASS_EXACT", {"6": 3}, 15, 18, 3, None, None, None),
    ("packet_q_origin_report", "FAIL_READ", {"6": 3}, 15, None, None, "dd", "pdd", None),
    ("gamma_n4", "PASS_EXACT", {"1": 60, "2": 12}, 12, 84, 72, None, None, None),
    ("missing_partition_guard", "FAIL_GUARD", {"1": 24, "3": 8, "9": 4}, 48,
     None, None, "d", "ppdpppd", ["Carry", "d"]),
    ("parity_not_a_state", "FAIL_SUCCESSOR", {"32": 1, "52": 1}, 82,
     None, None, "d", "dp", ["Raw", "d"]),
    ("immutable_context_count", "PASS_EXACT", {"1": 36, "2": 16, "4": 4}, 28,
     84, 56, None, None, None),
]

EXPECTED_MATCHED = [
    {"n": 2, "words": ["d", "pd"], "clauses": "R"},
    {"n": 3, "words": ["dd", "pdd"], "clauses": "R"},
    {"n": 4, "words": ["dp", "dppd"], "clauses": "G_and_T"},
]
EXPECTED_CONTINUATION = {
    "prefix": "dppd", "selected": [3, 5], "suffix": "ppdpppppd",
    "trace": [[5, 5, 0, 0], [5, 5, 0, 0], [5, 4, 0, 0],
              [4, 4, 0, 0], [4, 4, 0, 0], [4, 4, 0, 0],
              [4, 4, 0, 0], [4, 4, 0, 0], [4, 3, 0, 1]],
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def tagged_bytes(root: Path, path: str) -> bytes:
    return git(root, "show", f"{CONTENT_COMMIT}:{path}")


def validate_fixed_controls(record: dict, source_archive: bytes) -> None:
    fixed = record.get("fixed_controls")
    require(isinstance(fixed, dict), "fixed_controls is missing")
    require(set(fixed) == {"scope", "cases", "matched", "same_invocation", "status",
                            "evidence", "full_grammar_interpreter", "canonical_compiler_admission",
                            "upstream_commit", "upstream_blobs_sha256"}, "fixed control fields differ")
    require(fixed["status"] == "PASS_FIXED_CONTROLS" and
            fixed["evidence"] == "LOCAL_CONSISTENCY_CONTROL" and
            fixed["full_grammar_interpreter"] is False and
            fixed["canonical_compiler_admission"] is False, "fixed control status or boundary differs")
    require(fixed["upstream_commit"] == UPSTREAM_COMMIT and
            fixed["upstream_blobs_sha256"] == UPSTREAM_DIGESTS, "upstream binding differs")
    require(fixed["scope"] == EXPECTED_SCOPE, "fixed control scope/counts differ")
    require(fixed["matched"] == EXPECTED_MATCHED, "matched controls differ")
    require(fixed["same_invocation"] == EXPECTED_CONTINUATION,
            "seven-position continuation differs")
    cases = fixed["cases"]
    require(isinstance(cases, list) and len(cases) == len(EXPECTED_CASES),
            "fixed control case count differs")
    require([case.get("name") for case in cases] == [row[0] for row in EXPECTED_CASES],
            "fixed control case names/order differ")
    for case, (name, status, distribution, dimension, basis, fibers, left, right, command) in zip(
        cases, EXPECTED_CASES, strict=True
    ):
        kernel = {"status": status, "fiber_size_distribution": distribution,
                  "kernel_dimension": dimension}
        operator = {"status": status}
        semantic = {"status": status}
        if status == "PASS_EXACT":
            operator.update(basis_columns=basis, fibers=fibers)
            semantic["fibers"] = fibers
        else:
            semantic.update(left_word=left, right_word=right, command=command)
        require(case == {"name": name, "kernel": kernel, "operator": operator,
                         "semantic": semantic}, f"fixed control differs: {name}")
    with zipfile.ZipFile(io.BytesIO(source_archive)) as archive:
        member = archive.read("fixed_controls.py")
    require(hashlib.sha256(member).hexdigest() == RUNTIME_SOURCE_SHA256,
            "fixed-controls producer source differs")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repository.resolve()
    require(git(root, "show-ref", "--verify", "--hash", f"refs/tags/{TAG}").decode().strip()
            == TAG_OBJECT, "Paper XL tag object differs")
    require(git(root, "rev-parse", f"{TAG_OBJECT}^{{commit}}").decode().strip()
            == CONTENT_COMMIT, "Paper XL content commit differs")
    record = json.loads(tagged_bytes(root, "experiments/paper40/results/q2-controls.v1.json"))
    archive = tagged_bytes(root, "experiments/paper40/source/q2-source-v1.zip")
    validate_fixed_controls(record, archive)
    print("PASS Paper XL v1.0 tagged fixed-controls audit (9 cases; 84-to-72; continuation)")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, TypeError, ValueError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        raise SystemExit(f"FAIL: {error}") from error
