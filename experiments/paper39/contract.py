"""Shared immutable data declarations, not shared transition implementations."""

from dataclasses import dataclass

Block = frozenset[int]
Partition = tuple[tuple[int, Block], ...]


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Environment:
    defect: tuple[int, ...]
    seed: tuple[int, ...]
    enumeration: tuple[int, ...]

    def __post_init__(self):
        n = len(self.defect)
        require(n >= 2 and all(type(q) is int and 0 <= q < n for q in self.defect),
                "invalid coordinate action")
        fibers = [tuple(q for q in range(n) if self.defect[q] == target)
                  for target in range(n)]
        require(sorted(map(len, fibers)) == sorted([0, 2] + [1] * (n - 2)),
                "action must have exactly one binary kernel")
        require(2 <= len(self.seed) <= n and len(set(self.seed)) == len(self.seed)
                and all(type(q) is int and 0 <= q < n for q in self.seed), "invalid seed")
        require(set(self.enumeration) == set(range(len(self.seed)))
                and len(self.enumeration) == len(self.seed), "invalid atom enumeration")

    @property
    def n(self):
        return len(self.defect)

    @property
    def kernel(self):
        return next(tuple(q for q in range(self.n) if self.defect[q] == target)
                    for target in range(self.n) if self.defect.count(target) == 2)

    @property
    def collision(self):
        return self.defect[self.kernel[0]]

    def action(self, letter):
        require(letter in ("p", "d"), "unknown labelled generator")
        return tuple((q + 1) % self.n for q in range(self.n)) if letter == "p" else self.defect


@dataclass(frozen=True)
class Event:
    # Parent order binds the two fixed coordinate ports, not parent-pointer direction.
    parents: tuple[tuple[int, Block], tuple[int, Block]]
    target: int
    label: str = "d"

    @property
    def fresh(self):
        return self.parents[0][1] | self.parents[1][1]


@dataclass(frozen=True)
class Absorption:
    carrier_at: int
    carrier: Block
    partner_at: int
    partner: Block
    target: int
    merged: Block
    label: str = "d"


@dataclass(frozen=True)
class Summary:
    partition: Partition
    selected: Block
    origin: Event
    absorptions: tuple[Absorption, ...]

    @property
    def carrier(self):
        matches = [(q, block) for q, block in self.partition if self.selected <= block]
        require(len(matches) == 1, "selected carrier is not unique")
        return matches[0]


def primitive(value):
    """Canonical JSON-friendly encoding including every declared record field."""
    from dataclasses import fields, is_dataclass

    if is_dataclass(value):
        return {field.name: primitive(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, frozenset):
        return sorted(value)
    if isinstance(value, (tuple, list)):
        return [primitive(item) for item in value]
    if isinstance(value, dict):
        return {key: primitive(item) for key, item in value.items()}
    return value
