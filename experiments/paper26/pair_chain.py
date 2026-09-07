"""Exact finite pair-chain construction used by Paper XXVI.

The transition convention is source-row: ``transition[a][x]`` is the image
of state ``x`` under letter ``a``. Missing row mass in the normalized pair
matrix is exactly one-step pair absorption.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations
from typing import Iterable, Sequence

import numpy as np


Transition = Sequence[Sequence[int]]


def pair_states(n: int) -> list[tuple[int, int]]:
    return list(combinations(range(n), 2))


def build_pair_transfer(transition: Transition) -> tuple[np.ndarray, np.ndarray]:
    """Return integer transient adjacency and per-row merge multiplicities."""
    letters = [tuple(letter) for letter in transition]
    if not letters or not letters[0]:
        raise ValueError("at least one nonempty letter is required")
    n = len(letters[0])
    if any(len(letter) != n for letter in letters):
        raise ValueError("letters must act on one common carrier")
    states = pair_states(n)
    index = {pair: position for position, pair in enumerate(states)}
    transfer = np.zeros((len(states), len(states)), dtype=np.int64)
    merges = np.zeros(len(states), dtype=np.int64)
    for row, (left, right) in enumerate(states):
        for letter in letters:
            image_left, image_right = letter[left], letter[right]
            if image_left == image_right:
                merges[row] += 1
            else:
                target = tuple(sorted((image_left, image_right)))
                transfer[row, index[target]] += 1
    if not np.all(transfer.sum(axis=1) + merges == len(letters)):
        raise AssertionError("pair-chain row conservation failed")
    return transfer, merges


def pair_chain_diagnostics(transition: Transition) -> dict:
    """Compute the Perron gap and the worst-pair mean absorption time."""
    transfer, merges = build_pair_transfer(transition)
    alphabet_size = len(transition)
    kernel = transfer.astype(float) / alphabet_size
    eigenvalues = np.linalg.eigvals(kernel)
    rho = float(np.max(np.abs(eigenvalues)))
    means = np.linalg.solve(np.eye(kernel.shape[0]) - kernel, np.ones(kernel.shape[0]))
    return {
        "state_count": len(transition[0]),
        "alphabet_size": alphabet_size,
        "pair_count": kernel.shape[0],
        "rho": rho,
        "gap": 1.0 - rho,
        "H2": float(np.max(means)),
        "mean_by_pair": means.tolist(),
        "merge_multiplicity": merges.tolist(),
    }


def shortest_reset_length(transition: Transition) -> int | None:
    """Breadth-first search on nonempty image subsets."""
    letters = [tuple(letter) for letter in transition]
    start = frozenset(range(len(letters[0])))
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        subset, distance = queue.popleft()
        if len(subset) == 1:
            return distance
        for letter in letters:
            image = frozenset(letter[state] for state in subset)
            if image not in seen:
                seen.add(image)
                queue.append((image, distance + 1))
    return None


def cerny_transition(n: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    cycle = tuple((state + 1) % n for state in range(n))
    defect = tuple(0 if state == n - 1 else state for state in range(n))
    return cycle, defect


def rare_run_transition(n: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    sink = n - 1
    advance = tuple(state + 1 if state < sink else sink for state in range(n))
    restart = tuple(0 if state < sink else sink for state in range(n))
    return advance, restart


def apply_word(states: Iterable[int], transition: Transition, word: Iterable[int]) -> set[int]:
    image = set(states)
    for letter_index in word:
        letter = transition[letter_index]
        image = {letter[state] for state in image}
    return image
