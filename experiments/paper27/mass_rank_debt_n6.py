#!/usr/bin/env python3
"""Exact fixed-cycle census for cumulative V/W ledgers on the mass graph.

The default scope fixes the first letter to the 6-cycle and exhausts all
``6^6`` labelled second transformations.  Search states are fibre-mass
vectors, not transformations.  At a fixed mass state ``mu``, the cumulative
ledger is determined by the arrival length and the endpoint potential, so a
shorter admissible arrival dominates every longer one.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from collections import deque
from math import comb
from pathlib import Path
from typing import Sequence

from kernel_mass_potential import (
    cerny_letters,
    mass_kernel_mass,
    mass_rank,
    pushforward_mass,
    rank_debt,
)

Mass = tuple[int, ...]
Transformation = tuple[int, ...]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mass_potential(mass: Sequence[int], n: int, use_rank_debt: bool) -> int:
    rank = mass_rank(mass)
    value = 2 * (comb(n, 2) - mass_kernel_mass(mass)) - (rank - 1)
    return value - rank_debt(rank, n) if use_rank_debt else value


def mass_deadline(mass: Sequence[int], n: int, use_rank_debt: bool = True) -> int:
    """Return tau_n(mu)=(n-1)^2-P(mu), for P=W by default."""
    return (n - 1) ** 2 - mass_potential(mass, n, use_rank_debt)


def reconstruct_word(
    target: Mass,
    parent: dict[Mass, tuple[Mass, int]],
) -> tuple[int, ...]:
    word = []
    while target in parent:
        target, letter = parent[target]
        word.append(letter)
    return tuple(reversed(word))


def word_ledger(
    word: Sequence[int],
    letters: Sequence[Transformation],
    n: int,
) -> dict:
    """Serialize exact V/W balances along one mass path."""
    initial = (1,) * n
    initial_potential = (n - 1) ** 2
    mass = initial
    steps = []
    for length, letter_index in enumerate(word, start=1):
        target = pushforward_mass(mass, letters[letter_index])
        source_rank = mass_rank(mass)
        target_rank = mass_rank(target)
        source_v = mass_potential(mass, n, False)
        target_v = mass_potential(target, n, False)
        source_w = mass_potential(mass, n, True)
        target_w = mass_potential(target, n, True)
        v_deadline = mass_deadline(target, n, False)
        w_deadline = mass_deadline(target, n, True)
        steps.append(
            {
                "length": length,
                "letter": letter_index,
                "source": list(mass),
                "target": list(target),
                "source_rank": source_rank,
                "target_rank": target_rank,
                "support_drop": source_rank - target_rank,
                "v_credit": source_v - target_v,
                "w_credit": source_w - target_w,
                "is_checkpoint": target_rank < source_rank,
                "v_deadline": v_deadline,
                "w_deadline": w_deadline,
                "v_deadline_slack": v_deadline - length,
                "w_deadline_slack": w_deadline - length,
                "banked_v": initial_potential - target_v - length,
                "banked_w": initial_potential - target_w - length,
            }
        )
        mass = target
    checkpoint_slacks = [
        step["w_deadline_slack"] for step in steps if step["is_checkpoint"]
    ]
    return {
        "word": list(word),
        "word_length": len(word),
        "final_mass": list(mass),
        "is_reset": mass_rank(mass) == 1,
        "minimum_checkpoint_slack": min(checkpoint_slacks, default=0),
        "steps": steps,
    }


def banked_mass_search(
    letters: Sequence[Transformation],
    n: int,
    *,
    use_rank_debt: bool,
    capture: bool = False,
    required_checkpoint_slack: int = 0,
) -> dict:
    """Search BANKED_V or BANKED_W using only exact fibre-mass states.

    A support-preserving edge may temporarily make the bank negative inside a
    corridor. A support-decreasing edge is admitted only when the cumulative
    bank at the new checkpoint is at least ``required_checkpoint_slack``.
    Since edge credits telescope,

        bank(mu) = (n-1)^2 - P(mu) - arrival_length,

    where P is V or W.  Hence the first admissible BFS arrival at ``mu``
    dominates every later arrival.
    """
    initial = (1,) * n
    initial_potential = (n - 1) ** 2
    distance: dict[Mass, int] = {initial: 0}
    parent: dict[Mass, tuple[Mass, int]] = {}
    queue = deque([initial])
    explored_edges = 0
    blocked_drops = 0
    best_blocked: tuple[int, int, Mass, Mass, int] | None = None
    path_slack: dict[Mass, int | None] = {initial: None}
    best_terminal: tuple[int, int, Mass] | None = None

    while queue:
        mass = queue.popleft()
        length = distance[mass]
        if best_terminal is not None and length > best_terminal[0]:
            break
        if mass_rank(mass) == 1:
            slack = path_slack[mass]
            # For n=1 or an already-reset initial state there is no checkpoint;
            # the empty minimum is the neutral value zero.
            if slack is None:
                slack = 0
            if best_terminal is None or slack > best_terminal[1]:
                best_terminal = (length, slack, mass)
            continue
        source_rank = mass_rank(mass)
        for letter_index, letter in enumerate(letters):
            explored_edges += 1
            target = pushforward_mass(mass, letter)
            target_rank = mass_rank(target)
            if target_rank > source_rank:
                raise AssertionError("deterministic pushforward increased support")
            next_length = length + 1
            if target_rank < source_rank:
                bank = (
                    initial_potential
                    - mass_potential(target, n, use_rank_debt)
                    - next_length
                )
                if bank < required_checkpoint_slack:
                    blocked_drops += 1
                    candidate = (bank, -next_length, mass, target, letter_index)
                    if best_blocked is None or candidate[:2] > best_blocked[:2]:
                        best_blocked = candidate
                    continue
                target_slack = bank
            else:
                target_slack = path_slack[mass]
            current_slack = target_slack
            if target_rank == source_rank and current_slack is None:
                current_slack = None
            elif path_slack[mass] is not None and target_rank == source_rank:
                current_slack = path_slack[mass]
            elif target_rank < source_rank and path_slack[mass] is not None:
                current_slack = min(path_slack[mass], target_slack)
            old_length = distance.get(target)
            old_slack = path_slack.get(target)
            improves = old_length is None or next_length < old_length
            if old_length == next_length and current_slack is not None:
                improves = old_slack is None or current_slack > old_slack
            if not improves:
                continue
            distance[target] = next_length
            path_slack[target] = current_slack
            if capture:
                parent[target] = (mass, letter_index)
            queue.append(target)

    if best_terminal is not None:
        terminal_length, terminal_slack, terminal_mass = best_terminal
        word = reconstruct_word(terminal_mass, parent) if capture else None
        return {
            "found": True,
            "semantics": "BANKED_W" if use_rank_debt else "BANKED_V",
            "word": list(word) if word is not None else None,
            "word_length": terminal_length,
            "final_bank": initial_potential
            - mass_potential(terminal_mass, n, use_rank_debt)
            - terminal_length,
            "explored_mass_states": len(distance),
            "explored_edges": explored_edges,
            "blocked_support_drops": blocked_drops,
            "best_blocked_drop": None,
            "minimum_checkpoint_slack": terminal_slack,
            "required_checkpoint_slack": required_checkpoint_slack,
            "deadline": mass_deadline(terminal_mass, n, use_rank_debt),
        }

    blocked_record = None
    if capture and best_blocked is not None:
        bank, negative_length, source, target, letter_index = best_blocked
        source_word = reconstruct_word(source, parent)
        blocked_word = source_word + (letter_index,)
        blocked_record = {
            "bank_after_drop": bank,
            "word": list(blocked_word),
            "source": list(source),
            "target": list(target),
            "source_rank": mass_rank(source),
            "target_rank": mass_rank(target),
            "ledger": word_ledger(blocked_word, letters, n),
        }
        if len(blocked_word) != -negative_length:
            raise AssertionError("blocked-path length bookkeeping failed")
    return {
        "found": False,
        "semantics": "BANKED_W" if use_rank_debt else "BANKED_V",
        "word": None,
        "word_length": None,
        "final_bank": None,
        "explored_mass_states": len(distance),
        "explored_edges": explored_edges,
        "blocked_support_drops": blocked_drops,
        "best_blocked_drop": blocked_record,
        "minimum_checkpoint_slack": None,
        "required_checkpoint_slack": required_checkpoint_slack,
        "deadline": None,
    }


def maximum_checkpoint_slack(
    letters: Sequence[Transformation], n: int, *, capture: bool = False
) -> dict:
    """Maximize minimum W-deadline slack at strict support-drop checkpoints."""
    low = 0
    high = (n - 1) ** 2 - 1
    best = banked_mass_search(
        letters,
        n,
        use_rank_debt=True,
        capture=capture,
        required_checkpoint_slack=0,
    )
    if not best["found"]:
        return {"found": False, "maximum_checkpoint_slack": None, "search": best}
    while low < high:
        middle = (low + high + 1) // 2
        result = banked_mass_search(
            letters,
            n,
            use_rank_debt=True,
            capture=capture,
            required_checkpoint_slack=middle,
        )
        if result["found"]:
            low = middle
            best = result
        else:
            high = middle - 1
    if best["required_checkpoint_slack"] != low:
        best = banked_mass_search(
            letters,
            n,
            use_rank_debt=True,
            capture=capture,
            required_checkpoint_slack=low,
        )
    if best["minimum_checkpoint_slack"] != low:
        raise AssertionError("maximum checkpoint slack was not attained exactly")
    return {"found": True, "maximum_checkpoint_slack": low, "search": best}


def ordinary_mass_search(
    letters: Sequence[Transformation], n: int, *, capture: bool = False
) -> dict:
    """Test synchronization by unpruned reachability in the mass graph."""
    initial = (1,) * n
    distance = {initial: 0}
    parent: dict[Mass, tuple[Mass, int]] = {}
    queue = deque([initial])
    explored_edges = 0
    while queue:
        mass = queue.popleft()
        if mass_rank(mass) == 1:
            word = reconstruct_word(mass, parent) if capture else None
            return {
                "found": True,
                "word": list(word) if word is not None else None,
                "word_length": distance[mass],
                "explored_mass_states": len(distance),
                "explored_edges": explored_edges,
                "ledger": word_ledger(word, letters, n) if word is not None else None,
            }
        for letter_index, letter in enumerate(letters):
            explored_edges += 1
            target = pushforward_mass(mass, letter)
            if target in distance:
                continue
            distance[target] = distance[mass] + 1
            if capture:
                parent[target] = (mass, letter_index)
            queue.append(target)
    return {
        "found": False,
        "word": None,
        "word_length": None,
        "explored_mass_states": len(distance),
        "explored_edges": explored_edges,
        "ledger": None,
    }


def exact_failure_certificate(
    index: int,
    defect: Transformation,
    cycle: Transformation,
    n: int,
) -> dict:
    letters = (cycle, defect)
    banked = banked_mass_search(letters, n, use_rank_debt=True, capture=True)
    ordinary = ordinary_mass_search(letters, n, capture=True)
    if banked["found"] or not ordinary["found"]:
        raise AssertionError("requested BANKED_W failure is not a synchronizing failure")
    return {
        "index": index,
        "second_transformation": list(defect),
        "banked_w_search": banked,
        "ordinary_shortest_mass_path": ordinary,
    }


def deterministic_projection(record: dict) -> dict:
    """Fields compared by the independent full-recomputation validator."""
    return {
        "schema": record["schema"],
        "scope": record["scope"],
        "counts": record["counts"],
        "banked_v": record["banked_v"],
        "banked_w": record["banked_w"],
        "mass_graph": record["mass_graph"],
        "classification_digests": record["classification_digests"],
        "first_banked_w_counterexample": record["first_banked_w_counterexample"],
    }


def run_census(n: int = 6, *, limit: int | None = None, progress: int = 5000) -> dict:
    if n < 2:
        raise ValueError("n must be at least 2")
    cycle = cerny_letters(n)[0]
    total_scope = n**n
    row_limit = total_scope if limit is None else min(limit, total_scope)
    synchronizing = 0
    nonsynchronizing = 0
    v_pass = 0
    w_pass = 0
    first_failure = None
    max_w_states = 0
    max_v_states = 0
    max_sync_states = 0
    max_w_word = 0
    max_w_word_indices: list[int] = []
    selected_slacks: list[int] = []
    max_v_word = 0
    sync_digest = hashlib.sha256()
    v_digest = hashlib.sha256()
    w_digest = hashlib.sha256()
    combined_digest = hashlib.sha256()
    started = time.perf_counter()

    for index, defect_values in enumerate(itertools.product(range(n), repeat=n)):
        if index >= row_limit:
            break
        defect = tuple(defect_values)
        letters = (cycle, defect)
        w_result = banked_mass_search(letters, n, use_rank_debt=True)
        v_result = banked_mass_search(letters, n, use_rank_debt=False)
        if v_result["found"] and not w_result["found"]:
            raise AssertionError("BANKED_V path was not retained by BANKED_W")
        max_w_states = max(max_w_states, w_result["explored_mass_states"])
        max_v_states = max(max_v_states, v_result["explored_mass_states"])
        if w_result["found"]:
            is_sync = True
            sync_result = None
            w_pass += 1
            word_length = int(w_result["word_length"])
            if word_length > max_w_word:
                max_w_word = word_length
                max_w_word_indices = [index]
            elif word_length == max_w_word:
                max_w_word_indices.append(index)
            selected_slacks.append(int(w_result["minimum_checkpoint_slack"]))
        else:
            sync_result = ordinary_mass_search(letters, n)
            is_sync = bool(sync_result["found"])
            max_sync_states = max(max_sync_states, sync_result["explored_mass_states"])
        if is_sync:
            synchronizing += 1
            if v_result["found"]:
                v_pass += 1
                max_v_word = max(max_v_word, int(v_result["word_length"]))
            if not w_result["found"] and first_failure is None:
                first_failure = exact_failure_certificate(index, defect, cycle, n)
        else:
            nonsynchronizing += 1

        flags = bytes((int(is_sync), int(v_result["found"]), int(w_result["found"])))
        sync_digest.update(flags[:1])
        v_digest.update(flags[1:2])
        w_digest.update(flags[2:3])
        combined_digest.update(flags)
        if progress and (index + 1) % progress == 0:
            elapsed = time.perf_counter() - started
            print(
                f"{index + 1}/{row_limit}: sync={synchronizing}, "
                f"BANKED_W={w_pass}, elapsed={elapsed:.1f}s",
                flush=True,
            )

    producer = Path(__file__).resolve()
    core = producer.with_name("kernel_mass_potential.py")
    workspace = producer.parents[2]
    return {
        "schema": "fixed-cycle-mass-rank-debt-census-v1",
        "arithmetic": "exact nonnegative integer mass pushforward",
        "sources": {
            "producer": {
                "path": producer.relative_to(workspace).as_posix(),
                "sha256": file_sha256(producer),
            },
            "mass_core": {
                "path": core.relative_to(workspace).as_posix(),
                "sha256": file_sha256(core),
            },
        },
        "scope": {
            "n": n,
            "first_letter": list(cycle),
            "second_letter_enumeration": "lexicographic product(range(n), repeat=n)",
            "labelled_second_transformations_in_full_scope": total_scope,
            "rows_evaluated": row_limit,
            "complete": row_limit == total_scope,
        },
        "counts": {
            "synchronizing": synchronizing,
            "nonsynchronizing": nonsynchronizing,
        },
        "banked_v": {
            "pass": v_pass,
            "fail_among_synchronizing": synchronizing - v_pass,
            "maximum_admissible_word_length": max_v_word,
            "maximum_explored_mass_states": max_v_states,
        },
        "banked_w": {
            "pass": w_pass,
            "fail_among_synchronizing": synchronizing - w_pass,
            "maximum_admissible_word_length": max_w_word,
            "maximum_explored_mass_states": max_w_states,
            "selected_path_checkpoint_slack_minimum": min(selected_slacks, default=None),
            "selected_path_checkpoint_slack_maximum": max(selected_slacks, default=None),
            "selected_paths_with_zero_checkpoint_slack": sum(value == 0 for value in selected_slacks),
            "maximum_word_length_indices": max_w_word_indices,
        },
        "mass_graph": {
            "ambient_weak_compositions": comb(2 * n - 1, n - 1),
            "maximum_states_in_unpruned_fallback": max_sync_states,
            "state": "mu in N^n with sum(mu)=n",
            "transition": "mu -> a_*mu",
            "checkpoint_rule": "require cumulative bank >= 0 only after support drops",
        },
        "classification_digests": {
            "synchronizing_bits_sha256": sync_digest.hexdigest(),
            "banked_v_bits_sha256": v_digest.hexdigest(),
            "banked_w_bits_sha256": w_digest.hexdigest(),
            "combined_three_bytes_per_row_sha256": combined_digest.hexdigest(),
        },
        "first_banked_w_counterexample": first_failure,
        "claim_boundary": [
            "A complete record is an exact finite certificate only for the declared fixed-cycle labelled slice.",
            "BANKED_W passage proves a reset word of length at most (n-1)^2 for that row; it is not a universal theorem.",
            "A failed BANKED_W search is preserved without modifying the potential or checkpoint semantics.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/mass_rank_debt_fixed_cycle_n6.json"),
    )
    args = parser.parse_args()
    record = run_census(args.n, limit=args.limit, progress=args.progress)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(deterministic_projection(record), indent=2))


if __name__ == "__main__":
    main()
