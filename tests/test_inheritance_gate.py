"""Hostile controls for versioned paper-inheritance replay gates."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

from tools.release.verify_inheritance_gate import replay_source, validate_gate


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


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
    git(root, "tag", "paper31-v1.0")


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
