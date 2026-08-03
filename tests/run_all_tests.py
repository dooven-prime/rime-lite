#!/usr/bin/env python
"""Run the active mathematical and API regression tests sequentially.

No pytest. No test framework. Just plain assert-based verification.
Each test runs with stdout/stderr inherited so output streams directly.

The active suite includes the current CubieSpectralOperator regressions. The
separate slow runner is retained only as a convenience for rerunning those
files.
"""
import subprocess
import sys
from pathlib import Path

# Active tests. Some construct CubieSpectralOperator and are not sub-second.
TESTS = [
    "test_action_token.py",
    "test_cubie.py",
    "test_cubieoperator.py",
    "test_spectralstructure.py",
    "test_spectral_utils_api.py",
    "test_representation.py",
    "test_spectrum.py",
    "test_sectors.py",
    "test_commutant.py",
    "test_transport.py",
    "test_experiment_observation.py",
    "test_accessibility_engine.py",
    "test_wall_trajectory.py",
    "test_registry_v2.py",
    "test_registry_migration.py",
    "test_sofcompiler_contracts.py",
    "test_sofrs_v2.py",
    "test_sofaudit_v2.py",
    "test_typed_wall_record_census.py",
]

# Slow tests — each constructs CubieSpectralOperator (~1-2 min)
SLOW_TESTS = [
    "test_cubieoperator.py",
    "test_transport.py",
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
    print(f"  ALL ACTIVE TESTS PASSED  ({passed}/{N})")
print(f"{'=' * 60}")

if SLOW_TESTS:
    print(f"\nLonger tests can be rerun separately:")
    for name in SLOW_TESTS:
        print(f"  python tests/{name}")
    print(f"Run: python tests/run_slow_tests.py")
sys.exit(1 if failed else 0)
