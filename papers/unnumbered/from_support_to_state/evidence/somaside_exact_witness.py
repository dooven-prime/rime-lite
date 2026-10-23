"""One exact first-order obstruction; no trajectory simulation or census.

Default: check compact integer arithmetic using only the standard library.
--check-source: additionally re-extract both complete rows from pinned files.
--build: explicitly create the draft-owned witness; never overwrite a result.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DEFAULT_RESULT = HERE / "somaside_exact_witness.v1.json"
SOURCE = REPO / "experiments/paper16/source"
D23 = SOURCE / "digital_fly_v0_2/results/d2_3_partition_comparison_v0_2.json"
MANIFEST = SOURCE / "digital_fly_v0/results/carrier_v0_manifest.json"
ADMISSION = SOURCE / "digital_fly_v0_1/results/sd1_operator_admission_v0_1.json"
DEFAULT_CARRIER = (
    REPO / "experiments/exploratory/male_cns_connectome/digital_fly_v0/results"
)
PINNED_FILES = {
    "carrier_v0_edges.npz":
        "c94e885cc2e8cde78012ed0a68a4beb42eccfe1b64607bdc90ac46e675d6966d",
    "carrier_v0_nodes.parquet":
        "87aa46280d68a210f6c8ef4a044282fbbb62342bbeeaab8393b0fd7fa770515e",
}
SIGN_MAP = {
    "acetylcholine": 1, "dopamine": 1, "gaba": -1, "glutamate": 1,
    "histamine": 1, "octopamine": 1, "serotonin": 1,
}
MODEL = {
    "carrier": "Y_known_pm",
    "storage": "source_row_target_column",
    "action": "Y_transpose",
    "normalization": "absolute_outgoing_row_L1",
    "beta": [4, 5],
    "gain": 1,
    "clipping": [0, 1],
    "external_input": 0,
    "noise": 0,
    "observation": "somaSide_sector_mean",
    "difference_orientation": "a_minus_b",
}
SELECTION = {
    "record": "partition_results.somaSide.representative_witness_per_sector",
    "sector": "L",
    "source_indices": [1, 4],
    "body_ids": [10002, 10006],
    "coordinate": "M",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def rational(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def derive(rows: list[dict], sizes: dict[str, int]) -> dict:
    """Reconstruct clipping edge by edge, separately from the cross-product."""
    require(set(sizes) == {"<missing>", "L", "M", "R"}, "sector labels")
    require(all(positive_int(n) for n in sizes.values()), "sector sizes")
    require(sum(sizes.values()) == 211577, "node universe")
    require(len(rows) == 2, "two source rows required")
    summaries, direct_outputs = [], []
    for i, row in enumerate(rows):
        require(row["source_index"] == SELECTION["source_indices"][i], "source index")
        require(row["body_id"] == SELECTION["body_ids"][i], "body identity")
        require(row["sector"] == "L", "same input sector")
        require(row["sign"] == SIGN_MAP.get(row["consensus_nt"]), "proxy sign")
        require(row["sign"] in (-1, 1), "known-sign eligibility")
        targets, body_ids = set(), set()
        signed = []
        for target, body_id, sector, count in row["edges"]:
            require(type(target) is int and 0 <= target < 211577, "target index")
            require(positive_int(body_id), "target body identity")
            require(target not in targets and body_id not in body_ids, "duplicate edge")
            require(sector in sizes and positive_int(count), "edge sector/count")
            targets.add(target)
            body_ids.add(body_id)
            signed.append((sector, row["sign"] * count))
        # All arithmetic below is Python bigint/Fraction, never NumPy int64.
        s = sum(abs(w) for _, w in signed)
        require(s > 0, "zero-row source is ineligible")
        p = {j: sum(max(w, 0) for sector, w in signed if sector == j) for j in sizes}
        direct = {j: Fraction(4, 5 * sizes[j]) if j == row["sector"] else Fraction(0)
                  for j in sizes}
        for sector, w in signed:
            clipped = min(Fraction(1), max(Fraction(0), Fraction(w, s)))
            direct[sector] += clipped / (5 * sizes[sector])
        formula = {
            j: (Fraction(4, 5 * sizes[j]) if j == row["sector"] else Fraction(0))
            + Fraction(p[j], 5 * sizes[j] * s) for j in sizes
        }
        require(direct == formula, "edge-level clipping disagrees with formula")
        summaries.append({"row_abs_mass": s, "positive_mass_by_sector": p,
                          "outgoing_edge_count": len(signed)})
        direct_outputs.append(direct)
    j = SELECTION["coordinate"]
    a, b = summaries
    cross = (a["positive_mass_by_sector"][j] * b["row_abs_mass"]
             - b["positive_mass_by_sector"][j] * a["row_abs_mass"])
    denominator = 5 * sizes[j] * a["row_abs_mass"] * b["row_abs_mass"]
    delta = direct_outputs[0][j] - direct_outputs[1][j]
    require(delta == Fraction(cross, denominator) and cross != 0, "not an obstruction")
    return {
        "rows": summaries,
        "common_input": {j: rational(Fraction(1, sizes[j]) if j == "L" else Fraction(0))
                         for j in sizes},
        "successors": [{j: rational(v) for j, v in out.items()} for out in direct_outputs],
        "coordinate": j,
        "cross_product": cross,
        "unreduced_denominator": denominator,
        "exact_difference": rational(delta),
        "conclusion": "NO_EXACT_FIRST_ORDER_FACTORIZATION_ON_ELIGIBLE_UNIT_STATES",
    }


def check(data: dict) -> dict:
    require(data["format"] == "from-support-to-state.somaside-witness.v1", "format")
    require(data["model"] == MODEL, "model changed")
    require(data["selection"] == SELECTION, "selection changed")
    require(data["carrier_sha256"] == PINNED_FILES, "unbound carrier")
    require(data["producer_sha256"] == digest(Path(__file__)), "producer changed")
    actual = derive(data["rows"], data["sector_sizes"])
    require(data["derived"] == actual, "reported arithmetic differs from replay")
    return actual


def source_payload(carrier: Path) -> dict:
    """Re-extract complete source rows; imports are needed only in source mode."""
    import numpy as np
    import pandas as pd

    record = json.loads(D23.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    for name, expected in PINNED_FILES.items():
        require(digest(carrier / name) == expected, f"source file digest: {name}")
    provenance = record["source_provenance"]
    require(provenance["edge_artifact_sha256"] == PINNED_FILES["carrier_v0_edges.npz"],
            "old record edge binding")
    require(provenance["node_artifact_sha256"] == PINNED_FILES["carrier_v0_nodes.parquet"],
            "old record node binding")
    for key, field in (("raw", "raw_operator_sha256"),
                       ("normalized", "normalized_operator_sha256")):
        require(record["operator_hashes"]["Y_known_pm"][key]
                == admission["operators"]["Y_known_pm"][field], "operator identity")
    registration = record["registration"]
    require((registration["alpha"], registration["gamma"], registration["x_max"])
            == (0.2, 1.0, 1.0), "old dynamic parameters")
    representatives = record["partition_results"]["somaSide"]["representative_witness_per_sector"]
    old = next(w for w in representatives if w["sector"] == "L")
    require([old[f"node_{k}_index"] for k in ("a", "b")] == SELECTION["source_indices"],
            "not the previously recorded pair")
    require([old[f"node_{k}_body_id"] for k in ("a", "b")] == SELECTION["body_ids"],
            "old body identities")
    nodes = pd.read_parquet(carrier / "carrier_v0_nodes.parquet")
    labels = nodes["somaSide"].astype("string").fillna("<missing>").astype(str).tolist()
    sizes = dict(sorted(Counter(labels).items()))
    require(sizes == record["partition_results"]["somaSide"]["sector_sizes"], "partition")
    rows = []
    with np.load(carrier / "carrier_v0_edges.npz", allow_pickle=False) as edges:
        source, target, weight = (edges[k] for k in ("row", "col", "weight"))
        require(len(source) == len(target) == len(weight) == manifest["edge_universe"]["admitted_rows"],
                "edge universe")
        for index in SELECTION["source_indices"]:
            node = nodes.iloc[index]
            # Convert each scalar before multiplication or summation.
            extracted = [[int(target[k]), int(nodes.iloc[int(target[k])]["bodyId"]),
                          labels[int(target[k])], int(weight[k])]
                         for k in np.flatnonzero(source == index)]
            rows.append({
                "source_index": index, "body_id": int(node["bodyId"]),
                "sector": labels[index], "consensus_nt": str(node["consensus_nt"]),
                "sign": SIGN_MAP.get(str(node["consensus_nt"]), 0),
                "edges": sorted(extracted),
            })
    return {
        "sector_sizes": sizes,
        "rows": rows,
        "source_records": [
            {"path": p.relative_to(REPO).as_posix(), "checkout_sha256": digest(p)}
            for p in (D23, MANIFEST, ADMISSION)
        ],
        "upstream_table_sha256": {
            k: v for k, v in manifest["source_artifact"].items() if k.endswith("_sha256")
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--check-source", action="store_true")
    parser.add_argument("--carrier-dir", type=Path, default=DEFAULT_CARRIER)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    if args.build:
        payload = source_payload(args.carrier_dir)
        data = {
            "format": "from-support-to-state.somaside-witness.v1",
            "model": MODEL, "selection": SELECTION, "carrier_sha256": PINNED_FILES,
            "producer_sha256": digest(Path(__file__)),
            "boundary": "New draft-owned two-row certificate; not a recertification "
                        "of the old census, full release, or upstream reconstruction.",
            **payload,
            "derived": derive(payload["rows"], payload["sector_sizes"]),
        }
        check(data)
        with args.result.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=True)
            handle.write("\n")
    else:
        data = json.loads(args.result.read_text(encoding="utf-8"))
        check(data)
        if args.check_source:
            payload = source_payload(args.carrier_dir)
            for key, value in payload.items():
                require(data[key] == value, f"source replay differs: {key}")
    level = "SOURCE_EXTRACTION_AND_EXACT_ARITHMETIC" if args.build or args.check_source else "COMPACT_EXACT_ARITHMETIC_ONLY"
    print(json.dumps({"status": "PASS", "scope": level,
                      "cross_product": data["derived"]["cross_product"],
                      "exact_difference": data["derived"]["exact_difference"]}))


if __name__ == "__main__":
    main()
