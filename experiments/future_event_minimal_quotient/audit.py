"""Bounded controls for the unnumbered future-event manuscript.

The exact right congruences are computed by finite partition refinement.
The proposed all-n normal forms and literal probes are then checked against
that result. Neither finite check is used as a proof of the manuscript.
"""

from collections import Counter, defaultdict, deque
from functools import lru_cache
from itertools import combinations
from math import comb

from model import LETTERS, full_read, graph, nonterminal, packets, run, seed


DOMAIN = (3, 4, 5)


def registerable(states, transitions):
    reverse = defaultdict(list)
    first_sources = []
    for state in states:
        if state.origin is not None:
            continue
        for letter in LETTERS:
            following, output, _fusion = transitions[(state, letter)]
            if output is not None and output[0] == "registration":
                first_sources.append(state)
            elif following.origin is None:
                reverse[following].append(state)
    reached = set(first_sources)
    queue = deque(first_sources)
    while queue:
        for previous in reverse[queue.popleft()]:
            if previous not in reached:
                reached.add(previous)
                queue.append(previous)
    return reached


def _ids(signatures, states):
    names = {}
    return {state: names.setdefault(signatures[state], len(names))
            for state in states}


def quotient(states, transitions, observer):
    if observer == "future":
        initial = {state: None for state in states}
    elif observer == "full":
        initial = {state: full_read(state) for state in states}
    else:
        raise ValueError("unknown observer")
    blocks = _ids(initial, states)
    rounds = 0
    while True:
        signatures = {}
        for state in states:
            edges = []
            for letter in LETTERS:
                following, output, _fusion = transitions[(state, letter)]
                edges.append((output if observer == "future" else None,
                              blocks[following]))
            signatures[state] = (initial[state], tuple(edges))
        refined = _ids(signatures, states)
        rounds += 1
        if refined == blocks:
            return refined, rounds
        blocks = refined


def future_key(state, ready):
    if state in ready:
        return "pre", state.sites
    if nonterminal(state):
        return "registered", state.sites
    return ("sink",)


def full_key(state, ready):
    if state.origin is not None:
        return "registered_summary", state
    if state in ready:
        return "pre", state.sites
    return ("sink",)


def matches_partition(states, blocks, key):
    key_to_block, block_to_key = {}, {}
    for state in states:
        a, b = key(state), blocks[state]
        if a in key_to_block and key_to_block[a] != b:
            return False
        if b in block_to_key and block_to_key[b] != a:
            return False
        key_to_block[a], block_to_key[b] = b, a
    return True


def W(n, q):
    return "p" * ((-q) % n) + "d" + "pd" * (n - 2)


def gap(n, state):
    return (state.sites[1] - state.sites[0]) % n


def V(n, state):
    if state.origin is not None or not 1 <= gap(n, state) <= n - 2:
        raise ValueError("V needs a registerable pre-registration state")
    return "p" * ((1 - state.sites[1]) % n) + "dp" * (gap(n, state) - 1) + "d"


@lru_cache(maxsize=None)
def trace(n, state, word):
    return run(n, state, word)[1]


def certificate(n, left, right, ready):
    """Return one manuscript-family distinguishing word for two class keys."""
    lk, rk = future_key(left, ready)[0], future_key(right, ready)[0]
    if lk == "pre" or rk == "pre":
        if lk != "pre" or (rk == "pre" and gap(n, right) < gap(n, left)):
            left, right = right, left
        word = V(n, left)
        if trace(n, left, word) != trace(n, right, word):
            return word, "V"
        if future_key(right, ready)[0] != "pre":
            raise AssertionError("a new registration must separate regions")
        for q in range(n):
            candidate = word + W(n, q)
            if trace(n, left, candidate) != trace(n, right, candidate):
                return candidate, "V+W"
    else:
        for q in range(n):
            word = W(n, q)
            if trace(n, left, word) != trace(n, right, word):
                return word, "W"
    raise AssertionError("candidate normal forms have no prescribed separator")


def example():
    one = "d" + "p" * 3 + "d" + "p" + "d" + "p" * 4 + "p" * 2 + "d"
    two = ("d" + "p" * 4 + "d" + "p" + "d" + "p" * 3 + "d" +
           "p" * 2 + "p" * 4 + "d" + "p" + "d")
    first, _ = run(5, seed(5), one)
    second, _ = run(5, seed(5), two)
    expected = ((0, (0, 1, 2, 3)), (4, (4,)))
    if (packets(first.sites) != expected or first.sites != second.sites or
            first.origin != second.origin or
            len(first.chain) != 1 or len(second.chain) != 2 or
            not nonterminal(first)):
        raise AssertionError("introduction example did not replay")
    return {"n": 5, "word_one": one, "word_two": two,
            "placement": [[site, list(block)] for site, block in expected],
            "selected_chain_lengths": [1, 2]}


def audit_n(n):
    if n not in DOMAIN:
        raise ValueError("the public control domain is n=3..5")
    states, transitions, _words = graph(n)
    ready = registerable(states, transitions)
    future, future_rounds = quotient(states, transitions, "future")
    full, full_rounds = quotient(states, transitions, "full")
    if not matches_partition(states, future,
                             lambda state: future_key(state, ready)):
        raise AssertionError("future normal form disagrees with refinement")
    if not matches_partition(states, full,
                             lambda state: full_key(state, ready)):
        raise AssertionError("full normal form disagrees with refinement")

    criterion = all(
        (state in ready) ==
        ((0,) in (block for _site, block in packets(state.sites)) and
         (1,) in (block for _site, block in packets(state.sites)))
        for state in states if state.origin is None)
    if not criterion:
        raise AssertionError("registerability criterion failed")

    representatives = {}
    for state in states:
        representatives.setdefault(future_key(state, ready), state)
    methods = Counter()
    max_length = 0
    for left, right in combinations(representatives.values(), 2):
        word, method = certificate(n, left, right, ready)
        if len(word) > 6 * n - 10:
            raise AssertionError("literal certificate exceeds theorem bound")
        methods[method] += 1
        max_length = max(max_length, len(word))

    registered_states = sum(state.origin is not None for state in states)
    registered_placements = len({state.sites for state in states
                                 if nonterminal(state)})
    R = n * comb(2 * n - 4, n - 3)
    A = n * sum((n - 1 - k) * comb(n + k - 2, k)
                for k in range(1, n - 1))
    expected_future = 1 + R + A
    expected_full = 1 + R + registered_states
    if (len(ready), registered_placements, len(set(future.values())),
            len(set(full.values()))) != (R, A, expected_future, expected_full):
        raise AssertionError("bounded counts disagree with exact formulas")
    return {
        "n": n,
        "reachable_retained_states": len(states),
        "raw_edges": len(transitions),
        "registered_summaries": registered_states,
        "registerable_placements": len(ready),
        "registered_nonterminal_placements": registered_placements,
        "future_classes": expected_future,
        "full_classes": expected_full,
        "refinement_rounds": {"future": future_rounds, "full": full_rounds},
        "candidate_class_pairs_checked": sum(methods.values()),
        "certificate_methods": dict(sorted(methods.items())),
        "max_certificate_length": max_length,
        "declared_length_bound": 6 * n - 10,
    }


def report():
    return {
        "status": "BOUNDED_CONSISTENCY_ONLY",
        "domain": {"n": list(DOMAIN), "F": [0, 1],
                   "letters": list(LETTERS), "seed": "identity_singletons"},
        "introduction_example": example(),
        "controls": [audit_n(n) for n in DOMAIN],
    }
