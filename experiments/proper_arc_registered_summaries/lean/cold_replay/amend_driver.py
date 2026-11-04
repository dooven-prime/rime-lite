"""Record a pre-execution driver-only snapshot revision without altering proof inputs."""

import argparse
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from theorem_map import as_json, require, sha256

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--snapshot", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
old = args.snapshot.resolve(strict=True)
data = json.loads(old.read_text("utf-8"))
target = Path(data["lean_directory"])
require(not (old.parent/"cold-replay.v1.json").exists(), "driver amendment is pre-execution only")
require(not (target/".lake").exists(), "driver amendment would change an already started build")
require(not args.output.exists(), "refuse to replace an existing snapshot revision")
for name, expected in data["source_sha256"].items():
    require(sha256(target/name) == expected, f"pre-amendment cold source drift: {name}")
name = "cold_replay/run_replay.py"
previous = data["source_sha256"][name]
shutil.copyfile(BASE/name, target/name)
data["source_sha256"][name] = sha256(target/name)
data["previous_snapshot_sha256"] = sha256(old)
data["driver_amendment"] = {"utc": datetime.now(timezone.utc).isoformat(), "file": name,
    "previous_sha256": previous, "sha256": data["source_sha256"][name],
    "reason": "Use all owning validators' default replay CLI; the M2 interface has no --check-upstream-git flag. Historical Git bytes are verified by the map before and after replay.",
    "frozen_proof_inputs_changed": False}
args.output.write_text(as_json(data), encoding="utf-8", newline="\n")
print(json.dumps({"status": "PASS_PRE_EXECUTION_DRIVER_AMENDMENT", "snapshot": str(args.output)}))
