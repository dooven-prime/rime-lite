#!/usr/bin/env python3
"""Validate Paper XXXVI's exact-byte development closure and bounded control."""

from __future__ import annotations

import hashlib
import json
import re
from collections import deque
from itertools import combinations, permutations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper36"
MANIFEST = PACKAGE / "development-manifest.json"
RESULT = PACKAGE / "results" / "signed_lane_audit_v1.json"
PAPER = ROOT / "papers" / "paper36" / "Paper XXXVI.md"
EXPECTED_PATHS = (
    "papers/paper36/Paper XXXVI.md",
    "papers/paper36/references-v1.bib",
    "experiments/paper36/signed_lane_audit.py",
    "experiments/paper36/results/signed_lane_audit_v1.json",
    "experiments/paper36/seal_manifest.py",
    "experiments/paper36/validation/validate_package.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def text_bytes(path: Path) -> bytes:
    require(path.is_file(), f"missing file: {path}")
    data = path.read_bytes()
    require(b"\r" not in data, f"non-LF file: {path}")
    data.decode("utf-8")
    return data


def check_manifest() -> None:
    manifest = json.loads(text_bytes(MANIFEST))
    require(manifest.get("schema") == "rime.paper36.development-manifest.v1",
            "manifest schema mismatch")
    require(manifest.get("paper_id") == "PAPER36", "paper identity mismatch")
    require(manifest.get("status") == "DRAFT_PAPER_OWNED_CLOSURE",
            "manifest status mismatch")
    require(manifest.get("release_identity_claimed") is False,
            "draft closure claims release identity")
    require(manifest.get("validation_mode") == "LOCAL_CLOSURE_VERIFICATION",
            "manifest validation mode mismatch")
    require(manifest.get("digest_policy") == {
        "algorithm": "sha256",
        "scope": "exact_file_bytes",
        "path_resolution": "exact repository-relative path",
        "wildcards_allowed": False,
        "absolute_paths_allowed": False,
    }, "digest policy mismatch")
    artifacts = manifest.get("artifacts")
    require(isinstance(artifacts, list), "artifact list missing")
    require(tuple(row.get("path") for row in artifacts) == EXPECTED_PATHS,
            "manifest inventory differs from fixed package closure")
    for row in artifacts:
        relative = row["path"]
        path = Path(relative)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in relative,
                f"nonportable manifest path: {relative}")
        digest = hashlib.sha256(text_bytes(ROOT / path)).hexdigest()
        require(row.get("sha256") == digest, f"digest drift: {relative}")
    current = {
        path.relative_to(ROOT).as_posix()
        for path in PACKAGE.rglob("*")
        if path.is_file() and path != MANIFEST
        and "__pycache__" not in path.parts and ".lake" not in path.parts
        and path.suffix != ".pyc"
    }
    release_only = {
        "experiments/paper36/README.md",
        "experiments/paper36/release-environment.json",
        "experiments/paper36/release-manifest.json",
        "experiments/paper36/results/paper36_public_package_v1.validation-receipt.json",
        "experiments/paper36/validation/validate_release.py",
    }
    expected = {path for path in EXPECTED_PATHS if path.startswith("experiments/paper36/")}
    require(current - release_only == expected,
            f"package inventory drift: {sorted((current - release_only) ^ expected)}")


def check_source() -> None:
    manuscript = text_bytes(PAPER).decode("utf-8")
    require("C_{\\rm src}" in manuscript, "manuscript lacks C_src")
    require("C_0" not in manuscript and "C_{0}" not in manuscript,
            "manuscript uses stale C_0 notation")
    require("Theorem 3.3 (signed phase descent)" in manuscript,
            "signed quotient theorem missing")
    require("Theorem 4.3 (complete survivor frontier)" in manuscript,
            "survivor theorem missing")
    require("Theorem 5.1 (all-$g$ unsigned non-descent)" in manuscript,
            "matched obstruction theorem missing")
    require("does not claim that a sign bit is a universally minimal invariant"
            in manuscript, "minimality boundary missing")
    require("Paper XXXV" in manuscript and "[@paper35]" in manuscript,
            "direct predecessor attribution missing")
    require("## Computational Artifacts" in manuscript
            and "https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper36"
            in manuscript, "paper-owned artifact entry missing")
    tags = re.findall(r"\\tag\{([^}]+)\}", manuscript)
    require(len(tags) == len(set(tags)), "duplicate formula tags")
    require(len(re.findall(r"(?m)^\$\$$", manuscript)) % 2 == 0,
            "unbalanced displayed math")
    bibliography = text_bytes(ROOT / "papers" / "paper36" / "references-v1.bib").decode("utf-8")
    require("10.5281/zenodo.23085408" in bibliography,
            "Paper XXXV publication identity missing")
    cited = set(re.findall(r"(?<!\w)@([A-Za-z0-9_]+)", manuscript))
    entries = set(re.findall(r"(?m)^@\w+\{([^,]+),", bibliography))
    require(cited == entries, f"citation slice mismatch: {cited ^ entries}")


def ordinary(g: int, j: int) -> tuple[int, ...]:
    return tuple(j + t * g for t in range(5))


def action(
    g: int,
    targets: tuple[int, ...],
    signs: tuple[int, ...],
    phases: tuple[int, ...],
    punctured: tuple[int, ...],
) -> tuple[int, ...]:
    n = 5 * g
    values = [0] * n
    star = [t * g for t in range(1, 5)]
    for q, image_index in zip(star, punctured, strict=True):
        values[q] = star[image_index]
    for j, target in enumerate(targets, 1):
        for t, q in enumerate(ordinary(g, j)):
            values[q] = target + ((phases[j - 1] + t * signs[j - 1]) % 5) * g
    require(set(values[1:]) == set(range(1, n)), "invalid branch table")
    return tuple(values)


def step(
    state: tuple[int, ...], mapping: tuple[int, ...], r: int, g: int
) -> tuple[int, ...] | None:
    moved = [(mapping[q] + r) % (5 * g) for q in state]
    collapsed = tuple(g if q == 0 else q for q in moved)
    return collapsed if len(set(collapsed)) == 5 else None


def reach(
    start: tuple[int, ...], mapping: tuple[int, ...], g: int
) -> set[tuple[int, ...]]:
    found = {start}
    todo = deque([start])
    while todo:
        state = todo.popleft()
        for r in range(5 * g):
            child = step(state, mapping, r, g)
            if child is not None and child not in found:
                found.add(child)
                todo.append(child)
    return found


def signed_prediction(
    source: int, mapping: tuple[int, ...], g: int
) -> tuple[set[tuple[int, ...]], set[int]]:
    found = {(source, 1)}
    todo = deque([(source, 1)])
    boundary_signs: set[int] = set()
    while todo:
        j, current_sign = todo.popleft()
        images = tuple(mapping[q] for q in ordinary(g, j))
        target = images[0] % g
        difference = (images[1] - images[0]) % (5 * g)
        require(difference in (g, 4 * g), "branch is not locally dihedral")
        edge_sign = 1 if difference == g else -1
        boundary_signs.add(current_sign * edge_sign)
        for r in range(5 * g):
            next_lane = (target + r) % g
            if next_lane == 0:
                continue
            vertex = (next_lane, current_sign * edge_sign)
            if vertex not in found:
                found.add(vertex)
                todo.append(vertex)
    injections = {
        tuple(j + ((phase + sign * i) % 5) * g for i in range(5))
        for j, sign in found for phase in range(5)
    }
    return injections, boundary_signs


def survivors(
    states: set[tuple[int, ...]], mapping: tuple[int, ...], g: int
) -> dict[tuple[int, int], set[tuple[int, int, int]]]:
    observed = {pair: set() for pair in combinations(range(5), 2)}
    for state in states:
        for u in range(5 * g):
            placed = tuple((mapping[q] + u) % (5 * g) for q in state)
            pair = tuple(i for i in range(5) if placed[i] in (0, g))
            if len(pair) == 2:
                observed[pair].add(tuple(placed[i] for i in range(5) if i not in pair))
    return observed


def check_case(source: int, mapping: tuple[int, ...], g: int) -> frozenset[int]:
    actual = reach(ordinary(g, source), mapping, g)
    predicted, exit_signs = signed_prediction(source, mapping, g)
    require(actual == predicted, f"g={g}, C_src={source}: phase quotient differs")
    for j in range(1, g):
        image = tuple(mapping[q] for q in ordinary(g, j))
        for r in range(5 * g):
            should_enable = (image[0] + r) % g != 0
            for phase in range(5):
                rotated = ordinary(g, j)[phase:] + ordinary(g, j)[:phase]
                require((step(rotated, mapping, r, g) is not None) == should_enable,
                        f"g={g}, lane={j}, phase={phase}, r={r}: guard drift")
    actual_spectra = survivors(actual, mapping, g)
    for pair, placements in actual_spectra.items():
        candidate = next(
            (i for i in range(5) if set(pair) == {i, (i + 1) % 5}), None
        )
        expected: set[tuple[int, int, int]] = set()
        if candidate is not None:
            i = candidate
            remaining = tuple(q for q in range(5) if q not in pair)
            for sign in exit_signs:
                positions = tuple(
                    (((q - i) % 5 if sign == 1 else 1 - (q - i) % 5) * g) % (5 * g)
                    for q in range(5)
                )
                expected.add(tuple(positions[q] for q in remaining))
        require(placements == expected, f"g={g}, C_src={source}, F={pair}: survivor drift")
    return frozenset(exit_signs)


def unsigned(mapping: tuple[int, ...], g: int) -> tuple[tuple, tuple]:
    edges = []
    exits = []
    full_kernel = {t * g for t in range(5)}
    for j in range(1, g):
        lane = ordinary(g, j)
        for r in range(5 * g):
            image = step(lane, mapping, r, g)
            if image is not None:
                edges.append((j, r, tuple(sorted(image))))
            if {(mapping[q] + r) % (5 * g) for q in lane} == full_kernel:
                exits.append((j, r))
    return tuple(edges), tuple(exits)


def check_matched(g: int) -> dict[str, object]:
    lane_targets = tuple(range(1, g))
    punctured = (0, 1, 2, 3)
    phases = (0,) * (g - 1)
    id_map = action(g, lane_targets, (1,) * (g - 1), phases, punctured)
    reflection = action(g, lane_targets, (-1,) * (g - 1), phases, punctured)
    require(unsigned(id_map, g) == unsigned(reflection, g), "unsigned W3 graph drift")
    plus = survivors(reach(ordinary(g, 1), id_map, g), id_map, g)
    minus = survivors(reach(ordinary(g, 1), reflection, g), reflection, g)
    edges = {tuple(sorted((i, (i + 1) % 5))) for i in range(5)}
    require(set(plus) == set(minus), "W3 candidate pair scope differs")
    require(
        all((len(plus[f]), len(minus[f])) == ((1, 2) if f in edges else (0, 0))
            for f in plus),
        "W3 survivor spectra do not separate as declared",
    )
    return {
        "unsigned_labelled_graph_equal": True,
        "same_fused_pairs": True,
        "survivors_per_consecutive_pair": {"identity": 1, "reflection": 2},
    }


def independent_replay() -> list[dict[str, object]]:
    rows = []
    for g in (2, 3):
        counts = {"positive_only": 0, "both": 0}
        branch_count = 0
        cases = 0
        ids = tuple(range(1, g))
        for targets in permutations(ids):
            for signs in product((-1, 1), repeat=g - 1):
                for phases in product(range(5), repeat=g - 1):
                    for punctured in permutations(range(4)):
                        branch_count += 1
                        mapping = action(g, targets, signs, phases, punctured)
                        for source in ids:
                            cases += 1
                            exits = check_case(source, mapping, g)
                            if exits == frozenset({1}):
                                counts["positive_only"] += 1
                            else:
                                require(exits == frozenset({-1, 1}),
                                        "unexpected exit-sign class")
                                counts["both"] += 1
        rows.append({
            "g": g,
            "n": 5 * g,
            "delta": g,
            "branch_count": branch_count,
            "source_cases": cases,
            "exit_sign_cases": counts,
            "matched_identity_reflection": check_matched(g),
        })
    return rows


def check_result() -> tuple[int, int]:
    record = json.loads(text_bytes(RESULT))
    require(record.get("schema") == "rime.paper36.signed-lane-audit.v1",
            "result schema mismatch")
    require(record.get("status") == "BOUNDED_EXHAUSTIVE_G2_G3_CONSISTENCY_CONTROL",
            "result status mismatch")
    require(record.get("scope") == {
        "g_values": [2, 3],
        "branch_family": "all ordinary-lane permutations, signs, phases, and punctured-lane permutations",
        "source_policy": "every complete ordinary lane as C_src, five labels in positive order",
        "word_length_budget": None,
    }, "finite scope drift")
    require(record.get("checks") == [
        "full-support guard",
        "reachable signed phase classes",
        "source-addressed survivor spectra",
        "matched unsigned labelled graph and terminal spectra",
    ], "check inventory drift")
    require(record.get("claim_boundary") ==
            "Bounded exact consistency control; manuscript proofs own all-g theorems.",
            "evidence-status drift")
    expected = independent_replay()
    require(record.get("domains") == expected, "finite result differs from independent replay")
    require(
        [(row["branch_count"], row["source_cases"], row["exit_sign_cases"])
         for row in expected] == [
            (240, 240, {"positive_only": 120, "both": 120}),
            (4800, 9600, {"positive_only": 2400, "both": 7200}),
        ],
        "fixed branch/source coverage drift",
    )
    return sum(row["branch_count"] for row in expected), sum(
        row["source_cases"] for row in expected
    )


def main() -> None:
    check_manifest()
    check_source()
    branches, cases = check_result()
    print(f"PASS: Paper XXXVI development closure and bounded control "
          f"({branches} branches, {cases} source cases)")


if __name__ == "__main__":
    main()
