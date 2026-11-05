"""Compatibility entry point for the shared HAL reader builder."""

from pathlib import Path
import sys


PAPER = Path(__file__).resolve().parent
sys.path.insert(0, str(PAPER.parents[1] / "tex"))

from build_hal import build  # noqa: E402


if __name__ == "__main__":
    print(build(PAPER / "hal-reader.json"))
