"""Build the Registry v2.1 candidate evidence without rewriting v2.0."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = (
    ROOT
    / "experiments"
    / "paper10"
    / "results"
    / "registry_evidence_v2_1.json"
)
sys.path.insert(0, str(ROOT))

from experiments.paper10.validation.build_results import (  # noqa: E402
    SOURCE_PATHS,
    build as build_v2,
)


def build() -> dict:
    payload = build_v2()
    payload["schema"] = "paper10.registry-evidence.v2.1"
    payload["claim_scope"] = (
        "source-addressed finite certificates and observations for the Registry "
        "v2.1 candidate; no cross-carrier promotion or common dynamics theorem"
    )
    payload["runtime"]["builder"] = (
        "experiments/paper10/validation/build_results_v2_1.py"
    )
    return payload


def main() -> None:
    payload = build()
    RESULT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {RESULT_PATH}")


if __name__ == "__main__":
    main()
