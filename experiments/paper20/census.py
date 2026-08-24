"""Run the independent carrier-accessibility comparison census."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper20.adapters import (
    rubik_engine,
    s3_natural_regular_engine,
    z2_double_regular_engine,
)


MODEL_SOURCE_PATHS = {
    "z2": [],
    "s3": [],
    "rubik": [
        ROOT / "rime" / "base.py",
        ROOT / "rime" / "cube.py",
        ROOT / "rime" / "cubie.py",
        ROOT / "rime" / "cubieoperator.py",
        ROOT / "rime" / "helpers.py",
        ROOT / "rime" / "spectral_utils.py",
    ],
}


def source_reference(path: Path) -> dict:
    return {
        "uri": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def content_digest(payload: dict) -> str:
    unsigned = deepcopy(payload)
    unsigned.pop("content_sha256", None)
    encoded = json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_payload(model: str, max_depth: int) -> dict:
    if model not in MODEL_SOURCE_PATHS:
        raise ValueError(f"unknown model: {model}")
    if max_depth < 1:
        raise ValueError("max_depth must be positive")
    builders = {
        "z2": z2_double_regular_engine,
        "s3": s3_natural_regular_engine,
        "rubik": rubik_engine,
    }
    engine = builders[model]()
    result = engine.census(max_depth)
    payload = {
        "schema_version": "rime.carrier-accessibility-census.v1",
        "model": model,
        "dimension": engine.dimension,
        "sector_count": engine.sector_count,
        "transport_count": len(engine.transports),
        "max_depth_enumerated": max_depth,
        "tolerance": engine.tolerance,
        "support_tolerance": engine.support_tolerance,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "arithmetic": "complex128_with_declared_thresholds",
        },
        "claim_status": "computational_observation",
        "claim_boundary": (
            "Finite enumeration through max_depth_enumerated; null minimum depth "
            "does not imply all-depth inaccessibility without the carrier theorem."
        ),
        "enumeration_policy": "all ordered transport words and all intermediate sector routes",
        "source_artifacts": [
            source_reference(HERE / "engine.py"),
            source_reference(HERE / "adapters.py"),
            source_reference(Path(__file__).resolve()),
            *(source_reference(path) for path in MODEL_SOURCE_PATHS[model]),
        ],
        "result": result.__dict__,
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=tuple(MODEL_SOURCE_PATHS), default="s3")
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.max_depth < 1:
        raise SystemExit("--max-depth must be positive")
    payload = build_payload(args.model, args.max_depth)
    encoded = json.dumps(payload, indent=2) + "\n"
    if args.out:
        target = args.out if args.out.is_absolute() else ROOT / args.out
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")


if __name__ == "__main__":
    main()
