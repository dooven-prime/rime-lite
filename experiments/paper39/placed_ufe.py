"""Abstract forward-UFE history adapter; not the verified external UFE algorithm."""

from dataclasses import dataclass

from contract import Absorption, Event, Summary, require


@dataclass(frozen=True)
class PlacedUFE:
    # Dynamic state: abstract effective unions plus injective current class placement.
    unions: tuple[tuple[int, int], ...]
    placement: tuple[tuple[frozenset[int], int], ...]


def order_placement(placement):
    return tuple(sorted(placement, key=lambda item: tuple(sorted(item[0]))))


def initial(env):
    return PlacedUFE((), order_placement((frozenset({atom}), q)
                                        for atom, q in enumerate(env.seed)))


def prefix_events(env, state):
    classes = [frozenset({atom}) for atom in range(len(env.seed))]
    events = []
    for x, y in state.unions:
        require(0 <= x < len(env.seed) and 0 <= y < len(env.seed), "invalid UFE index")
        left = next(block for block in classes if env.enumeration[x] in block)
        right = next(block for block in classes if env.enumeration[y] in block)
        require(left != right, "ineffective union")
        event = Event(tuple(zip(env.kernel, (left, right))), env.collision)
        events.append(event)
        classes.remove(left)
        classes.remove(right)
        classes.append(left | right)
    require(set(classes) == {block for block, _ in state.placement}, "UFE class/placement mismatch")
    return tuple(events)


def project(state):
    return tuple(sorted((q, block) for block, q in state.placement))


def step(env, state, letter):
    placement = dict(state.placement)
    inverse = {q: block for block, q in placement.items()}
    unions = state.unions
    if letter == "d" and all(q in inverse for q in env.kernel):
        left, right = (inverse[q] for q in env.kernel)
        pick = lambda block: min(i for i, atom in enumerate(env.enumeration) if atom in block)
        unions += ((pick(left), pick(right)),)
        del placement[left]
        del placement[right]
        placement[left | right] = env.kernel[0]
    action = env.action(letter)
    result = order_placement((block, action[q]) for block, q in placement.items())
    require(len({q for _, q in result}) == len(result), "noninjective UFE placement")
    return PlacedUFE(unions, result)


def decode(env, state, selected):
    events = prefix_events(env, state)
    origin_index = next((i for i, event in enumerate(events) if event.fresh == selected), None)
    if origin_index is None:
        return None
    absorptions = []
    for event in events[origin_index + 1:]:
        containing = [(side, parent) for side, parent in enumerate(event.parents)
                      if selected <= parent[1]]
        if containing:
            side, (q, carrier) = containing[0]
            s, partner = event.parents[1 - side]
            absorptions.append(Absorption(q, carrier, s, partner, env.collision, carrier | partner))
    return Summary(project(state), selected, events[origin_index], tuple(absorptions))


def command(env, state, selected, kind, letter):
    require(kind in ("Carry", "Absorb"), "unknown command")
    summary = decode(env, state, selected)
    if summary is None:
        return None
    q, _ = summary.carrier
    action = env.action(letter)
    count = sum(action[s] == action[q] for _, s in state.placement)
    if (kind == "Carry") != (count == 1):
        return None
    return step(env, state, letter)


def to_forest(env, state):
    # This mathematical decoder folds union inputs; it is not retained adapter data.
    from forest import Forest, Tree

    trees = {frozenset({atom}): Tree(atom) for atom in range(len(env.seed))}
    marker = None
    for event in prefix_events(env, state):
        children = tuple((q, trees.pop(block)) for q, block in event.parents)
        trees[event.fresh] = Tree(children=children, target=event.target, label=event.label)
        marker = event.fresh
    return Forest(tuple(sorted((q, trees[block]) for block, q in state.placement)), marker)


def rename(state, permutation):
    return PlacedUFE(state.unions, order_placement(
        (frozenset(permutation[x] for x in block), q) for block, q in state.placement))
