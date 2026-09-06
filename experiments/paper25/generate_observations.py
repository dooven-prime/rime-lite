"""Generate the five Paper XXV paper-owned observation artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper25.markov_probability_alignment import (
    build_payload as build_markov_alignment,
)
from experiments.paper25.markov_stability import build_payload as build_markov
from experiments.paper25.perturbation_sweep import build_payload as build_perturbation
from experiments.paper25.rubik_transport import build_payload as build_rubik
from experiments.paper25.transformation_laws import build_payload as build_transformation


RUBIK_RUNTIME_SOURCES = (
    "rime/base.py",
    "rime/cube.py",
    "rime/cubie.py",
    "rime/cubieoperator.py",
    "rime/helpers.py",
    "rime/spectral_utils.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(name: str, payload: dict, sources: tuple[str, ...]) -> None:
    payload["source_artifacts"] = [
        {"uri": source, "sha256": _sha256(ROOT / source)} for source in sources
    ]
    path = RESULTS / name
    path.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"WROTE {path.relative_to(ROOT).as_posix()}")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    _write(
        "transformation_laws_v1.json",
        build_transformation(),
        ("experiments/paper25/transformation_laws.py",),
    )
    _write(
        "rubik_qh_transport_v1.json",
        build_rubik(),
        (
            "experiments/paper25/rubik_transport.py",
            *RUBIK_RUNTIME_SOURCES,
        ),
    )
    _write(
        "rubik_perturbation_sweep_v1.json",
        build_perturbation(),
        (
            "experiments/paper25/perturbation_sweep.py",
            "experiments/paper25/rubik_transport.py",
            *RUBIK_RUNTIME_SOURCES,
        ),
    )
    markov = build_markov()
    _write(
        "nonnormal_markov_stability_v1.json",
        markov,
        (
            "experiments/paper25/markov_stability.py",
            "experiments/paper25/markov_helpers.py",
            "experiments/paper25/perturbation_sweep.py",
        ),
    )
    _write(
        "markov_probability_alignment_v1.json",
        build_markov_alignment(markov),
        (
            "experiments/paper25/markov_probability_alignment.py",
            "experiments/paper25/markov_helpers.py",
            "experiments/paper25/markov_stability.py",
        ),
    )


if __name__ == "__main__":
    main()
