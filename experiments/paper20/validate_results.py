"""Validate carrier-accessibility census artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper20.census import build_payload, content_digest

EXPECTED = {
    "z2": {
        "depth": 3,
        "support": 9,
        "composition": 7,
        "obstructed": 2,
        "routes": 648,
        "active_routes": 31,
        "disjoint": 2,
        "unresolved": 0,
        "minimum_depth_histogram": {"1": 7, "null": 2},
    },
    "s3": {
        "depth": 2,
        "support": 36,
        "composition": 28,
        "obstructed": 8,
        "routes": 7776,
        "active_routes": 318,
        "disjoint": 8,
        "unresolved": 0,
        "minimum_depth_histogram": {"1": 28, "null": 8},
    },
    "rubik": {
        "depth": 2,
        "support": 53,
        "composition": 43,
        "obstructed": 10,
        "routes": 236196,
        "active_routes": 20556,
        "disjoint": 26,
        "unresolved": 12,
        "minimum_depth_histogram": {"1": 29, "2": 14, "null": 38},
    },
}


def _canonical_pairs(value: object, label: str, errors: list[str]) -> set[tuple[int, int]]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return set()
    try:
        pairs = [tuple(map(int, pair)) for pair in value]
    except (TypeError, ValueError):
        errors.append(f"{label} contains an invalid pair")
        return set()
    if any(len(pair) != 2 for pair in pairs):
        errors.append(f"{label} contains a non-binary pair")
    if pairs != sorted(pairs) or len(pairs) != len(set(pairs)):
        errors.append(f"{label} is not a sorted unique pair list")
    return set(pairs)


def validate(path: Path, *, recompute: bool = False) -> list[str]:
    errors: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("content_sha256") != content_digest(payload):
        errors.append("content digest mismatch")
    model = payload.get("model")
    if payload.get("schema_version") != "rime.carrier-accessibility-census.v1":
        errors.append("schema version mismatch")
    if payload.get("claim_status") != "computational_observation":
        errors.append("claim status must remain computational_observation")
    depth = payload.get("max_depth_enumerated")
    if not isinstance(depth, int) or depth < 1:
        errors.append("max_depth_enumerated must be a positive integer")
        return errors
    result = payload.get("result", {})
    if not isinstance(result, dict):
        errors.append("result must be an object")
        return errors
    profiles = result.get("carrier_profiles", [])
    sector_count = payload.get("sector_count")
    if not isinstance(sector_count, int) or sector_count < 1:
        errors.append("sector_count must be a positive integer")
        return errors
    try:
        supports = {item["sector"]: set(item["carrier_support"]) for item in profiles}
    except (KeyError, TypeError):
        errors.append("carrier profiles are malformed")
        return errors
    if set(supports) != set(range(sector_count)):
        errors.append("carrier profiles do not cover the declared sectors")
    direct = result.get("direct_support", [])
    if len(direct) != sector_count or any(
        not isinstance(row, list) or len(row) != sector_count for row in direct
    ):
        errors.append("direct support matrix shape mismatch")
    else:
        support_edges = sum(
            value > payload.get("support_tolerance", 0.0) for row in direct for value in row
        )
        if result.get("support_edge_count") != support_edges:
            errors.append("support edge count differs from direct support matrix")

    count_fields = (
        "routed_counts",
        "active_route_counts",
        "support_path_pair_counts",
        "carrier_path_pair_counts",
        "composition_pair_counts",
        "obstructed_pair_counts",
        "cross_carrier_stitch_pair_counts",
        "within_carrier_obstructed_pair_counts",
    )
    pair_fields = (
        "obstructed_pairs",
        "cross_carrier_stitch_pairs",
        "within_carrier_obstructed_pairs",
    )
    expected_depth_keys = {str(index) for index in range(1, depth + 1)}
    for field in count_fields + pair_fields:
        if set(result.get(field, {})) != expected_depth_keys:
            errors.append(f"{field} does not cover exactly the declared depths")

    for current_depth in range(1, depth + 1):
        key = str(current_depth)
        support = result.get("support_path_pair_counts", {}).get(key)
        carrier = result.get("carrier_path_pair_counts", {}).get(key)
        composition = result.get("composition_pair_counts", {}).get(key)
        obstructed = result.get("obstructed_pair_counts", {}).get(key)
        cross_count = result.get("cross_carrier_stitch_pair_counts", {}).get(key)
        within_count = result.get("within_carrier_obstructed_pair_counts", {}).get(key)
        counts = (support, carrier, composition, obstructed, cross_count, within_count)
        if any(not isinstance(value, int) for value in counts):
            errors.append(f"depth {current_depth} relation counts are missing or non-integer")
            continue
        if not composition <= carrier <= support:
            errors.append(f"depth {current_depth} carrier reachability sandwich failed")
        if support - composition != obstructed:
            errors.append(f"depth {current_depth} strict-inclusion count is inconsistent")
        if support - carrier != cross_count:
            errors.append(f"depth {current_depth} cross-carrier count is inconsistent")
        if carrier - composition != within_count:
            errors.append(f"depth {current_depth} within-carrier count is inconsistent")
        obstructed_pairs = _canonical_pairs(
            result.get("obstructed_pairs", {}).get(key),
            f"depth {current_depth} obstructed_pairs",
            errors,
        )
        cross_pairs = _canonical_pairs(
            result.get("cross_carrier_stitch_pairs", {}).get(key),
            f"depth {current_depth} cross_carrier_stitch_pairs",
            errors,
        )
        within_pairs = _canonical_pairs(
            result.get("within_carrier_obstructed_pairs", {}).get(key),
            f"depth {current_depth} within_carrier_obstructed_pairs",
            errors,
        )
        if len(obstructed_pairs) != obstructed:
            errors.append(f"depth {current_depth} obstructed pair count mismatch")
        if len(cross_pairs) != cross_count:
            errors.append(f"depth {current_depth} cross-carrier pair count mismatch")
        if len(within_pairs) != within_count:
            errors.append(f"depth {current_depth} within-carrier pair count mismatch")
        if cross_pairs & within_pairs or obstructed_pairs != cross_pairs | within_pairs:
            errors.append(f"depth {current_depth} obstruction partition mismatch")
        for source, target in obstructed_pairs:
            if supports.get(source, set()) & supports.get(target, set()):
                errors.append(
                    f"obstructed pair {source}->{target} has overlapping carrier support"
                )
        for source, target in within_pairs:
            if not supports.get(source, set()) & supports.get(target, set()):
                errors.append(
                    f"within-carrier pair {source}->{target} has disjoint carrier support"
                )

    key = str(depth)
    support = result.get("support_path_pair_counts", {}).get(key)
    composition = result.get("composition_pair_counts", {}).get(key)
    obstructed = result.get("obstructed_pair_counts", {}).get(key)
    declared_disjoint = {tuple(pair) for pair in result.get("carrier_disjoint_pairs", [])}
    if result.get("carrier_disjoint_pairs", []) != sorted(result.get("carrier_disjoint_pairs", [])):
        errors.append("carrier-disjoint pairs are not in canonical source-target order")
    recomputed_disjoint = {
        (i, j) for i in supports for j in supports if not supports[i] & supports[j]
    }
    if declared_disjoint != recomputed_disjoint:
        errors.append("carrier-disjoint pair registry is inconsistent")
    if result.get("carrier_disjoint_pair_count") != len(recomputed_disjoint):
        errors.append("carrier-disjoint pair count is inconsistent")
    for pair, minimum in result.get("minimum_active_depth_within_bound", {}).items():
        if minimum is not None and not 1 <= minimum <= depth:
            errors.append(f"{pair}: minimum depth exceeds declared bound")
        endpoints = tuple(map(int, pair.split("->")))
        if endpoints in recomputed_disjoint and minimum is not None:
            errors.append(f"{pair}: carrier-disjoint pair reported active")
    expected_pair_keys = {
        f"{source}->{target}"
        for source in range(sector_count)
        for target in range(sector_count)
    }
    if set(result.get("minimum_active_depth_within_bound", {})) != expected_pair_keys:
        errors.append("minimum-depth table does not cover every ordered sector pair")
    recomputed_unresolved = sum(
        minimum is None
        and bool(supports[int(pair.split("->")[0])] & supports[int(pair.split("->")[1])])
        for pair, minimum in result.get("minimum_active_depth_within_bound", {}).items()
        if pair in expected_pair_keys
    )
    if result.get("unresolved_overlapping_pair_count") != recomputed_unresolved:
        errors.append("unresolved overlapping pair count is inconsistent")
    references = payload.get("source_artifacts", [])
    uris = [reference.get("uri") for reference in references]
    if len(uris) != len(set(uris)):
        errors.append("source artifact URIs are not unique")
    if model == "rubik":
        required = {"rime/cubie.py", "rime/cubieoperator.py"}
        if not required <= set(uris):
            errors.append("Rubik source closure is incomplete")
    for reference in references:
        source = ROOT / reference["uri"]
        if not source.is_file():
            errors.append(f"missing source: {reference['uri']}")
            continue
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual != reference.get("sha256"):
            errors.append(f"stale source: {reference['uri']}")
    expected = EXPECTED.get(model)
    if expected is None:
        errors.append(f"unknown model: {model}")
    else:
        minimum_histogram: dict[str, int] = {}
        for minimum in result.get("minimum_active_depth_within_bound", {}).values():
            histogram_key = "null" if minimum is None else str(minimum)
            minimum_histogram[histogram_key] = minimum_histogram.get(histogram_key, 0) + 1
        actual = {
            "depth": depth,
            "support": support,
            "composition": composition,
            "obstructed": obstructed,
            "routes": result.get("routed_counts", {}).get(key),
            "active_routes": result.get("active_route_counts", {}).get(key),
            "disjoint": result.get("carrier_disjoint_pair_count"),
            "unresolved": result.get("unresolved_overlapping_pair_count"),
            "minimum_depth_histogram": minimum_histogram,
        }
        if actual != expected:
            errors.append("registered census baseline changed")
    if recompute and model in EXPECTED and isinstance(depth, int) and depth >= 1:
        rebuilt = build_payload(model, depth)
        normalized_rebuild = json.loads(json.dumps(rebuilt))
        if normalized_rebuild != payload:
            errors.append("producer replay mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--recompute", action="store_true")
    args = parser.parse_args()
    paths = args.paths
    if not paths:
        paths = sorted((HERE / "results").glob("*.json"))
    failures = 0
    for path in paths:
        resolved = path if path.is_absolute() else ROOT / path
        errors = validate(resolved, recompute=args.recompute)
        if errors:
            failures += 1
            print(f"FAIL {resolved}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {resolved}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
