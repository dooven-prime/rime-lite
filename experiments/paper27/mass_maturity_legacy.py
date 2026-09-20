#!/usr/bin/env python3
"""Exact finite mass-transport primitives used by the maturity probes.

The mass of a transformation image is the vector ``mu(x)=|t^-1(x)|``.
Letters push this vector forward.  All routines in this module use exact
integer arithmetic and retain the endpoint-shortest convention: a first exit
is reached by a shortest rank-preserving prefix followed by one strict drop.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import deque
from math import comb, factorial
from pathlib import Path
from typing import Iterable, Sequence

Mass = tuple[int, ...]
Transformation = tuple[int, ...]
Letters = tuple[Transformation, ...]


def pushforward_mass(mass: Mass, letter: Transformation) -> Mass:
    """Push ``mass`` through a deterministic transformation."""
    if len(mass) != len(letter):
        raise ValueError("mass and letter must have the same state count")
    out = [0] * len(mass)
    for source, value in enumerate(mass):
        out[letter[source]] += value
    return tuple(out)


def mass_rank(mass: Mass) -> int:
    return sum(value > 0 for value in mass)


def mass_kernel_mass(mass: Mass) -> int:
    return sum(comb(value, 2) for value in mass)


def mass_l2_sq(mass: Mass) -> int:
    return sum(value * value for value in mass)


def rank_debt(rank: int, n: int) -> int:
    if not 1 <= rank <= n:
        raise ValueError("rank must lie between 1 and n")
    if rank == n:
        return 0
    return (n - rank - 1) * (rank - 1)


def mass_potential(mass: Mass, n: int, *, use_rank_debt: bool = True) -> int:
    rank = mass_rank(mass)
    value = 2 * (comb(n, 2) - mass_kernel_mass(mass)) - (rank - 1)
    return value - rank_debt(rank, n) if use_rank_debt else value


def mass_deadline(mass: Mass, n: int, *, use_rank_debt: bool = True) -> int:
    return (n - 1) ** 2 - mass_potential(mass, n, use_rank_debt=use_rank_debt)


def simplified_deadline(mass: Mass, n: int) -> int:
    """Closed-form checkpoint deadline, including the initial endpoint."""
    rank = mass_rank(mass)
    if rank == n:
        return 0
    return mass_l2_sq(mass) + (rank - 1) * (n - rank) - 2 * n + 1


def _reconstruct(target: Mass, parent: dict[Mass, tuple[Mass, int]]) -> tuple[int, ...]:
    word: list[int] = []
    while target in parent:
        target, letter = parent[target]
        word.append(letter)
    return tuple(reversed(word))


def reachable_masses(letters: Letters, n: int) -> set[Mass]:
    initial = (1,) * n
    reached = {initial}
    queue = deque([initial])
    while queue:
        mass = queue.popleft()
        for letter in letters:
            target = pushforward_mass(mass, letter)
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def first_exit_corridors(mass: Mass, letters: Letters) -> dict:
    """Return all shortest first strict-drop endpoints from ``mass``.

    Endpoints are coalesced by target mass.  The returned word is a shortest
    representative for that endpoint and its prefix is rank-preserving.
    """
    source_rank = mass_rank(mass)
    if source_rank <= 1:
        return {"omega": 0, "exits": []}
    seen: dict[Mass, int] = {mass: 0}
    parent: dict[Mass, tuple[Mass, int]] = {}
    queue = deque([mass])
    shortest: int | None = None
    exits: dict[Mass, dict] = {}
    while queue:
        current = queue.popleft()
        depth = seen[current]
        if shortest is not None and depth >= shortest:
            continue
        for letter_index, letter in enumerate(letters):
            target = pushforward_mass(current, letter)
            target_rank = mass_rank(target)
            length = depth + 1
            if target_rank < source_rank:
                if shortest is None:
                    shortest = length
                if length == shortest and target not in exits:
                    exits[target] = {
                        "target": target,
                        "length": length,
                        "target_rank": target_rank,
                        "letter": letter_index,
                        "word": _reconstruct(current, parent) + (letter_index,),
                    }
                continue
            if target not in seen:
                seen[target] = length
                parent[target] = (current, letter_index)
                queue.append(target)
    return {"omega": shortest or 0, "exits": sorted(exits.values(), key=lambda row: (row["length"], row["target"], row["letter"]))}


def first_exit_profiles(letters: Letters, n: int) -> dict[Mass, dict]:
    return {
        mass: first_exit_corridors(mass, letters)
        for mass in reachable_masses(letters, n)
        if mass_rank(mass) > 1
    }


def available_r1_reserves(letters: Letters, n: int) -> dict[Mass, int]:
    reserve: dict[Mass, int] = {}
    for mass, profile in first_exit_profiles(letters, n).items():
        tau = simplified_deadline(mass, n)
        best = 0
        for exit_row in profile["exits"]:
            target = exit_row["target"]
            best = max(best, simplified_deadline(target, n) - tau - exit_row["length"])
        reserve[mass] = max(0, best)
    return reserve


def word_ledger(word: Sequence[int], letters: Letters, n: int) -> dict:
    mass = (1,) * n
    steps = []
    for length, letter_index in enumerate(word, start=1):
        target = pushforward_mass(mass, letters[letter_index])
        source_rank = mass_rank(mass)
        target_rank = mass_rank(target)
        bank = simplified_deadline(target, n) - length
        steps.append({
            "length": length,
            "letter": letter_index,
            "source": list(mass),
            "target": list(target),
            "source_rank": source_rank,
            "target_rank": target_rank,
            "support_drop": source_rank - target_rank,
            "is_checkpoint": target_rank < source_rank,
            "deadline": simplified_deadline(target, n),
            "bank_w": bank,
        })
        mass = target
    checkpoints = [row["bank_w"] for row in steps if row["is_checkpoint"]]
    return {
        "word": list(word),
        "word_length": len(word),
        "final_mass": list(mass),
        "is_reset": mass_rank(mass) == 1,
        "minimum_checkpoint_bank": min(checkpoints, default=0),
        "steps": steps,
    }


def available_r1_search(letters: Letters, n: int, *, capture: bool = False) -> dict:
    reserve = available_r1_reserves(letters, n)
    initial = (1,) * n
    distance = {initial: 0}
    parent: dict[Mass, tuple[Mass, int]] = {}
    queue = deque([initial])
    while queue:
        mass = queue.popleft()
        length = distance[mass]
        if mass_rank(mass) == 1:
            word = _reconstruct(mass, parent) if capture else None
            return {"found": True, "semantics": "AVAILABLE_R1", "word": list(word) if word is not None else None, "word_length": length, "reserve_state_count": len(reserve), "ledger": word_ledger(word, letters, n) if word is not None else None}
        source_rank = mass_rank(mass)
        for letter_index, letter in enumerate(letters):
            target = pushforward_mass(mass, letter)
            next_length = length + 1
            if mass_rank(target) < source_rank:
                bank = simplified_deadline(target, n) - next_length
                if bank + reserve.get(target, 0) < 0:
                    continue
            if target in distance:
                continue
            distance[target] = next_length
            if capture:
                parent[target] = (mass, letter_index)
            queue.append(target)
    return {"found": False, "semantics": "AVAILABLE_R1", "word": None, "word_length": None, "reserve_state_count": len(reserve), "ledger": None}


def realizable_r1_search(letters: Letters, n: int, *, capture: bool = False) -> dict:
    initial = ((1,) * n, False)
    distance = {initial: 0}
    parent: dict[tuple[Mass, bool], tuple[tuple[Mass, bool], int]] = {}
    queue = deque([initial])
    while queue:
        mass, pending = queue.popleft()
        length = distance[(mass, pending)]
        if mass_rank(mass) == 1:
            bank = simplified_deadline(mass, n) - length
            if bank < 0:
                continue
            word = None
            if capture:
                cursor = (mass, pending)
                path = []
                while cursor in parent:
                    cursor, letter_index = parent[cursor]
                    path.append(letter_index)
                word = tuple(reversed(path))
            return {"found": True, "semantics": "REALIZABLE_R1", "word": list(word) if word is not None else None, "word_length": length, "pending_at_terminal": False, "ledger": word_ledger(word, letters, n) if word is not None else None}
        source_rank = mass_rank(mass)
        for letter_index, letter in enumerate(letters):
            target = pushforward_mass(mass, letter)
            next_length = length + 1
            target_rank = mass_rank(target)
            next_pending = pending
            if target_rank < source_rank:
                bank = simplified_deadline(target, n) - next_length
                if pending:
                    if bank < 0:
                        continue
                    next_pending = False
                elif bank < 0:
                    next_pending = True
            state = (target, next_pending)
            if state in distance:
                continue
            distance[state] = next_length
            if capture:
                parent[state] = ((mass, pending), letter_index)
            queue.append(state)
    return {"found": False, "semantics": "REALIZABLE_R1", "word": None, "word_length": None, "pending_at_terminal": None, "ledger": None}


def pair_distances(letters: Letters, n: int) -> dict[tuple[int, int], int | None]:
    pairs = [(x, y) for x in range(n) for y in range(x + 1, n)]
    result: dict[tuple[int, int], int | None] = {}
    # A pair distance is a hitting time, so each source pair needs a forward
    # search until some letter identifies its two images.  The state space is
    # only O(n^2) and this avoids the common (incorrect) multi-source BFS that
    # measures distance *from* a pair rather than *to* the diagonal.
    for source in pairs:
        queue = deque([(source, 0)])
        seen = {source}
        found: int | None = None
        while queue:
            (x, y), depth = queue.popleft()
            for letter in letters:
                image = (letter[x], letter[y])
                if image[0] == image[1]:
                    found = depth + 1
                    queue.clear()
                    break
                next_pair = tuple(sorted(image))
                if next_pair not in seen:
                    seen.add(next_pair)
                    queue.append((next_pair, depth + 1))
            if found is not None:
                break
        result[source] = found
    return result


def unit_exit_records(letters: Letters, n: int) -> list[dict]:
    distances = pair_distances(letters, n)
    rows: list[dict] = []
    for source_mass, profile in first_exit_profiles(letters, n).items():
        for exit_row in profile["exits"]:
            if mass_rank(source_mass) - exit_row["target_rank"] != 1:
                continue
            source_support = [index for index, value in enumerate(source_mass) if value]
            target = exit_row["target"]
            corridor_map = tuple(range(n))
            for letter_index in exit_row["word"]:
                corridor_map = tuple(letters[letter_index][state] for state in corridor_map)
            merged = [(x, y) for i, x in enumerate(source_support) for y in source_support[i + 1:] if corridor_map[x] == corridor_map[y]]
            if len(merged) != 1:
                continue
            x, y = merged[0]
            weighted = source_mass[x] * source_mass[y]
            d2 = distances.get(tuple(sorted((x, y))))
            # For a unit exit the exact weighted pair value is the maturity
            # release tau(target)-tau(source), not merely 2*m_x*m_y: the
            # latter omits the rank correction in the deadline.
            weighted_value = simplified_deadline(target, n) - simplified_deadline(source_mass, n)
            rows.append({"source_mass": list(source_mass), "target_mass": list(target), "rank": mass_rank(source_mass), "x": x, "y": y, "mass_x": source_mass[x], "mass_y": source_mass[y], "d2": d2, "corridor_length": exit_row["length"], "surplus": weighted_value - exit_row["length"], "weighted_pair_value": weighted_value, "weighted_pair_gap": weighted_value - exit_row["length"], "pair_distance_matches_corridor": d2 == exit_row["length"]})
    return sorted(rows, key=lambda row: (tuple(row["source_mass"]), row["corridor_length"], row["target_mass"], row["letter"] if "letter" in row else 0))


def summarize_transition(letters: Letters, n: int, *, include_units: bool = False) -> dict:
    available = available_r1_search(letters, n)
    realizable = realizable_r1_search(letters, n)
    result = {"available_r1": available, "realizable_r1": realizable, "available_r1_found": available["found"], "realizable_r1_found": realizable["found"]}
    if include_units:
        units = unit_exit_records(letters, n)
        result["unit_exit_records"] = units
        result["unit_exit_record_count"] = len(units)
    return result


def row_scope(mode: str, n: int):
    transforms = list(itertools.product(range(n), repeat=n))
    if mode == "permutation":
        total = factorial(n) * (n ** n)
        def rows():
            for index, permutation in enumerate(itertools.permutations(range(n))):
                for second in transforms:
                    yield index * len(transforms) + transforms.index(second), (tuple(permutation), tuple(second))
        return total, rows(), {"alphabet_size": 2, "first_letter": "all labelled permutations"}
    if mode == "fixed-cycle":
        try:
            from .families import cerny_transition  # type: ignore
        except ImportError:
            from families import cerny_transition
        cycle = cerny_transition(n)[0]
        return n ** n, ((index, (cycle, tuple(second))) for index, second in enumerate(transforms)), {"alphabet_size": 2, "first_letter": "standard n-cycle"}
    raise ValueError(f"unknown mode: {mode}")


def run_census(mode: str, n: int, *, limit: int | None = None, progress: int = 5000, include_units: bool = False) -> dict:
    try:
        from .registry import shortest_reset_word  # type: ignore
    except ImportError:
        from registry import shortest_reset_word
    total, rows, metadata = row_scope(mode, n)
    row_limit = total if limit is None else min(limit, total)
    sync = nonsync = available = realizable = 0
    records = []
    for evaluated, (_index, letters) in enumerate(rows):
        if evaluated >= row_limit:
            break
        summary = summarize_transition(letters, n, include_units=include_units)
        if shortest_reset_word(tuple(letters)) is None:
            nonsync += 1
        else:
            sync += 1
        if summary["realizable_r1_found"]:
            realizable += 1
        if summary["available_r1_found"]:
            available += 1
        # The compact mass search is a maturity diagnostic, not a replacement
        # for the registry's exact reset test.
        record = {"index": _index, **summary}
        records.append(record)
    return {"schema": "mass-maturity-census-v1", "arithmetic": "exact integer mass transport", "scope": {"mode": mode, "n": n, "rows_evaluated": len(records), "rows_in_complete_scope": total, "complete": len(records) == total, **metadata}, "counts": {"synchronizing": sync, "nonsynchronizing": nonsync, "available_r1_pass": available, "realizable_r1_pass": realizable}, "records": records, "claim_boundary": ["Mass maturity fields are exact finite diagnostics.", "They do not prove a general synchronization bound."]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("permutation", "fixed-cycle"), default="fixed-cycle")
    parser.add_argument("--states", type=int, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = run_census(args.mode, args.states, limit=args.limit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"rows": payload["scope"]["rows_evaluated"], "out": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
