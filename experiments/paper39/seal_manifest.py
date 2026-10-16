"""Explicit authoring-time sealing; validators never invoke this writer."""

import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE / "validation"))
from validate_package import manifest_data


def main():
    data = manifest_data()
    target = PACKAGE / "development-manifest.json"
    target.write_bytes((json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print("Sealed development inventory only; run validate_package.py before relying on replay status.")


if __name__ == "__main__":
    main()
