#!/usr/bin/env python3
"""Build the fail-closed S1 annotation-intersection structural carrier.

The release weight table is a segment/body-pair table.  This script only
admits rows whose two endpoint IDs occur in the curated annotation table.  It
does not claim that this operation reconstructs a neuron-level connectome.
The resulting sparse COO edge arrays retain the release orientation:
``row=source, column=target``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.ipc as ipc


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "digital_fly_v0"
RESULTS = OUT / "results"
WEIGHTS = DATA / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
ANNOTATIONS = DATA / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTERS = DATA / "body-neurotransmitters-male-cns-v1.0.feather"


def label(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "<missing>"
    text = str(value).strip()
    return text if text and text.lower() != "nan" else "<missing>"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="deterministic prefix of the weight table (testing only; default scans all rows)",
    )
    parser.add_argument("--output-prefix", default="carrier_v0")
    args = parser.parse_args()
    if args.max_rows is not None and args.max_rows <= 0:
        raise ValueError("--max-rows must be positive")
    for path in (WEIGHTS, ANNOTATIONS, NEUROTRANSMITTERS):
        if not path.is_file():
            raise FileNotFoundError(path)

    annotations = pd.read_feather(
        ANNOTATIONS, columns=["bodyId", "superclass", "somaSide", "rootSide", "type"]
    )
    if not annotations["bodyId"].is_unique:
        raise ValueError("annotation bodyId is not unique")
    annotations["bodyId"] = annotations["bodyId"].astype("int64")
    annotations = annotations.sort_values("bodyId", kind="mergesort").reset_index(drop=True)
    node_ids = annotations["bodyId"].to_numpy(dtype=np.int64)
    nt = pd.read_feather(
        NEUROTRANSMITTERS, columns=["body", "consensus_nt", "predicted_nt_confidence"]
    )
    if not nt["body"].is_unique:
        raise ValueError("neurotransmitter body IDs are not unique")
    nt = nt.rename(columns={"body": "bodyId"})
    nt["nt_record_present"] = True
    nt["bodyId"] = nt["bodyId"].astype("int64")
    nt = nt[["bodyId", "consensus_nt", "predicted_nt_confidence", "nt_record_present"]]
    nodes = annotations.merge(nt, how="left", on="bodyId", validate="one_to_one")
    nodes["nt_record_present"] = nodes["nt_record_present"].fillna(False).astype(bool)
    for column in ("superclass", "somaSide", "rootSide", "type"):
        nodes[column] = nodes[column].map(label)
    nodes["consensus_nt"] = nodes.apply(
        lambda row: (
            "nt_missing"
            if not row["nt_record_present"]
            else ("unclear" if label(row["consensus_nt"]) == "<missing>" else label(row["consensus_nt"]))
        ),
        axis=1,
    )

    rows_chunks: list[np.ndarray] = []
    cols_chunks: list[np.ndarray] = []
    weight_chunks: list[np.ndarray] = []
    admitted_rows = 0
    raw_rows = 0
    raw_weight_sum = 0
    source = pa.memory_map(str(WEIGHTS), "r")
    reader = ipc.open_file(source)
    try:
        sorted_ids = node_ids
        for batch_index in range(reader.num_record_batches):
            if args.max_rows is not None and raw_rows >= args.max_rows:
                break
            batch = reader.get_batch(batch_index)
            pre = batch.column("body_pre").to_numpy(zero_copy_only=False)
            post = batch.column("body_post").to_numpy(zero_copy_only=False)
            weights = batch.column("weight").to_numpy(zero_copy_only=False)
            if args.max_rows is not None and raw_rows + len(weights) > args.max_rows:
                keep = args.max_rows - raw_rows
                pre, post, weights = pre[:keep], post[:keep], weights[:keep]
            raw_rows += len(weights)
            raw_weight_sum += int(weights.sum(dtype=np.int64))
            # searchsorted is substantially cheaper than a Python lookup for
            # the 150M-row release table, and IDs are sorted above.
            pre_pos = np.searchsorted(sorted_ids, pre)
            post_pos = np.searchsorted(sorted_ids, post)
            pre_ok = (pre_pos < len(sorted_ids)) & (sorted_ids[np.minimum(pre_pos, len(sorted_ids) - 1)] == pre)
            post_ok = (post_pos < len(sorted_ids)) & (sorted_ids[np.minimum(post_pos, len(sorted_ids) - 1)] == post)
            keep_mask = pre_ok & post_ok
            if np.any(keep_mask):
                rows_chunks.append(pre_pos[keep_mask].astype(np.int32, copy=False))
                cols_chunks.append(post_pos[keep_mask].astype(np.int32, copy=False))
                weight_chunks.append(weights[keep_mask].astype(np.int32, copy=False))
                admitted_rows += int(keep_mask.sum())
    finally:
        source.close()

    if rows_chunks:
        edge_rows = np.concatenate(rows_chunks)
        edge_cols = np.concatenate(cols_chunks)
        edge_weights = np.concatenate(weight_chunks)
    else:
        edge_rows = np.empty(0, dtype=np.int32)
        edge_cols = np.empty(0, dtype=np.int32)
        edge_weights = np.empty(0, dtype=np.int32)
    if len(edge_rows) != admitted_rows:
        raise AssertionError("admitted edge count mismatch")
    # The release-wide edge audit established distinct body pairs.  We retain
    # that receipt rather than materialising a Python set of ~26M tuples here.

    source_nt = nodes["consensus_nt"].to_numpy(dtype=object)[edge_rows]
    nt_counts: dict[str, int] = {}
    nt_weight_sums: dict[str, int] = {}
    for nt_label in sorted(nodes["consensus_nt"].unique().tolist()):
        key = str(nt_label)
        mask = source_nt == nt_label
        nt_counts[key] = int(mask.sum())
        nt_weight_sums[key] = int(edge_weights[mask].sum(dtype=np.int64))
    nt_node_counts = nodes["consensus_nt"].value_counts().to_dict()
    nt_partition_receipt = {
        "axis": "presynaptic source node consensus_nt",
        "labels_including_unclear_and_nt_missing": sorted(nt_counts),
        "node_count_by_label": {str(key): int(value) for key, value in sorted(nt_node_counts.items())},
        "nt_missing_node_count": int(nt_node_counts.get("nt_missing", 0)),
        "unclear_node_count": int(nt_node_counts.get("unclear", 0)),
        "edge_count_by_label": dict(sorted(nt_counts.items())),
        "weight_sum_by_label": dict(sorted(nt_weight_sums.items())),
        "edge_class_count_sum": int(sum(nt_counts.values())),
        "edge_class_weight_sum": int(sum(nt_weight_sums.values())),
        "edge_count_identity_holds": sum(nt_counts.values()) == admitted_rows,
        "weight_sum_identity_holds": sum(nt_weight_sums.values()) == int(edge_weights.sum(dtype=np.int64)),
        "exact_one_source_label_per_admitted_edge": True,
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    prefix = args.output_prefix
    edge_path = RESULTS / f"{prefix}_edges.npz"
    node_path = RESULTS / f"{prefix}_nodes.parquet"
    manifest_path = RESULTS / f"{prefix}_manifest.json"
    np.savez(edge_path, row=edge_rows, col=edge_cols, weight=edge_weights)
    nodes.to_parquet(node_path, index=False)

    mapping_payload = nodes[["bodyId", "superclass", "somaSide", "rootSide", "type", "consensus_nt"]].to_json(
        orient="records", force_ascii=False
    ).encode("utf-8")
    manifest = {
        "schema": "rime.exploratory.digital-fly-carrier-manifest.v0",
        "status": "validated_for_pilot",
        "release": "MaleCNS v1.0",
        "source_artifact": {
            "weights": str(WEIGHTS.relative_to(ROOT)),
            "annotations": str(ANNOTATIONS.relative_to(ROOT)),
            "neurotransmitters": str(NEUROTRANSMITTERS.relative_to(ROOT)),
            "weights_sha256": sha256_file(WEIGHTS),
            "annotations_sha256": sha256_file(ANNOTATIONS),
            "neurotransmitters_sha256": sha256_file(NEUROTRANSMITTERS),
        },
        "carrier_basis": "annotation_intersection_structural",
        "node_universe": {
            "definition": "all curated annotation body IDs; admitted edges require both endpoints in this universe",
            "count": int(len(nodes)),
            "endpoint_inclusion_rule": "body_pre and body_post both present in body-annotations bodyId",
            "isolated_nodes_included": True,
        },
        "edge_universe": {
            "raw_rows_scanned": raw_rows,
            "admitted_rows": admitted_rows,
            "admitted_fraction": admitted_rows / raw_rows if raw_rows else None,
            "raw_weight_sum_scanned": raw_weight_sum,
            "duplicate_body_pairs": 0,
            "orientation": "source_row_target_column",
        },
        "artifacts": {
            "edges": str(edge_path.relative_to(ROOT)),
            "nodes": str(node_path.relative_to(ROOT)),
        },
        "sectorization": {
            "observation_fields": ["superclass", "somaSide", "rootSide", "type"],
            "mapping_sha256": hashlib.sha256(mapping_payload).hexdigest(),
            "missing_label": "<missing>",
            "unannotated_endpoint_policy": "not_a_relay_witness",
        },
        "operator_family": {
            "labels": ["single_Y", "presynaptic_consensus_nt_masked"],
            "neurotransmitter_semantics": "structural_identity_only",
            "unclear_policy": "retain_explicit_label",
            "decomposition_identity": "Y_admitted = sum_a Y^(a) + Y^(unclear) + Y^(nt_missing); missing and unclear are distinct labels",
            "decomposition_receipt": nt_partition_receipt,
        },
        "weight_variants": {
            "binary": "1 for each admitted edge",
            "raw": "release weight (detected synapse-count measurement)",
            "log": "log2(1 + release weight)",
        },
        "normalization": {
            "name": "outgoing_row_l1",
            "formula": "Y_norm[i,j] = Y[i,j] / sum_j Y[i,j]",
            "zero_row_policy": "retain zero row",
            "incoming_update": "Y_norm.T @ x",
        },
        "route_audit": {
            "depth2_artifact": "results/path_lifting_audit_full_v3.json",
            "depth3_artifact": "results/path_lifting_depth3_audit_full_v1.json",
            "coverage_receipt": "results/superclass_aggregate_full_v3.json",
        },
        "dynamic_model": {
            "state_basis": "admitted annotation-intersection node basis",
            "sector_role": "observation map C only; never D0 state carrier",
            "activation": "clipped_relu(phi(z)=min(x_max,max(0,z)), phi(0)=0)",
            "gain_semantics": "direct dimensionless gamma under outgoing_row_l1; spectral_radius is diagnostic only",
            "noise": "zero or seeded Gaussian",
        },
        "claim_boundary": {
            "supports": ["model-relative structural response experiments"],
            "does_not_support": ["neuron reconstruction", "physiological capacity", "causal or in-vivo claims"],
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"raw_rows": raw_rows, "admitted_rows": admitted_rows, "nodes": len(nodes), "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
