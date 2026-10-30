"""Replay the bounded controls and cross-check raw edges with packet grouping."""

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit import DOMAIN, report  # noqa: E402
from model import (LETTERS, SELECTED, Fusion, State, graph, packets, run,
                   seed)  # noqa: E402


def packet_step(n, state, letter):
    """Independent packet-map update, not the atomwise implementation."""
    before = dict(packets(state.sites))
    fused = None
    if letter == "d" and 0 in before and 1 in before:
        fused = Fusion(before[0], before[1])
    after = {}
    for site, block in before.items():
        target = ((site + 1) % n if letter == "p" else
                  0 if site == 1 else site)
        after.setdefault(target, set()).update(block)
    sites = [None] * n
    for site, block in after.items():
        for atom in block:
            sites[atom] = site
    if any(site is None for site in sites):
        raise AssertionError("packet update lost an atom")
    origin, chain, output = state.origin, state.chain, None
    if fused is not None:
        if origin is None and frozenset(fused.left + fused.right) == SELECTED:
            origin = fused
            output = ("registration", fused)
        elif origin is not None and (
                SELECTED <= frozenset(fused.left) or
                SELECTED <= frozenset(fused.right)):
            chain = chain + (fused,)
            output = ("absorption", fused)
    return State(tuple(sites), origin, chain), output, fused


def check_hashes(manifest):
    for relative, expected in manifest["sha256"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError(f"source byte drift: {relative}")


def main():
    manifest = json.loads((ROOT / "control-manifest.v1.json").read_text(
        encoding="utf-8"))
    if manifest["status"] != "BOUNDED_LOCAL_CLOSURE":
        raise AssertionError("unexpected manifest status")
    check_hashes(manifest)
    saved = json.loads((ROOT / "results" / "future_event_controls.v1.json")
                       .read_text(encoding="utf-8"))
    reproduced = report()
    if saved != reproduced:
        raise AssertionError("saved result differs from fresh bounded replay")

    checked = 0
    for n in DOMAIN:
        states, transitions, words = graph(n)
        for state in states:
            if run(n, seed(n), words[state])[0] != state:
                raise AssertionError(
                    f"stored source history does not replay at n={n}")
            for letter in LETTERS:
                if transitions[(state, letter)] != packet_step(n, state, letter):
                    raise AssertionError(
                        f"packet/atom edge mismatch at n={n}, word={words[state]}")
                checked += 1
    print(f"PASS: n=3..5, {checked} raw edges, two exact finite quotients, "
          "all candidate-class separator pairs, and fixed source bytes")


if __name__ == "__main__":
    main()
