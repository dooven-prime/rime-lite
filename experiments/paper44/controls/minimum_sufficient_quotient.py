"""Finite right-congruence quotients for two selected-summary consumers.

The full-summary observer emits the current complete registered state at each
prefix (and ``None`` before registration). The future-event observer emits
only selected registration/absorption events on transitions. Both quotients
are computed over the complete reachable consumer-state graph for fixed F.
"""

from collections import Counter, defaultdict, deque
from functools import lru_cache
import argparse
import json
from math import comb

import shortest_summary_search as search


def _partition(signatures):
    """Assign stable integer block ids to hashable signatures."""
    ids = {}
    result = {}
    for state, signature in signatures.items():
        result[state] = ids.setdefault(signature, len(ids))
    return result


def _same_partition(left, right, states):
    """Compare partitions independently of their integer block labels."""
    forward = {}
    backward = {}
    for state in states:
        a, b = left[state], right[state]
        if (a in forward and forward[a] != b) or (
                b in backward and backward[b] != a):
            return False
        forward[a] = b
        backward[b] = a
    return True


def _event_output(F, state, next_state):
    old_origin, old_chain = state[1], state[2]
    new_origin, new_chain = next_state[1], next_state[2]
    if old_origin is None and new_origin is not None:
        letter, (k0, U0), (k1, V1), collision = new_origin
        return ("registration", (letter, k0, k1, U0, V1, collision,
                                  tuple(sorted(F))))
    if old_origin is not None and len(new_chain) > len(old_chain):
        return ("selected_absorption", new_chain[-1])
    return None


def _registerable_states(states, transitions):
    """Find pre-registration states that can reach a registration edge."""
    reverse = defaultdict(list)
    registration_sources = set()
    for state in states:
        for letter in search.RAW_LETTERS:
            next_state = transitions[(state, letter)]
            reverse[next_state].append(state)
            if state[1] is None and next_state[1] is not None:
                registration_sources.add(state)

    registerable = set(registration_sources)
    queue = deque(registration_sources)
    while queue:
        state = queue.popleft()
        for previous in reverse[state]:
            if previous[1] is None and previous not in registerable:
                registerable.add(previous)
                queue.append(previous)
    return registerable


def _criterion_registerable(state, F):
    singleton_blocks = {frozenset(block) for _position, block in state[0]}
    return all(frozenset((atom,)) in singleton_blocks for atom in F)


def registerable_placement_count(n):
    """All-n candidate count for registerable pre-registration placements."""
    if n < 3:
        raise ValueError("n must be at least 3")
    return n * comb(2 * n - 4, n - 3)


def rank_one_transition_count(n):
    """Full-frontier fixed-plan DP transition count for a rank-one target."""
    if n < 3:
        raise ValueError("n must be at least 3")
    return 1 + comb(2 * n - 4, n - 3)


def registered_nonterminal_placement_count(n):
    """All-n candidate count of registered placements with outside packets."""
    if n < 3:
        raise ValueError("n must be at least 3")
    return n * sum((n - 1 - k) * comb(n + k - 2, k)
                   for k in range(1, n - 1))


def registered_nonterminal_placement_count_closed(n):
    if n < 3:
        raise ValueError("n must be at least 3")
    return 2 * (2 * n - 3) * comb(2 * n - 4, n - 2) - n * (n - 1)


def future_quotient_candidate_bound_closed(n):
    """Closed form for U_n = 1 + R_n + A_n."""
    if n < 3:
        raise ValueError("n must be at least 3")
    return (1 + n * comb(2 * n - 4, n - 3)
            + 2 * (2 * n - 3) * comb(2 * n - 4, n - 2)
            - n * (n - 1))


def chain_extension_count(r):
    """Sum of h(a,b) over all a+b=r."""
    if r < 0:
        raise ValueError("r must be nonnegative")
    if r == 0:
        return 1
    return 2 * 3 ** (r - 1)


def registered_rank_one_summary_count(n):
    """Number of registered rank-one summaries for F={0,1}."""
    if n < 3:
        raise ValueError("n must be at least 3")
    return 2 * n * 3 ** (n - 3)


def first_absorption_prefix_quotient_count(n):
    """Exact finite-sum count for the first-absorption-prefix observer.

    The observer retains the registration record and the first selected
    absorption record, if any, while continuing to emit future events.
    """
    if n < 3:
        raise ValueError("n must be at least 3")
    count = (1 + registerable_placement_count(n) + 2 * (n - 2)
             + n * comb(2 * n - 4, n - 2))
    for r in range(1, n - 2):
        k = n - 2 - r
        count += n * r * (r + 1) * comb(n + k - 2, k)
    return count


def first_absorption_prefix_quotient_count_closed(n):
    """Closed form for the first-absorption-prefix quotient count."""
    if n < 3:
        raise ValueError("n must be at least 3")
    central = comb(2 * n - 4, n - 2)
    numerator = (9 * n * n - 27 * n + 24) * central
    quotient, remainder = divmod(numerator, n + 1)
    if remainder:
        raise ArithmeticError("closed first-prefix count is not integral")
    registered = quotient - n * (n - 1) * (n - 2)
    return (1 + registerable_placement_count(n) + 2 * (n - 2)
            + registered)


@lru_cache(maxsize=None)
def chain_multiplicity(a, b):
    """Number of selected chains expanding the fixed pair by (a,b)."""
    if a < 0 or b < 0:
        return 0
    if a == 0 and b == 0:
        return 1
    return (sum(chain_multiplicity(a - i, b) for i in range(1, a + 1))
            + sum(chain_multiplicity(a, b - j) for j in range(1, b + 1)))


def predicted_future_nonsink_class_histogram(n):
    """Candidate future-class size histogram from placement and chain counts."""
    if n < 3:
        raise ValueError("n must be at least 3")
    histogram = Counter({1: registerable_placement_count(n)})
    for a in range(n - 2):
        for b in range(n - 2 - a):
            k = n - 2 - a - b
            class_size = chain_multiplicity(a, b)
            placements = n * comb(n + k - 2, k)
            histogram[class_size] += placements
    return dict(sorted(histogram.items()))


def predicted_histogram_conservation(n, registered_summary_count):
    """Class-count and weighted-state-count checks for the candidate histogram."""
    histogram = predicted_future_nonsink_class_histogram(n)
    return {
        "class_count": sum(histogram.values()),
        "weighted_state_count": sum(size * count
                                     for size, count in histogram.items()),
        "expected_class_count": (registerable_placement_count(n)
                                  + registered_nonterminal_placement_count(n)),
        "expected_state_count": (
            registerable_placement_count(n) + registered_summary_count
            - registered_rank_one_summary_count(n)),
    }


def future_quotient_candidate_bound(n):
    return (1 + registerable_placement_count(n)
            + registered_nonterminal_placement_count(n))


def _quotient(states, transitions, F, observer):
    pair_criterion_applies = F == frozenset((0, 1))
    if observer == "full_summary":
        initial = {
            state: (("unregistered",) if state[1] is None else
                    ("registered_summary", state))
            for state in states
        }
    elif observer == "future_events":
        initial = {state: ("no-current-output",) for state in states}
    elif observer == "first_absorption_prefix":
        initial = {
            state: _first_absorption_prefix_output(F, state)
            for state in states
        }
    else:
        raise ValueError("unknown observer")

    blocks = _partition(initial)
    iterations = 0
    while True:
        signatures = {}
        for state in states:
            edges = []
            for letter in search.RAW_LETTERS:
                next_state = transitions[(state, letter)]
                output = (_event_output(F, state, next_state)
                          if observer in ("future_events",
                                          "first_absorption_prefix")
                          else None)
                edges.append((letter, output, blocks[next_state]))
            signatures[state] = (initial[state], tuple(edges))
        refined = _partition(signatures)
        iterations += 1
        stable = _same_partition(blocks, refined, states)
        blocks = refined
        if stable:
            break

    class_members = defaultdict(list)
    for state in states:
        class_members[blocks[state]].append(state)
    sizes = Counter(len(members) for members in class_members.values())
    registered = [state for state in states if state[1] is not None]
    preregistered = [state for state in states if state[1] is None]
    registerable = _registerable_states(states, transitions)
    dead = [state for state in preregistered if state not in registerable]
    terminal = [state for state in states if len(state[0]) == 1]
    return {
        "observer": observer,
        "class_count": len(class_members),
        "refinement_rounds": iterations,
        "class_size_histogram": {
            str(size): count for size, count in sorted(sizes.items())},
        "largest_class_size": max(sizes, default=0),
        "registered_state_count": len(registered),
        "registered_states_are_singleton_classes": all(
            len(class_members[blocks[state]]) == 1 for state in registered),
        "preregistration_state_count": len(preregistered),
        "registerable_preregistration_state_count": len(registerable),
        "registerable_preregistration_states_are_singleton_classes": all(
            len(class_members[blocks[state]]) == 1
            for state in preregistered if state in registerable),
        "dead_preregistration_state_count": len(dead),
        "dead_preregistration_class_count": len(
            {blocks[state] for state in dead}),
        "dead_preregistration_states_one_class": (
            len({blocks[state] for state in dead}) <= 1),
        "registerability_criterion_matches_search": (
            all((state in registerable) == _criterion_registerable(state, F)
                for state in preregistered)
            if pair_criterion_applies else None),
        "terminal_state_count": len(terminal),
        "terminal_class_count": len({blocks[state] for state in terminal}),
        "terminal_states_one_class": len(
            {blocks[state] for state in terminal}) <= 1,
        "terminal_class_size": (len(class_members[blocks[terminal[0]]])
                                if terminal else 0),
    }


def _first_absorption_prefix_output(F, state):
    """Current output for the first-absorption-prefix observer."""
    _partition, origin, chain = state
    if origin is None:
        return ("unregistered",)
    first = chain[0] if chain else ("stop",)
    return ("registered", origin, first)


def first_absorption_prefix_quotient(n, F=(0, 1), *, max_states=None):
    """Compute the exact bounded quotient for the first-record observer."""
    F = search.validate_input(n, F)
    states_by_distance, _parent = search.bfs_distances(
        n, F, max_states=max_states, retain_predecessors=False)
    states = list(states_by_distance)
    transitions = {
        (state, letter): search.successor(n, F, state, letter)
        for state in states for letter in search.RAW_LETTERS
    }
    return _quotient(states, transitions, F, "first_absorption_prefix")


def quotient_report(n, F=(0, 1), *, max_states=None):
    """Compute exact reachable-state right-congruence data for fixed F."""
    F = search.validate_input(n, F)
    states_by_distance, _parent = search.bfs_distances(
        n, F, max_states=max_states, retain_predecessors=False)
    states = list(states_by_distance)
    transitions = {
        (state, letter): search.successor(n, F, state, letter)
        for state in states for letter in search.RAW_LETTERS
    }
    registerable = _registerable_states(states, transitions)
    criterion_applies = F == frozenset((0, 1))
    criterion_holds = (all(
        (state in registerable) == _criterion_registerable(state, F)
        for state in states if state[1] is None)
        if criterion_applies else None)
    report = {
        "n": n,
        "F": sorted(F),
        "reachable_states": len(states),
        "transition_count": len(transitions),
        "registerability_criterion_applies": criterion_applies,
        "registerability_criterion_matches_search": criterion_holds,
        "full_summary": _quotient(states, transitions, F, "full_summary"),
        "future_events": _quotient(states, transitions, F, "future_events"),
    }
    if F == frozenset((0, 1)):
        predicted_histogram = predicted_future_nonsink_class_histogram(n)
        predicted_histogram_classes = sum(predicted_histogram.values())
        predicted_histogram_states = sum(
            size * count for size, count in predicted_histogram.items())
        histogram_conservation = predicted_histogram_conservation(
            n, report["full_summary"]["registered_state_count"])
        observed_histogram = Counter({
            int(size): count for size, count in
            report["future_events"]["class_size_histogram"].items()})
        sink_size = report["future_events"]["terminal_class_size"]
        observed_histogram[sink_size] -= 1
        if observed_histogram[sink_size] == 0:
            del observed_histogram[sink_size]
        registered_rank_one_states = sum(
            state[1] is not None and len(state[0]) == 1 for state in states)
        expected_nonsink_states = (
            registerable_placement_count(n)
            + report["full_summary"]["registered_state_count"]
            - registered_rank_one_summary_count(n))
        report["candidate_counts"] = {
            "R_n": registerable_placement_count(n),
            "rank_one_transition_count": rank_one_transition_count(n),
            "A_n_sum": registered_nonterminal_placement_count(n),
            "A_n_closed": registered_nonterminal_placement_count_closed(n),
            "U_n_closed": future_quotient_candidate_bound_closed(n),
            "registered_rank_one_summary_count":
                registered_rank_one_summary_count(n),
            "chain_extension_counts": {
                str(r): chain_extension_count(r) for r in range(n - 2)},
            "future_quotient_candidate_bound":
                future_quotient_candidate_bound(n),
            "full_summary_quotient_candidate_bound": (
                report["full_summary"]["registered_state_count"]
                + registerable_placement_count(n) + 1),
            "full_summary_quotient_equals_candidate_bound": (
                report["full_summary"]["class_count"]
                == report["full_summary"]["registered_state_count"]
                + registerable_placement_count(n) + 1),
            "future_quotient_equals_candidate_bound": (
                report["future_events"]["class_count"]
                == future_quotient_candidate_bound(n)),
            "predicted_future_nonsink_class_histogram": predicted_histogram,
            "observed_future_nonsink_class_histogram":
                dict(sorted(observed_histogram.items())),
            "finite_histograms_match": (
                predicted_histogram == dict(sorted(observed_histogram.items()))),
            "predicted_histogram_class_count": predicted_histogram_classes,
            "predicted_histogram_expected_class_count": (
                histogram_conservation["expected_class_count"]),
            "predicted_histogram_class_count_matches": (
                predicted_histogram_classes
                == registerable_placement_count(n)
                + registered_nonterminal_placement_count(n)),
            "predicted_histogram_weighted_state_count":
                predicted_histogram_states,
            "predicted_histogram_expected_state_count":
                histogram_conservation["expected_state_count"],
            "observed_nonsink_state_count": (
                report["full_summary"]["registerable_preregistration_state_count"]
                + report["full_summary"]["registered_state_count"]
                - registered_rank_one_states),
            "registered_rank_one_count_matches": (
                registered_rank_one_states
                == registered_rank_one_summary_count(n)),
            "predicted_histogram_weighted_count_matches": (
                predicted_histogram_states == expected_nonsink_states
                == report["full_summary"][
                    "registerable_preregistration_state_count"]
                + report["full_summary"]["registered_state_count"]
                - registered_rank_one_states),
            "R_n_equals_n_times_rank_one_minus_one": (
                registerable_placement_count(n)
                == n * (rank_one_transition_count(n) - 1)),
        }
    return report


def census(max_n=7, min_n=3, F=(0, 1), *, max_states=None):
    return [quotient_report(n, F, max_states=max_states)
            for n in range(min_n, max_n + 1)]


def _future_trace(n, F, state, word):
    """Return the complete per-letter Mealy trace, including ``None`` outputs."""
    F = frozenset(F)
    trace = []
    for index, letter in enumerate(word):
        next_state = search.successor(n, F, state, letter)
        event = _event_output(F, state, next_state)
        trace.append({"index": index, "letter": letter, "event": event})
        state = next_state
    return trace


def _run_future_word(n, F, state, word):
    """Replay a raw word and return its endpoint and event trace."""
    F = frozenset(F)
    current = state
    events = []
    for letter in word:
        following = search.successor(n, F, current, letter)
        events.append(_event_output(F, current, following))
        current = following
    return current, tuple(events)


def _future_category(state, registerable, F):
    """Return the three-category key used by the constructive certificate."""
    if state[1] is None:
        return "registerable" if state in registerable else "sink"
    return "registered" if len(state[0]) > 1 else "sink"


def _registered_carrier_site(n, state, F):
    """Return the physical site of a registered selected carrier."""
    carrier_sites = [
        position for position, packet in state[0]
        if F <= frozenset(packet)
    ]
    if len(carrier_sites) != 1:
        raise ValueError("registered state must have one selected carrier")
    return carrier_sites[0]


def constructive_distinguishing_suffix(n, left, right, F=(0, 1)):
    """Construct a bounded suffix for two different future-event classes.

    The construction uses only the all-parameter probes from the theorem
    package: ``V_x`` for a registerable preregistration state and the finite
    ``W_q`` family for registered nonterminal placements.  It returns a
    dictionary with the word, method, traces, endpoints, and the proof bound.
    ``None`` is returned for two states in the same future-event class.
    """
    F = search.validate_input(n, F)
    if F != frozenset((0, 1)):
        raise ValueError("the constructive certificate is for F={0,1}")
    if left == right:
        return None

    # Registerability is a semantic property of the reachable graph.  Build
    # it from the pair's reachable component, which keeps this helper useful
    # in small independent audits without exposing quotient block labels.
    distances, _parent = search.bfs_distances(
        n, F, retain_predecessors=False)
    states = list(distances)
    if left not in distances or right not in distances:
        raise ValueError("both states must be reachable from the identity seed")
    transitions = {
        (state, letter): search.successor(n, F, state, letter)
        for state in states for letter in search.RAW_LETTERS
    }
    registerable = _registerable_states(states, transitions)
    left_category = _future_category(left, registerable, F)
    right_category = _future_category(right, registerable, F)

    return _constructive_suffix_from_categories(
        n, left, right, F, left_category, right_category)


def _constructive_suffix_from_categories(
        n, left, right, F, left_category, right_category):
    """Internal constructive separator with graph classification supplied."""
    if left == right:
        return None

    def finish(word, method, bound):
        left_end, left_trace = _run_future_word(n, F, left, word)
        right_end, right_trace = _run_future_word(n, F, right, word)
        if left_trace == right_trace:
            return None
        return {
            "word": word,
            "method": method,
            "bound": bound,
            "left_trace": left_trace,
            "right_trace": right_trace,
            "left_endpoint": left_end,
            "right_endpoint": right_end,
        }

    # Same-category preregistration pairs use the smaller forward gap as the
    # target.  A same-trace endpoint collision is then handled by W_q.
    if left_category == right_category == "registerable":
        def source_gap(state):
            positions = {
                frozenset(packet): position for position, packet in state[0]
            }
            return ((positions[frozenset((1,))]
                     - positions[frozenset((0,))]) % n)

        if source_gap(left) <= source_gap(right):
            target, other = left, right
        else:
            target, other = right, left
        registration_word = explicit_first_registration_probe(n, target, F)
        target_end, target_trace = _run_future_word(
            n, F, target, registration_word)
        other_end, other_trace = _run_future_word(
            n, F, other, registration_word)
        if target_trace != other_trace:
            return finish(registration_word, "V", 3 * n - 6)
        if target_end[1] is None or other_end[1] is None:
            raise AssertionError("equal V traces must register both endpoints")
        for q in range(n):
            probe = "p" * ((-q) % n) + "d" + "pd" * (n - 2)
            candidate = finish(registration_word + probe, "V+W", 6 * n - 10)
            if candidate is not None:
                return candidate
        return None

    # Registered placement pairs are separated by the finite W_q family.
    if left_category == right_category == "registered":
        for q in range(n):
            probe = "p" * ((-q) % n) + "d" + "pd" * (n - 2)
            candidate = finish(probe, "W", 3 * n - 4)
            if candidate is not None:
                return candidate
        return None

    # Cross-category pairs use the event-type distinction first.  For a
    # preregistration/registered pair, if V produces the same registration
    # trace, continue from both registered endpoints with the W family.  This
    # mirrors the proof and preserves the 6n-10 concatenated bound.
    if left_category == "registerable" and right_category == "registered":
        registration_word = explicit_first_registration_probe(n, left, F)
        left_end, left_trace = _run_future_word(
            n, F, left, registration_word)
        right_end, right_trace = _run_future_word(
            n, F, right, registration_word)
        if left_trace != right_trace:
            return finish(registration_word, "V", 3 * n - 6)
        for q in range(n):
            probe = "p" * ((-q) % n) + "d" + "pd" * (n - 2)
            candidate = finish(
                registration_word + probe, "V+W", 6 * n - 10)
            if candidate is not None:
                return candidate
        return None
    if left_category == "registered" and right_category == "registerable":
        result = _constructive_suffix_from_categories(
            n, right, left, F, right_category, left_category)
        if result is not None:
            result["left_trace"], result["right_trace"] = (
                result["right_trace"], result["left_trace"])
            result["left_endpoint"], result["right_endpoint"] = (
                result["right_endpoint"], result["left_endpoint"])
        return result
    if left_category == "registerable":
        word = explicit_first_registration_probe(n, left, F)
        candidate = finish(word, "V", 3 * n - 6)
        if candidate is not None:
            return candidate
    if right_category == "registerable":
        word = explicit_first_registration_probe(n, right, F)
        candidate = finish(word, "V", 3 * n - 6)
        if candidate is not None:
            return candidate
    if left_category == "registered":
        q = _registered_carrier_site(n, left, F)
        word = "p" * ((-q) % n) + "d" + "pd" * (n - 2)
        candidate = finish(word, "W", 3 * n - 4)
        if candidate is not None:
            return candidate
    if right_category == "registered":
        q = _registered_carrier_site(n, right, F)
        word = "p" * ((-q) % n) + "d" + "pd" * (n - 2)
        candidate = finish(word, "W", 3 * n - 4)
        if candidate is not None:
            return candidate
    return None


def constructive_distinguishing_audit(n, F=(0, 1)):
    """Audit the constructive certificate on every candidate class pair.

    One representative is retained for every normal-form placement and one
    for the sink.  The returned counts therefore test every pair of candidate
    future-event classes, rather than merely comparing quotient cardinalities.
    """
    F = search.validate_input(n, F)
    states_by_distance, _parent = search.bfs_distances(
        n, F, retain_predecessors=False)
    states = list(states_by_distance)
    transitions = {
        (state, letter): search.successor(n, F, state, letter)
        for state in states for letter in search.RAW_LETTERS
    }
    registerable = _registerable_states(states, transitions)
    representatives = {}
    sink = None
    for state in states:
        category = _future_category(state, registerable, F)
        if category == "sink":
            sink = sink or state
        else:
            representatives.setdefault((category, state[0]), state)
    if sink is None:
        raise AssertionError("reachable graph must contain a future-event sink")
    candidates = [sink] + list(representatives.values())
    checked = 0
    failures = []
    max_length = 0
    for index, left in enumerate(candidates):
        for right in candidates[index + 1:]:
            left_category = _future_category(left, registerable, F)
            right_category = _future_category(right, registerable, F)
            result = _constructive_suffix_from_categories(
                n, left, right, F, left_category, right_category)
            checked += 1
            if result is None:
                failures.append((left, right))
                continue
            max_length = max(max_length, len(result["word"]))
            if len(result["word"]) > result["bound"]:
                failures.append((left, right, "probe-specific-bound"))
            if len(result["word"]) > 6 * n - 10:
                failures.append((left, right, "length"))
            if result["left_trace"] == result["right_trace"]:
                failures.append((left, right, "trace"))
    return {
        "n": n,
        "candidate_classes": len(candidates),
        "checked_pairs": checked,
        "failures": len(failures),
        "max_constructed_length": max_length,
        "length_bound": 6 * n - 10,
    }


def shortest_distinguishing_suffix(states, transitions, F, left, right,
                                   observer="future_events"):
    """Return a shortest common raw suffix distinguishing two states.

    Returns ``None`` if the states are equivalent under the selected observer.
    For ``full_summary``, the empty suffix may distinguish current outputs.
    """
    F = frozenset(F)
    if observer not in ("future_events", "full_summary"):
        raise ValueError("unknown observer")
    if observer == "full_summary" and left != right:
        left_output = None if left[1] is None else left
        right_output = None if right[1] is None else right
        if left_output != right_output:
            return ""

    queue = deque([(left, right, "")])
    visited = {(left, right)}
    while queue:
        left_state, right_state, prefix = queue.popleft()
        for letter in search.RAW_LETTERS:
            next_left = transitions[(left_state, letter)]
            next_right = transitions[(right_state, letter)]
            if observer == "future_events":
                left_output = _event_output(F, left_state, next_left)
                right_output = _event_output(F, right_state, next_right)
                if left_output != right_output:
                    return prefix + letter
            else:
                left_output = None if next_left[1] is None else next_left
                right_output = None if next_right[1] is None else next_right
                if left_output != right_output:
                    return prefix + letter
            pair = (next_left, next_right)
            if pair not in visited:
                visited.add(pair)
                queue.append((next_left, next_right, prefix + letter))
    return None


def shortest_registration_distinguishing_suffix(states, transitions, F,
                                                 left, right):
    """Find a suffix distinguished by the first registration event alone.

    The search stops once both states register on the same letter: any later
    selected-absorption output belongs to the post-registration probe and is
    intentionally excluded from this diagnostic.
    """
    F = frozenset(F)
    if left[1] is not None or right[1] is not None:
        raise ValueError("registration-only search requires pre-registration states")
    queue = deque([(left, right, "")])
    visited = {(left, right)}
    while queue:
        left_state, right_state, prefix = queue.popleft()
        for letter in search.RAW_LETTERS:
            next_left = transitions[(left_state, letter)]
            next_right = transitions[(right_state, letter)]
            left_output = (_event_output(F, left_state, next_left)
                           if left_state[1] is None else None)
            right_output = (_event_output(F, right_state, next_right)
                            if right_state[1] is None else None)
            if left_output != right_output:
                return prefix + letter
            if left_output is not None:
                # Equal registration output: this diagnostic has reached its
                # boundary and does not inspect later selected absorptions.
                continue
            pair = (next_left, next_right)
            if pair not in visited:
                visited.add(pair)
                queue.append((next_left, next_right, prefix + letter))
    return None


def shortest_first_registration_prefix(n, F, state):
    """Return a shortest word on which a preregistration state registers.

    The returned word ends on the first registration transition from
    ``state``.  ``None`` means that the state is not registerable.
    """
    F = search.validate_input(n, F)
    if state[1] is not None:
        raise ValueError("first-registration search requires a preregistration state")
    queue = deque([state])
    parent = {state: None}
    while queue:
        current = queue.popleft()
        for letter in search.RAW_LETTERS:
            following = search.successor(n, F, current, letter)
            if current[1] is None and following[1] is not None:
                letters = [letter]
                cursor = current
                while parent[cursor] is not None:
                    previous, previous_letter = parent[cursor]
                    letters.append(previous_letter)
                    cursor = previous
                return "".join(reversed(letters)), following
            if following not in parent:
                parent[following] = (current, letter)
                queue.append(following)
    return None


def explicit_first_registration_probe(n, state, F=(0, 1)):
    """Return the gap probe V_x for a registerable preregistration state.

    If ``a`` and ``b`` are the physical sites of singleton sources 0 and 1,
    respectively, ``g=(b-a) mod n`` is their forward gap.  Source order and
    registerability imply ``1 <= g <= n-2``; the returned raw word is
    ``p^([1-b]_n)(dp)^(g-1)d``.
    """
    F = search.validate_input(n, F)
    if F != frozenset((0, 1)) or state[1] is not None:
        raise ValueError("the explicit gap probe is for preregistration F={0,1}")
    positions = {
        frozenset(packet): position for position, packet in state[0]
    }
    singleton_zero = frozenset((0,))
    singleton_one = frozenset((1,))
    if singleton_zero not in positions or singleton_one not in positions:
        raise ValueError("sources 0 and 1 must remain singleton packets")
    a, b = positions[singleton_zero], positions[singleton_one]
    gap = (b - a) % n
    if not 1 <= gap <= n - 2:
        raise ValueError("source-order gap is not a proper adjacent gap")
    return "p" * ((1 - b) % n) + "dp" * (gap - 1) + "d"


def explicit_registration_coalescence_census(n, F=(0, 1)):
    """Audit the exact coalescence fibers of the explicit gap probes V_x.

    This finite control checks that the distinct comparisons coalescing under
    ``V_x`` are exactly the placements obtained by moving singleton source 1
    into one of the preceding holes, keeping every other packet fixed.
    """
    F = search.validate_input(n, F)
    states_by_distance, _parent = search.bfs_distances(
        n, F, retain_predecessors=False)
    states = list(states_by_distance)
    transitions = {
        (state, letter): search.successor(n, F, state, letter)
        for state in states for letter in search.RAW_LETTERS
    }
    registerable = sorted(
        (state for state in _registerable_states(states, transitions)
         if state[1] is None), key=repr)
    gaps = {}
    probes = {}
    predicted_rights = {}
    for state in registerable:
        state_positions = {
            frozenset(packet): position for position, packet in state[0]
        }
        a = state_positions[frozenset((0,))]
        b = state_positions[frozenset((1,))]
        gaps[state] = (b - a) % n
        probes[state] = explicit_first_registration_probe(n, state, F)
        predicted_rights[state] = set()
        for h in range(1, gaps[state]):
            moved = {
                site: packet for site, packet in state[0] if packet != (1,)
            }
            moved[(a + h) % n] = (1,)
            predicted_rights[state].add(
                (tuple(sorted(moved.items())), state[1], state[2]))

    coalescences = 0
    direction_violations = 0
    shape_violations = 0
    registerable_set = set(registerable)
    unreachable_predicted = sum(
        len(rights - registerable_set) for rights in predicted_rights.values()
    )
    bidirectional_pairs = set()
    directed_edges = set()
    for left in registerable:
        word = probes[left]
        for right in registerable:
            if left == right:
                continue
            left_state, right_state = left, right
            traces_equal = True
            for letter in word:
                left_next = transitions[(left_state, letter)]
                right_next = transitions[(right_state, letter)]
                if _event_output(F, left_state, left_next) != _event_output(
                        F, right_state, right_next):
                    traces_equal = False
                left_state, right_state = left_next, right_next
            coalesces = traces_equal and left_state[0] == right_state[0]
            if coalesces != (right in predicted_rights[left]):
                shape_violations += 1
            if coalesces:
                coalescences += 1
                directed_edges.add((left, right))
                if not gaps[right] < gaps[left]:
                    direction_violations += 1
                if (right, left) in directed_edges:
                    bidirectional_pairs.add(frozenset((left, right)))
    expected = 0 if n == 3 else n * comb(2 * n - 4, n - 4)
    return {
        "n": n,
        "registerable_states": len(registerable),
        "directed_coalescences": coalescences,
        "closed_form_directed_coalescences": expected,
        "direction_violations": direction_violations,
        "shape_violations": shape_violations,
        "unreachable_predicted": unreachable_predicted,
        "bidirectional_pairs": len(bidirectional_pairs),
    }


def first_registration_prefix_comparison(n, F, left, right, *, prefix=None):
    """Classify one target's shortest first-registration prefix on a pair.

    ``left`` must be preregistration and registerable.  The result separates
    an already different event trace, different post-registration placements,
    and exact placement coalescence.  This is a diagnostic for the proposed
    non-coalescence lemma, not a proof that some successful prefix exists.
    """
    F = search.validate_input(n, F)
    if left[1] is not None or right[1] is not None:
        raise ValueError("comparison requires two preregistration states")
    if prefix is None:
        result = shortest_first_registration_prefix(n, F, left)
        if result is None:
            return None
        prefix, left_terminal = result
    else:
        left_terminal = None

    left_state, right_state = left, right
    left_trace, right_trace = [], []
    registered_left_before_final = False
    for index, letter in enumerate(prefix):
        left_next = search.successor(n, F, left_state, letter)
        right_next = search.successor(n, F, right_state, letter)
        left_trace.append(_event_output(F, left_state, left_next))
        right_trace.append(_event_output(F, right_state, right_next))
        left_state, right_state = left_next, right_next
        if index < len(prefix) - 1 and left_state[1] is not None:
            registered_left_before_final = True

    if left_terminal is not None and left_state != left_terminal:
        raise AssertionError("registration prefix replay disagrees with search")
    if not prefix or left_state[1] is None or registered_left_before_final:
        raise AssertionError("prefix does not end at first registration of left")

    traces_differ = left_trace != right_trace
    both_registered = left_state[1] is not None and right_state[1] is not None
    placements_differ = (both_registered
                         and left_state[0] != right_state[0])
    if traces_differ:
        case = "different_trace"
    elif not both_registered:
        raise AssertionError("equal traces require matching final registration")
    elif placements_differ:
        case = "different_registered_placement"
    else:
        case = "coalesced_same_placement"
    return {
        "word": prefix,
        "case": case,
        "trace_equal": not traces_differ,
        "left_terminal": left_state,
        "right_terminal": right_state,
        "placements_differ": placements_differ,
        "left_trace": tuple(left_trace),
        "right_trace": tuple(right_trace),
    }


def first_registration_noncoalescence_census(n, F=(0, 1), *, max_pairs=None):
    """Finite diagnostic over registerable preregistration state pairs.

    For each unordered pair, test the shortest first-registration prefix in
    both orientations.  The output records whether either orientation avoids
    same-placement coalescence; it is bounded evidence only.
    """
    F = search.validate_input(n, F)
    states_by_distance, _parent = search.bfs_distances(
        n, F, retain_predecessors=False)
    states = list(states_by_distance)
    transitions = {
        (state, letter): search.successor(n, F, state, letter)
        for state in states for letter in search.RAW_LETTERS
    }
    registerable = sorted(
        (state for state in _registerable_states(states, transitions)
         if state[1] is None), key=repr)
    prefixes = {}
    cases = Counter()
    pairs_with_noncoalescing_orientation = 0
    checked_pairs = 0
    for index, left in enumerate(registerable):
        for right in registerable[index + 1:]:
            if max_pairs is not None and checked_pairs >= max_pairs:
                return {
                    "n": n,
                    "registerable_states": len(registerable),
                    "checked_pairs": checked_pairs,
                    "total_pairs": len(registerable) * (len(registerable) - 1) // 2,
                    "truncated": True,
                    "orientation_cases": dict(sorted(cases.items())),
                    "pairs_with_noncoalescing_orientation":
                        pairs_with_noncoalescing_orientation,
                }
            checked_pairs += 1
            pair_has_noncoalescing = False
            for target, comparison in ((left, right), (right, left)):
                if target not in prefixes:
                    prefixes[target] = shortest_first_registration_prefix(
                        n, F, target)
                prefix_result = prefixes[target]
                if prefix_result is None:
                    cases["target_not_registerable"] += 1
                    continue
                result = first_registration_prefix_comparison(
                    n, F, target, comparison, prefix=prefix_result[0])
                cases[result["case"]] += 1
                pair_has_noncoalescing |= result["case"] != "coalesced_same_placement"
            pairs_with_noncoalescing_orientation += pair_has_noncoalescing
    return {
        "n": n,
        "registerable_states": len(registerable),
        "checked_pairs": checked_pairs,
        "total_pairs": len(registerable) * (len(registerable) - 1) // 2,
        "truncated": False,
        "orientation_cases": dict(sorted(cases.items())),
        "pairs_with_noncoalescing_orientation":
            pairs_with_noncoalescing_orientation,
    }


def adjacent_registerable_placement_count(n):
    """Count the registerable preregistration placements used by the probe lemma.

    These are the states in which singleton sources 0 and 1 occupy adjacent
    positions in source order.  This is a deliberately restricted subfamily;
    it is not the full ``R_n`` census.
    """
    if n < 3:
        raise ValueError("n must be at least 3")
    return n * comb(2 * n - 5, n - 3)


def adjacent_registration_probe(n, state, F=(0, 1)):
    """Return the raw registration-plus-carrier-sweep probe for one state.

    The state must be preregistration, with singleton 0 and 1 at consecutive
    positions q and q+1.  After rotation and registration, ``(pd)^(n-2)``
    repeatedly returns the carrier to port 0 and records each outside packet
    when it reaches port 1.  This is a constructive probe for this subfamily,
    not a separator for arbitrary preregistration placements.
    """
    F = search.validate_input(n, F)
    if F != frozenset((0, 1)) or state[1] is not None:
        raise ValueError("the probe is for preregistration F={0,1} states")
    positions = {frozenset(packet): position for position, packet in state[0]}
    if positions.get(frozenset((0,))) is None:
        raise ValueError("source 0 must remain a singleton")
    if positions.get(frozenset((1,))) is None:
        raise ValueError("source 1 must remain a singleton")
    q = positions[frozenset((0,))]
    if positions[frozenset((1,))] != (q + 1) % n:
        raise ValueError("source singletons are not adjacent in source order")
    return "p" * ((-q) % n) + "d" + "pd" * (n - 2)


def aligned_registered_probe(n, state, F=(0, 1)):
    """Return the aligned sweep probe for a registered nonterminal state.

    The carrier is first rotated from its current site ``q`` to site 0.  The
    initial ``d`` records the packet at normalized site 1, if any; the
    following ``(pd)^(n-2)`` records normalized sites n-1 through 2.  Full
    selected-event records make this probe injective among placements with a
    common carrier site.  This helper deliberately does not claim to separate
    placements whose carrier sites differ.
    """
    F = search.validate_input(n, F)
    if state[1] is None:
        raise ValueError("the aligned sweep requires a registered state")
    carrier_sites = [position for position, packet in state[0]
                     if F <= frozenset(packet)]
    if len(carrier_sites) != 1:
        raise ValueError("registered state must have one F-carrier")
    if len(state[0]) <= 1:
        raise ValueError("the aligned sweep requires an outside packet")
    q = carrier_sites[0]
    return "p" * ((-q) % n) + "d" + "pd" * (n - 2)


def outside_anchor_registered_probe(n, state, q, F=(0, 1)):
    """Return ``W_q`` when ``q`` is an outside-packet site.

    Unlike :func:`aligned_registered_probe`, this probe deliberately anchors
    at an outside packet. Its first selected full event recovers the carrier
    phase, including when a comparison state has different occupancy at the
    anchor site.
    """
    F = search.validate_input(n, F)
    if state[1] is None or len(state[0]) <= 1:
        raise ValueError("require a registered nonterminal state")
    outside_sites = [
        position for position, packet in state[0]
        if not (F <= frozenset(packet))
    ]
    if q not in outside_sites:
        raise ValueError("q must contain an outside packet")
    return "p" * ((-q) % n) + "d" + "pd" * (n - 2)


def registered_probe_family_signature(n, state, F=(0, 1)):
    """Return traces for every phase-aligned probe ``W_q``.

    The finite family is an all-parameter separator for registered
    nonterminal placements when combined with the aligned-sweep and
    outside-anchor phase lemmas.  The remaining future-quotient uncertainty
    is confined to the registerable pre-registration placements.
    """
    F = search.validate_input(n, F)
    if state[1] is None or len(state[0]) <= 1:
        raise ValueError("require a registered nonterminal state")
    return tuple(
        tuple(entry["event"]
              for entry in _future_trace(
                  n, F, state, "p" * ((-q) % n) + "d" + "pd" * (n - 2)))
        for q in range(n)
    )


def distinguishing_example_report(n=7, F=(0, 1), *, max_pairs=64):
    """Search sampled candidate pairs for shortest future-event separators."""
    F = search.validate_input(n, F)
    states_by_distance, _parent = search.bfs_distances(
        n, F, retain_predecessors=False)
    states = list(states_by_distance)
    transitions = {
        (state, letter): search.successor(n, F, state, letter)
        for state in states for letter in search.RAW_LETTERS
    }
    registerable = _registerable_states(states, transitions)
    prereg = sorted(
        {state for state in registerable if state[1] is None}, key=repr)
    registered = sorted(
        {state for state in states
         if state[1] is not None and len(state[0]) > 1}, key=repr)

    def find_pair(candidates, predicate):
        checked = 0
        for i, left in enumerate(candidates):
            for right in candidates[i + 1:]:
                if not predicate(left, right):
                    continue
                checked += 1
                suffix = shortest_distinguishing_suffix(
                    states, transitions, F, left, right)
                if suffix is not None:
                    return left, right, suffix, checked
                if checked >= max_pairs:
                    return left, right, None, checked
        return None, None, None, checked

    examples = {}
    left, right, suffix, checked = find_pair(
        prereg, lambda x, y: x[0] != y[0])
    examples["registerable_preregistration"] = {
        "left_state": repr(left), "right_state": repr(right),
        "shortest_suffix": suffix, "pairs_checked": checked,
        "registration_only_suffix": (
            shortest_registration_distinguishing_suffix(
                states, transitions, F, left, right)
            if left is not None else None),
        "left_event_trace": _future_trace(n, F, left, suffix or ""),
        "right_event_trace": _future_trace(n, F, right, suffix or ""),
    } if left is not None else {"shortest_suffix": None, "pairs_checked": 0}

    post_registration_probe = None
    if n <= 5:
        for i, candidate_left in enumerate(prereg):
            for candidate_right in prereg[i + 1:]:
                registration_suffix = shortest_registration_distinguishing_suffix(
                    states, transitions, F, candidate_left, candidate_right)
                if registration_suffix is not None:
                    continue
                full_suffix = shortest_distinguishing_suffix(
                    states, transitions, F, candidate_left, candidate_right)
                if full_suffix is None:
                    continue
                post_registration_probe = {
                    "left_state": repr(candidate_left),
                    "right_state": repr(candidate_right),
                    "shortest_suffix": full_suffix,
                    "registration_only_suffix": None,
                    "left_event_trace": _future_trace(
                        n, F, candidate_left, full_suffix),
                    "right_event_trace": _future_trace(
                        n, F, candidate_right, full_suffix),
                }
                break
            if post_registration_probe is not None:
                break
    examples["registration_requires_post_event_probe"] = post_registration_probe

    left, right, suffix, checked = find_pair(
        registered, lambda x, y: x[0] != y[0])
    examples["registered_distinct_placements"] = {
        "left_state": repr(left), "right_state": repr(right),
        "shortest_suffix": suffix, "pairs_checked": checked,
        "registration_only_suffix": None,
        "left_event_trace": _future_trace(n, F, left, suffix or ""),
        "right_event_trace": _future_trace(n, F, right, suffix or ""),
    } if left is not None else {"shortest_suffix": None, "pairs_checked": 0}

    by_placement = defaultdict(list)
    for state in states:
        if state[1] is not None and len(state[0]) > 1:
            by_placement[state[0]].append(state)
    history_pair = next(((left, right) for members in by_placement.values()
                         for i, left in enumerate(members)
                         for right in members[i + 1:]
                         if left[2] != right[2]), None)
    if history_pair is None:
        examples["same_placement_different_selected_history"] = {
            "equivalent_for_future_events": None}
    else:
        left, right = history_pair
        suffix = shortest_distinguishing_suffix(
            states, transitions, F, left, right)
        examples["same_placement_different_selected_history"] = {
            "left_state": repr(left), "right_state": repr(right),
            "shortest_suffix": suffix,
            "equivalent_for_future_events": suffix is None,
        }
    return {"n": n, "F": sorted(F), "examples": examples}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=3)
    parser.add_argument("--max-n", type=int, default=7)
    parser.add_argument("--F", nargs="+", type=int, default=[0, 1])
    parser.add_argument("--max-states", type=int, default=None)
    parser.add_argument("--distinguishing-examples", action="store_true")
    parser.add_argument(
        "--constructive-distinguishing-audit", action="store_true")
    parser.add_argument("--first-registration-audit", action="store_true")
    parser.add_argument("--max-pairs", type=int, default=64)
    args = parser.parse_args(argv)
    if args.constructive_distinguishing_audit:
        result = [constructive_distinguishing_audit(n, args.F)
                  for n in range(args.min_n, args.max_n + 1)]
    elif args.first_registration_audit:
        result = first_registration_noncoalescence_census(
            args.max_n, args.F, max_pairs=args.max_pairs)
    elif args.distinguishing_examples:
        result = distinguishing_example_report(
            args.max_n, args.F, max_pairs=args.max_pairs)
    else:
        result = census(args.max_n, args.min_n, args.F,
                        max_states=args.max_states)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
