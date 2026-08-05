"""Paper XI registry wall-density audit.

Claim status:
    - Registry/taxonomy evidence for Paper XI.
    - A first-pass density sample over the current 15 Paper XI taxonomy species.
    - Not a theorem and not a population estimate for all possible SOFs.

Wall types follow the Paper XI taxonomy:
    A = collision / spectral
    B = repair
    C = terminal-side / absorbing
    D = plateau / rate
    E = nonsmooth / discrete
    F = bridge / incidence
"""

from __future__ import annotations

import sys
from collections import OrderedDict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


WALL_TYPES = OrderedDict(
    [
        ("A", "Collision/spectral"),
        ("B", "Repair"),
        ("C", "Terminal-side/absorbing"),
        ("D", "Plateau/rate"),
        ("E", "Nonsmooth/discrete"),
        ("F", "Bridge/incidence"),
    ]
)


SPECIES = [
    ("Rubik QT/HT", ["A", "B", "F"]),
    ("Rubik Type III/IV wild", ["F"]),
    ("Synthetic Type III/IV", ["F"]),
    ("Xu ridge model", ["D"]),
    ("Mechanism-separated SOF", ["D"]),
    ("Engineered near-threshold", ["B"]),
    ("Finite spectral triple", []),
    ("Control Kalman", ["B"]),
    ("PDE subdomain", []),
    ("Combinatorial coloring", []),
    ("Barrier option GBM", ["C"]),
    ("Quantum Clifford+CNOT", ["B"]),
    ("Markov absorbing", ["C"]),
    ("Graph P3/C4", ["E"]),
    ("NN Transformer activation", ["B", "E"]),
]


def compute_density(
    species: list[tuple[str, list[str]]] = SPECIES,
) -> dict[str, dict[str, object]]:
    n_species = len(species)
    density: dict[str, dict[str, object]] = {}
    for wall_type, name in WALL_TYPES.items():
        matches = [species_name for species_name, walls in species if wall_type in walls]
        density[wall_type] = {
            "name": name,
            "count": len(matches),
            "density": len(matches) / n_species,
            "examples": matches,
        }
    return density


def print_table() -> None:
    n_species = len(SPECIES)
    density = compute_density(SPECIES)

    print(f"Wall density over {n_species} Paper XI taxonomy species:")
    print(f"  {'Type':>6s}  {'Name':<25s}  {'Count':>5s}  {'Density':>7s}  Examples")
    print(f"  {'-' * 6}  {'-' * 25}  {'-' * 5}  {'-' * 7}  {'-' * 40}")

    for wall_type, row in density.items():
        examples = ", ".join(row["examples"][:3])
        extra = row["count"] - 3
        if extra > 0:
            examples += f"... (+{extra})"
        print(
            f"  {wall_type:>6s}  {row['name']:<25s}  "
            f"{row['count']:>5d}  {row['density']:>6.1%}  {examples}"
        )

    no_wall = sum(1 for _, walls in SPECIES if not walls)
    print()
    print(
        f"  No wall type registered: {no_wall}/{n_species} "
        "(static/structural species)"
    )


if __name__ == "__main__":
    print_table()
