"""Paper VI v2.1 admission-ledger owning gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
subprocess.run(
    [sys.executable, "experiments/paper6/validation/normal_spectral_chart_audit.py"],
    cwd=ROOT,
    check=True,
)

payload = json.loads(
    (ROOT / "experiments/paper6/results/normality_gated_admission_v2_1.json").read_text(
        encoding="utf-8"
    )
)
records = payload["admission_records"]
assert [row["status"] for row in records].count("ADMITTED") == 4
assert [row["status"] for row in records].count("REJECTED") == 1
for row in records:
    for field in (
        "commutator",
        "qt_normality",
        "ht_normality",
        "qt_hermiticity",
        "ht_hermiticity",
    ):
        assert field in row["pair_residuals"]
    if row["status"] == "ADMITTED":
        assert row["sector_count"] is not None
        assert row["r1_op"] is not None
        assert row["r1_lie"] is not None
    else:
        assert row["sector_count"] is None

manuscript = (ROOT / "papers/paper6/Paper VI.md").read_text(encoding="utf-8")
assert "Computational Proposition 3.2" not in manuscript
assert "Computational Proposition 4.1" not in manuscript
assert "Numerical Certificate 3.2" in manuscript
assert "Numerical Certificate 4.1" in manuscript
print("test_paper6_v2_1.py: OK")
