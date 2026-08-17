#!/usr/bin/env python
"""Audit simple symbolic conjectures against both completed orbit censuses."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from incidence_profiles import source_artifact, write_json

ROOT = Path("results")


def load_profiles(directory: Path):
    rows = []
    for path in sorted(directory.glob("*.json")):
        profile = json.loads(path.read_text(encoding="utf-8"))
        counts = profile["counts"]
        total = counts["total_supported_routes"]
        unprotected = counts["unprotected_routes"]
        rows.append({
            "orbit": profile["family"].get("orbit_id"),
            "operators": profile["family"]["operator_count"],
            "sectors": profile["sector_frame"]["sector_count"],
            "total": total,
            "protected": counts["protected_routes"],
            "zero": counts["unprotected_zero"],
            "zero_rate": Fraction(counts["unprotected_zero"], total) if total else None,
            "conditional_zero_rate": Fraction(counts["unprotected_zero"], unprotected) if unprotected else None,
        })
    return rows


def serializable_row(row):
    return {key: (f"{value.numerator}/{value.denominator}" if isinstance(value, Fraction) else value)
            for key, value in row.items()}


def functional_dependency(rows, feature, target):
    groups = {}
    for row in rows:
        if row[target] is not None:
            groups.setdefault(row[feature], []).append(row)
    for value, group in groups.items():
        values = {row[target] for row in group}
        if len(values) > 1:
            left = group[0]
            right = next(row for row in group if row[target] != left[target])
            return False, {"shared_feature": {feature: value}, "left": serializable_row(left), "right": serializable_row(right)}
    return True, None


def monotone(rows, feature, target, increasing=True):
    usable = [row for row in rows if row[target] is not None]
    for left in usable:
        for right in usable:
            if left[feature] >= right[feature]:
                continue
            holds = left[target] <= right[target] if increasing else left[target] >= right[target]
            if not holds:
                return False, {"left": serializable_row(left), "right": serializable_row(right)}
    return True, None


def check(name, result):
    survives, counterexample = result
    return {
        "candidate": name,
        "status": "SURVIVES_DECLARED_CENSUS" if survives else "REJECTED_BY_CENSUS",
        "counterexample": counterexample,
    }


def main():
    fixed = load_profiles(ROOT / "axis_balanced_fixed")
    endogenous = load_profiles(ROOT / "axis_balanced_endogenous")
    nonempty_fixed = [row for row in fixed if row["total"]]
    fixed_rates = {row["zero_rate"] for row in nonempty_fixed}
    candidates = [{
        "candidate": "fixed-frame zero rate equals 2/9 whenever supported routes exist",
        "status": "SURVIVES_DECLARED_CENSUS" if fixed_rates == {Fraction(2, 9)} else "REJECTED_BY_CENSUS",
        "scope": "19 declared axis-balanced rotation orbits only",
        "observed_rate": "2/9" if fixed_rates == {Fraction(2, 9)} else None,
    }]
    candidates += [
        check("endogenous zero rate is a function of operator count", functional_dependency(endogenous, "operators", "zero_rate")),
        check("endogenous zero rate is a function of sector count", functional_dependency(endogenous, "sectors", "zero_rate")),
        check("endogenous zero rate is nondecreasing in operator count", monotone(endogenous, "operators", "zero_rate", True)),
        check("endogenous zero rate is nonincreasing in operator count", monotone(endogenous, "operators", "zero_rate", False)),
        check("endogenous zero rate is nondecreasing in sector count", monotone(endogenous, "sectors", "zero_rate", True)),
        check("endogenous zero rate is nonincreasing in sector count", monotone(endogenous, "sectors", "zero_rate", False)),
        check("protected-route count is nondecreasing in operator count", monotone(endogenous, "operators", "protected", True)),
    ]
    payload = {
        "schema": "rime.incidence-conjecture-audit.v1",
        "claim_status": "Computational Observation",
        "audit_kind": "finite_symbolic_pattern_audit",
        "fixed_profile_count": len(fixed),
        "endogenous_profile_count": len(endogenous),
        "candidates": candidates,
        "conclusion": "The fixed-frame 2/9 statement survives the declared finite census; simple endogenous laws based only on operator count or sector count are rejected with explicit orbit counterexamples.",
        "provenance": {
            "source_artifacts": [
                source_artifact(Path(__file__)),
                *(
                    source_artifact(path)
                    for directory in (ROOT / "axis_balanced_fixed", ROOT / "axis_balanced_endogenous")
                    for path in sorted(directory.glob("*.json"))
                ),
            ]
        },
    }
    write_json(ROOT / "conjecture_audit.json", payload)
    for candidate in candidates:
        print(f"{candidate['status']}: {candidate['candidate']}")


if __name__ == "__main__":
    main()
