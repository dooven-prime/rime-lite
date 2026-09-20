#!/usr/bin/env python3
"""Refresh declared Paper XXVII manifest hashes and closure classes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "experiments" / "paper27" / "release-manifest.json"

CLOSURE_CLASSES = [
    "normative-manuscript-build",
    "theorem-facing-computational",
    "public-package-documentation",
]

NORMATIVE_PATHS = {
    "figures/paper27/fig1_entry_relation_interface.png",
    "figures/paper27/render.py",
    "papers/paper27/Paper XXVII.md",
    "papers/paper27/paper27_arxiv.pdf",
    "papers/paper27/references-v1.bib",
}

DOCUMENTATION_ROLES = {
    "evidence-readme",
}

EXCLUDED_ROLES = {
    "claim-surface-map",
    "paper-readme",
    "reader-release-manifest",
    "related-work-audit",
    "result-inventory",
    "theorem-dependency-audit",
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def closure_class(path: str, role: str) -> str:
    if path in NORMATIVE_PATHS:
        return "normative-manuscript-build"
    if role in DOCUMENTATION_ROLES:
        return "public-package-documentation"
    return "theorem-facing-computational"


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["schema"] = "rime.paper27.release-manifest.v3"
    payload["release_version"] = "1.0"
    payload["status"] = "RELEASE_CANDIDATE"
    payload["release_identity_claimed"] = False
    payload.pop("generated_at", None)
    payload.pop("excluded_from_release_identity", None)
    payload["release_candidate_date"] = "2026-09-20"
    payload["excluded_from_package_inventory"] = [
        "experiments/paper27/results/paper27_public_package_v1.validation-receipt.json",
        "**/__pycache__/**",
        "**/*.pyc",
    ]
    payload["closure_policy"] = {
        "classes": CLOSURE_CLASSES,
        "release_identity_classes": CLOSURE_CLASSES[:2],
        "package_inventory_classes": CLOSURE_CLASSES,
        "note": (
            "Public package documentation is integrity-checked but excluded "
            "from the release identity."
        ),
    }

    rows_by_path = {
        row["path"]: row
        for row in payload["artifacts"]
        if row["role"] not in EXCLUDED_ROLES and (ROOT / row["path"]).is_file()
    }
    additions = {
        "experiments/paper27/README.md": "evidence-readme",
        "experiments/paper27/results/single_defect_n7_extremal_carrier_input_v1.json": "theorem-input",
        "experiments/paper27/validation/refresh_release_manifest.py": "release-tool",
        "figures/paper27/fig1_entry_relation_interface.png": "reader-figure",
        "figures/paper27/render.py": "figure-renderer",
        "papers/paper27/paper27_arxiv.pdf": "reader-pdf",
        "papers/paper27/references-v1.bib": "bibliography",
    }
    for path, role in additions.items():
        rows_by_path.setdefault(path, {"path": path, "role": role})

    refreshed = []
    for path_text, row in sorted(rows_by_path.items()):
        if "\\" in path_text:
            raise SystemExit(f"manifest path is not POSIX-normalized: {path_text}")
        path = ROOT / path_text
        if not path.is_file():
            raise SystemExit(f"declared manifest file is missing: {path_text}")
        refreshed.append(
            {
                "role": row["role"],
                "closure_class": closure_class(path_text, row["role"]),
                "path": path_text,
                "sha256": sha256(path),
            }
        )
    payload["artifacts"] = refreshed
    MANIFEST.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    counts = {
        name: sum(row["closure_class"] == name for row in refreshed)
        for name in CLOSURE_CLASSES
    }
    print(json.dumps({"artifacts": len(refreshed), "classes": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
