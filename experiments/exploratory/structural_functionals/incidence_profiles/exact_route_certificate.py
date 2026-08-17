#!/usr/bin/env python
"""Create a theorem-bound route certificate from a numerical profile.

The output is intentionally conditional: it proves what remains once exact
carrier commutation/support hypotheses are supplied, and never upgrades a
floating-point SVD into an exact identity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from incidence_profiles import PHYSICAL_CARRIERS, source_artifact, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    counts = profile["counts"]
    residuals = profile["sector_frame"]["physical_carrier_commutator_residuals"]
    mechanisms = counts["zero_mechanism_counts"]
    forced = mechanisms.get("physical_carrier_forced", 0)
    overlapping = mechanisms.get("within_carrier_image_kernel", 0)
    conflicts = mechanisms.get("numerical_cancellation_or_threshold_conflict", 0)
    output = {
        "schema": "rime.exact-route-certificate.v1",
        "claim_status": "Computational Certificate",
        "certificate_kind": "conditional_exact_route_promotion",
        "source_profile": args.profile.as_posix(),
        "provenance": {
            "source_artifacts": [
                source_artifact(Path(__file__)),
                source_artifact(Path(__file__).with_name("incidence_profiles.py")),
                source_artifact(args.profile),
            ]
        },
        "statement": (
            "Under exact sector-projector reduction, exact operative-matrix "
            "reduction, and exact support-mask hypotheses, "
            "all physical-carrier-forced routes satisfy AB=0 exactly."
        ),
        "theorem": "Carrier-Forced Routed Incidence (THEOREMS.md, Theorem 1)",
        "observed_route_counts": {
            "physical_carrier_forced": forced,
            "within_carrier_image_kernel": overlapping,
            "numerical_cancellation_or_threshold_conflict": conflicts,
        },
        "carrier_labels": list(PHYSICAL_CARRIERS),
        "numerical_hypothesis_diagnostics": {
            "commutator_residuals": residuals,
            "max_commutator_residual": max(residuals.values(), default=0.0),
            "warning": "Residuals do not establish exact commutation.",
        },
        "upgrade_requirements": [
            "replace numerical sector bases with exact algebraic projectors",
            "verify [P_i,C_b]=0 exactly for every sector and carrier",
            "verify [X_g,C_b]=0 exactly for every operative generator and carrier",
            "verify each declared carrier support mask exactly",
            "retain within-carrier routes as image-kernel certificates, not carrier-forced routes",
        ],
        "verified_conditional_conclusion": forced > 0 and overlapping == 0 and conflicts == 0,
    }
    write_json(args.output, output)


if __name__ == "__main__":
    main()
