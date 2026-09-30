#!/usr/bin/env python3
"""Public build entry point for RIME TeX artifacts.

This wraps the legacy ``_build.py`` module so manual commands can use the
non-underscored script name while older automation continues to work.
"""

from __future__ import annotations

import sys

from _build import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
