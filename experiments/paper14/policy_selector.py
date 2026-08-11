"""Optional downstream policy control for Paper XIV candidate action sets.

This module is intentionally separate from ``action_engine``.  It demonstrates
that a downstream policy can select from a generated CandidateAction set
without changing audit projection, interpretation, or candidate generation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


POLICY_VERSION = "1.0"


@dataclass(frozen=True)
class ActionSelectionPolicy:
    policy_id: str
    family_order: tuple[str, ...] = (
        "Investigate",
        "RequestEvidence",
        "Mitigate",
        "Rollback",
        "Escalate",
        "NoAction",
    )
    max_actions: int = 4
    policy_version: str = POLICY_VERSION

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if self.max_actions <= 0:
            raise ValueError("max_actions must be positive")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def select_action_plan(
    actions: list[dict[str, Any]], policy: ActionSelectionPolicy
) -> dict[str, Any]:
    """Select a policy-relative subset from an already generated action set."""

    disposition_rank = {name: index for index, name in enumerate(policy.family_order)}
    ordered = sorted(
        actions,
        key=lambda item: (
            disposition_rank.get(item["disposition"], len(disposition_rank)),
            item["action_id"],
        ),
    )
    selected = ordered[: policy.max_actions]
    return {
        "status": "illustrative_policy_selection",
        "policy_id": policy.policy_id,
        "policy": policy.to_dict(),
        "selected_action_ids": [item["action_id"] for item in selected],
        "rationale": [
            "selection uses the declared family precedence and action-count limit",
            "another policy may select a different subset from the same Action Set",
        ],
    }


def validate_selected_action_plan(
    actions: list[dict[str, Any]], plan: dict[str, Any]
) -> list[str]:
    """Validate a downstream plan without changing the canonical Candidate Set."""

    candidate_ids = {item.get("action_id") for item in actions}
    selected_ids = plan.get("selected_action_ids", [])
    errors: list[str] = []
    if len(selected_ids) != len(set(selected_ids)):
        errors.append("selected action IDs must be unique")
    if not set(selected_ids) <= candidate_ids:
        errors.append("selected action IDs must belong to the Candidate Set")
    return errors
