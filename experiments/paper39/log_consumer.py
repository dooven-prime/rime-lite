"""Independent occurrence-log specification; no forest or UFE imports."""

from dataclasses import dataclass

from contract import Absorption, Environment, Event, Partition, Summary, require


@dataclass(frozen=True)
class History:
    partition: Partition
    events: tuple[Event, ...] = ()


def initial(env: Environment):
    return History(tuple(sorted((q, frozenset({atom})) for atom, q in enumerate(env.seed))))


def step(env, history, letter):
    action = env.action(letter)
    packets = dict(history.partition)
    grouped = {}
    for q, block in history.partition:
        grouped.setdefault(action[q], set()).update(block)
    events = history.events
    if letter == "d" and all(q in packets for q in env.kernel):
        events += (Event(tuple((q, packets[q]) for q in env.kernel), env.collision),)
    return History(tuple((q, frozenset(block)) for q, block in sorted(grouped.items())), events)


def decode(history, selected):
    matches = [i for i, event in enumerate(history.events) if event.fresh == selected]
    if not matches:
        return None
    require(len(matches) == 1, "fresh event is not unique")
    i = matches[0]
    records = []
    for event in history.events[i + 1:]:
        for side, (q, block) in enumerate(event.parents):
            if selected <= block:
                s, partner = event.parents[1 - side]
                records.append(Absorption(q, block, s, partner, event.target, block | partner))
    return Summary(history.partition, selected, history.events[i], tuple(records))


def command(env, summary, kind, letter):
    require(kind in ("Carry", "Absorb"), "unknown command")
    if summary is None:
        return None
    action = env.action(letter)
    q, carrier = summary.carrier
    group = [(s, block) for s, block in summary.partition if action[s] == action[q]]
    if (kind == "Carry") != (len(group) == 1):
        return None
    records = summary.absorptions
    if kind == "Absorb":
        require(letter == "d" and len(group) == 2, "invalid absorption")
        s, partner = next((s, block) for s, block in group if s != q)
        records += (Absorption(q, carrier, s, partner, action[q], carrier | partner),)
    new_partition = {}
    for s, block in summary.partition:
        new_partition.setdefault(action[s], set()).update(block)
    return Summary(tuple((s, frozenset(block)) for s, block in sorted(new_partition.items())),
                   summary.selected, summary.origin, records)
