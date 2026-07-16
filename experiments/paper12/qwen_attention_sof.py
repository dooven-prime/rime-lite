"""Paper XII diagnostic: real Qwen attention-head SOF audit.

Claim status:
    - Real pretrained-LLM diagnostic case study for Paper XII.
    - Demonstrates natural attention-head sectorization without synthetic
      generators or hand-built token partitions.
    - Not an explainability theory and not a theorem about all LLMs.

Default model:
    Qwen/Qwen2.5-0.5B-Instruct, layer 12, local cache only.

Key default observations:
    Head 3:  1 group, all tokens attend to one target (global attention).
    Head 1:  3 groups with sizes [38, 4, 3] (coarse ternary clustering).
    Head 6:  4 natural sectors after the >=2-token filter.
    Head 13: 13 groups (more dispersed attention).

The SOF audit uses Head 6 sectors in token space and the layer's attention
matrices as observables.  No random generator is introduced.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:
    import torch
    import transformers
    from transformers import AutoModel, AutoTokenizer
except ImportError as exc:  # pragma: no cover - user-facing dependency error
    raise SystemExit(
        "Missing optional dependencies 'torch' and/or 'transformers'. "
        "Run this script in the project environment with the local model cache."
    ) from exc

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine  # noqa: E402


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_REVISION = "7ae557604adf67be50417f59c2c2f167def9a775"
TEXT = (
    "The cat sat on the mat because it was tired. "
    "Later the dog chased the cat around the garden. "
    "The bird flew over the fence and landed on the roof. "
    "Meanwhile the fish swam in the pond under the bridge."
)


@dataclass
class HeadRecord:
    head: int
    n_groups: int
    sector_count: int
    sizes: list[int]
    groups: dict[int, list[int]]


def clean_token(token: str) -> str:
    return token.replace("\u0120", "_")


def resolve_device(requested: str) -> str:
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requested, but CUDA is unavailable")
    return requested


def resolve_dtype(name: str) -> torch.dtype:
    return {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }[name]


def load_qwen(
    *,
    model_name: str,
    revision: str,
    cache_dir: Path | None,
    local_files_only: bool,
    device: str,
    dtype: torch.dtype,
) -> tuple[object, object]:
    cache = str(cache_dir) if cache_dir is not None else None
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        revision=revision,
        cache_dir=cache,
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    model = AutoModel.from_pretrained(
        model_name,
        revision=revision,
        cache_dir=cache,
        trust_remote_code=True,
        torch_dtype=dtype,
        attn_implementation="eager",
        local_files_only=local_files_only,
    )
    model.to(device)
    model.eval()
    return tokenizer, model


def head_records(attentions: np.ndarray, min_sector_size: int = 2) -> list[HeadRecord]:
    records = []
    for head in range(attentions.shape[0]):
        top_target = attentions[head].argmax(axis=1)
        groups: dict[int, list[int]] = {}
        for token_idx, target_idx in enumerate(top_target):
            groups.setdefault(int(target_idx), []).append(token_idx)

        sizes = sorted((len(members) for members in groups.values()), reverse=True)
        sector_count = sum(1 for size in sizes if size >= min_sector_size)
        records.append(
            HeadRecord(
                head=head,
                n_groups=len(groups),
                sector_count=sector_count,
                sizes=sizes,
                groups=groups,
            )
        )
    return records


def sectors_from_head(
    record: HeadRecord,
    n_tokens: int,
    min_sector_size: int = 2,
) -> tuple[list[np.ndarray], list[dict], list[int]]:
    del n_tokens  # The strict realization is built on the retained token subspace.
    sectors: list[np.ndarray] = []
    metadata: list[dict] = []

    ordered_groups = sorted(record.groups.items(), key=lambda item: (-len(item[1]), item[0]))
    retained_members = [
        token
        for _, members in ordered_groups
        if len(members) >= min_sector_size
        for token in members
    ]
    retained_position = {token: idx for idx, token in enumerate(retained_members)}
    eye = np.eye(len(retained_members), dtype=complex)
    for target_idx, members in ordered_groups:
        if len(members) < min_sector_size:
            continue
        sectors.append(eye[:, [retained_position[token] for token in members]])
        metadata.append({"target": target_idx, "members": members})
    return sectors, metadata, retained_members


def audit_attention_sof(sectors: list[np.ndarray], attentions: np.ndarray) -> dict:
    observables = [attentions[head].astype(complex) for head in range(attentions.shape[0])]
    engine = AccessibilityEngine(sectors, observables, tol=1e-8, max_depth=3)
    audit = engine.audit()
    frozen = engine.frozen_pairs()
    R1, R2, _ = engine.support()
    D, _ = engine.depth()
    return {
        **audit,
        **frozen,
        "support_graph": np.any(R1, axis=0),
        "bridge_graph": np.any(R2, axis=0),
        "D": D,
    }


def run(
    *,
    model_name: str = MODEL_NAME,
    revision: str = MODEL_REVISION,
    cache_dir: Path | None = None,
    local_files_only: bool = True,
    sector_head: int = 6,
    requested_device: str = "auto",
    dtype_name: str = "float32",
) -> dict:
    device = resolve_device(requested_device)
    dtype = resolve_dtype(dtype_name)
    tokenizer, model = load_qwen(
        model_name=model_name,
        revision=revision,
        cache_dir=cache_dir,
        local_files_only=local_files_only,
        device=device,
        dtype=dtype,
    )
    inputs = tokenizer(TEXT, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    layer = model.config.num_hidden_layers // 2
    layer_attn = outputs.attentions[layer][0].detach().cpu().numpy()
    records = head_records(layer_attn, min_sector_size=2)
    selected = records[sector_head]
    sectors, sector_metadata, retained_tokens = sectors_from_head(
        selected, len(tokens), min_sector_size=2
    )
    restricted_attn = layer_attn[:, retained_tokens][:, :, retained_tokens]
    audit = audit_attention_sof(sectors, restricted_attn) if len(sectors) >= 2 else None

    return {
        "model_name": model_name,
        "requested_revision": revision,
        "resolved_revision": getattr(model.config, "_commit_hash", None) or revision,
        "local_files_only": local_files_only,
        "cache_dir_supplied": cache_dir is not None,
        "requested_device": requested_device,
        "resolved_device": device,
        "dtype": dtype_name,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "torch_version": str(torch.__version__),
        "transformers_version": transformers.__version__,
        "layers": model.config.num_hidden_layers,
        "heads": model.config.num_attention_heads,
        "hidden_size": model.config.hidden_size,
        "use_sliding_window": bool(getattr(model.config, "use_sliding_window", False)),
        "layer": layer,
        "tokens": [clean_token(token) for token in tokens],
        "records": records,
        "sector_head": sector_head,
        "sector_metadata": sector_metadata,
        "retained_tokens": retained_tokens,
        "audit": audit,
    }


def print_head_summary(records: list[HeadRecord], highlighted: set[int]) -> None:
    for record in records:
        marker = "*" if record.head in highlighted else " "
        print(
            f"  {marker} Head {record.head:>2d}: "
            f"{record.n_groups:>2d} groups, "
            f"{record.sector_count:>2d} sectors>=2, "
            f"sizes={record.sizes}"
        )


def sofreport(result: dict) -> dict:
    audit = result["audit"]
    selected = result["records"][result["sector_head"]]
    head_diversity = [
        {
            "head": record.head,
            "group_count": record.n_groups,
            "filtered_sector_count": record.sector_count,
            "group_sizes": record.sizes,
        }
        for record in result["records"]
    ]

    if audit is None:
        support_matrix = None
        bridge_matrix = None
        repair_matrix = None
        claim_status = "boundary"
        claim_note = "selected attention head produced fewer than two retained sectors"
    else:
        support = audit["support_graph"]
        depth = audit["D"]
        repaired = [
            {"source": i, "target": j, "depth": int(depth[i, j])}
            for i in range(audit["n_sec"])
            for j in range(audit["n_sec"])
            if i != j and not support[i, j] and depth[i, j] < 3
        ]
        support_matrix = {
            "kind": "aggregated_R1_over_attention_heads",
            "matrix": support.astype(int).tolist(),
            "offdiag_density_pct": audit["R1_pct"],
        }
        bridge_matrix = {
            "kind": "aggregated_R2_over_attention-head commutators",
            "matrix": audit["bridge_graph"].astype(int).tolist(),
            "offdiag_density_pct": audit["R2_pct"],
        }
        repair_matrix = {
            "kind": "finite attention-observable Lie-depth repair",
            "depth_matrix": depth.astype(int).tolist(),
            "repaired_pairs": repaired,
            "repaired_count": audit["D_repaired"],
            "terminally_frozen_count": audit["frozen_D"],
        }
        claim_status = "diagnostic"
        claim_note = "real pretrained-Qwen attention-head diagnostic"

    return {
        "sofrs_version": "1.0",
        "report_id": "qwen_attention",
        "system": result["model_name"],
        "claim_status": claim_status,
        "claim_note": claim_note,
        "provenance": {
            "source_identity": result["model_name"],
            "model": result["model_name"],
            "model_revision": result["resolved_revision"],
            "tokenizer_revision": result["resolved_revision"],
            "local_files_only": result["local_files_only"],
            "cache_dir_supplied": result["cache_dir_supplied"],
            "script": "experiments/paper12/qwen_attention_sof.py",
            "python_version": result["python_version"],
            "platform": result["platform"],
            "numpy_version": result["numpy_version"],
            "torch_version": result["torch_version"],
            "transformers_version": result["transformers_version"],
            "requested_device": result["requested_device"],
            "resolved_device": result["resolved_device"],
            "dtype": result["dtype"],
            "attention_implementation": "eager",
            "layer": result["layer"],
            "layers": result["layers"],
            "attention_heads": result["heads"],
            "hidden_size": result["hidden_size"],
            "use_sliding_window": result["use_sliding_window"],
            "input_text": TEXT,
            "token_count": len(result["tokens"]),
            "analyzed_token_count": len(result["retained_tokens"]),
        },
        "sectorization": {
            "origin": "top-attention target groups from one pretrained attention head",
            "space": "retained token subspace",
            "selected_head": selected.head,
            "raw_group_count": selected.n_groups,
            "retained_sector_count": len(result["sector_metadata"]),
            "minimum_sector_size": 2,
            "retained_token_indices": result["retained_tokens"],
            "excluded_singleton_count": len(result["tokens"])
            - len(result["retained_tokens"]),
            "sectors": result["sector_metadata"],
            "strict_sof_realization_on_retained_subspace": True,
        },
        "observable_family": {
            "attention_heads": "all attention matrices from the audited layer",
            "head_diversity": head_diversity,
        },
        "support_matrix": support_matrix,
        "bridge_matrix": bridge_matrix,
        "repair_matrix": repair_matrix,
        "wall_record": {
            "status": "not_applicable",
            "reason": "single pretrained snapshot; no deformation path supplied",
        },
        **(
            {
                "protocol_boundary": {
                    "reason": "the selected head produced fewer than two retained sectors",
                    "unavailable_diagnostics": [
                        "support_matrix",
                        "bridge_matrix",
                        "repair_matrix",
                    ],
                }
            }
            if audit is None
            else {}
        ),
        "failure_modes": [
            "sector counts depend on the prompt, layer, head, and minimum-size filter",
            "singleton attention groups are excluded from the analyzed subspace",
            "attention-derived sectors are not claimed to be unique or canonical",
            "attention weights alone do not establish causal explanation",
            "single-model diagnostic is not a theorem about all language models",
        ],
    }


def write_sofreport(report: dict, output: Path | None = None) -> Path:
    path = output or (
        Path(__file__).resolve().parent / "results" / "qwen.sofreport"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def print_report(result: dict) -> None:
    print("=" * 88)
    print("  Paper XII: Qwen Attention-Head SOF Diagnostic")
    print("=" * 88)
    print(
        f"  Model: {result['model_name']} | layers={result['layers']}, "
        f"heads={result['heads']}, hidden={result['hidden_size']}"
    )
    print(f"  Text tokens: {len(result['tokens'])} | audited layer: {result['layer']}")
    print("  Sectorization source: token groups induced by top-attention targets")
    print("  Observables: attention matrices from the same layer; no random generators")
    print()

    print("  Head diversity:")
    print_head_summary(result["records"], highlighted={1, 3, 6, 13})
    print()

    selected = result["records"][result["sector_head"]]
    print(
        f"  Natural sectors from Head {selected.head}: "
        f"{len(result['sector_metadata'])} sectors after >=2-token filtering"
    )
    print(
        f"  Strict audit subspace: {len(result['retained_tokens'])}/{len(result['tokens'])} "
        "tokens retained; singleton groups excluded"
    )
    for idx, meta in enumerate(result["sector_metadata"]):
        sample = [result["tokens"][token_idx] for token_idx in meta["members"][:8]]
        print(
            f"    Sector {idx}: target={meta['target']}, "
            f"size={len(meta['members'])}, sample={sample}"
        )

    audit = result["audit"]
    if audit is None:
        print()
        print("  Too few sectors for an SOF audit.")
    else:
        print()
        print("  SOF audit on Head 6 sectors:")
        print(f"    R1 offdiag density: {audit['R1_pct']:.1f}%")
        print(f"    R2 offdiag density: {audit['R2_pct']:.1f}%")
        print(f"    frozen_R1:          {audit['frozen_R1']}")
        print(f"    D_repaired:         {audit['D_repaired']}")
        print(f"    frozen_D:           {audit['frozen_D']}")
        print(f"    D_max:              {audit['D_max']}")
        print("    D matrix:")
        for idx in range(audit["D"].shape[0]):
            row = " ".join(
                f"{audit['D'][idx, j]:>3d}" if idx != j else "  -"
                for j in range(audit["D"].shape[1])
            )
            print(f"      {idx}: [{row}]")

    print()
    print("  Interpretation:")
    print("    pretrained attention heads naturally produce different sector granularities;")
    print("    Head 3 behaves like a global-attention head;")
    print("    Head 1 gives a coarse three-way token clustering;")
    print("    Head 13 gives a dispersed attention partition;")
    print("    Head 6 supplies a four-sector SOF without synthetic generators.")
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="allow Hugging Face downloads instead of requiring the local cache",
    )
    parser.add_argument("--model", default=MODEL_NAME, help="Hugging Face model id")
    parser.add_argument(
        "--revision",
        default=MODEL_REVISION,
        help="pinned Hugging Face commit or tag",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="optional Hugging Face cache directory; no machine path is hard-coded",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
    )
    parser.add_argument(
        "--dtype",
        choices=("float32", "float16", "bfloat16"),
        default="float32",
    )
    parser.add_argument("--sector-head", type=int, default=6, help="head used for sectorization")
    parser.add_argument("--output", type=Path, help="optional .sofreport output path")
    args = parser.parse_args()

    result = run(
        model_name=args.model,
        revision=args.revision,
        cache_dir=args.cache_dir,
        local_files_only=not args.allow_download,
        sector_head=args.sector_head,
        requested_device=args.device,
        dtype_name=args.dtype,
    )
    print_report(result)
    print(f"SOFRS v1.0: {write_sofreport(sofreport(result), args.output)}")


if __name__ == "__main__":
    main()
