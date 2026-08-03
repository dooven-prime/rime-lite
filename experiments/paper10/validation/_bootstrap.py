"""Make Paper X validation use the current source tree."""

from pathlib import Path
import sys


VALIDATION_DIR = Path(__file__).resolve().parent
PAPER_DIR = VALIDATION_DIR.parent
ROOT = PAPER_DIR.parents[1]

for path in (VALIDATION_DIR, PAPER_DIR, ROOT):
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)
