#!/usr/bin/env python3
"""Audit fixed-scope adapters against canonical ``Lambda_4^complete``.

The construction phase rebuilds the complete tied endpoint-shortest rank-four
relation directly from the P28.6c oracle equations.  It then separates:

* origin coverage of the tagged inherited section domain;
* projection existence for the frozen rank-five transfer records; and
* A0/A1/A2-typed adapter-to-canonical alignment.

Only after that payload has a digest are the already frozen GFPC and PEC
component artifacts opened.  The final phase transports their witnesses along
the exact-row correspondence; it never reruns a success evaluator.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from paper28_prepare_second_rank4_section_candidate import (
    _record_from_edge as _canonical_record_from_edge,
)
from paper28_project_seed_mechanisms import (
    Context,
    _corridor_boundary,
    _cycle,
    _fusion_exact,
    _participation_type,
)
from section_return_core import (
    CompleteExitOracle,
    deserialize_packet_state,
    fusion_witness,
    mass_partition,
)

SCHEMA = "paper28-canonical-return-certificate-alignment-v1"
RECEIPT_SCHEMA = "paper28-canonical-return-certificate-alignment-receipt-v1"
GFPC_SCHEMA = "paper28-gfpc-component-completion-v1"
PEC_SCHEMA = "paper28-pec-component-completion-v1"

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_CAND2_PROJECTABILITY = (
    RESULTS / "paper28_fixed_scope_projectability_support_separation_v1.json.gz"
)
DEFAULT_EXPANDED_PROJECTABILITY = (
    RESULTS / "paper28_expanded_family_support_separation_v1.json.gz"
)
DEFAULT_EXT_PROJECTABILITY = (
    RESULTS / "paper28_extremal_carrier_support_separation_v1.json.gz"
)
DEFAULT_GFPC = RESULTS / "paper28_gfpc_component_completion_v1.json.gz"
DEFAULT_PEC = RESULTS / "paper28_pec_component_completion_v1.json.gz"
DEFAULT_OUTPUT = RESULTS / "paper28_canonical_return_certificate_alignment_v1.json.gz"

CARRIER_SPECS = (
    {
        "id": "ext",
        "section": "Sec_4,ext^(7)",
        "expected_contexts": 35,
        "candidate": RESULTS / "paper28_ext_rank4_section_candidate_v1.json.gz",
        "candidate_schema": "paper28-ext-rank4-section-candidate-v1",
        "rank5_candidate": RESULTS / "paper28_rank5_section_candidate_v1.json.gz",
        "rank5_schema": "paper28-rank5-section-return-candidate-v1",
        "projectability_source": "ext",
    },
    {
        "id": "cand2",
        "section": "Sec_4,cand2^(7)",
        "expected_contexts": 48,
        "candidate": RESULTS / "paper28_second_rank4_section_candidate_v1.json.gz",
        "candidate_schema": "paper28-second-rank4-section-candidate-v1",
        "rank5_candidate": RESULTS
        / "paper28_second_rank5_section_candidate_v1.json.gz",
        "rank5_schema": "paper28-second-rank5-section-candidate-v1",
        "projectability_source": "cand2",
    },
    {
        "id": "cand3",
        "section": "Sec_4,cand3^(7)",
        "expected_contexts": 36,
        "candidate": RESULTS / "paper28_third_rank4_section_candidate_v1.json.gz",
        "candidate_schema": "paper28-third-rank4-section-candidate-v1",
        "rank5_candidate": RESULTS / "paper28_third_rank5_section_candidate_v1.json.gz",
        "rank5_schema": "paper28-third-rank5-section-candidate-v1",
        "projectability_source": "expanded",
    },
    {
        "id": "cand4",
        "section": "Sec_4,cand4^(7)",
        "expected_contexts": 36,
        "candidate": RESULTS / "paper28_fourth_rank4_section_candidate_v1.json.gz",
        "candidate_schema": "paper28-fourth-rank4-section-candidate-v1",
        "rank5_candidate": RESULTS
        / "paper28_fourth_rank5_section_candidate_v1.json.gz",
        "rank5_schema": "paper28-fourth-rank5-section-candidate-v1",
        "projectability_source": "expanded",
    },
    {
        "id": "cand5",
        "section": "Sec_4,cand5^(7)",
        "expected_contexts": 10,
        "candidate": RESULTS / "paper28_fifth_rank4_section_candidate_v1.json.gz",
        "candidate_schema": "paper28-fifth-rank4-section-candidate-v1",
        "rank5_candidate": RESULTS / "paper28_fifth_rank5_section_candidate_v1.json.gz",
        "rank5_schema": "paper28-fifth-rank5-section-candidate-v1",
        "projectability_source": "expanded",
    },
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(path: Path) -> Path:
    return path.with_name(f"{path.name.removesuffix('.json.gz')}.receipt.json")


def _verify_content_digest(payload: Mapping[str, Any], label: str) -> None:
    candidate = dict(payload)
    stored = str(candidate.pop("content_sha256"))
    if _digest(candidate) != stored:
        raise AssertionError(f"{label} content digest mismatch")


def _input_record(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload["content_sha256"],
    }


def _context_from_payload(payload: Mapping[str, Any]) -> Context:
    context = Context(
        n=int(payload["ambient_n"]),
        defect=tuple(int(value) for value in payload["defect"]),
        packets=deserialize_packet_state(payload["packets"]),
        distinguished=frozenset(
            int(value) for value in payload["distinguished_packet"]
        ),
        origin="p28.6v-canonical-replay",
        seed_surface="P28_6V_CANONICAL_RELATION",
        is_seed=True,
    )
    if context.payload != payload:
        raise AssertionError("canonical context replay changed typed source data")
    return context


def _typed_exact_row(record: Mapping[str, Any]) -> dict[str, Any]:
    """Remove only artifact identity, never theorem-facing exact data."""

    return {
        "skeleton": record["skeleton"],
        "accounting": record["accounting"],
        "exact": record["exact"],
    }


def _rows_by_source(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["exact"]["source_context_id"])].append(record)
    for source_rows in grouped.values():
        source_rows.sort(key=lambda row: str(row["receipt_id"]))
    return grouped


def _projectability_carriers(
    *,
    cand2: Mapping[str, Any],
    expanded: Mapping[str, Any],
    ext: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    carriers = {
        "cand2": cand2["projectability"],
        "ext": ext["projectability"],
    }
    carriers.update(
        {str(row["carrier_id"]): row for row in expanded["projectability"]["carriers"]}
    )
    if set(carriers) != {"ext", "cand2", "cand3", "cand4", "cand5"}:
        raise AssertionError("projectability carrier domain drift")
    return carriers


def _verify_projectability_binding(
    *,
    carrier_id: str,
    spec: Mapping[str, Any],
    projectability_artifact: Mapping[str, Any],
    candidate_path: Path,
    rank5_path: Path,
) -> None:
    source = str(spec["projectability_source"])
    if source == "cand2":
        inputs = projectability_artifact["inputs"]
        rank4_input = inputs["rank4_candidate"]
        rank5_input = inputs["rank5_candidate"]
    elif source == "expanded":
        inputs = projectability_artifact["projectability_inputs"][carrier_id]
        rank4_input = inputs["rank4_candidate"]
        rank5_input = inputs["rank5_candidate"]
    elif source == "ext":
        inputs = projectability_artifact["inputs"]
        rank4_input = None
        rank5_input = inputs["rank5_candidate"]
    else:
        raise AssertionError(f"unknown projectability source: {source}")

    if rank5_input["sha256"] != _sha256(rank5_path):
        raise AssertionError(f"{carrier_id} rank-five projectability binding drift")
    if rank4_input is not None and rank4_input["sha256"] != _sha256(candidate_path):
        raise AssertionError(f"{carrier_id} rank-four projectability binding drift")


def _handoff_target_is_bound(
    *,
    context_id: str,
    provenance: Mapping[str, Any],
    transfer: Mapping[str, Any],
) -> bool:
    eta = provenance["eta"]
    target_id = str(transfer["exact"]["target_context"]["context_id"])
    if eta["type"] == "IDENTITY":
        return target_id == context_id and str(eta["target_context_id"]) == context_id
    if eta["type"] == "ATOM_BIJECTION":
        return (
            target_id == str(eta["actual_target_context_id"])
            and str(eta["theorem_context_id"]) == context_id
            and bool(eta["distinguished_packet_preserved"])
        )
    return False


def _canonical_macro_relation(
    context_payload: Mapping[str, Any],
    oracle_cache: dict[tuple[int, tuple[int, ...]], CompleteExitOracle],
) -> list[dict[str, Any]]:
    context = _context_from_payload(context_payload)
    action_key = (context.n, context.defect)
    oracle = oracle_cache.setdefault(
        action_key,
        CompleteExitOracle((_cycle(context.n), context.defect), context.n),
    )
    rows = []
    for edge in oracle.macro_edges(context.mass):
        record, _ = _canonical_record_from_edge(context, edge)
        rows.append(_typed_exact_row(record))
    rows.sort(key=_digest)
    return rows


def _canonical_first_exit_row(
    context: Context, exit_row: Mapping[str, Any]
) -> dict[str, Any]:
    letters = (_cycle(context.n), context.defect)
    word = [int(value) for value in exit_row["word"]]
    target_packets, fusion = fusion_witness(context.packets, word, letters)
    outgoing = frozenset(int(value) for value in fusion["fresh_packet"])
    target_context = Context(
        n=context.n,
        defect=context.defect,
        packets=target_packets,
        distinguished=outgoing,
        origin=context.origin,
        seed_surface=context.seed_surface,
        is_seed=False,
    )
    ancestry_update = {
        "incoming_distinguished_packet": sorted(context.distinguished),
        "participation_type": _participation_type(context.distinguished, [fusion]),
        "outgoing_distinguished_packet": sorted(outgoing),
        "update_rule": "FINAL_STRICT_FUSION_PACKET",
    }
    return {
        "source_context_id": context.context_id,
        "source_rank": len(context.packets),
        "source_partition": list(mass_partition(context.mass)),
        "source_packet_ids": [
            sorted(packet) for _, packet in sorted(context.packets.items())
        ],
        "word": word,
        "length": int(exit_row["length"]),
        "surplus": int(exit_row["surplus"]),
        "corridor_boundary": _corridor_boundary(context.packets, word, letters),
        "fusion_packet_identity": _fusion_exact(fusion),
        "target_rank": len(target_packets),
        "target_partition": list(
            mass_partition(tuple(int(value) for value in exit_row["target"]))
        ),
        "target_endpoint": [int(value) for value in exit_row["target"]],
        "target_context": target_context.payload,
        "ancestry_update": ancestry_update,
    }


def _canonical_first_exit_relation(
    context: Context,
    oracle_cache: dict[tuple[int, tuple[int, ...]], CompleteExitOracle],
) -> list[dict[str, Any]]:
    action_key = (context.n, context.defect)
    oracle = oracle_cache.setdefault(
        action_key,
        CompleteExitOracle((_cycle(context.n), context.defect), context.n),
    )
    rows = [
        _canonical_first_exit_row(context, exit_row)
        for exit_row in oracle.exits(context.mass)
    ]
    rows.sort(key=_digest)
    if len({_digest(row) for row in rows}) != len(rows):
        raise AssertionError("duplicate canonical first-exit typed row")
    return rows


def _context_from_first_exit(row: Mapping[str, Any]) -> Context:
    return _context_from_payload(row["target_context"])


def _word_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[int, ...], Mapping[str, Any]]:
    index: dict[tuple[int, ...], Mapping[str, Any]] = {}
    for row in rows:
        word = tuple(int(value) for value in row["word"])
        if word in index:
            raise AssertionError("canonical first-exit word is not unique")
        index[word] = row
    return index


def _completion_carriers(
    payload: Mapping[str, Any], mechanism: str
) -> dict[str, Mapping[str, Any]]:
    expected_key = "G_GFPC_j_fs" if mechanism == "GFPC" else "G_PEC_j_fs"
    carriers = {
        str(row["carrier_id"]): row for row in payload["evaluation"]["carriers"]
    }
    for row in carriers.values():
        if expected_key not in row:
            raise AssertionError(f"{mechanism} completion relation is absent")
    return carriers


def _local_return_ids(context_row: Mapping[str, Any]) -> list[str]:
    return sorted(
        str(receipt_id)
        for channel in context_row["channels"]
        for receipt_id in channel["local_return_exact_lift_ids"]
    )


def build_payload(
    *,
    cand2_projectability_path: Path = DEFAULT_CAND2_PROJECTABILITY,
    expanded_projectability_path: Path = DEFAULT_EXPANDED_PROJECTABILITY,
    ext_projectability_path: Path = DEFAULT_EXT_PROJECTABILITY,
    gfpc_path: Path = DEFAULT_GFPC,
    pec_path: Path = DEFAULT_PEC,
    carrier_specs: Sequence[Mapping[str, Any]] = CARRIER_SPECS,
) -> dict[str, Any]:
    cand2_projectability = _load(cand2_projectability_path)
    expanded_projectability = _load(expanded_projectability_path)
    ext_projectability = _load(ext_projectability_path)
    for artifact, expected, label in (
        (
            cand2_projectability,
            "paper28-fixed-scope-projectability-support-separation-v1",
            "cand2 projectability",
        ),
        (
            expanded_projectability,
            "paper28-expanded-family-support-separation-v1",
            "expanded projectability",
        ),
        (
            ext_projectability,
            "paper28-extremal-carrier-support-separation-v1",
            "ext projectability",
        ),
    ):
        if artifact.get("schema") != expected:
            raise AssertionError(f"unexpected {label} schema")
        _verify_content_digest(artifact, label)

    projectability_artifacts = {
        "cand2": cand2_projectability,
        "expanded": expanded_projectability,
        "ext": ext_projectability,
    }
    projectability = _projectability_carriers(
        cand2=cand2_projectability,
        expanded=expanded_projectability,
        ext=ext_projectability,
    )

    oracle_cache: dict[tuple[int, tuple[int, ...]], CompleteExitOracle] = {}
    alignment_rows = []
    carrier_summaries = []
    origin_rows = []
    projection_rows = []
    full_correspondence: dict[tuple[str, str], dict[str, str]] = {}
    input_records: dict[str, Any] = {
        "projectability": {
            "cand2": _input_record(cand2_projectability_path, cand2_projectability),
            "expanded": _input_record(
                expanded_projectability_path, expanded_projectability
            ),
            "ext": _input_record(ext_projectability_path, ext_projectability),
        },
        "rank4_adapters": {},
        "rank5_transfer_relations": {},
    }

    for spec in carrier_specs:
        carrier_id = str(spec["id"])
        candidate_path = Path(spec["candidate"])
        rank5_path = Path(spec["rank5_candidate"])
        candidate = _load(candidate_path)
        rank5 = _load(rank5_path)
        if candidate.get("schema") != spec["candidate_schema"]:
            raise AssertionError(f"unexpected {carrier_id} rank-four adapter schema")
        if rank5.get("schema") != spec["rank5_schema"]:
            raise AssertionError(f"unexpected {carrier_id} rank-five schema")
        _verify_content_digest(candidate, f"{carrier_id} rank-four adapter")
        _verify_content_digest(rank5, f"{carrier_id} rank-five relation")
        if candidate["scope"]["evaluation_status"] != "NOT_RUN":
            raise AssertionError(f"{carrier_id} adapter is not pre-evaluation")
        if rank5["scope"]["evaluation_status"] != "NOT_RUN":
            raise AssertionError(f"{carrier_id} transfer relation is not pre-Good_5")
        if rank5["evaluator"]["status"] != "ABSENT_BY_DESIGN":
            raise AssertionError(f"{carrier_id} rank-five evaluator is present")

        source_projectability = projectability_artifacts[
            str(spec["projectability_source"])
        ]
        _verify_projectability_binding(
            carrier_id=carrier_id,
            spec=spec,
            projectability_artifact=source_projectability,
            candidate_path=candidate_path,
            rank5_path=rank5_path,
        )
        input_records["rank4_adapters"][carrier_id] = _input_record(
            candidate_path, candidate
        )
        input_records["rank5_transfer_relations"][carrier_id] = _input_record(
            rank5_path, rank5
        )

        projectability_rows = projectability[carrier_id]["rows"]
        expected_contexts = int(spec["expected_contexts"])
        if len(projectability_rows) != expected_contexts:
            raise AssertionError(f"{carrier_id} projectability count drift")
        projectability_by_context = {
            str(row["context_id"]): row for row in projectability_rows
        }
        if len(projectability_by_context) != expected_contexts:
            raise AssertionError(f"{carrier_id} duplicate projectability context")

        menu_contexts = {
            str(row["source_context"]["context_id"]): row["source_context"]
            for row in candidate["construction"]["menus"]["contexts"]
        }
        fs_records = candidate["construction"]["exact_lifts"]["receipts"]
        fs_by_source = _rows_by_source(fs_records)
        if set(menu_contexts) != set(projectability_by_context):
            raise AssertionError(f"{carrier_id} inherited/admitted domain drift")
        if set(fs_by_source) != set(menu_contexts):
            raise AssertionError(f"{carrier_id} adapter relation domain drift")

        transfer_by_id = {
            str(row["receipt_id"]): row
            for row in rank5["construction"]["exact_lifts"]["receipts"]
        }
        carrier_transfer_ids: set[str] = set()
        carrier_lambda4_rows = 0
        carrier_type_i_paths = 0
        carrier_type_ii_paths = 0
        carrier_provenance_count = 0
        for context_id in sorted(menu_contexts):
            projectability_row = projectability_by_context[context_id]
            provenance_fiber = projectability_row["provenance_fiber"]
            if not provenance_fiber:
                raise AssertionError(f"{carrier_id}/{context_id} has no origin")

            for provenance_row in provenance_fiber:
                provenance = provenance_row["kappa_4_ISE"]
                transfer_id = str(provenance["e"]["receipt_id"])
                transfer = transfer_by_id.get(transfer_id)
                if transfer is None:
                    raise AssertionError("projected provenance has no transfer record")
                if provenance["e"]["receipt_sha256"] != _digest(transfer):
                    raise AssertionError(
                        "transfer receipt digest changed under projection"
                    )
                if provenance["e"]["words"] != transfer["exact"]["words"]:
                    raise AssertionError("transfer word changed under projection")
                if str(provenance["C_up"]["context_id"]) != str(
                    transfer["exact"]["source_context_id"]
                ):
                    raise AssertionError("projected provenance source mismatch")
                if not _handoff_target_is_bound(
                    context_id=context_id,
                    provenance=provenance,
                    transfer=transfer,
                ):
                    raise AssertionError(
                        "transfer target is not bound to admitted source"
                    )
                carrier_transfer_ids.add(transfer_id)
                carrier_provenance_count += 1
                projection_rows.append(
                    {
                        "carrier_id": carrier_id,
                        "context_id": context_id,
                        "transfer_record_id": transfer_id,
                        "kappa_4_ISE_id": provenance_row["kappa_4_ISE_id"],
                    }
                )

            origin_rows.append(
                {
                    "carrier_id": carrier_id,
                    "section": spec["section"],
                    "context_id": context_id,
                    "return_certificate_id": projectability_row[
                        "return_certificate_id"
                    ],
                    "transfer_origin_ids": sorted(
                        str(row["kappa_4_ISE"]["e"]["receipt_id"])
                        for row in provenance_fiber
                    ),
                    "origin_covered": True,
                }
            )

            source_context = _context_from_payload(menu_contexts[context_id])
            lambda4_rows = _canonical_first_exit_relation(source_context, oracle_cache)
            lambda4_by_word = _word_index(lambda4_rows)
            canonical_macro_rows = _canonical_macro_relation(
                menu_contexts[context_id], oracle_cache
            )
            fs_rows = fs_by_source[context_id]
            fs_semantics: dict[str, Mapping[str, Any]] = {}
            fs_id_by_semantic: dict[str, str] = {}
            fs_record_by_semantic: dict[str, Mapping[str, Any]] = {}
            for record in fs_rows:
                typed = _typed_exact_row(record)
                semantic_id = _digest(typed)
                previous = fs_semantics.get(semantic_id)
                if previous is not None and previous != typed:
                    raise AssertionError("fs semantic digest collision")
                if semantic_id in fs_id_by_semantic:
                    raise AssertionError("duplicate fs typed exact row")
                fs_semantics[semantic_id] = typed
                fs_id_by_semantic[semantic_id] = str(record["receipt_id"])
                fs_record_by_semantic[semantic_id] = record

            canonical_macro_semantics = {
                _digest(row): row for row in canonical_macro_rows
            }
            if len(canonical_macro_semantics) != len(canonical_macro_rows):
                raise AssertionError("duplicate canonical macro replay row")
            missing_canonical = sorted(
                set(fs_semantics) - set(canonical_macro_semantics)
            )
            missing_adapter = sorted(set(canonical_macro_semantics) - set(fs_semantics))
            if missing_canonical or missing_adapter:
                raise AssertionError(
                    f"{carrier_id}/{context_id} adapter/macro replay mismatch"
                )

            correspondence = []
            correspondence_by_fs: dict[str, str] = {}
            for semantic_id in sorted(fs_semantics):
                fs_receipt_id = fs_id_by_semantic[semantic_id]
                fs_record = fs_record_by_semantic[semantic_id]
                words = [
                    tuple(int(value) for value in word)
                    for word in fs_record["exact"]["words"]
                ]
                first = lambda4_by_word.get(words[0])
                if first is None:
                    raise AssertionError("macro first corridor is absent from Lambda_4")
                segments = [first]
                segment_ids = [f"l4exit-{_digest(first)[:24]}"]
                if len(words) == 2:
                    intermediate_context = _context_from_first_exit(first)
                    lambda3_rows = _canonical_first_exit_relation(
                        intermediate_context, oracle_cache
                    )
                    second = _word_index(lambda3_rows).get(words[1])
                    if second is None:
                        raise AssertionError(
                            "macro repayment corridor is absent from Lambda_3"
                        )
                    segments.append(second)
                    segment_ids.append(f"l3exit-{_digest(second)[:24]}")
                    carrier_type_ii_paths += 1
                elif len(words) == 1:
                    carrier_type_i_paths += 1
                else:
                    raise AssertionError("rank-four adapter corridor count drift")

                if [row["word"] for row in segments] != fs_record["exact"]["words"]:
                    raise AssertionError("canonical path changed exact corridor words")
                if [row["fusion_packet_identity"] for row in segments] != fs_record[
                    "exact"
                ]["fusion_packet_identities"]:
                    raise AssertionError("canonical path changed fusion identities")
                if (
                    segments[-1]["target_context"]
                    != fs_record["exact"]["target_context"]
                ):
                    raise AssertionError("canonical path changed theorem endpoint")

                canonical_path_id = f"lcanpath-{semantic_id[:24]}"
                correspondence.append(
                    {
                        "fs_receipt_id": fs_receipt_id,
                        "canonical_path_id": canonical_path_id,
                        "canonical_segment_ids": segment_ids,
                        "canonical_segment_count": len(segments),
                        "macro_typed_replay_sha256": semantic_id,
                    }
                )
                correspondence_by_fs[fs_receipt_id] = canonical_path_id
                full_correspondence[(carrier_id, fs_receipt_id)] = {
                    "canonical_path_id": canonical_path_id,
                    "context_id": context_id,
                    "macro_typed_replay_sha256": semantic_id,
                }

            canonical_lambda = {
                "definition": (
                    "Lambda_4^complete(C): complete first-exit relation with "
                    "all tied endpoint-shortest typed exact rows"
                ),
                "source_context_id": context_id,
                "exact_first_exit_row_count": len(lambda4_rows),
                "typed_relation_sha256": _digest(lambda4_rows),
                "canonical_first_exit_row_ids_sha256": _digest(
                    sorted(f"l4exit-{_digest(row)[:24]}" for row in lambda4_rows)
                ),
            }
            fs_certificate = projectability_row["return_certificate"]
            canonical_certificate = {
                "b_4": fs_certificate["b_4"],
                "chi_4": fs_certificate["chi_4"],
                "Lambda_4_complete": canonical_lambda,
                "nu_4": fs_certificate["nu_4"],
            }
            canonical_certificate_id = f"kret4can-{_digest(canonical_certificate)[:24]}"
            same_provenance = [
                {
                    "kappa_4_ISE_id": row["kappa_4_ISE_id"],
                    "fs_return_certificate_id": projectability_row[
                        "return_certificate_id"
                    ],
                    "canonical_return_certificate_id": canonical_certificate_id,
                    "transport": "IDENTICAL_PROVENANCE_RECORD",
                }
                for row in provenance_fiber
            ]
            alignment_rows.append(
                {
                    "carrier_id": carrier_id,
                    "section": spec["section"],
                    "context_id": context_id,
                    "fs_return_certificate_id": projectability_row[
                        "return_certificate_id"
                    ],
                    "canonical_return_certificate_id": canonical_certificate_id,
                    "canonical_return_certificate": canonical_certificate,
                    "alignment_strength": {
                        "A0_every_fs_lift_has_canonical_first_exit_path": True,
                        "A1_typed_observables_and_provenance_transport": True,
                        "A2_adapter_equals_Lambda_4_complete": False,
                        "A2_status": "NOT_CLAIMED_DIFFERENT_RELATION_TYPES",
                        "raw_serialization_identity_required": False,
                    },
                    "fs_exact_lift_count": len(fs_rows),
                    "lambda4_complete_exact_row_count": len(lambda4_rows),
                    "canonical_macro_path_count": len(correspondence),
                    "row_correspondence_sha256": _digest(correspondence),
                    "row_correspondence": correspondence,
                    "same_provenance": same_provenance,
                }
            )
            carrier_lambda4_rows += len(lambda4_rows)

        carrier_summaries.append(
            {
                "carrier_id": carrier_id,
                "section": spec["section"],
                "inherited_context_count": expected_contexts,
                "transfer_record_count": len(carrier_transfer_ids),
                "projected_provenance_count": carrier_provenance_count,
                "fs_exact_lift_count": len(fs_records),
                "lambda4_complete_exact_row_count": carrier_lambda4_rows,
                "canonical_macro_path_count": len(fs_records),
                "type_I_path_count": carrier_type_i_paths,
                "type_II_path_count": carrier_type_ii_paths,
                "A0_holds": True,
                "A1_holds": True,
                "A2_adapter_equals_Lambda4_claimed": False,
            }
        )

    if len(origin_rows) != 165 or len(alignment_rows) != 165:
        raise AssertionError("tagged inherited section domain is not 165")
    transfer_projection_counts = Counter(
        (row["carrier_id"], row["transfer_record_id"]) for row in projection_rows
    )
    if not transfer_projection_counts or min(transfer_projection_counts.values()) < 1:
        raise AssertionError("a frozen transfer record has no ISE projection")

    alignment_core = {
        "canonical_constructor": {
            "equation_source": "P28.6c complete first-exit equations",
            "implementation": "CompleteExitOracle.exits",
            "source_exact": True,
            "endpoint_shortest": True,
            "all_tied_realizations_retained": True,
            "success_evaluator_loaded": False,
        },
        "inherited_section_domain": {
            "name": "Sec_4^{inh,fs}(7)",
            "definition": (
                "tagged admitted rank-four pairs possessing at least one frozen "
                "pre-Good_5 rank-five transfer origin"
            ),
            "context_count": len(origin_rows),
            "origin_coverage_holds": all(row["origin_covered"] for row in origin_rows),
            "rows": origin_rows,
        },
        "projection_existence": {
            "domain": (
                "the frozen source-authorized TransferRecord_5 relation used by "
                "the five fixed-scope projectability audits"
            ),
            "transfer_record_count": len(transfer_projection_counts),
            "projected_provenance_count": len(projection_rows),
            "every_transfer_has_projection": True,
            "rows": sorted(
                projection_rows,
                key=lambda row: (
                    row["carrier_id"],
                    row["transfer_record_id"],
                    row["kappa_4_ISE_id"],
                ),
            ),
        },
        "alignment_definition": {
            "name": "Align_4(C; kappa_4^fs, kappa_4^can)",
            "A0": (
                "every fs macro lift has a one- or two-segment canonical "
                "first-exit path image"
            ),
            "A1": (
                "boundary, ancestry, normalization, exact-row observables, and "
                "ISE provenance transport along the image"
            ),
            "A2": (
                "NOT_CLAIMED: the adapter is a Type-I/II macro relation, while "
                "Lambda_4^complete(C) is the single first-exit relation"
            ),
            "raw_serialization_equality": "NOT_REQUIRED_OR_CLAIMED",
        },
        "carrier_summaries": carrier_summaries,
        "rows": alignment_rows,
    }
    frozen_alignment_sha256 = _digest(alignment_core)

    # Post-freeze theorem transport.  These inputs are deliberately opened only
    # after the success-free alignment core has its immutable digest.
    gfpc = _load(gfpc_path)
    pec = _load(pec_path)
    if gfpc.get("schema") != GFPC_SCHEMA or pec.get("schema") != PEC_SCHEMA:
        raise AssertionError("unexpected component completion schema")
    _verify_content_digest(gfpc, "GFPC completion")
    _verify_content_digest(pec, "PEC completion")
    if not gfpc["theorem"]["holds"] or not pec["theorem"]["holds"]:
        raise AssertionError("a fixed-scope component theorem is not closed")
    gfpc_carriers = _completion_carriers(gfpc, "GFPC")
    pec_carriers = _completion_carriers(pec, "PEC")
    completion_assignment = {
        "ext": ("GFPC", gfpc_carriers["ext"]),
        "cand2": ("GFPC", gfpc_carriers["cand2"]),
        "cand3": ("PEC", pec_carriers["cand3"]),
        "cand4": ("PEC", pec_carriers["cand4"]),
        "cand5": ("PEC", pec_carriers["cand5"]),
    }
    alignment_by_source = {
        (row["carrier_id"], row["context_id"]): row for row in alignment_rows
    }
    transported_rows = []
    transport_summaries = []
    for carrier_id in ("ext", "cand2", "cand3", "cand4", "cand5"):
        mechanism, completion = completion_assignment[carrier_id]
        completion_contexts = {
            str(row["context_id"]): row for row in completion["contexts"]
        }
        successful_count = 0
        for context_id in sorted(completion_contexts):
            context_row = completion_contexts[context_id]
            alignment = alignment_by_source[(carrier_id, context_id)]
            correspondence = {
                str(row["fs_receipt_id"]): str(row["canonical_path_id"])
                for row in alignment["row_correspondence"]
            }
            success_ids = _local_return_ids(context_row)
            if not success_ids:
                raise AssertionError("closed component source lost LocalReturn")
            if not set(success_ids).issubset(correspondence):
                raise AssertionError("a successful fs lift lacks a canonical image")
            good_key = (
                "G_GFPC_j_fs_kappa_4_ISE_ids"
                if mechanism == "GFPC"
                else "G_PEC_j_fs_kappa_4_ISE_ids"
            )
            good_provenance = sorted(str(value) for value in context_row[good_key])
            canonical_provenance = {
                str(row["kappa_4_ISE_id"]) for row in alignment["same_provenance"]
            }
            if not good_provenance or not set(good_provenance).issubset(
                canonical_provenance
            ):
                raise AssertionError("component support did not transport by SameProv")
            canonical_success_ids = sorted(
                correspondence[value] for value in success_ids
            )
            successful_count += len(canonical_success_ids)
            transported_rows.append(
                {
                    "carrier_id": carrier_id,
                    "context_id": context_id,
                    "mechanism": mechanism,
                    "canonical_return_certificate_id": alignment[
                        "canonical_return_certificate_id"
                    ],
                    "kappa_4_ISE_ids": good_provenance,
                    "canonical_local_return_path_count": len(canonical_success_ids),
                    "canonical_local_return_path_ids_sha256": _digest(
                        canonical_success_ids
                    ),
                    "support_transport": "IDENTICAL_PROVENANCE_RECORD",
                    "local_return_transport": ("A0_CANONICAL_FIRST_EXIT_PATH_IMAGE"),
                }
            )
        transport_summaries.append(
            {
                "carrier_id": carrier_id,
                "mechanism": mechanism,
                "source_count": len(completion_contexts),
                "canonically_completed_source_count": len(completion_contexts),
                "canonical_local_return_path_count": successful_count,
            }
        )

    if len(transported_rows) != 165:
        raise AssertionError("canonical mechanism transport does not cover 165 sources")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "tagged_inherited_section_context_count": 165,
            "all_n_claim": False,
            "all_rank_claim": False,
            "all_Sec_4_origin_coverage_claim": False,
            "success_evaluator_rerun": False,
        },
        "phase_order": [
            "load_frozen_pre_evaluation_rank4_adapters",
            "load_frozen_pre_Good5_transfer_relations_and_projectability_payloads",
            "rebuild_Lambda_4_complete_from_P28_6c_equations_without_success",
            "freeze_origin_projection_and_alignment_core",
            "only_then_load_frozen_GFPC_and_PEC_component_theorems",
            "transport_support_and_LocalReturn_without_rerunning_evaluators",
        ],
        "inputs": {
            **input_records,
            "post_freeze_component_theorems": {
                "GFPC": _input_record(gfpc_path, gfpc),
                "PEC": _input_record(pec_path, pec),
            },
        },
        "alignment_core": alignment_core,
        "frozen_alignment_core_sha256": frozen_alignment_sha256,
        "canonical_mechanism_transport": {
            "loaded_after_alignment_freeze": True,
            "component_evaluator_rerun": False,
            "support_transport_uses_same_provenance": True,
            "local_return_transport_uses_A0_canonical_paths": True,
            "source_count": len(transported_rows),
            "canonically_completed_source_count": len(transported_rows),
            "carrier_summaries": transport_summaries,
            "rows": transported_rows,
        },
        "theorems": {
            "fixed_scope_origin_coverage": True,
            "fixed_scope_projection_existence": True,
            "A0_alignment": True,
            "A1_alignment": True,
            "A2_adapter_equals_Lambda4_complete": False,
            "adapter_macro_equals_canonical_path_replay": True,
            "raw_adapter_serialization_equality": False,
            "canonical_fixed_scope_mechanism_cover": True,
        },
        "claim_boundary": {
            "proved": [
                "all 165 tagged admitted sources lie in Sec_4^{inh,fs}(7)",
                "every transfer record in the frozen inherited transfer domain has an ISE projection",
                "all five adapters are A0/A1 aligned with canonical Lambda_4^complete",
                "every Type-I/II adapter lift replays as a one/two-step canonical first-exit path",
                "the frozen GFPC/PEC support and LocalReturn witnesses transport to canonical path certificates",
            ],
            "not_claimed": [
                "Sec_4 implies Sec_4^inh for arbitrary n or for all admitted sections",
                "all-n TransferRecord_5 implies Proj_ISE existence",
                "equality of a Type-I/II macro adapter with the single first-exit relation Lambda_4^complete",
                "raw JSON or receipt-id equality between adapters and canonical relations",
                "all-n GFPC or PEC component completion",
                "all-rank F5",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    output: Path,
    payload: Mapping[str, Any],
    input_paths: Sequence[Path],
) -> dict[str, Any]:
    source_paths = [
        Path(__file__).resolve(),
        HERE / "paper28_prepare_second_rank4_section_candidate.py",
        HERE / "paper28_project_seed_mechanisms.py",
        HERE / "section_return_core.py",
        HERE
        / "validation"
        / "validate_paper28_canonical_return_certificate_alignment.py",
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": (
            "FULL_CANONICAL_REPLAY_THEN_POST_FREEZE_COMPONENT_TRANSPORT"
        ),
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "frozen_alignment_core_sha256": payload["frozen_alignment_core_sha256"],
        },
        "inputs": [
            {"name": path.name, "sha256": _sha256(path)} for path in input_paths
        ],
        "source_closure": [
            {
                "name": path.relative_to(HERE).as_posix(),
                "sha256": _sha256(path),
            }
            for path in source_paths
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cand2-projectability",
        type=Path,
        default=DEFAULT_CAND2_PROJECTABILITY,
    )
    parser.add_argument(
        "--expanded-projectability",
        type=Path,
        default=DEFAULT_EXPANDED_PROJECTABILITY,
    )
    parser.add_argument(
        "--ext-projectability",
        type=Path,
        default=DEFAULT_EXT_PROJECTABILITY,
    )
    parser.add_argument("--gfpc", type=Path, default=DEFAULT_GFPC)
    parser.add_argument("--pec", type=Path, default=DEFAULT_PEC)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_payload(
        cand2_projectability_path=args.cand2_projectability,
        expanded_projectability_path=args.expanded_projectability,
        ext_projectability_path=args.ext_projectability,
        gfpc_path=args.gfpc,
        pec_path=args.pec,
    )
    _write(args.output, payload)
    input_paths = [
        args.cand2_projectability,
        args.expanded_projectability,
        args.ext_projectability,
        *(Path(spec["candidate"]) for spec in CARRIER_SPECS),
        *(Path(spec["rank5_candidate"]) for spec in CARRIER_SPECS),
        args.gfpc,
        args.pec,
    ]
    receipt = build_receipt(
        output=args.output,
        payload=payload,
        input_paths=input_paths,
    )
    default_receipt_path(args.output).write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="ascii",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.output.as_posix(),
                "artifact_sha256": _sha256(args.output),
                "frozen_alignment_core_sha256": payload["frozen_alignment_core_sha256"],
                "inherited_sources": payload["alignment_core"][
                    "inherited_section_domain"
                ]["context_count"],
                "transfer_records": payload["alignment_core"]["projection_existence"][
                    "transfer_record_count"
                ],
                "lambda4_complete_exact_rows": sum(
                    row["lambda4_complete_exact_row_count"]
                    for row in payload["alignment_core"]["carrier_summaries"]
                ),
                "canonical_macro_paths": sum(
                    row["canonical_macro_path_count"]
                    for row in payload["alignment_core"]["carrier_summaries"]
                ),
                "canonically_completed_sources": payload[
                    "canonical_mechanism_transport"
                ]["canonically_completed_source_count"],
                "A0": True,
                "A1": True,
                "A2_adapter_equals_Lambda4": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
