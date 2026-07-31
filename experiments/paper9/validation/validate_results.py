"""Validate the current Paper IX versioned result records."""

from __future__ import annotations

import json
from pathlib import Path


PAPER_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PAPER_DIR / "results"
RATE_PATH = RESULTS_DIR / "rate_hierarchy.json"
NN_PATH = RESULTS_DIR / "nn_training_sof_tau.json"
ACTIVATION_PATH = RESULTS_DIR / "nn_activation_sof.json"
CALIBRATED_PATH = RESULTS_DIR / "calibrated_response.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"missing Paper IX result: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def endpoint_half_response(times: list[int], values: list[float]) -> int | None:
    if not values:
        return None
    start = values[0]
    endpoint = values[-1]
    delta = endpoint - start
    if abs(delta) < 1.0e-12:
        return None
    for time, value in zip(times, values):
        normalized = (value - start) / delta
        if normalized >= 0.5:
            return time
    return None


def validate_rate() -> None:
    record = read_json(RATE_PATH)
    if record["schema_version"] != "paper9-rate-hierarchy-v3.0":
        raise AssertionError("unexpected rate-hierarchy schema version")
    observed = record["observed"]
    eta = record["threshold_policy"]["eta"]
    if abs(observed["tau_direct"] - eta) > 1.0e-14:
        raise AssertionError("direct first-crossing parameter is inconsistent")
    if abs(observed["tau_commutator"] - eta ** 0.5) > 1.0e-14:
        raise AssertionError("commutator first-crossing parameter is inconsistent")
    if abs(observed["ratio"] - eta ** -0.5) > 1.0e-12:
        raise AssertionError("scale-separated response-time ratio is inconsistent")
    if observed["max_validation_residual"] > 1.0e-14:
        raise AssertionError("engineered matrix residual is too large")


def validate_nn() -> None:
    record = read_json(NN_PATH)
    if record["schema_version"] != "paper9-nn-training-v2.0":
        raise AssertionError("unexpected NN-training schema version")
    semantics = record["semantics"]
    if semantics["coherent_sector_tracking"]:
        raise AssertionError("NN audit must not claim coherent sector tracking")
    if semantics["temporal_repair_claimed"]:
        raise AssertionError("NN audit must not claim a temporal repair event")

    runs = {row["activation"]: row for row in record["runs"]}
    if set(runs) != {"ReLU", "GeLU"}:
        raise AssertionError("default NN activation census changed")
    for activation, row in runs.items():
        taus = [row["tau_K0"], row["tau_K1"], row["tau_K2"]]
        if taus != [60, 80, 120]:
            raise AssertionError(
                f"unexpected default proxy response times for {activation}: {taus}"
            )
        recomputed = [
            endpoint_half_response(row["times"], row[field])
            for field in ("K0", "K1", "K2")
        ]
        if recomputed != taus:
            raise AssertionError(
                f"endpoint-normalized response policy mismatch for "
                f"{activation}: recorded={taus}, recomputed={recomputed}"
            )
        for binary_row in row["binary"]:
            retired = {"D_repaired", "D_frozen", "frozen_D"}
            if retired.intersection(binary_row):
                raise AssertionError("retired binary field name in NN result")


def validate_activation() -> None:
    record = read_json(ACTIVATION_PATH)
    if record["schema_version"] != "paper9-nn-activation-v2.0":
        raise AssertionError("unexpected activation schema version")
    if record["semantics"]["temporal_claim"]:
        raise AssertionError("static activation audit must not claim dynamics")
    if len(record["rows"]) != 4:
        raise AssertionError("default activation census changed")


def validate_calibrated_response() -> None:
    record = read_json(CALIBRATED_PATH)
    if record["schema_version"] != "paper9-calibrated-response-v1.0":
        raise AssertionError("unexpected calibrated-response schema version")
    if record["tau_k0_grow"] != 30 or record["tau_k1_response"] != 1380:
        raise AssertionError("calibrated half-response times changed")
    if not record["measured_separation"]:
        raise AssertionError("calibrated response ordering failed")
    if record["claim_status"] != "Computational Certificate":
        raise AssertionError("calibrated response evidence level changed")


def main() -> None:
    validate_rate()
    validate_nn()
    validate_activation()
    validate_calibrated_response()
    print("Paper IX result validation passed.")
    print(f"  rate hierarchy: {RATE_PATH}")
    print(f"  NN training:    {NN_PATH}")
    print(f"  NN activation:  {ACTIVATION_PATH}")
    print(f"  calibrated:     {CALIBRATED_PATH}")


if __name__ == "__main__":
    main()
