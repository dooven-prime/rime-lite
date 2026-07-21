"""Regenerate Paper XIII signature tables from validated .sofaudit files."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT = RESULTS / "signature_tables.md"
PAPER = HERE.parents[1] / "papers" / "paper13" / "Paper XIII.md"

DOMAIN_ROWS = {
    "GridWorld": [
        ("F1 action aliasing", "gridworld_f1"),
        ("F2 persistence loss", "gridworld_f2"),
        ("F3 forbidden edge", "gridworld_f3"),
        ("F4 bridge deletion", "gridworld_f4"),
        ("F5 deformation", "gridworld_f5"),
    ],
    "SIR": [
        ("F1 rate equalization", "sir_f1"),
        ("F2 missing edge", "sir_f2"),
        ("F3 forbidden direct", "sir_f3"),
        ("F4 rate distortion", "sir_f4"),
        ("F5 wall record", "sir_f5"),
    ],
    "Traffic": [
        ("F1 phase aliasing", "traffic_f1"),
        ("F2 missing phase", "traffic_f2"),
        ("F3 forbidden diagonal", "traffic_f3"),
        ("F4 timing distortion", "traffic_f4"),
        ("F5 wall record", "traffic_f5"),
    ],
    "Compiler IR": [
        ("F1 CFG/def-use aliasing", "compiler_f1"),
        ("F2 dead branch loss", "compiler_f2"),
        ("F3 spurious CFG edge", "compiler_f3"),
        ("F4 lost def-use", "compiler_f4"),
        ("F5 pass-pipeline wall", "compiler_f5"),
    ],
    "Network Routing (Appendix)": [
        ("F1 route aliasing", "network_f1"),
        ("F2 blocked prefix", "network_f2"),
        ("F3 forbidden route", "network_f3"),
        ("F4 metric distortion", "network_f4"),
        ("F5 ACL policy wall", "network_f5"),
    ],
}


def load(stem: str) -> dict:
    return json.loads((RESULTS / f"{stem}.sofaudit").read_text(encoding="utf-8"))


def mismatch(signature: dict, key: str) -> int:
    return int(signature[key]["total_mismatch"])


def frozen_tuple(signature: dict, *, path_dependent: bool) -> str:
    if path_dependent:
        return "path-dependent*"
    frozen = signature["frozen_disagreement"]
    values = (
        int(frozen["frozen_R1"]["delta"]),
        int(frozen["frozen_D_word"]["delta"]),
        int(frozen["frozen_D_lie"]["delta"]),
    )
    return "(" + ", ".join(f"{value:+d}" if value else "0" for value in values) + ")"


def row(label: str, stem: str) -> str:
    payload = load(stem)
    signature = payload["signature"]
    constraints = signature["constraint_violations"] or {"count": 0}
    response = signature["action_response_failure"] or {"total_large_deltas": 0}
    wall = signature["wall_record_mismatch"]
    wall_text = f"{wall['n_steps']} steps" if wall else "--"
    frozen_text = frozen_tuple(
        signature,
        path_dependent=(stem == "sir_f5"),
    )
    return (
        f"| {label} | {mismatch(signature, 'support_mismatch')} "
        f"| {mismatch(signature, 'bridge_word_mismatch')} "
        f"| {mismatch(signature, 'bridge_lie_mismatch')} "
        f"| {int(signature['depth_distortion']['total_mismatch'])} "
        f"| {frozen_text} | {int(constraints['count'])} "
        f"| {int(response['total_large_deltas'])} | {wall_text} |"
    )


def render() -> str:
    header = (
        "| Failure | Delta_supp | Delta_brw | Delta_brl | Delta_dep "
        "| Delta_frz=(R1,W,L) | Delta_cns | Delta_ctrl | Delta_wal |\n"
        "|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    )
    sections = []
    for domain, rows in DOMAIN_ROWS.items():
        body = "\n".join(row(label, stem) for label, stem in rows)
        sections.append(f"## {domain}\n\n{header}\n{body}")
    sections.append(
        "*SIR F5 has frozen-count delta (-2, -4, -4) at beta=0 and "
        "(0, 0, 0) for every sampled beta>0.*"
    )
    sections.append(
        "*Traffic F5 records a 21-step rate-order / trajectory-mismatch path; "
        "the sampled interval rho in [0.01, 100] excludes the rho -> 0 and "
        "rho -> infinity limit walls, so frozen-count deltas remain (0, 0, 0).*"
    )
    sections.append(
        "*Compiler IR F5 has zero single-snapshot mismatch but a 3-step pass-path "
        "wall record: the reference follows simplifycfg while the candidate remains "
        "fixed at the pre-simplifycfg snapshot.*"
    )
    sections.append(
        "*Network Routing is an appendix validation domain. F2 is an ACL edge-removal "
        "signature, while F3 has zero direct-support mismatch but nonzero bridge "
        "and constraint diagnostics.*"
    )
    return "\n\n".join(sections) + "\n"


def main() -> None:
    rendered = render()
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    paper = PAPER.read_text(encoding="utf-8")
    expected_rows = [
        line
        for line in rendered.splitlines()
        if line.startswith("| F") and not line.startswith("| Failure")
    ]
    missing = [line for line in expected_rows if line not in paper]
    if missing:
        for line in missing:
            print(f"MISSING FROM PAPER: {line}")
        raise SystemExit("Paper XIII signature tables differ from generated artifacts.")
    print(f"PASS {PAPER} contains all generated signature rows")


if __name__ == "__main__":
    main()
