"""Paper VII v2.1 structured-incidence and fixed-frame owning gates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)


run("experiments/paper7/validation/structured_incidence_geometry.py")
run("experiments/paper7/validation/register_fixed_frame_profiles.py")

results = ROOT / "experiments/paper7/results"
structured = json.loads((results / "structured_incidence_geometry_v2_1.json").read_text())
for row in structured["diagonal_ambient"]["rows"]:
    assert row["zero_product_locus_codimension"] == row["d"]
assert structured["represented_pullback_control"]["pullback_codimension"] == 0

profile = json.loads((results / "fixed_frame_incidence_profiles_v2_1.json").read_text())
assert profile["family_index"]["labelled_nonempty_family_count"] == 63
assert profile["family_index"]["rotation_orbit_representative_count"] == 19
assert profile["exact_numerator_certificate"]["int64_preoperation_audit"]["all_operations_safe"]

legacy_pairs = (
    ("incidence_geometry.json", "incidence_variety_codim.py"),
    ("projected_composition_audit.json", "rank_protected_bridge_audit.py"),
    ("full_array_lie_atlas.json", "atlas_r2_boundary.py"),
)
for result_name, script_name in legacy_pairs:
    result = json.loads((results / result_name).read_text(encoding="utf-8"))
    script = ROOT / "experiments/paper7/validation" / script_name
    assert result["runtime"]["script_sha256"] == hashlib.sha256(script.read_bytes()).hexdigest()

print("test_paper7_v2_1.py: OK")
