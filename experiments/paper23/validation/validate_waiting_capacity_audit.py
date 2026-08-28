#!/usr/bin/env python3
"""Validate batch waiting--capacity profiles."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _bootstrap  # noqa: F401
from registry import payload_digest


def _fraction(value: dict[str, int] | None) -> Fraction | None:
    return None if value is None else Fraction(value["numerator"], value["denominator"])


def validate(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if payload.get("schema") != "rime.synchronizing-automata.waiting-capacity-tradeoff-audit.v1":
        errors.append("schema mismatch")
    unsigned = dict(payload)
    digest = unsigned.pop("content_sha256", None)
    if digest != payload_digest(unsigned):
        errors.append("content digest mismatch")
    for row in payload.get("rows", []):
        controls = row.get("Omega_epsilon_kappa", {})
        ranks = set(map(int, controls))
        if set(row.get("H", [])).intersection(row.get("U", [])):
            errors.append(f"H/U overlap at {row.get('id')}")
        if set(row.get("H", [])).union(row.get("U", [])) != ranks:
            errors.append(f"H/U partition mismatch at {row.get('id')}")
        for rank_key, control in controls.items():
            if _fraction(control["kappa_r"]) != Fraction(
                control["Omega_r"], control["epsilon_r"]
            ):
                errors.append(f"kappa mismatch at {row.get('id')} rank {rank_key}")
            chi = _fraction(control["statewise_ratio_chi_r"])
            kappa = _fraction(control["kappa_r"])
            if chi > kappa:
                errors.append(f"chi exceeds kappa at {row.get('id')} rank {rank_key}")
            u_value = Fraction(control["u_r"])
            h_value = _fraction(control["h_r"])
            if chi != max(u_value, h_value):
                errors.append(
                    f"statewise branch mismatch at {row.get('id')} rank {rank_key}"
                )
        tail_sum = Fraction(0)
        for index, tail in row.get("statewise_branch_tail_profile", {}).items():
            u_tail = Fraction(tail["unit_tail_u_bar_j"])
            h_tail = _fraction(tail["high_tail_h_bar_j"])
            chi_tail = _fraction(tail["chi_tail"])
            if chi_tail != max(u_tail, h_tail) or not tail["tail_identity_holds"]:
                errors.append(
                    f"tail branch mismatch at {row.get('id')} index {index}"
                )
            tail_sum += chi_tail
        phi_statewise = _fraction(row.get("phi_statewise"))
        combined = _fraction(row.get("combined_statewise_bound"))
        global_status = row.get("global_finite_bound_status")
        if global_status == "AVAILABLE":
            if phi_statewise is None or combined is None:
                errors.append(f"missing global envelope at {row.get('id')}")
            elif combined != phi_statewise or tail_sum != phi_statewise:
                errors.append(f"global tail sum mismatch at {row.get('id')}")
        elif phi_statewise is not None or combined is not None:
            errors.append(
                f"global envelope emitted for infinite active rank at {row.get('id')}"
            )
        depth = row.get("reset_depth")
        if depth is not None and _fraction(row["capacity_bound_slack"]) < 0:
            errors.append(f"capacity bound failed at {row.get('id')}")
        if depth is not None:
            statewise = phi_statewise
            kappa = _fraction(row.get("phi_kappa"))
            statewise_slack = _fraction(row.get("statewise_bound_slack"))
            if statewise is None or kappa is None or statewise > kappa:
                errors.append(f"invalid statewise envelope at {row.get('id')}")
            if statewise_slack != statewise - depth or statewise_slack < 0:
                errors.append(f"statewise bound failed at {row.get('id')}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    errors = validate(args.artifact)
    if errors:
        print(f"FAIL {args.artifact}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS WAITING-CAPACITY-AUDIT: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
