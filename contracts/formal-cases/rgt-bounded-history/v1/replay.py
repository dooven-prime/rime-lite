"""Finite cross-language replay against the exact released Paper XL snapshot."""

import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
LEAN = ROOT / "experiments/paper40/lean"
ARCHIVE = ROOT / "experiments/paper40/source/q2-source-v1.zip"
ARCHIVE_SHA = "2f473984c02c7d085d4bbec37fe06823c4399d201a08ed35251be57f3ffe3244"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


@contextmanager
def frozen_runtime():
    require(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA, "released runtime ZIP drift")
    binding = json.loads((ARCHIVE.parent / "snapshot.v1.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="rgt-frozen-runtime-") as directory:
        with zipfile.ZipFile(ARCHIVE) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)), "duplicate runtime ZIP member")
            expected = {row["path"]: row for row in binding["source_manifest"]["files"]}
            require(set(names) == set(expected) | {"source-manifest.json"}, "runtime inventory drift")
            for name in names:
                path = PurePosixPath(name)
                require(not path.is_absolute() and ".." not in path.parts and "\\" not in name, "unsafe ZIP member")
                raw = archive.read(name)
                if name in expected:
                    row = expected[name]
                    require(len(raw) == row["size"] and hashlib.sha256(raw).hexdigest() == row["sha256"], name)
            archive.extractall(directory)
        sys.path.insert(0, directory)
        try:
            yield {name: importlib.import_module("q2." + name)
                   for name in ("model", "request", "syntax", "values", "engine", "replay")}
        finally:
            sys.path.remove(directory)
            for name in list(sys.modules):
                if name == "q2" or name.startswith("q2."):
                    del sys.modules[name]


def state_code(state, m):
    packets = dict(state.partition)
    sites = [next(q for q, block in state.partition if i in block) for i in range(m)]
    events = [[0 if i in e.parents[0][1] else 1 if i in e.parents[1][1] else 2
               for i in range(m)] for e in state.events]
    require(len(packets) == len(state.partition), "duplicate site")
    return sites, events


def python_observation(modules, request, state):
    model, values, syntax = (modules[name] for name in ("model", "values", "syntax"))
    summary = model.decode(state, request.selected)
    sites, events = state_code(state, len(request.env.seed))
    if summary is None:
        causal, q, report, guards = None, None, None, None
    else:
        leaves = values.leaves(summary)
        bare = lambda value: values.bare(value, request.env)
        carrier = next((q, sorted(block)) for q, block in summary.partition if request.selected <= block)
        causal = {"partition": bare(leaves["CurrentPartition"]), "selected": sorted(request.selected),
                  "origin": bare(leaves["OriginSnapshot"]), "absorptions": bare(leaves["AbsorptionSequence"]),
                  "carrier": {"some": list(carrier)}}
        q = bare(syntax.evaluate(request.q, leaves, request.env, request.budget))
        require(len(request.reports) == 1, "fixed case must have one declared report")
        report = bare(syntax.evaluate(request.reports[0][1], leaves, request.env, request.budget))
        guards = [syntax.evaluate(c.guard, leaves, request.env, request.budget).data for c in request.commands]
    return {"site": sites, "events": events, "causal": causal, "q": q, "report": report,
            "candidate_code": canonical(q), "report_code": canonical(report), "guards": guards}


def compare_vectors(actual, expected):
    require(len(actual) == len(expected), "Lean response count mismatch")
    for index, (left, right) in enumerate(zip(actual, expected)):
        require(canonical(left) == canonical(right), "Lean/Python observation mismatch at query " + str(index))


def clause_values(observations, successors, commands):
    flags = {"R": True, "G": True, "T": True}
    fibers = {}
    for index, value in enumerate(observations):
        if value["causal"] is not None:
            fibers.setdefault(value["candidate_code"], []).append(index)
    for members in fibers.values():
        pivot = members[0]
        for other in members[1:]:
            left, right = observations[pivot], observations[other]
            flags["R"] &= left["report_code"] == right["report_code"]
            flags["G"] &= left["guards"] == right["guards"]
        for column, command in enumerate(commands):
            enabled = [i for i in members if observations[i]["guards"][column]]
            if enabled:
                next_codes = {successors[i, command.letter]["candidate_code"] for i in enabled}
                flags["T"] &= len(next_codes) <= 1
    return flags


def replay(lake, env=None):
    catalog = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    queries, expected, prepared = [], [], []
    with frozen_runtime() as modules:
        for case in catalog["cases"]:
            raw = case["request"]
            n = len(raw["environment"]["defect"])
            require(raw["environment"] == {"defect": [0, 0] + list(range(2, n)), "seed": list(range(n))},
                    "case is not the declared C1 identity-seed environment")
            require(n == (3 if case["id"] in ("R", "P") else 4), "case/environment mismatch")
            require(raw["selected"] == (list(range(n)) if n == 3 else [0, 1]), "selected-block drift")
            request = modules["request"].prepare(raw)
            domain = modules["model"].saturate(request.env, request.selected, request.budget)
            observations, successors = [], {}
            for index, state in enumerate(domain.logs):
                word = domain.word(index)
                value = python_observation(modules, request, state)
                observations.append(value)
                queries.append({"case": case["id"], "word": word})
                expected.append(value)
                for letter in ("p", "d"):
                    next_state = modules["model"].step(request.env, state, letter)
                    next_value = python_observation(modules, request, next_state)
                    successors[index, letter] = next_value
                    queries.append({"case": case["id"], "word": word + letter})
                    expected.append(next_value)
            result = modules["engine"].check(raw)
            require(result["status"] == case["expected_status"] and result["domain_complete"], "Q2 verdict drift")
            verification = None
            if case["id"] != "P":
                verification = modules["replay"].verify_rejection(raw, result)
                require(verification["status"] == "VALID_REJECTION_WITNESS", "frozen rejection replay failed")
                words = [result["witness"][side]["word"] for side in ("left", "right")]
                require(words == case["display_histories"], "display history drift")
            flags = clause_values(observations, successors, request.commands)
            require(flags[case["id"]] is False if case["id"] != "P" else all(flags.values()), "clause mismatch")
            traces = []
            for word in case["display_histories"] or []:
                require(len(word) <= 7 * n * (n - 1) // 2, "certificate exceeds the quadratic bound")
                state = modules["model"].initial(request.env)
                trace = [python_observation(modules, request, state)]
                for letter in word:
                    state = modules["model"].step(request.env, state, letter)
                    trace.append(python_observation(modules, request, state))
                item = {"word": word, "states": trace}
                if case["id"] == "T":
                    successor = modules["model"].step(request.env, state, "d")
                    item["common_enabled_letter"] = "d"
                    item["successor_word"] = word + "d"
                    item["successor_state"] = python_observation(modules, request, successor)
                    require(len(word + "d") <= 7 * n * (n - 1) // 2 + 1, "T extension exceeds B+1")
                traces.append(item)
            prepared.append({"id": case["id"], "request_sha256": digest(raw), "n": n,
                "domain": result["domain"], "q_states": result["q_states"], "clauses": flags,
                "checked_complete_states": len(domain.logs), "checked_edges": 2 * len(domain.logs),
                "quadratic_budget": 7 * n * (n - 1) // 2, "q2_result": result,
                "rejection_replay": verification, "display_traces": traces})
        command = [str(lake), "env", "lean", "--run", "ReplayC1.lean"]
        process = subprocess.run(command, cwd=LEAN, env=env, input="".join(canonical(q) + "\n" for q in queries),
                                 capture_output=True, text=True, encoding="utf-8", errors="strict", timeout=600)
        require(process.returncode == 0, "Lean replay failed: " + process.stdout + process.stderr)
        actual = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
        compare_vectors(actual, expected)
    return {"status": "PASS_FIXED_C1_CONSUMER_CORRESPONDENCE", "runtime_archive_sha256": ARCHIVE_SHA,
            "lean_queries": len(queries), "compared_observations_sha256": digest(actual), "cases": prepared,
            "scope": "Exact finite generated-domain and every-generator-edge comparison for the four declared C1 consumers",
            "all_parameter_runtime_correspondence_proved": False, "frozen_parser_formalized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake", default="lake")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.report is not None and args.report.exists():
        raise FileExistsError(args.report)
    result = replay(args.lake)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(canonical({"status": result["status"], "lean_queries": result["lean_queries"],
                     "cases": [{"id": row["id"], "clauses": row["clauses"]} for row in result["cases"]]}))


if __name__ == "__main__":
    main()
