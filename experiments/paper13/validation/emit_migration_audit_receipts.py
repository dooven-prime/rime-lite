"""Emit stable SOFAUDIT v2 validation receipts for migrated audit artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from validate_sofaudit_v2 import DEFAULT_DIR, ROOT, build_validation_receipt


OUT = ROOT / "experiments" / "paper13" / "results" / "receipts"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for audit_path in sorted(DEFAULT_DIR.glob("*.sofaudit.json")):
        receipt = build_validation_receipt(audit_path)
        output = OUT / f"{receipt['audit']['audit_id']}.validation-receipt.json"
        output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        count += 1
    print(f"Wrote {count} migrated SOFAUDIT validation receipts to {OUT}")


if __name__ == "__main__":
    main()
