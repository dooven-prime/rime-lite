"""Placed fusion trees and ancestor-path decoder, without an execution log."""

from dataclasses import dataclass

from contract import Absorption, Event, Summary, require


@dataclass(frozen=True)
class Tree:
    atom: int | None = None
    children: tuple = ()
    target: int | None = None
    label: str | None = None

    @property
    def leaves(self):
        if self.atom is not None:
            return frozenset({self.atom})
        return frozenset().union(*(child.leaves for _, child in self.children))


@dataclass(frozen=True)
class Forest:
    roots: tuple[tuple[int, Tree], ...]
    marker: frozenset[int] | None = None


def initial(env):
    return Forest(tuple(sorted((q, Tree(atom)) for atom, q in enumerate(env.seed))))


def project(state):
    return tuple(sorted((q, tree.leaves) for q, tree in state.roots))


def step(env, state, letter):
    grouped = {}
    for q, tree in state.roots:
        destination = (q + 1) % env.n if letter == "p" else env.defect[q]
        require(letter in ("p", "d"), "unknown generator")
        grouped.setdefault(destination, []).append((q, tree))
    roots, marker = [], state.marker
    for destination, incoming in sorted(grouped.items()):
        if len(incoming) == 1:
            tree = incoming[0][1]
        else:
            incoming = sorted(incoming, key=lambda item: item[0])
            require(letter == "d" and tuple(q for q, _ in incoming) == env.kernel,
                    "not the declared binary collision")
            tree = Tree(children=tuple(incoming), target=destination, label=letter)
            marker = tree.leaves
        roots.append((destination, tree))
    return Forest(tuple(roots), marker)


def nodes(tree):
    yield tree
    for _, child in tree.children:
        yield from nodes(child)


def check_wellformed(env, state):
    leaves, internal, all_nodes = set(), {}, []
    for q, root in state.roots:
        require(0 <= q < env.n, "root outside carrier")
        for node in nodes(root):
            all_nodes.append(node)
            if node.atom is not None:
                require(not node.children and node.target is None and node.label is None,
                        "malformed leaf")
                require(node.atom not in leaves, "duplicate atom")
                leaves.add(node.atom)
            else:
                require(tuple(q for q, _ in node.children) == env.kernel
                        and node.target == env.collision and node.label == "d",
                        "event metadata drift")
                left, right = (child.leaves for _, child in node.children)
                require(left and right and left.isdisjoint(right), "invalid binary node")
                require(node.leaves not in internal, "duplicate event reference")
                internal[node.leaves] = node
    require(leaves == set(range(len(env.seed))), "atom budget drift")
    require(len({q for q, _ in state.roots}) == len(state.roots), "duplicate root placement")
    require(len(internal) == len(env.seed) - len(state.roots)
            and len(all_nodes) == 2 * len(env.seed) - len(state.roots), "node bound failed")
    require(state.marker is None or state.marker in internal, "dangling marker")


def decode(state, selected):
    def path(tree):
        if not tree.children:
            return None
        if tree.leaves == selected:
            return tree, ()
        for side, (q, child) in enumerate(tree.children):
            found = path(child)
            if found is not None:
                origin, prior = found
                s, other = tree.children[1 - side]
                record = Absorption(q, child.leaves, s, other.leaves,
                                    tree.target, tree.leaves, tree.label)
                return origin, prior + (record,)
        return None

    for _, root in state.roots:
        found = path(root)
        if found is not None:
            origin, records = found
            snapshot = Event(tuple((q, tree.leaves) for q, tree in origin.children),
                             origin.target, origin.label)
            return Summary(project(state), selected, snapshot, records)
    return None


def command(env, state, selected, kind, letter):
    require(kind in ("Carry", "Absorb"), "unknown command")
    if decode(state, selected) is None:
        return None
    roots = dict(state.roots)
    q = next(q for q, tree in state.roots if selected <= tree.leaves)
    action = env.action(letter)
    collides = any(s != q and action[s] == action[q] for s in roots)
    if (kind == "Absorb") != collides:
        return None
    return step(env, state, letter)


def rename(state, permutation):
    def tree_map(tree):
        if tree.atom is not None:
            return Tree(permutation[tree.atom])
        return Tree(children=tuple((q, tree_map(child)) for q, child in tree.children),
                    target=tree.target, label=tree.label)

    marker = None if state.marker is None else frozenset(permutation[x] for x in state.marker)
    return Forest(tuple((q, tree_map(tree)) for q, tree in state.roots), marker)
