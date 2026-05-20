#!/usr/bin/env python
"""Run all fast mathematical invariant tests sequentially.

No pytest. No test framework. Just plain assert-based verification.
Each test runs with stdout/stderr inherited so output streams directly.

Slow tests (require CubieSpectralOperator ~2-5 min each):
  test_cubieoperator.py  — canonical engine: spectral theorem, Bose-Mesner, k-set recon
  test_commutant_gap.py  — Δ_comm, transport invariants
  test_transport.py      — K symmetry, T7 pairs, N=2 control
  test_f3.py             — isotypic decomposition, multiplicity reservoir

Run them with: python tests/run_slow_tests.py
"""
import subprocess
import sys
from pathlib import Path

# Fast tests — no CubieSpectralOperator construction (<<1s each)
TESTS = [
    "test_action_token.py",
    "test_cubie.py",
    "test_cubieoperator.py",
    "test_spectralstructure.py",
    "test_representation.py",
    "test_spectrum.py",
    "test_sectors.py",
    "test_commutant.py",
]

# Slow tests — each constructs CubieSpectralOperator (~1-2 min)
SLOW_TESTS = [
    "test_commutant_gap.py",
    "test_transport.py",
    "test_f3.py",
]

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent  # rime-lite root, where rime/ package lives
N = len(TESTS)
env = {**__import__('os').environ, 'PYTHONPATH': str(PROJECT_ROOT)}
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
        cwd=str(PROJECT_ROOT),
        env=env,
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
    print(f"  ALL FAST TESTS PASSED  ({passed}/{N})")
print(f"{'=' * 60}")

if SLOW_TESTS:
    print(f"\nSlow tests (require CubieSpectralOperator, ~2-5 min each):")
    for name in SLOW_TESTS:
        print(f"  python tests/{name}")
    print(f"Run: python tests/run_slow_tests.py")
sys.exit(1 if failed else 0)
