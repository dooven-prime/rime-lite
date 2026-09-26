"""Render the Paper XXVIII finite-mechanism architecture figure."""

from __future__ import annotations

import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main() -> None:
    subprocess.run(
        [
            "dot",
            "-Tpng",
            "-Gdpi=190",
            str(HERE / "fig1_finite_mechanism_structure.dot"),
            "-o",
            str(HERE / "fig1_finite_mechanism_structure.png"),
        ],
        check=True,
        cwd=HERE,
    )


if __name__ == "__main__":
    main()
