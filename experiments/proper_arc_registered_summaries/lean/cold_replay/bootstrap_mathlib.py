"""Recover a fresh Git checkout using verified codeload blobs after a pack disconnect."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import time
import zlib

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from theorem_map import as_json, require, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--curl", type=Path, required=True)
    parser.add_argument("--api-fallback", action="store_true")
    parser.add_argument("--attempt", choices=("v1", "v2", "v3"))
    args = parser.parse_args()
    project = args.project.resolve(strict=True)
    evidence = args.evidence.resolve(strict=True)
    version = args.attempt or ("v2" if args.api_fallback else "v1")
    output = evidence / f"mathlib-archive-bootstrap.{version}.json"
    require(not output.exists(), "bootstrap receipt already exists")
    lock = json.loads((project / "lake-manifest.json").read_text("utf-8"))
    package = next(row for row in lock["packages"] if row["name"] == "mathlib")
    revision = package["rev"]
    require(revision == "db584cd6d46c92f209a44c0f1c829460d327499d", "unexpected Mathlib revision")
    require(package["url"] == "https://github.com/leanprover-community/mathlib4.git", "unexpected source")
    root = project / lock["packagesDir"] / "mathlib"
    require(root.is_dir() and not root.is_symlink() and not root.is_junction(), "shared package directory")
    require(not (root / ".git/objects/info/alternates").exists(), "shared object store")
    require(not (root / ".lake").exists(), "Mathlib already has build artifacts")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(evidence.parent / "isolated-caches/gitconfig")})
    record = {"schema": "proper_arc_mathlib_archive_bootstrap.v1", "status": "RUNNING",
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "helper_sha256": sha256(Path(__file__)), "revision": revision,
              "lock_sha256": sha256(project / "lake-manifest.json"), "commands": []}

    def save():
        output.write_text(as_json(record), encoding="utf-8", newline="\n")

    def command(name, argv, *, stdin=None, timeout=1200):
        log = evidence / ("bootstrap-" + (version + "-" if version != "v1" else "") + name + ".log")
        require(not log.exists(), "bootstrap log already exists")
        start = time.monotonic()
        process = subprocess.run(argv, cwd=root, env=env, input=stdin, capture_output=True, timeout=timeout)
        log.write_bytes(process.stdout + process.stderr)
        record["commands"].append({"name": name, "command": argv, "exit_code": process.returncode,
            "seconds": time.monotonic() - start, "log": log.name, "log_sha256": sha256(log)})
        save()
        print(f"{'PASS' if process.returncode == 0 else 'FAIL'} {name}", flush=True)
        return process

    def api(suffix, name):
        result = command(name, [str(args.curl.resolve(strict=True)), "-4", "--fail", "--location",
            "--retry", "3", "--retry-all-errors", "--connect-timeout", "20", "--max-time", "180",
            "--silent", "--show-error", "https://api.github.com/repos/leanprover-community/mathlib4/git/" + suffix])
        require(result.returncode == 0, "official GitHub API acquisition failed")
        return json.loads(result.stdout)

    def store_object(kind, data, expected):
        raw = kind.encode() + b" " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(raw).hexdigest() == expected, f"Git {kind} identity mismatch")
        destination = root / ".git/objects" / expected[:2] / expected[2:]
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(zlib.compress(raw))

    def api_inventory():
        obj = api("commits/" + revision, "api-commit")
        require(obj["sha"] == revision and obj["verification"]["reason"] == "unsigned",
                "unsupported commit reconstruction")
        tree = obj["tree"]["sha"]
        prefix = "tree " + tree + "\n" + "".join("parent " + p["sha"] + "\n" for p in obj["parents"])
        authors = []
        for key in ("author", "committer"):
            person = obj[key]
            stamp = int(datetime.fromisoformat(person["date"].replace("Z", "+00:00")).timestamp())
            authors.append(f"{key} {person['name']} <{person['email']}> {stamp} ")
        zones = ["+0000", "-0000"] + [f"{'+' if sign > 0 else '-'}{minutes//60:02d}{minutes%60:02d}"
            for sign in (1, -1) for minutes in range(15, 14*60+1, 15)]
        commit_data = None
        for suffix in ("\n", "", "\n\n"):
            for left in zones:
                for right in zones:
                    candidate = (prefix + authors[0] + left + "\n" + authors[1] + right + "\n\n"
                                 + obj["message"] + suffix).encode()
                    raw = b"commit " + str(len(candidate)).encode() + b"\0" + candidate
                    if hashlib.sha1(raw).hexdigest() == revision:
                        commit_data = candidate
                        break
                if commit_data is not None:
                    break
            if commit_data is not None:
                break
        require(commit_data is not None, "API metadata does not reconstruct the pinned commit")
        inventory = api("trees/" + tree + "?recursive=1", "api-tree")
        require(not inventory["truncated"] and inventory["sha"] == tree, "incomplete Git tree")
        items = {row["path"]: row for row in inventory["tree"]}
        require(len(items) == len(inventory["tree"]), "duplicate Git tree path")
        children = {}
        for name, row in items.items():
            path = PurePosixPath(name)
            require(not path.is_absolute() and ".." not in path.parts and path.parts[0] != ".git",
                    "unsafe tree path")
            parent = path.parent.as_posix()
            children.setdefault(parent, []).append((path.name, row))
        for parent, rows in children.items():
            data = b""
            for name, row in sorted(rows, key=lambda item: (item[0] + ("/" if item[1]["type"] == "tree" else "")).encode()):
                mode = f"{int(row['mode'], 8):o}"
                data += mode.encode() + b" " + name.encode() + b"\0" + bytes.fromhex(row["sha"])
            expected = tree if parent == "." else items[parent]["sha"]
            store_object("tree", data, expected)
        store_object("commit", commit_data, revision)
        (root / ".git/shallow").write_text(revision + "\n", encoding="ascii")
        for row in items.values():
            require(row["type"] == "tree" or row["type"] == "blob" and row["mode"] in ("100644", "100755", "120000"),
                    "unsupported Git source entry")
        record.update({"commit_reconstructed_at_exact_sha": True, "root_tree_sha": tree,
                       "all_tree_objects_hash_checked": True})
        return {name: row["sha"] for name, row in items.items() if row["type"] == "blob"}

    try:
        save()
        if args.api_fallback:
            entries = api_inventory()
        else:
            fetched = False
            for attempt in range(1, 5):
                p = command(f"tree-fetch-{attempt}", ["git", "fetch", "--filter=blob:none", "--depth", "1",
                            "origin", revision], timeout=300)
                if p.returncode == 0:
                    fetched = True
                    break
                time.sleep(3)
            require(fetched, "could not acquire the pinned commit/tree")
            commit = command("commit-object", ["git", "cat-file", "commit", revision])
            require(commit.returncode == 0, "missing commit object")
            raw = b"commit " + str(len(commit.stdout)).encode() + b"\0" + commit.stdout
            require(hashlib.sha1(raw).hexdigest() == revision, "commit object identity mismatch")
            listing = command("tree-inventory", ["git", "ls-tree", "-r", "-z", revision])
            require(listing.returncode == 0, "missing tree inventory")
            entries = {}
            for row in listing.stdout.split(b"\0"):
                if not row:
                    continue
                metadata, name = row.split(b"\t", 1)
                mode, kind, digest = metadata.decode().split()
                require(kind == "blob" and mode in ("100644", "100755"), "unsupported source tree entry")
                entries[name.decode("utf-8")] = digest
        archive = evidence / "mathlib-source.tar.gz"
        require(not archive.exists(), "source archive already exists")
        url = f"https://codeload.github.com/leanprover-community/mathlib4/tar.gz/{revision}"
        download = command("source-download", [str(args.curl.resolve(strict=True)), "-4", "--fail",
            "--location", "--retry", "4", "--retry-all-errors", "--connect-timeout", "20", "--max-time",
            "1200", "--silent", "--show-error", "--output", str(archive), url], timeout=6600)
        require(download.returncode == 0, "source archive download failed")
        seen = set()
        with tarfile.open(archive, "r:gz") as source:
            for member in source:
                parts = PurePosixPath(member.name).parts
                require(parts and parts[0] == f"mathlib4-{revision}" and ".." not in parts,
                        "unexpected archive path")
                if member.isdir():
                    continue
                require(member.isfile() or member.issym(), "unsupported archive member")
                name = PurePosixPath(*parts[1:]).as_posix()
                require(name in entries and name not in seen and parts[1] != ".git", "unexpected source member")
                if member.issym():
                    data = member.linkname.encode()
                else:
                    stream = source.extractfile(member)
                    require(stream is not None, "unreadable archive member")
                    data = stream.read()
                digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                require(digest == entries[name], f"source blob mismatch: {name}")
                target = root / name
                require(not target.exists(), f"refuse to replace an existing source: {name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                seen.add(name)
        require(seen == set(entries), "archive omits tracked source files")
        names = sorted(entries)
        require(all(not any(c in name for c in '\n\r"\\') for name in names), "unsupported Git input path")
        objects = command("import-verified-blobs", ["git", "hash-object", "-w", "--no-filters", "--stdin-paths"],
                          stdin=("\n".join(names) + "\n").encode())
        require(objects.returncode == 0 and objects.stdout.decode().splitlines() == [entries[n] for n in names],
                "Git blob import mismatch")
        symlinks = command("windows-symlink-policy", ["git", "config", "core.symlinks", "false"])
        require(symlinks.returncode == 0, "cannot set Windows symlink checkout policy")
        index = command("verified-index", ["git", "read-tree", revision])
        require(index.returncode == 0, "cannot construct index from verified tree")
        checkout = command("checkout", ["git", "checkout", "--detach", revision])
        require(checkout.returncode == 0, "checkout failed")
        status = command("tracked-status", ["git", "status", "--porcelain=v1", "--untracked-files=no"])
        require(status.returncode == 0 and not status.stdout, "tracked source drift after checkout")
        require(not (root / ".lake").exists(), "build artifacts appeared during source acquisition")
        record.update({"status": "PASS_VERIFIED_FRESH_NETWORK_SOURCE_BOOTSTRAP", "source_url": url,
            "archive_sha256": sha256(archive), "archive_bytes": archive.stat().st_size,
            "verified_tracked_blob_count": len(entries), "blob_content_matches_commit_tree": True,
            "symlinks_stored_as_git_windows_link_text": True,
            "local_object_or_build_cache_reused": False, "finished_utc": datetime.now(timezone.utc).isoformat()})
        save()
    except Exception as error:
        record.update({"status": "FAILED", "error": str(error)})
        save()
        raise


if __name__ == "__main__":
    main()
