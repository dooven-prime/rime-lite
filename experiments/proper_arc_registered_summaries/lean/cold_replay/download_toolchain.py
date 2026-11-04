"""Download the official immutable Lean ZIP with checked HTTP byte ranges."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
import zipfile
from email.parser import Parser

URL = "https://github.com/leanprover/lean4/releases/download/v4.33.0/lean-4.33.0-windows.zip"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("refuse to replace an existing toolchain archive")
    parts = output.parent/"lean-http-parts"
    parts.mkdir(exist_ok=True)
    header_file = parts/"official-head.txt"
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if curl is None:
        raise RuntimeError("curl is required for the official TLS transfer")
    result = subprocess.run([curl, "-4", "--fail", "--head", "--location", "--retry", "3",
        "--retry-all-errors", "--connect-timeout", "20", "--max-time", "90", "--silent", "--show-error",
        "--dump-header", str(header_file), "--output", "NUL", "--write-out", "%{url_effective}", URL],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    blocks = header_file.read_text("utf-8").strip().split("\n\n")
    headers = Parser().parsestr(blocks[-1].split("\n", 1)[1])
    size = int(headers["Content-Length"])
    etag = headers["ETag"]
    final_url = result.stdout.strip()
    metadata = parts/"transfer.json"
    identity = {"url": URL, "bytes": size, "etag": etag, "chunk_bytes": 8*1024*1024}
    if metadata.exists():
        if json.loads(metadata.read_text("utf-8")) != identity:
            raise RuntimeError("HTTP transfer identity changed")
    else:
        metadata.write_text(json.dumps(identity, indent=2), encoding="utf-8")
    chunk = identity["chunk_bytes"]
    count = (size+chunk-1)//chunk
    started = time.monotonic()

    def acquire(i):
        start = i*chunk
        end = min(size, start+chunk)-1
        path = parts/f"{i:04d}.part"
        for attempt in range(5):
            offset = path.stat().st_size if path.exists() else 0
            if offset == end-start+1:
                return path
            if offset > end-start+1:
                raise RuntimeError("oversized HTTP part")
            try:
                req = urllib.request.Request(final_url, headers={"Range": f"bytes={start+offset}-{end}",
                    "User-Agent": "proper-arc-cold-replay/1"})
                with urllib.request.urlopen(req, timeout=90) as response:
                    expected = f"bytes {start+offset}-{end}/{size}"
                    if response.status != 206 or response.headers.get("Content-Range") != expected or response.headers.get("ETag") != etag:
                        raise RuntimeError("server did not honor the pinned HTTP range")
                    with path.open("ab") as target:
                        shutil.copyfileobj(response, target, length=1024*1024)
                if path.stat().st_size != end-start+1:
                    raise RuntimeError("truncated HTTP range")
                return path
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2*(attempt+1))
        raise AssertionError("unreachable")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        tasks = {executor.submit(acquire, i): i for i in range(count)}
        done = 0
        for task in as_completed(tasks):
            task.result()
            done += 1
            if done % 8 == 0 or done == count:
                print(f"HTTP parts {done}/{count}, elapsed {time.monotonic()-started:.1f}s", flush=True)
    digest = hashlib.sha256()
    with output.open("xb") as archive:
        for i in range(count):
            with (parts/f"{i:04d}.part").open("rb") as part:
                while block := part.read(1024*1024):
                    digest.update(block)
                    archive.write(block)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("official ZIP CRC validation failed")
    receipt = {"schema": "proper_arc_fresh_toolchain_transfer.v1", **identity,
        "sha256": digest.hexdigest(), "zip_crc_passed": True, "publisher_asset_digest_verified": False,
        "finished_utc": datetime.now(timezone.utc).isoformat(), "seconds": time.monotonic()-started,
        "source": "FRESH_HTTPS_DOWNLOAD_NO_LOCAL_TOOLCHAIN_COPY"}
    args.evidence.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
