#!/usr/bin/env python3
"""Pure local geometry for the fixed-cycle n=6 Safety-Floor theorem."""
from __future__ import annotations

from typing import Any


Transformation = tuple[int, ...]
ANTIPODAL_BLOCKS = ((0, 3), (1, 4), (2, 5))


def binary_kernel_pair(defect: Transformation) -> tuple[int, int]:
    fibers: dict[int, list[int]] = {}
    for source, target in enumerate(defect):
        fibers.setdefault(target, []).append(source)
    pairs = [tuple(fiber) for fiber in fibers.values() if len(fiber) == 2]
    if len(pairs) != 1:
        raise AssertionError("rank-five defect lost its unique binary kernel")
    return pairs[0]


def antipodal_block_action(defect: Transformation) -> tuple[int, ...] | None:
    """Return the induced action on antipodal blocks, when it is defined."""
    action: list[int] = []
    for left, right in ANTIPODAL_BLOCKS:
        target_blocks = {defect[left] % 3, defect[right] % 3}
        if len(target_blocks) != 1:
            return None
        action.append(next(iter(target_blocks)))
    induced = tuple(action)
    if len(set(defect)) == 5 and sorted(induced) != [0, 1, 2]:
        raise AssertionError("rank-five antipodal-block action is not bijective")
    return induced


def apply_pair_word(
    defect: Transformation,
    offset: int,
    word: tuple[str, ...],
) -> list[tuple[int, int]]:
    pair = (0, offset)
    trace = [pair]
    for label in word:
        if label == "p":
            pair = ((pair[0] + 1) % 6, (pair[1] + 1) % 6)
        elif label == "d":
            pair = (defect[pair[0]], defect[pair[1]])
        else:
            raise AssertionError("unknown structural witness label")
        trace.append(pair)
    return trace


def _antipodal_target_geometry(defect: Transformation) -> dict[str, Any]:
    fibers: dict[int, list[int]] = {}
    for source, target in enumerate(defect):
        fibers.setdefault(target, []).append(source)
    kernel = binary_kernel_pair(defect)
    collision_image = defect[kernel[0]]
    missing = sorted(set(range(6)) - set(defect))
    if len(missing) != 1:
        raise AssertionError("rank-five defect lost its unique missing image")
    partial_target_block = missing[0] % 3
    full_target_blocks = [
        block for block in range(3) if block != partial_target_block
    ]
    dirty_pairs: dict[str, list[list[int]]] = {}
    for target_block in full_target_blocks:
        left, right = ANTIPODAL_BLOCKS[target_block]
        pairs = sorted(
            [first, second]
            for first in fibers[left]
            for second in fibers[right]
            if (second - first) % 6 != 3
        )
        if pairs:
            dirty_pairs[str(target_block)] = pairs
    return {
        "kernel_root_block": kernel[0] % 3,
        "collision_image": collision_image,
        "collision_image_block": collision_image % 3,
        "partial_target_block": partial_target_block,
        "full_target_blocks": full_target_blocks,
        "dirty_full_blocks": sorted(int(block) for block in dirty_pairs),
        "dirty_preimage_pairs_by_target_block": dirty_pairs,
    }


def structural_floor_witness(defect: Transformation) -> dict[str, Any] | None:
    """Construct two bounded strict exits unless the antipodal blocks persist."""
    block_action = antipodal_block_action(defect)
    if block_action is not None:
        return None
    kernel = binary_kernel_pair(defect)
    collision_image = defect[kernel[0]]
    routes: list[dict[str, Any]] = []
    if (kernel[1] - kernel[0]) % 6 != 3:
        kernel_type = "NON_ANTIPODAL"
        target_geometry = None
        for first, second in (kernel, kernel[::-1]):
            routes.append({
                "offset": (second - first) % 6,
                "word": ["p"] * first + ["d"],
                "kind": "direct-nonantipodal-kernel",
                "oriented_kernel_pair": [first, second],
            })
    else:
        kernel_type = "ANTIPODAL_NONPRESERVING"
        target_geometry = _antipodal_target_geometry(defect)
        kernel_root = int(target_geometry["kernel_root_block"])
        routes.append({
            "offset": 3,
            "word": ["p"] * kernel_root + ["d"],
            "kind": "direct-antipodal-kernel",
            "oriented_kernel_pair": list(kernel),
        })
        fibers: dict[int, list[int]] = {}
        for source, target in enumerate(defect):
            fibers.setdefault(target, []).append(source)
        bridges: list[
            tuple[int, int, tuple[str, ...], tuple[int, int], int, int]
        ] = []
        for target_block, (left, right) in enumerate(ANTIPODAL_BLOCKS):
            if left not in fibers or right not in fibers:
                continue
            turn = (kernel_root - target_block) % 3
            for first_image, second_image in ((left, right), (right, left)):
                for first in fibers[first_image]:
                    for second in fibers[second_image]:
                        offset = (second - first) % 6
                        if offset == 3:
                            continue
                        word = (
                            ("p",) * first
                            + ("d",)
                            + ("p",) * turn
                            + ("d",)
                        )
                        if len(word) <= 6:
                            bridges.append(
                                (
                                    len(word),
                                    offset,
                                    word,
                                    (first, second),
                                    target_block,
                                    turn,
                                )
                            )
        if not bridges:
            raise AssertionError("nonpreserving antipodal kernel lacks bounded bridge")
        length, offset, word, source_pair, target_block, turn = min(bridges)
        if target_block == kernel_root:
            bridge_case = "T0_FULL_DIRTY"
        elif target_geometry["partial_target_block"] == kernel_root:
            if target_geometry["collision_image_block"] == target_block:
                bridge_case = "T0_PARTIAL_COLLISION_IMAGE_FULL"
            else:
                bridge_case = "T0_PARTIAL_DIRTY_COMPLEMENT"
        else:
            bridge_case = "T0_FULL_CLEAN_OTHER_DIRTY"
        routes.append({
            "offset": offset,
            "word": list(word),
            "kind": "antipodal-kernel-block-escape",
            "source_pair": list(source_pair),
            "target_block": target_block,
            "block_turn_q": turn,
            "bridge_case": bridge_case,
            "length": length,
        })

    offsets = [route["offset"] for route in routes]
    if len(routes) != 2 or len(set(offsets)) != 2:
        raise AssertionError("structural Safety-Floor witness lost distinct offsets")
    for route in routes:
        word = tuple(route["word"])
        trace = apply_pair_word(defect, route["offset"], word)
        if len(word) > 6 or trace[-1][0] != trace[-1][1]:
            raise AssertionError("structural Safety-Floor witness does not fuse")
        if any(left == right for left, right in trace[:-1]):
            raise AssertionError("structural Safety-Floor witness fuses before its endpoint")
    return {
        "kernel_type": kernel_type,
        "binary_kernel_pair": list(kernel),
        "collision_image": collision_image,
        "antipodal_target_geometry": target_geometry,
        "routes": routes,
        "maximum_length": max(len(route["word"]) for route in routes),
    }
