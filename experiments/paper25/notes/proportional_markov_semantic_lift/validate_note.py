#!/usr/bin/env python3
"""Validate the Paper XXV companion-note ownership and claim boundary."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PACKAGE = Path(__file__).resolve().parent
NOTE = PACKAGE / "NOTE.md"
NOTE_PATH = "experiments/paper25/notes/proportional_markov_semantic_lift/NOTE.md"


def main() -> None:
    assert NOTE.is_file()
    text = NOTE.read_text(encoding="utf-8")
    assert "owned by Paper XXV" in text
    assert "no independent paper" in text
    claims = json.loads((PACKAGE / "claim-surface-map.json").read_text(encoding="utf-8"))
    assert claims["schema"] == "rime.paper25.companion-note.claim-surface.v1"
    assert claims["paper_id"] == "PAPER25_COMPANION_NOTE"
    assert claims["supplement_id"] == "PAPER25-S1"
    assert claims["release_identity_claimed"] is False
    assert claims["manuscript"] == NOTE_PATH

    by_id = {claim["id"]: claim for claim in claims["claims"]}
    assert by_id["A4_HITTING_TIME_PROPORTIONAL_LIFT"]["status"] == "THEOREM"
    assert by_id["A5_STATIONARY_MASS_PROPORTIONAL_LIFT"]["status"] == "THEOREM"
    assert by_id["ABSOLUTE_GAP_NONMONOTONICITY"]["status"] == "EXPLICIT_NEGATIVE_BOUNDARY"
    assert by_id["SUBSET_TO_PAIR_COMPARISON"]["status"] == "OPEN"

    proof = (ROOT / by_id["A5_STATIONARY_MASS_PROPORTIONAL_LIFT"]["proof"]).read_text(encoding="utf-8")
    assert "stationary" in proof.lower()
    assert "regeneration" in proof.lower()

    assert "Stationary-Mass Local Proof Audit" in text
    assert "Supplementary Technical Note S1" in text
    assert "P_{\\rm shortcut}" in text
    assert "P_{\\rm trap}" in text
    assert "\\frac{180}{67}" in text
    assert "\\frac{100}{7}" in text
    assert "N'D" in text
    assert "\\frac{d\\pi_j}{da}" in text
    assert "not independent validation" in text
    private_prefix = "experiments/" + "exploratory"
    assert private_prefix not in text

    print("PASS PAPER25-COMPANION-NOTE")


if __name__ == "__main__":
    main()
