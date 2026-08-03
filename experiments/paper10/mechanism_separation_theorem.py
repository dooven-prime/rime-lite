"""Compatibility entry point for the immutable Registry v1 source path.

The calibrated response construction is owned by Paper IX v2 and implemented
in ``experiments.paper9.calibrated_response``. Registry v1 retains this path as
historical provenance, so the wrapper remains executable without duplicating
the scientific implementation.
"""

from experiments.paper9.calibrated_response import audit, main

__all__ = ["audit", "main"]


if __name__ == "__main__":
    main()
