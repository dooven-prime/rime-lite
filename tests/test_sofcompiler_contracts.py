"""Regression check for the three SOF compiler contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "schemas" / "sofcompiler" / "validate_examples.py"
OUTPUT_FIXTURE = (
    ROOT
    / "schemas"
    / "sofcompiler"
    / "examples"
    / "strict-associative-compiler-output-v1.0.json"
)


result = subprocess.run(
    [sys.executable, str(VALIDATOR)],
    cwd=ROOT,
    text=True,
    capture_output=True,
)

if result.stdout:
    print(result.stdout, end="")
if result.stderr:
    print(result.stderr, end="", file=sys.stderr)

assert result.returncode == 0, "SOF compiler contract validation failed"

output = json.loads(OUTPUT_FIXTURE.read_text(encoding="utf-8"))
assert output["item_type"] == "ClaimItem_v1 | DegradationItem_v1"
assert output["items"], "compiler output fixture must not be empty"
for item in output["items"]:
    assert item["item_kind"] in {"claim", "degradation"}
    if item["item_kind"] == "claim":
        assert item["source_ir_kind"] == "claim"
        assert item["source_ir_id"] == item["claim_id"]
        assert item["claim_status"] is not None
    else:
        assert "action" in item and "reason_kind" in item

print("test_sofcompiler_contracts.py: OK")
