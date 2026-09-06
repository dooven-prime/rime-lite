"""Finite Markov helpers needed by the two-state diagnostic control."""

from __future__ import annotations

import numpy as np


TOL = 1e-12


def validate_transition(transition: np.ndarray, tol: float = TOL) -> None:
    """Validate the paper's row-stochastic transition convention."""
    if transition.ndim != 2 or transition.shape[0] != transition.shape[1]:
        raise ValueError("transition matrix must be square")
    if np.min(transition) < -tol:
        raise ValueError("transition matrix has negative entries")
    if not np.allclose(transition.sum(axis=1), 1.0, atol=tol):
        raise ValueError("transition matrix must be row-stochastic")


def stationary_distribution(
    transition: np.ndarray, tol: float = TOL
) -> np.ndarray:
    """Return the normalized stationary left eigenvector."""
    values, vectors = np.linalg.eig(transition.T)
    index = int(np.argmin(np.abs(values - 1.0)))
    vector = np.real_if_close(vectors[:, index]).real
    if vector.sum() < 0:
        vector = -vector
    vector = np.maximum(vector, 0.0)
    total = float(vector.sum())
    if total <= tol:
        raise ValueError("stationary eigenvector could not be normalized")
    return vector / total


def support_reachable(
    transition: np.ndarray,
    source: int,
    target_states: set[int],
    tol: float = TOL,
) -> bool:
    """Return whether positive transition support reaches the target."""
    support = transition > tol
    frontier = {source}
    seen = {source}
    while frontier:
        if frontier.intersection(target_states):
            return True
        frontier = {
            target
            for state in frontier
            for target in np.flatnonzero(support[state])
            if target not in seen
        }
        seen.update(frontier)
    return bool(seen.intersection(target_states))


def expected_hitting_time(
    transition: np.ndarray,
    source: int,
    target_states: set[int],
    tol: float = TOL,
) -> float | None:
    """Solve the finite hitting-time system when the target is reachable."""
    if not support_reachable(transition, source, target_states, tol):
        return None
    if source in target_states:
        return 0.0
    transient = [
        state for state in range(transition.shape[0]) if state not in target_states
    ]
    index = {state: position for position, state in enumerate(transient)}
    subkernel = transition[np.ix_(transient, transient)]
    try:
        values = np.linalg.solve(
            np.eye(len(transient)) - subkernel, np.ones(len(transient))
        )
    except np.linalg.LinAlgError:
        return None
    value = float(values[index[source]])
    return value if np.isfinite(value) and value >= -tol else None


def eventual_hit_probability(
    transition: np.ndarray,
    source: int,
    target_states: set[int],
    tol: float = 1e-12,
) -> float:
    """Return the finite-chain probability of ever hitting ``target_states``."""
    if source in target_states:
        return 1.0

    support = np.asarray(transition) > tol
    can_reach = set(target_states)
    frontier = set(target_states)
    while frontier:
        predecessors = {
            state
            for state in range(support.shape[0])
            if any(support[state, target] for target in frontier)
        } - can_reach
        can_reach.update(predecessors)
        frontier = predecessors
    if source not in can_reach:
        return 0.0

    transient = sorted(can_reach - target_states)
    index = {state: position for position, state in enumerate(transient)}
    subkernel = transition[np.ix_(transient, transient)]
    direct = transition[np.ix_(transient, sorted(target_states))].sum(axis=1)
    values = np.linalg.solve(np.eye(len(transient)) - subkernel, direct)
    return float(min(1.0, max(0.0, values[index[source]])))
