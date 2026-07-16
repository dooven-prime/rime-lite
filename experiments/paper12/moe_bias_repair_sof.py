"""Paper XII diagnostic: DeepSeek-style MoE routing-repair SOF Report.

This is a finite control inspired by two DeepSeekMoE design ideas:
fine-grained routed experts with an always-active shared expert, and
auxiliary-loss-free load balancing by routing-bias updates. It is not an audit
of DeepSeek weights or a claim that routing repair is Lie-depth D-repair.

Private expert sectors are measured separately from the shared baseline. If the
shared expert were folded into the private routing graph, its universal channel
would mask private dead-expert events. The report therefore records:

    private frozen expert: no token selects that routed expert at a step;
    routing repair: a previously frozen private expert later receives tokens;
    shared baseline: active for every token but excluded from private repair.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


N_PRIVATE_EXPERTS = 12
N_TOKENS = 384
TOP_K = 2
STEPS = 80
BIAS_STEP = 0.08
SEED = 7


def private_routes(logits: np.ndarray, routing_bias: np.ndarray) -> np.ndarray:
    adjusted = logits + routing_bias[:, None]
    return np.argsort(-adjusted, axis=0)[:TOP_K]


def expert_loads(routes: np.ndarray) -> np.ndarray:
    return np.bincount(routes.ravel(), minlength=N_PRIVATE_EXPERTS)


def update_bias(routing_bias: np.ndarray, loads: np.ndarray) -> np.ndarray:
    target = TOP_K * N_TOKENS / N_PRIVATE_EXPERTS
    # DeepSeek-style rule: underloaded experts gain routing preference and
    # overloaded experts lose it. This is a routing update, not gradient learning.
    return routing_bias + BIAS_STEP * np.sign(target - loads)


def run_control() -> dict:
    rng = np.random.RandomState(SEED)
    logits = 0.35 * rng.randn(N_PRIVATE_EXPERTS, N_TOKENS)
    # Two initially dominant routed experts create a private dead-expert regime.
    logits[0] += 3.0
    logits[1] += 2.4
    logits[2:] -= 2.2

    routing_bias = np.zeros(N_PRIVATE_EXPERTS)
    load_history = []
    frozen_history = []
    first_active = np.full(N_PRIVATE_EXPERTS, -1, dtype=int)

    for step in range(STEPS + 1):
        routes = private_routes(logits, routing_bias)
        loads = expert_loads(routes)
        frozen = loads == 0
        load_history.append(loads)
        frozen_history.append(frozen)
        first_active[(first_active < 0) & ~frozen] = step
        if step < STEPS:
            routing_bias = update_bias(routing_bias, loads)

    loads = np.asarray(load_history)
    frozen = np.asarray(frozen_history)
    initially_frozen = frozen[0]
    repaired = initially_frozen & (first_active >= 0)
    persistent = initially_frozen & (first_active < 0)
    repair_steps = first_active[repaired]
    repair_events = [
        {
            "expert": int(expert),
            "first_active_step": int(first_active[expert]),
            "initial_load": int(loads[0, expert]),
            "final_load": int(loads[-1, expert]),
        }
        for expert in np.flatnonzero(repaired)
    ]

    return {
        "loads": loads,
        "frozen": frozen,
        "first_active": first_active,
        "initially_frozen": initially_frozen,
        "repaired": repaired,
        "persistent": persistent,
        "repair_events": repair_events,
        "shared_expert_tokens": N_TOKENS,
        "private_active_history": (~frozen).sum(axis=1),
        "first_repair_step": int(repair_steps.min()) if len(repair_steps) else None,
        "final_bias": routing_bias,
    }


def sofreport(result: dict) -> dict:
    initially_frozen = int(result["initially_frozen"].sum())
    repaired = int(result["repaired"].sum())
    persistent = int(result["persistent"].sum())
    repair_index = repaired / initially_frozen if initially_frozen else 0.0
    return {
        "sofrs_version": "1.0",
        "report_id": "moe_bias_repair",
        "system": "DeepSeek-style synthetic MoE routing control",
        "claim_status": "diagnostic",
        "claim_note": "finite private-expert routing-repair control",
        "sectorization": {
            "origin": "private routed-expert activity",
            "private_experts": N_PRIVATE_EXPERTS,
            "top_k": TOP_K,
            "tokens": N_TOKENS,
            "shared_baseline": "always active and excluded from private freeze counts",
            "realization_status": "constructed routing diagnostic",
        },
        "observable_family": {
            "private_loads": "token route count per private expert and step",
            "routing_bias": "load-balancing preference update",
            "frozen_state": "zero private load at a step",
        },
        "support_matrix": {
            "kind": "private expert load trajectory",
            "steps": list(range(STEPS + 1)),
            "load_matrix": result["loads"].astype(int).tolist(),
            "active_private_experts": result["private_active_history"].astype(int).tolist(),
        },
        "bridge_matrix": {
            "status": "not_applicable",
            "reason": "repair is induced by routing-bias deformation, not a two-step sector bridge",
        },
        "repair_matrix": {
            "kind": "frozen-to-routed private expert transition",
            "initially_frozen": initially_frozen,
            "repaired": repaired,
            "persistent_frozen": persistent,
            "repair_index": repair_index,
            "first_repair_step": result["first_repair_step"],
            "events": result["repair_events"],
        },
        "wall_record": {
            "wall_type": "routing activation threshold",
            "first_wall_step": result["first_repair_step"],
            "trajectory_summary": {
                "frozen_matrix": result["frozen"].astype(int).tolist(),
                "final_bias": result["final_bias"].tolist(),
            },
        },
        "failure_modes": [
            "synthetic finite control rather than an audit of DeepSeek weights",
            "shared expert is excluded from private freeze and repair counts",
            "routing repair is not Lie-depth D-repair",
            "bias updates are routing controls rather than gradient learning",
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "moe_bias_repair.sofreport"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def print_report(result: dict) -> None:
    initially_frozen = int(result["initially_frozen"].sum())
    repaired = int(result["repaired"].sum())
    persistent = int(result["persistent"].sum())
    repair_index = repaired / initially_frozen if initially_frozen else 0.0

    print("=" * 88)
    print("  Paper XII: DeepSeek-Style MoE Routing-Repair SOF Report")
    print("=" * 88)
    print(f"  Private routed experts: {N_PRIVATE_EXPERTS}, top_k={TOP_K}, tokens={N_TOKENS}")
    print("  Sectorization: private routed-expert activity sectors + separate shared baseline")
    print("  Observable Family: private routing loads, frozen-expert trajectory, routing biases")
    print()
    print("  Initial private routing state:")
    print(f"    active private experts: {result['private_active_history'][0]}/{N_PRIVATE_EXPERTS}")
    print(f"    frozen private experts: {initially_frozen}/{N_PRIVATE_EXPERTS}")
    print(f"    shared-expert baseline: active for {result['shared_expert_tokens']}/{N_TOKENS} tokens")
    print()
    print("  Routing-repair trajectory:")
    print(f"    first private repair step: {result['first_repair_step']}")
    print(f"    repaired private experts: {repaired}/{initially_frozen}")
    print(f"    persistent frozen experts: {persistent}/{initially_frozen}")
    print(f"    routing repair index: {repair_index:.1%}")
    for event in result["repair_events"]:
        print(
            f"    expert {event['expert']:>2d}: step {event['first_active_step']:>2d}, "
            f"load {event['initial_load']} -> {event['final_load']}"
        )
    print()
    print("  Wall Record:")
    print("    load-imbalance wall: private experts initially receive zero routes")
    print("    routing-repair wall: routing bias raises a formerly frozen expert above top-k")
    print("    shared baseline is reported separately so it cannot hide private dead experts")
    print()
    print("  Claim Status:")
    print("    DeepSeek-style finite routing control, not a DeepSeek weight audit")
    print("    routing repair is an observable repair analogue, not Lie-depth D-repair")
    print(f"SOFRS v1.0: {write_sofreport(sofreport(result))}")
    print("Done.")


if __name__ == "__main__":
    print_report(run_control())
