"""
Create per-document arXiv upload ZIP files.

Input:
  output/arxiv/
    ccs/
    paper1/
    paper2/
    paper3/

Output:
  output/arxiv/
    ccs.zip
    paper1.zip
    paper2.zip
    paper3.zip

Each ZIP contains the package directory contents at archive root, not an
extra top-level package directory.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
ARXIV_DIR = Path(
    os.environ.get("RIME_ARXIV_OUTPUT_DIR", ROOT / "output" / "arxiv")
).resolve()
PACKAGES = ("ccs", "paper1", "paper2", "paper3")
JUNK_SUFFIXES = {
    ".log",
    ".out",
    ".toc",
    ".fls",
    ".fdb_latexmk",
    ".synctex",
    ".synctex.gz",
    ".blg",
}


def _is_build_junk(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in JUNK_SUFFIXES)


def _package_files(package_dir: Path) -> list[Path]:
    files = [
        path
        for path in package_dir.rglob("*")
        if path.is_file() and not _is_build_junk(path)
    ]
    return sorted(files, key=lambda p: p.relative_to(package_dir).as_posix())


def make_zip(name: str, output_dir: Path = ARXIV_DIR) -> Path | None:
    package_dir = ARXIV_DIR / name
    zip_path = output_dir / f"{name}.zip"

    if not package_dir.is_dir():
        print(f"ERROR: missing package directory: {package_dir}")
        return None

    files = _package_files(package_dir)
    if not files:
        print(f"ERROR: no files to package: {package_dir}")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = path.relative_to(package_dir).as_posix()
            zf.write(path, arcname)

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        nested_prefix = f"{name}/"
        if any(item.startswith(nested_prefix) for item in names):
            print(f"ERROR: nested package directory detected in {zip_path}")
            return None

    size_kb = zip_path.stat().st_size / 1024
    print(f"{zip_path}  ({len(files)} files, {size_kb:.1f} KiB)")
    return zip_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Create per-document arXiv upload ZIP files."
    )
    parser.add_argument(
        "packages",
        nargs="*",
        choices=PACKAGES,
        help="Package names to zip. Defaults to all packages.",
    )
    parser.add_argument(
        "--version",
        help=(
            "Also copy the generated ZIPs into output/arxiv/releases/VERSION/ "
            "for v1/v2-style release snapshots."
        ),
    )
    args = parser.parse_args(argv[1:])

    packages = args.packages or list(PACKAGES)
    ok = True
    generated: list[Path] = []
    for name in packages:
        zip_path = make_zip(name)
        if zip_path is None:
            ok = False
        else:
            generated.append(zip_path)

    if ok and args.version:
        version_dir = ARXIV_DIR / "releases" / args.version
        version_dir.mkdir(parents=True, exist_ok=True)
        for zip_path in generated:
            dst = version_dir / zip_path.name
            shutil.copy2(zip_path, dst)
        print(f"version snapshot: {version_dir}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
