"""Create and byte-check a deterministic, selected-source candidate archive."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

import replay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    replay.check_structure()
    manifest = json.loads(replay.MANIFEST.read_text())
    if replay.source_index() != manifest["inputs"]:
        raise ValueError("candidate source byte drift")
    receipt_path = replay.PACKAGE / "results/candidate-local-replay.v2.json"
    receipt = json.loads(receipt_path.read_text())
    if (receipt["status"] != "PASS" or not receipt["lean_replayed"]
            or receipt["manifest_sha256"] != replay.digest(replay.MANIFEST)):
        raise ValueError("no passing Lean replay for these exact inputs")
    if [g["name"] for g in receipt["groups"]] != [g[0] for g in replay.menus()]:
        raise ValueError("receipt group menu differs")
    for group, (_, _, _, targets) in zip(receipt["groups"], replay.menus()):
        if replay.parse_axioms(group["audit_output"]["stdout"], targets) != group["axiom_audit"]:
            raise ValueError("receipt axiom records differ")
    names = sorted(set(manifest["inputs"]) | {
        replay.MANIFEST.relative_to(replay.ROOT).as_posix(),
        receipt_path.relative_to(replay.ROOT).as_posix(),
    })
    config = json.loads((replay.PACKAGE / "reader-profile.json").read_text())
    timestamp = datetime.fromtimestamp(int(config["source_date_epoch"]), timezone.utc).timetuple()[:6]
    output = args.output.resolve()
    if output.exists():
        raise ValueError("refusing to overwrite an existing archive")
    for name in names:
        path = (replay.ROOT / name).resolve()
        if not path.is_relative_to(replay.ROOT) or path == output:
            raise ValueError(f"unsafe archive path: {name}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in names:
            info = zipfile.ZipInfo(name, date_time=timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (replay.ROOT / name).read_bytes(), compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.namelist() != names or archive.testzip() is not None:
            raise ValueError("archive inventory or CRC differs")
        for name in names:
            if hashlib.sha256(archive.read(name)).hexdigest() != replay.digest(replay.ROOT / name):
                raise ValueError(f"archived byte drift: {name}")
    print(json.dumps({"status": "PASS_LOCAL_CANDIDATE_ARCHIVE", "files": len(names),
                      "sha256": replay.digest(output), "size": output.stat().st_size,
                      "output": str(output), "publication_identity": None}, indent=2))


if __name__ == "__main__":
    main()
