"""Literal raw-letter model and constructive controls for two-layer RSR-2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, TypeAlias


Packet: TypeAlias = tuple[int, ...]
Action: TypeAlias = tuple[str, int | None]
Word: TypeAlias = tuple[Action, ...]
Layer: TypeAlias = tuple[Packet, ...]


@dataclass(frozen=True)
class Event:
    kind: str
    layer: int | None
    packet: Packet
    left: Packet = ()
    right: Packet = ()


@dataclass(frozen=True)
class State:
    n: int
    layers: tuple[Layer, Layer]
    events: tuple[Event, ...] = ()

    @property
    def partition(self) -> tuple[Packet, ...]:
        packets = [packet for layer in self.layers for packet in layer if packet]
        return tuple(sorted(packets, key=lambda block: (block[0], len(block), block)))


def seed(n: int) -> State:
    if n < 2:
        raise ValueError("RSR-2 controls require n >= 2")
    layer0 = tuple((atom,) for atom in range(n))
    layer1 = ((),) * n
    return State(n, (layer0, layer1))


def _validate_state(state: State) -> None:
    if len(state.layers) != 2 or any(len(layer) != state.n for layer in state.layers):
        raise ValueError("state must have two n-site layers")
    atoms = [atom for layer in state.layers for packet in layer for atom in packet]
    if sorted(atoms) != list(range(state.n)) or len(atoms) != len(set(atoms)):
        raise ValueError("occupied packets must partition the atom set")
    if any(packet != tuple(sorted(packet)) or not packet
           for layer in state.layers for packet in layer if packet):
        raise ValueError("packets must be nonempty and canonically sorted")


def step(state: State, action: Action) -> State:
    kind, layer = action
    if kind in {"p", "d"}:
        if layer not in (0, 1):
            raise ValueError("horizontal generators require layer 0 or 1")
        layers = [list(state.layers[0]), list(state.layers[1])]
        if kind == "p":
            old = layers[layer]
            layers[layer] = [old[-1], *old[:-1]]
            result = State(state.n, (tuple(layers[0]), tuple(layers[1])), state.events)
        else:
            old = layers[layer]
            left, right = old[0], old[1]
            if left and right:
                packet = tuple(sorted((*left, *right)))
                layers[layer][0], layers[layer][1] = packet, ()
                event = Event("fusion", layer, packet, left, right)
                result = State(state.n, (tuple(layers[0]), tuple(layers[1])),
                               state.events + (event,))
            elif right:
                layers[layer][0], layers[layer][1] = right, ()
                result = State(state.n, (tuple(layers[0]), tuple(layers[1])), state.events)
            else:
                result = state
    elif kind == "v" and layer is None:
        source = state.layers[0][0]
        target = state.layers[1][0]
        if not source or target:
            raise ValueError("v requires occupied layer-0/site-0 and empty layer-1/site-0")
        layers = [list(state.layers[0]), list(state.layers[1])]
        layers[0][0], layers[1][0] = (), source
        event = Event("vertical", None, source)
        result = State(state.n, (tuple(layers[0]), tuple(layers[1])),
                       state.events + (event,))
    else:
        raise ValueError(f"unknown RSR-2 generator: {action!r}")
    _validate_state(result)
    return result


def replay(state: State, word: Iterable[Action]) -> State:
    for action in word:
        state = step(state, action)
    return state


def _p(layer: int, count: int) -> list[Action]:
    return [("p", layer)] * count


def _d(layer: int) -> Action:
    return ("d", layer)


def _site_of(state: State, layer: int, packet: Packet) -> int:
    try:
        return state.layers[layer].index(packet)
    except ValueError as error:
        raise ValueError(f"packet {packet} is not on layer {layer}") from error


def load_permutation(n: int, sigma: tuple[int, ...]) -> tuple[State, Word]:
    """Move singleton atoms into layer 1 in the requested site order."""
    if len(sigma) != n or set(sigma) != set(range(n)):
        raise ValueError("sigma must be a permutation of range(n)")
    state = seed(n)
    word: list[Action] = []
    for index, atom in enumerate(reversed(sigma)):
        site = _site_of(state, 0, (atom,))
        turns = (-site) % n
        route = _p(0, turns) + [("v", None)]
        if index < n - 1:
            route += _p(1, 1)
        word.extend(route)
        state = replay(state, route)
    expected = tuple((atom,) for atom in sigma)
    if state.layers != (((),) * n, expected):
        raise AssertionError("permutation-loading construction ended at wrong placement")
    if len(word) > n * n + n - 1:
        raise AssertionError("permutation-loading cost exceeded its bound")
    return state, tuple(word)


def adjacent_fusion_word(state: State, layer: int, left: Packet,
                         right: Packet) -> Word:
    """Fuse source-adjacent ordered packets using an expanded raw word."""
    if layer not in (0, 1) or left == right:
        raise ValueError("fusion requires a layer and two distinct packets")
    q_left = _site_of(state, layer, left)
    q_right = _site_of(state, layer, right)
    gap = (q_right - q_left - 1) % state.n
    for offset in range(1, gap + 1):
        if state.layers[layer][(q_left + offset) % state.n]:
            raise ValueError("ordered parents are not adjacent in cyclic packet order")

    prefix = _p(layer, (-q_left) % state.n)
    if gap == 0:
        routed = prefix
    else:
        routed = prefix + _p(layer, state.n - gap) + [_d(layer)]
        for _ in range(gap - 1):
            routed.extend([("p", layer), _d(layer)])
        routed.append(("p", layer))

    routed_state = replay(state, routed)
    if routed_state.layers[layer][0] != left or routed_state.layers[layer][1] != right:
        raise AssertionError("adjacent-parent route did not establish ordered ports")
    if len(routed_state.events) != len(state.events):
        raise AssertionError("routing prefix caused an unintended fusion or transfer")

    word = tuple(routed + [_d(layer)])
    fused_state = replay(state, word)
    expected = Event("fusion", layer, tuple(sorted((*left, *right))), left, right)
    if fused_state.events[-1] != expected or len(fused_state.events) != len(state.events) + 1:
        raise AssertionError("final d did not create exactly the requested fusion")
    if len(word) > 2 * state.n + gap:
        raise AssertionError("adjacent fusion cost exceeded its bound")
    return word


def _normalize_partition(n: int, blocks: Iterable[Iterable[int]]) -> tuple[Packet, ...]:
    normalized = tuple(tuple(sorted(block)) for block in blocks)
    if any(not block for block in normalized):
        raise ValueError("target blocks must be nonempty")
    atoms = [atom for block in normalized for atom in block]
    if sorted(atoms) != list(range(n)) or len(atoms) != len(set(atoms)):
        raise ValueError("target blocks must partition range(n)")
    return tuple(sorted(normalized, key=lambda block: (block[0], len(block), block)))


def construct_partition(n: int, blocks: Iterable[Iterable[int]]) -> tuple[State, Word]:
    """Construct a terminal state with the requested endpoint partition."""
    target = _normalize_partition(n, blocks)
    sigma = tuple(atom for block in target for atom in block)
    state, loading_word = load_permutation(n, sigma)
    word = list(loading_word)

    for block in target:
        current = [(atom,) for atom in block]
        while len(current) > 1:
            left, right = current[0], current[1]
            route = adjacent_fusion_word(state, 1, left, right)
            state = replay(state, route)
            word.extend(route)
            merged = tuple(sorted((*left, *right)))
            current = [merged, *current[2:]]

    if state.partition != target:
        raise AssertionError(f"constructed partition {state.partition}, expected {target}")
    if state.layers[0] != ((),) * n:
        raise AssertionError("partition construction left packets on layer 0")

    fusion_count = n - len(target)
    bound = n * n + n - 1 + 2 * n * fusion_count + fusion_count * (fusion_count - 1) // 2
    if len(word) > bound:
        raise AssertionError(f"word length {len(word)} exceeded bound {bound}")
    return state, tuple(word)


def construct_partition_interleaved(
    n: int, blocks: Iterable[Iterable[int]]
) -> tuple[State, Word]:
    """Load target blocks and fuse each block during loading.

    Raw words use the original guarded transition semantics.  After k loads,
    upper occupied sites are in range(k), so the next upper turn clears the
    sync port without wraparound.  Only a continuation of the current block
    emits d_1.  This gives length <= n*n + 2*n - block_count - 1.
    """
    target = _normalize_partition(n, blocks)
    state = seed(n)
    word: list[Action] = []
    loaded = 0
    for block in reversed(target):
        suffix: Packet = ()
        for atom in reversed(block):
            route: list[Action] = []
            if loaded:
                route.append(("p", 1))
            site = _site_of(state, 0, (atom,))
            route.extend(_p(0, (-site) % n))
            route.append(("v", None))
            if suffix:
                route.append(("d", 1))
            state = replay(state, route)
            word.extend(route)
            loaded += 1
            suffix = tuple(sorted((atom, *suffix)))
            if state.layers[1][0] != suffix:
                raise AssertionError("interleaved carrier is not at the sync port")
            if any(state.layers[1][loaded:]):
                raise AssertionError("interleaved upper packing crossed its frontier")

    expected_upper: list[Packet] = [()] * n
    offset = 0
    for block in target:
        expected_upper[offset] = block
        offset += len(block)
    if state.layers != (((),) * n, tuple(expected_upper)):
        raise AssertionError("interleaved construction ended at the wrong placement")
    if state.partition != target:
        raise AssertionError("interleaved construction changed the target blocks")
    if len(word) > n * n + 2 * n - len(target) - 1:
        raise AssertionError("interleaved construction exceeded its raw-letter budget")
    return state, tuple(word)


def set_partitions(n: int) -> Iterable[tuple[Packet, ...]]:
    """Generate each set partition of range(n) exactly once."""
    if n < 0:
        raise ValueError("n must be nonnegative")

    def extend(next_atom: int, blocks: list[list[int]]):
        if next_atom == n:
            yield tuple(sorted((tuple(block) for block in blocks),
                               key=lambda block: (block[0], len(block), block)))
            return
        blocks.append([next_atom])
        yield from extend(next_atom + 1, blocks)
        blocks.pop()
        for index in range(len(blocks)):
            blocks[index].append(next_atom)
            yield from extend(next_atom + 1, blocks)
            blocks[index].pop()

    yield from extend(0, [])
