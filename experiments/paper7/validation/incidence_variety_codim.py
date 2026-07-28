"""Paper VII v2: exact dimension tables for matrix-composition incidence.

For A in C^{m x n} and B in C^{n x p}, the closed zero-product locus is

    Z = {(A, B): AB = 0}.

The nonzero-factor locus Z^x = Z intersect {A != 0, B != 0} is constructible.
This script evaluates the exact integer dimension and codimension formulas for
its fixed-rank locally closed strata.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import hashlib
import json
import platform
from pathlib import Path


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
JSON_PATH = RESULTS_DIR / "incidence_geometry.json"
TEXT_PATH = RESULTS_DIR / "incidence_geometry.txt"


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ambient_dimension(m: int, n: int, p: int) -> int:
    return m * n + n * p


def fixed_a_rank_dimension(m: int, n: int, p: int, r: int) -> int:
    """Dimension for rank(A)=r and AB=0, with B unrestricted."""
    if not 0 <= r <= min(m, n):
        raise ValueError("inadmissible rank(A)")
    return r * (m + n - r) + p * (n - r)


def fixed_a_rank_codimension(m: int, n: int, p: int, r: int) -> int:
    return ambient_dimension(m, n, p) - fixed_a_rank_dimension(m, n, p, r)


def fixed_double_rank_dimension(
    m: int,
    n: int,
    p: int,
    r: int,
    s: int,
) -> int:
    """Dimension for rank(A)=r, rank(B)=s, and AB=0."""
    if not 0 <= r <= min(m, n):
        raise ValueError("inadmissible rank(A)")
    if not 0 <= s <= min(n - r, p):
        raise ValueError("inadmissible rank(B) under im(B) subset ker(A)")
    rank_a_base = r * (m + n - r)
    rank_s_maps_into_kernel = s * (n - r + p - s)
    return rank_a_base + rank_s_maps_into_kernel


def fixed_double_rank_codimension(
    m: int,
    n: int,
    p: int,
    r: int,
    s: int,
) -> int:
    return ambient_dimension(m, n, p) - fixed_double_rank_dimension(
        m, n, p, r, s
    )


def fixed_double_rank_relative_codimension(r: int, s: int) -> int:
    """Codimension inside the ambient rank-(r,s) matrix-pair stratum."""
    return r * s


def admissible_type_iv_a_ranks(m: int, n: int) -> range:
    """Ranks with A != 0 and ker(A) != 0."""
    return range(1, min(m, n - 1) + 1)


def type_iv_codimension(m: int, n: int, p: int) -> tuple[int, list[int]]:
    rows = [
        (fixed_a_rank_codimension(m, n, p, r), r)
        for r in admissible_type_iv_a_ranks(m, n)
    ]
    if not rows:
        raise ValueError("the nonzero-factor incidence locus is empty")
    minimum = min(value for value, _ in rows)
    minimizers = [r for value, r in rows if value == minimum]
    return minimum, minimizers


def configuration_record(m: int, n: int, p: int, label: str) -> dict:
    rank_rows = []
    double_rank_rows = []
    for r in admissible_type_iv_a_ranks(m, n):
        rank_rows.append(
            {
                "rank_a": r,
                "dimension": fixed_a_rank_dimension(m, n, p, r),
                "codimension": fixed_a_rank_codimension(m, n, p, r),
            }
        )
        for s in range(1, min(n - r, p) + 1):
            double_rank_rows.append(
                {
                    "rank_a": r,
                    "rank_b": s,
                    "dimension": fixed_double_rank_dimension(
                        m, n, p, r, s
                    ),
                    "codimension": fixed_double_rank_codimension(
                        m, n, p, r, s
                    ),
                    "relative_codimension_in_rank_pair_stratum": (
                        fixed_double_rank_relative_codimension(r, s)
                    ),
                }
            )
    codimension, minimizers = type_iv_codimension(m, n, p)
    return {
        "label": label,
        "m": m,
        "n": n,
        "p": p,
        "ambient_dimension": ambient_dimension(m, n, p),
        "type_iv_codimension": codimension,
        "minimizing_rank_a": minimizers,
        "fixed_rank_a_strata": rank_rows,
        "fixed_double_rank_strata": double_rank_rows,
    }


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    configurations = [
        configuration_record(d, d, d, f"square_d_{d}")
        for d in (2, 3, 4, 5, 6, 8, 10)
    ]
    configurations.extend(
        [
            configuration_record(3, 2, 3, "synthetic_3_2_3"),
            configuration_record(2, 3, 2, "small_asymmetric"),
            configuration_record(3, 4, 3, "medium_asymmetric"),
            configuration_record(5, 6, 5, "large_asymmetric"),
            configuration_record(4, 2, 4, "narrow_intermediate"),
            configuration_record(2, 5, 2, "wide_intermediate"),
        ]
    )

    payload = {
        "schema": "paper7.incidence-geometry.v2",
        "field": "complex",
        "closed_locus": "Z={(A,B):AB=0}",
        "constructible_locus": "Zx=Z intersect {A!=0,B!=0}",
        "formulas": {
            "fixed_rank_a_dimension": "r(m+n-r)+p(n-r)",
            "fixed_rank_a_codimension": "(m-r)(n-r)+pr",
            "fixed_double_rank_dimension": (
                "r(m+n-r)+s(n-r+p-s)"
            ),
            "fixed_double_rank_relative_codimension": "rs",
            "admissible_rank_a": "1<=r<=min(m,n-1)",
            "admissible_rank_b": "1<=s<=min(n-r,p)",
        },
        "runtime": {
            "python": platform.python_version(),
            "script_sha256": source_sha256(Path(__file__)),
        },
        "configurations": configurations,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "Paper VII v2 incidence geometry",
        "=" * 72,
        "Z={(A,B):AB=0} is closed; Zx=Z intersect {A!=0,B!=0} is constructible.",
        "fixed rank(A)=r: codim=(m-r)(n-r)+pr",
        "fixed ranks (r,s): dim=r(m+n-r)+s(n-r+p-s)",
        "relative codim inside the rank-(r,s) pair stratum: rs",
        "",
    ]
    for record in configurations:
        lines.append(
            f"{record['label']}: ambient={record['ambient_dimension']}, "
            f"codim={record['type_iv_codimension']}, "
            f"rankA={record['minimizing_rank_a']}"
        )
    TEXT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nJSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
