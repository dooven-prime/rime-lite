"""Hostile controls for versioned paper-inheritance replay gates."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

from tools.release.verify_inheritance_gate import replay_source, validate_gate


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def git_text(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def source() -> dict[str, object]:
    return {
        "paper_id": "PAPER31",
        "release_tag": "paper31-v1.0",
        "validator": "validator.py",
        "arguments": ["--replay"],
        "receipt": "receipt.json",
        "required_replay": {"finite_replayed": True},
        "required_stdout": ["PASS finite truth"],
    }


def gate_payload(owner: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "schema": "rime.paper-inheritance-gate.v1",
        "consumer": "PAPER34",
        "status": "PRE_INHERITANCE_GATE",
        "sources": [owner or source()],
        "semantic_constraints": {
            "domain_objects_must_reference_declared_concrete_state_space": True,
            "abstract_witness_only_statement_sufficient": False,
            "forbidden_as_admission_evidence": [
                "separate_witnesses_do_not_combine"
            ],
        },
    }


def make_repository(root: Path, validator_body: str) -> None:
    git(root, "init")
    git(root, "config", "user.name", "Inheritance Gate Test")
    git(root, "config", "user.email", "inheritance@example.invalid")
    (root / "receipt.json").write_text(
        json.dumps({"replay": {"finite_replayed": True}}) + "\n",
        encoding="utf-8",
    )
    (root / "validator.py").write_text(validator_body, encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-m", "release fixture")
    git(root, "tag", "-a", "paper31-v1.0", "-m", "Paper XXXI v1.0")
    anchor = {
        "paper_id": "PAPER31",
        "release_tag": {
            "name": "paper31-v1.0",
            "tag_object_sha": git_text(root, "rev-parse", "refs/tags/paper31-v1.0"),
            "target_commit_sha": git_text(
                root, "rev-parse", "refs/tags/paper31-v1.0^{commit}"
            ),
        },
    }
    anchor_path = root / "docs" / "release-anchors" / "paper31-v1.0.json"
    anchor_path.parent.mkdir(parents=True)
    anchor_path.write_text(json.dumps(anchor) + "\n", encoding="utf-8")


def test_gate_uses_tagged_bytes_and_clears_pythonoptimize(monkeypatch) -> None:
    validator = """\
import os
import sys
if sys.argv[1:] != [\"--replay\"]:
    raise SystemExit(2)
if \"PYTHONOPTIMIZE\" in os.environ:
    raise SystemExit(3)
print(\"PASS finite truth\")
"""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_repository(root, validator)
        (root / "validator.py").write_text("raise SystemExit(9)\n", encoding="utf-8")
        monkeypatch.setenv("PYTHONOPTIMIZE", "2")
        replay_source(root, source(), timeout=30)


def test_gate_rejects_noncanonical_receipt_truth() -> None:
    validator = "print('PASS finite truth')\n"
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_repository(root, validator)
        bad = source()
        bad["required_replay"] = {"finite_replayed": True, "invented": True}
        try:
            replay_source(root, bad, timeout=30)
        except ValueError as error:
            assert "receipt replay truth is not canonical" in str(error)
        else:
            raise AssertionError("noncanonical replay truth was accepted")


def test_gate_rejects_missing_truth_marker() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_repository(root, "print('PASS different stage')\n")
        try:
            replay_source(root, source(), timeout=30)
        except ValueError as error:
            assert "omitted required truth markers" in str(error)
        else:
            raise AssertionError("missing replay truth marker was accepted")


def test_gate_rejects_tagged_source_intervention() -> None:
    validator = """\
from pathlib import Path
Path(\"receipt.json\").write_text('{}\\n', encoding=\"utf-8\")
print(\"PASS finite truth\")
"""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_repository(root, validator)
        try:
            replay_source(root, source(), timeout=30)
        except ValueError as error:
            assert "modified tagged source bytes" in str(error)
        else:
            raise AssertionError("tagged-source intervention was accepted")


def test_gate_rejects_force_moved_tag() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_repository(root, "print('PASS finite truth')\n")
        (root / "later.txt").write_text("later\n", encoding="utf-8")
        git(root, "add", "later.txt")
        git(root, "commit", "-m", "later commit")
        git(root, "tag", "-f", "-a", "paper31-v1.0", "-m", "moved tag")
        try:
            replay_source(root, source(), timeout=30)
        except ValueError as error:
            assert "release tag object identity mismatch" in str(error)
        else:
            raise AssertionError("force-moved release tag was accepted")


def test_gate_rejects_lightweight_tag_recreation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_repository(root, "print('PASS finite truth')\n")
        git(root, "tag", "-d", "paper31-v1.0")
        git(root, "tag", "paper31-v1.0")
        try:
            replay_source(root, source(), timeout=30)
        except ValueError as error:
            assert "release tag object identity mismatch" in str(error)
        else:
            raise AssertionError("lightweight release-tag recreation was accepted")


def test_gate_semantic_constraints_are_fail_closed() -> None:
    validate_gate(gate_payload())
    hostile = gate_payload()
    hostile["semantic_constraints"] = {
        "domain_objects_must_reference_declared_concrete_state_space": False,
        "abstract_witness_only_statement_sufficient": True,
        "forbidden_as_admission_evidence": [],
    }
    try:
        validate_gate(hostile)
    except ValueError as error:
        assert "semantic constraints are not canonical" in str(error)
    else:
        raise AssertionError("weakened semantic constraints were accepted")
