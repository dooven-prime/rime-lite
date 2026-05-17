#!/usr/bin/env python
"""Run slow mathematical invariant tests (require CubieSpectralOperator).

Each test constructs CubieSpectralOperator (228x228 eigendecomposition,
transport tensor, commutant basis, etc.) and takes ~2-5 min.

No pytest. No test framework. Just plain assert-based verification.
"""
import subprocess
import sys
from pathlib import Path

SLOW_TESTS = [
    "test_commutant_gap.py",
    "test_transport.py",
    "test_f3.py",
]

ROOT = Path(__file__).resolve().parent
N = len(SLOW_TESTS)
passed = 0
failed = []

for name in SLOW_TESTS:
    path = ROOT / name
    header = f" {name} "
    print(f"\n{'=' * 60}")
    print(f"{header:=^60}")
    print(f"{'=' * 60}")
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
    )
    if result.returncode == 0:
        passed += 1
    else:
        failed.append(name)

print(f"\n{'=' * 60}")
if failed:
    print(f"  FAILED: {len(failed)}/{N}")
    for f in failed:
        print(f"    - {f}")
else:
    print(f"  ALL SLOW TESTS PASSED  ({passed}/{N})")
print(f"{'=' * 60}")
sys.exit(1 if failed else 0)
