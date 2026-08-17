#!/usr/bin/env python
"""Emit exact combinatorial and conditional algebraic certificates."""
from fractions import Fraction
from pathlib import Path

from incidence_profiles import (
    REPO_ROOT,
    Qsqrt5,
    axis_conjugacy_certificate,
    lagrange_projector_certificate,
    named_family,
    source_artifact,
    write_json,
)


def main():
    output = Path("results/exact_certificates")
    conjugacy = axis_conjugacy_certificate(
        named_family("drop_axis0_ht"), named_family("drop_axis2_ht")
    )
    conjugacy["provenance"] = {
        "source_artifacts": [
            source_artifact(Path(__file__)),
            source_artifact(Path(__file__).with_name("incidence_profiles.py")),
            source_artifact(REPO_ROOT / "rime" / "base.py"),
            source_artifact(REPO_ROOT / "rime" / "cube.py"),
            source_artifact(REPO_ROOT / "rime" / "cubie.py"),
        ]
    }
    write_json(output / "drop_axis0_vs_axis2_ht.json", conjugacy)

    # Exact candidate spectrum of the n=8 family averaging operator from the
    # registered CCS expressions. This verifies the interpolation identities;
    # it intentionally does not claim that a numerical eigensolver proved the
    # exact spectrum.
    n8_eigenvalues = [
        Qsqrt5(1),
        Qsqrt5(Fraction(5, 8), Fraction(1, 8)),
        Qsqrt5(Fraction(3, 4)),
        Qsqrt5(Fraction(1, 2)),
        Qsqrt5(Fraction(5, 8), Fraction(-1, 8)),
        Qsqrt5(Fraction(1, 4)),
        Qsqrt5(0),
    ]
    lagrange = lagrange_projector_certificate(n8_eigenvalues)
    lagrange["provenance"] = {
        "source_artifacts": [
            source_artifact(Path(__file__)),
            source_artifact(Path(__file__).with_name("incidence_profiles.py")),
        ]
    }
    write_json(output / "n8_lagrange_projectors.json", lagrange)


if __name__ == "__main__":
    main()
