#!/usr/bin/env python3
"""Shared contracts for the registered finite-history execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from optimized_exact_common import ROOT, load_json, runtime_identity, sha256_file


SCOPE_PATH = ROOT / "finite_history_scope.v1.json"
D0_PATH = ROOT / "results" / "finite_history_D0.v1.npy"
BUDGET_PATH = ROOT / "gross_compute_budget.v1.json"
OPTIMIZED_REGISTRATION_PATH = (
    ROOT / "optimized_exact_implementation_benchmark.registration-v1.json"
)
PREFLIGHT_PATH = ROOT / "finite_history_closure.preflight-v1.json"
PREFLIGHT_RECEIPT_PATH = (
    ROOT / "finite_history_closure.preflight-v1.validation-receipt.json"
)
REGISTRATION_PATH = ROOT / "finite_history_closure.registration-v1.json"
REGISTRATION_RECEIPT_PATH = (
    ROOT / "finite_history_closure.registration-v1.validation-receipt.json"
)
RUNTIME_ROOT = ROOT / ".runtime-work" / "finite-history" / "v1"
ARRAY_NAMES = (
    "indptr",
    "indices",
    "numerators",
    "row_abs",
    "sector_codes",
    "sector_sizes",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    temporary.replace(path)


def artifact(path: Path, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def verify_artifact(entry: dict[str, Any]) -> Path:
    path = (ROOT / entry["path"]).resolve()
    require(path.is_relative_to(ROOT.resolve()), f"artifact escapes root: {entry['role']}")
    require(path.is_file(), f"missing artifact: {entry['role']}")
    require(path.stat().st_size == int(entry["bytes"]), f"size mismatch: {entry['role']}")
    require(sha256_file(path) == entry["sha256"], f"digest mismatch: {entry['role']}")
    return path


def load_scope_contract() -> tuple[dict[str, Any], np.ndarray]:
    scope = load_json(SCOPE_PATH)
    require(
        scope["status"] == "SCOPE_INSTANTIATED_AWAITING_RUNNER_AND_PREFLIGHT",
        "finite-history scope status mismatch",
    )
    require(scope["execution_authority"] == "NONE", "scope grants execution authority")
    rectangle = scope["orbit_window_rectangle"]
    require(rectangle["maximum_history_order_H"] == 2, "registered H mismatch")
    require(rectangle["orbit_horizon_T"] == 4, "registered T mismatch")
    require(rectangle["orders"] == [0, 1, 2], "registered orders mismatch")
    d0 = np.load(D0_PATH, mmap_mode="r", allow_pickle=False)
    require(d0.dtype == np.dtype("int64"), "D0 dtype mismatch")
    require(d0.shape == (711,), "D0 shape mismatch")
    require(bool(np.all(d0[1:] > d0[:-1])), "D0 must be strictly ascending")
    return scope, d0


def load_backend_contract() -> tuple[dict[str, Any], Path, Path]:
    registration = load_json(OPTIMIZED_REGISTRATION_PATH)
    require(registration["runtime"] == runtime_identity(), "runtime identity mismatch")
    for entry in registration["artifact_closure"]:
        verify_artifact(entry)
    cache_manifest_path = verify_artifact(registration["cache_manifest"])
    kernel_path = verify_artifact(registration["compiled_kernel"])
    manifest = load_json(cache_manifest_path)
    cache_dir = cache_manifest_path.parent
    for entry in manifest["arrays"].values():
        path = cache_dir / entry["path"]
        require(path.stat().st_size == entry["bytes"], f"cache size mismatch: {entry['path']}")
        require(sha256_file(path) == entry["sha256"], f"cache digest mismatch: {entry['path']}")
    labels = manifest["sector_labels"]
    labels_path = cache_dir / labels["path"]
    require(labels_path.stat().st_size == labels["bytes"], "sector-label size mismatch")
    require(sha256_file(labels_path) == labels["sha256"], "sector-label digest mismatch")
    return registration, cache_dir, kernel_path


def resource_caps() -> dict[str, int | float]:
    budget = load_json(BUDGET_PATH)
    gross = budget["gross_caps"]
    primary = budget["nonfungible_pools"]["primary_scientific_computation"]
    return {
        "maximum_workers": int(gross["maximum_workers"]),
        "peak_process_tree_rss_bytes": int(float(gross["peak_process_tree_rss_gib"]) * 2**30),
        "incremental_run_storage_bytes": int(float(gross["incremental_run_storage_gib"]) * 2**30),
        "primary_cpu_seconds": float(primary["cpu_core_hours"]) * 3600.0,
        "primary_wall_seconds": float(primary["nominal_wall_hours_at_four_workers"]) * 3600.0,
        "poll_interval_seconds": int(budget["accounting"]["poll_interval_seconds_maximum"]),
    }


def verify_registration() -> dict[str, Any]:
    registration = load_json(REGISTRATION_PATH)
    require(registration["status"] == "REGISTERED_READY_TO_EXECUTE", "experiment is not registered")
    require(
        registration["execution_authority"] == "FINITE_HISTORY_ORBIT_WINDOW_V1_ONLY",
        "unexpected execution authority",
    )
    require(registration["runtime"] == runtime_identity(), "registration runtime mismatch")
    for entry in registration["artifact_closure"]:
        verify_artifact(entry)
    receipt = load_json(REGISTRATION_RECEIPT_PATH)
    require(receipt["status"] == "PASS", "registration validation did not pass")
    require(
        receipt["registration"]["sha256"] == sha256_file(REGISTRATION_PATH),
        "registration receipt binding mismatch",
    )
    return registration
