"""Raw p/d semantics for the fixed selected pair F={0,1}.

The placement is stored atomwise: sites[z] is the site of source atom z.
Nonempty site fibers are exactly the current packets. This representation
keeps every actual fusion while avoiding an additional packet-order cache.
"""

from collections import deque
from dataclasses import dataclass


LETTERS = ("p", "d")
SELECTED = frozenset((0, 1))


@dataclass(frozen=True)
class Fusion:
    left: tuple[int, ...]
    right: tuple[int, ...]
    letter: str = "d"
    ports: tuple[int, int] = (0, 1)
    target: int = 0


@dataclass(frozen=True)
class State:
    sites: tuple[int, ...]
    origin: Fusion | None = None
    chain: tuple[Fusion, ...] = ()


def seed(n: int) -> State:
    if type(n) is not int or n < 3:
        raise ValueError("control domain is n>=3")
    return State(tuple(range(n)))


def packets(sites: tuple[int, ...]) -> tuple[tuple[int, tuple[int, ...]], ...]:
    return tuple(
        (site, tuple(atom for atom, current in enumerate(sites)
                     if current == site))
        for site in sorted(set(sites))
    )


def step(n: int, state: State, letter: str):
    """Return (actual successor, selected output or None, raw fusion or None)."""
    if letter not in LETTERS or len(state.sites) != n:
        raise ValueError("invalid raw letter or state size")
    if letter == "p":
        return (State(tuple((site + 1) % n for site in state.sites),
                      state.origin, state.chain), None, None)

    left = tuple(atom for atom, site in enumerate(state.sites) if site == 0)
    right = tuple(atom for atom, site in enumerate(state.sites) if site == 1)
    sites = tuple(0 if site == 1 else site for site in state.sites)
    fusion = Fusion(left, right) if left and right else None
    origin, chain, output = state.origin, state.chain, None
    if fusion is not None:
        if origin is None and frozenset(left + right) == SELECTED:
            origin = fusion
            output = ("registration", fusion)
        elif origin is not None and (
                SELECTED <= frozenset(left) or SELECTED <= frozenset(right)):
            chain = chain + (fusion,)
            output = ("absorption", fusion)
    return State(sites, origin, chain), output, fusion


def run(n: int, state: State, word: str):
    outputs = []
    for letter in word:
        state, output, _fusion = step(n, state, letter)
        outputs.append(output)
    return state, tuple(outputs)


def graph(n: int):
    """Exhaust the retained-state graph, recording a real seed word per state."""
    start = seed(n)
    words = {start: ""}
    transitions = {}
    queue = deque((start,))
    while queue:
        state = queue.popleft()
        for letter in LETTERS:
            following, output, fusion = step(n, state, letter)
            transitions[(state, letter)] = (following, output, fusion)
            if following not in words:
                words[following] = words[state] + letter
                queue.append(following)
    return tuple(words), transitions, words


def full_read(state: State):
    return None if state.origin is None else state


def carrier_site(state: State) -> int:
    if state.origin is None:
        raise ValueError("unregistered state has no selected carrier")
    sites = {state.sites[atom] for atom in SELECTED}
    if len(sites) != 1:
        raise AssertionError("registered pair must occupy one packet")
    return next(iter(sites))


def nonterminal(state: State) -> bool:
    return state.origin is not None and len(set(state.sites)) > 1
