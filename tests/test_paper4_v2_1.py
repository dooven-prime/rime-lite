"""Paper IV v2.1 owning gates and immutable-v2 regression."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "experiments/paper4/results/rubik_joint_spectrum_registration.observation.json"
CANDIDATE = ROOT / "experiments/paper4/results/rubik_joint_spectrum_registration_v2_1.observation.json"
EXPECTED_FROZEN_SHA256 = "dc3729809f75e66f58d6750849ec28d5cd4a33bc05ea4a8d24f364eb3c655e9a"


def run(*parts: str) -> None:
    subprocess.run([sys.executable, *parts], cwd=ROOT, check=True)


assert hashlib.sha256(FROZEN.read_bytes()).hexdigest() == EXPECTED_FROZEN_SHA256
assert FROZEN.read_bytes() != CANDIDATE.read_bytes()
run("experiments/paper4/validation/rubik_collision_quotient.py")
run("experiments/paper4/validation/v59_collision_vs_transport.py")
run(
    "experiments/paper4/validation/rubik_joint_spectrum_registration.py",
    "--check-result",
)

record = json.loads(CANDIDATE.read_text(encoding="utf-8"))
assert record["run"]["status"] == "passed"
assert record["claim"]["status"] == "computational_certificate"
manuscript = (ROOT / "papers/paper4/Paper IV.md").read_text(encoding="utf-8")
for assumption in ("Assumption R1", "Assumption R2", "Assumption R3"):
    assert assumption in manuscript

print("test_paper4_v2_1.py: OK")
