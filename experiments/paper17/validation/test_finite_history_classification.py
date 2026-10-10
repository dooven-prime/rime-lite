#!/usr/bin/env python3
"""Toy hostile checks for cross-source/cross-time history classification."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_finite_history_closure_v1 import _classify


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    sources = [10, 20]
    sequences = {
        10: (0, 1, 2, 3, 4),
        20: (0, 5, 6, 7, 8),
    }
    result = _classify(sources, sequences, H=2, T=4)
    require(result["orders"][0]["outcome"] == "FAILED_EXACT_CLOSURE", "order-zero outcome mismatch")
    require(result["orders"][0]["first_failure_witness"] is not None, "missing order-zero failure witness")
    require(result["orders"][1]["N_h"] == 6, "order-one window count mismatch")
    require(result["orders"][2]["N_h"] == 4, "order-two window count mismatch")
    require(
        result["orders"][2]["horizon_bounded_shift_checks"] == 2,
        "order-two shift count mismatch",
    )
    require(
        result["minimal_closing_order_on_registered_domain"] == 1,
        "toy minimal-closing-order mismatch",
    )
    print("FINITE_HISTORY_CLASSIFICATION_TEST_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
