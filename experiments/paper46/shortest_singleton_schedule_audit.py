"""Bounded audit of shortest words for the all-upper singleton endpoint.

The target has singleton packets, so no prefix of a realizing word can contain
an effective fusion.  The reverse graph below therefore keeps only singleton
placements and reverses the five guarded generators.  This gives an exact
finite check of all shortest words at the tested values of ``n``; it is not an
all-parameter proof.
"""

from __future__ import annotations

from typing import Iterator, TypeAlias


Atom: TypeAlias = int | None
Layer: TypeAlias = tuple[Atom, ...]
Placement: TypeAlias = tuple[Layer, Layer]
Action: TypeAlias = str

def seed(n: int) -> Placement:
    return (tuple(range(n)), (None,) * n)


def target(n: int) -> Placement:
    upper: list[Atom] = [None] * n
    upper[n - 1] = 0
    for atom in range(1, n):
        upper[atom - 1] = atom
    return ((None,) * n, tuple(upper))


def _inverse_rotate(layer: Layer) -> Layer:
    """Undo the model's forward rotation (old site ``i`` moves to ``i+1``)."""

    return layer[1:] + layer[:1]


def _swap_hole(layer: Layer) -> Layer | None:
    """Undo a nonfusing ``d`` when its forward predecessor is determined."""

    if layer[0] is None or layer[1] is not None:
        return None
    previous = list(layer)
    previous[0], previous[1] = None, previous[0]
    return tuple(previous)


def predecessors(state: Placement) -> Iterator[tuple[Action, Placement]]:
    """Yield all singleton-state predecessors of ``state``.

    No-op defects are omitted: inserting one would make a word strictly longer
    without changing the state, and an effective fusion cannot be undone while
    the target remains injective.
    """

    lower, upper = state
    yield "p0", (_inverse_rotate(lower), upper)
    yield "p1", (lower, _inverse_rotate(upper))

    previous_lower = _swap_hole(lower)
    if previous_lower is not None:
        yield "d0", (previous_lower, upper)

    previous_upper = _swap_hole(upper)
    if previous_upper is not None:
        yield "d1", (lower, previous_upper)

    if lower[0] is None and upper[0] is not None:
        previous_lower = list(lower)
        previous_upper = list(upper)
        previous_lower[0], previous_upper[0] = previous_upper[0], None
        yield "v", (tuple(previous_lower), tuple(previous_upper))


def reverse_layers(n: int, depth: int) -> list[set[Placement]]:
    """Return states that can reach the target in each exact reverse depth."""

    layers: list[set[Placement]] = [{target(n)}]
    for _ in range(depth):
        previous: set[Placement] = set()
        for state in layers[-1]:
            previous.update(previous_state for _, previous_state in predecessors(state))
        layers.append(previous)
    return layers


def shortest_words(n: int) -> list[tuple[Action, ...]]:
    """Enumerate all shortest target words for the small audit range."""

    if n < 2:
        raise ValueError("RSR-2 requires n >= 2")
    depth = 3 * n - 2
    reverse = reverse_layers(n, depth)
    start = seed(n)
    forward: list[set[Placement]] = [{start}]
    for _ in range(depth):
        next_layer: set[Placement] = set()
        for state in forward[-1]:
            for _, successor in successors(state):
                next_layer.add(successor)
        forward.append(next_layer)
    if start not in reverse[depth]:
        return []

    words: list[tuple[Action, ...]] = []

    def visit(current: Placement, distance: int, suffix: list[Action]) -> None:
        if distance == depth:
            assert current == start
            words.append(tuple(reversed(suffix)))
            return
        for action, previous in predecessors(current):
            if (previous in reverse[distance + 1] and
                    previous in forward[depth - distance - 1]):
                visit(previous, distance + 1, suffix + [action])

    visit(target(n), 0, [])
    return words


def successors(state: Placement) -> Iterator[tuple[Action, Placement]]:
    """Yield singleton-state successors, omitting no-op defects and fusions."""

    lower, upper = state
    yield "p0", (tuple((lower[-1],) + lower[:-1]), upper)
    yield "p1", (lower, tuple((upper[-1],) + upper[:-1]))
    if lower[0] is None and lower[1] is not None:
        next_lower = list(lower)
        next_lower[0], next_lower[1] = next_lower[1], None
        yield "d0", (tuple(next_lower), upper)
    if upper[0] is None and upper[1] is not None:
        next_upper = list(upper)
        next_upper[0], next_upper[1] = next_upper[1], None
        yield "d1", (lower, tuple(next_upper))
    if lower[0] is not None and upper[0] is None:
        next_lower = list(lower)
        next_upper = list(upper)
        next_lower[0], next_upper[0] = None, next_lower[0]
        yield "v", (tuple(next_lower), tuple(next_upper))


def rotation_family_word(n: int, choices: tuple[bool, ...]) -> tuple[Action, ...]:
    if len(choices) != n - 1:
        raise ValueError("one choice is required for each transfer round")
    word: list[Action] = ["v"]
    for swap in choices:
        word.extend(("p1", "p0") if swap else ("p0", "p1"))
        word.append("v")
    return tuple(word)


def is_rotation_family_word(word: tuple[Action, ...], n: int) -> bool:
    if len(word) != 3 * n - 2 or word[0] != "v":
        return False
    for index in range(n - 1):
        start = 1 + 3 * index
        if word[start + 2] != "v":
            return False
        if word[start : start + 2] not in (("p0", "p1"), ("p1", "p0")):
            return False
    return True


def audit(n_values: range = range(2, 8)) -> dict[int, list[tuple[Action, ...]]]:
    results: dict[int, list[tuple[Action, ...]]] = {}
    for n in n_values:
        words = shortest_words(n)
        results[n] = words
        expected = 2 ** (n - 1)
        if n >= 3:
            assert len(words) == expected
            assert all(is_rotation_family_word(word, n) for word in words)
        else:
            assert len(words) == 4
            assert any("d0" in word for word in words)
        assert all(len(word) == 3 * n - 2 for word in words)
    return results


if __name__ == "__main__":
    for n, words in audit().items():
        print(f"n={n}: shortest_words={len(words)}")
        for word in words:
            print("  " + " ".join(word))
