#!/usr/bin/env python
"""Run all mathematical invariant tests sequentially.

No pytest. No test framework. Just plain assert-based verification.
Each test runs with stdout/stderr inherited so output streams directly.
"""
import subprocess
import sys
from pathlib import Path

TESTS = [
    "test_action_token.py",
    "test_cubie.py",
    "test_representation.py",
    "test_spectralstructure.py",
    "test_spectrum.py",
    "test_sectors.py",
    "test_commutant.py",
    "test_transport.py",
    "test_f3.py",
]

ROOT = Path(__file__).resolve().parent
N = len(TESTS)
passed = 0
failed = []

for name in TESTS:
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
    print(f"  ALL TESTS PASSED  ({passed}/{N})")
print(f"{'=' * 60}")
sys.exit(1 if failed else 0)
