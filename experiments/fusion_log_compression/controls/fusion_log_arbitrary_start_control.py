"""Bounded exact-log/endpoint and raw-word controls for arbitrary packet starts."""

from collections import Counter, deque
from math import comb, factorial
from pathlib import Path
import argparse
import json

import core


def cyclic_equal(left, right):
    return any(left == right[i:] + right[:i] for i in range(len(right)))


class Builder:
    def __init__(self, n, initial):
        self.n = n
        self.part = dict(initial)
        self.maps = dict(zip(("p", "d"), core.letters(n)[:2]))
        self.word, self.events = [], []
        self.K = self.M = 0

    def emit(self, word, fusion=False):
        for letter in word:
            self.part, event = core.step(self.part, self.maps[letter], letter, self.n)
            if event is not None:
                if not fusion:
                    raise AssertionError("unexpected fusion during routing")
                self.events.append(event)
            self.word.append(letter)

    def batch(self, q, amount):
        if not 1 <= amount <= self.n - 2:
            raise AssertionError("invalid batch size")
        before = dict(self.part)
        if q not in before or any((q - k) % self.n in before for k in range(1, amount + 1)):
            raise AssertionError("batch crosses an occupied site")
        word = ("p" * ((1 - q) % self.n) + "d" + "pd" * (amount - 1)
                + "p" * ((q - amount) % self.n))
        self.emit(word)
        expected = dict(before)
        expected[(q - amount) % self.n] = expected.pop(q)
        if self.part != expected or len(word) > 2 * self.n + amount:
            raise AssertionError("batch placement or length mismatch")
        self.K += 1
        self.M += amount

    def fuse(self, event):
        left, right = frozenset(event[3]), frozenset(event[4])
        sites = {block: q for q, block in self.part.items()}
        a, b = sites[left], sites[right]
        gap = (b - a - 1) % self.n
        if gap:
            self.batch(b, gap)
        self.emit("p" * ((-a) % self.n))
        count = len(self.events)
        self.emit("d", fusion=True)
        if self.events[count:] != [event]:
            raise AssertionError("literal ordered event changed")

    def place(self, target):
        if Counter(self.part.values()) != Counter(target.values()):
            raise AssertionError("different target source blocks")
        order = [block for _q, block in sorted(self.part.items())]
        wanted = [block for _q, block in sorted(target.items())]
        if not cyclic_equal(order, wanted):
            raise AssertionError("target reverses cyclic packet order")
        count = len(order)

        def gaps(part):
            sites = {block: q for q, block in part.items()}
            return [(sites[order[(i + 1) % count]] - sites[order[i]] - 1) % self.n
                    for i in range(count)]

        if count > 1:
            total, prefix = 0, []
            for current, desired in zip(gaps(self.part), gaps(target)):
                total += current - desired
                prefix.append(total)
            if total:
                raise AssertionError("gap masses differ")
            flow = [x - min(prefix) for x in prefix]
            cut = flow.index(0)
            for offset in range(1, count):
                edge = (cut + offset) % count
                if flow[edge]:
                    block = order[(edge + 1) % count]
                    q = next(q for q, value in self.part.items() if value == block)
                    self.batch(q, flow[edge])
        block = order[0]
        current = next(q for q, value in self.part.items() if value == block)
        desired = next(q for q, value in target.items() if value == block)
        self.emit("p" * ((desired - current) % self.n))
        if self.part != target:
            raise AssertionError("terminal literal placement mismatch")


def states_from(n, initial):
    maps = dict(zip(("p", "d"), core.letters(n)[:2]))
    start = (core.pkey(initial), ())
    queue, seen = deque([start]), {start}
    while queue:
        key, log = queue.popleft()
        yield key, log
        for letter in ("p", "d"):
            successor, event = core.step(core.from_pkey(key), maps[letter], letter, n)
            state = (core.pkey(successor), log + (event,) if event is not None else log)
            if state not in seen:
                seen.add(state)
                queue.append(state)
                if len(seen) > 250000:
                    raise RuntimeError("bounded source-domain cap exceeded")


def check_case(n, initial):
    t = len(initial)
    rank_counts, fibres = Counter(), Counter()
    maximum, total = 0, 0
    for placement, log in states_from(n, initial):
        target = core.from_pkey(placement)
        s = len(target)
        builder = Builder(n, initial)
        for event in log:
            builder.fuse(event)
        builder.place(target)
        if tuple(builder.events) != log or builder.part != target:
            raise AssertionError("complete log/endpoint not retained")
        d, h = t - s, n - t
        bound = 3 * n * d + h * d + d * (d - 1) // 2 + (3 * n - s) * (s - 1) + n - 1
        m_bound = d * h + d * (d - 1) // 2 + (n - s) * (s - 1)
        if len(builder.word) > bound or builder.K > t - 1 or builder.M > m_bound:
            raise AssertionError("general-start construction budget exceeded")
        if bound > 7 * n * (n - 1) // 2:
            raise AssertionError("uniform quadratic comparison failed")
        rank_counts[s] += 1
        fibres[log] += 1
        maximum = max(maximum, len(builder.word))
        total += 1
    for s in range(1, t + 1):
        predicted = factorial(t) // factorial(s) * s * comb(n, s)
        logs = [log for log in fibres if len(log) == t - s]
        if rank_counts[s] != predicted or len(logs) != factorial(t) // factorial(s):
            raise AssertionError("joint or log count mismatch")
        if any(fibres[log] != s * comb(n, s) for log in logs):
            raise AssertionError("complete endpoint fibre mismatch")
    return {"n": n, "initial_rank": t, "atom_count": 2 * t,
            "initial": core.pkey(initial), "complete_log_endpoint_pairs": total,
            "rank_counts": dict(sorted(rank_counts.items())), "max_constructed_word": maximum,
            "all_logs_endpoints_and_budgets_match": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 3 <= args.max_n <= 6:
        raise ValueError("this control is restricted to 3 <= max-n <= 6")
    if args.output is not None and args.output.exists():
        raise FileExistsError(args.output)
    cases = []
    for n in range(3, args.max_n + 1):
        for t in range(1, n + 1):
            layouts = (tuple(range(t)), tuple((i * n // t + 1) % n for i in range(t)))
            for sites in dict.fromkeys(layouts):
                initial = {q: frozenset((i, i + t)) for i, q in enumerate(sites)}
                row = check_case(n, initial)
                cases.append(row)
        print(json.dumps({"n": n, "cases_completed": len(cases)}), flush=True)
    report = {"status": "PASS_BOUNDED_ARBITRARY_START_CONTROL", "evidence": "BOUNDED_CONSISTENCY_ONLY",
              "cases": cases, "shared_raw_step_implementation": "core.step",
              "kernel_formalization_claimed": False}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "cases": len(cases),
                      "complete_pairs_replayed": sum(row["complete_log_endpoint_pairs"] for row in cases)}))


if __name__ == "__main__":
    main()
