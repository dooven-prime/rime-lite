"""Compatibility entry point for the withdrawn Paper III T7 detector.

The old implementation checked only two-step support-graph reachability and
incorrectly reported nonzero compositional morphisms. The canonical audit now
evaluates the projected matrix products explicitly.
"""

from pathlib import Path
import sys

PAPER3_DIR = Path(__file__).resolve().parents[1]
if str(PAPER3_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER3_DIR))

from validation.composition_obstruction import run_audit


if __name__ == "__main__":
    print("Legacy T7 claim withdrawn; running composition-obstruction audit.")
    run_audit()
