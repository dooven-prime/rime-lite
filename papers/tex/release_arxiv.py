"""
End-to-end arXiv release helper.

Default workflow:
  1. Build all four PDFs in dependency order.
  2. Prepare output/arxiv/<package>/ upload directories.
  3. Create ccs.zip, paper1.zip, paper2.zip, paper3.zip.
  4. Verify package shape, ZIP roots, package self-compilation, and
     known PDF text guards.

Useful commands:
  python release_arxiv.py
  python release_arxiv.py --version v1
  python release_arxiv.py --check-only
  python release_arxiv.py --skip-build --version v2
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
BUILD_DIR = Path(
    os.environ.get("RIME_TEX_OUTPUT_DIR", ROOT / "output" / "tex")
).resolve()
ARXIV_DIR = Path(
    os.environ.get("RIME_ARXIV_OUTPUT_DIR", ROOT / "output" / "arxiv")
).resolve()
PACKAGES = ("ccs", "paper1", "paper2", "paper3")
TARGETS = {
    "ccs": "ccs_arxiv",
    "paper1": "paper1_arxiv",
    "paper2": "paper2_arxiv",
    "paper3": "paper3_arxiv",
}
EXPECTED_FIGURES = {
    "ccs": 15,
    "paper1": 5,
    "paper2": 6,
    "paper3": 5,
}
BUILD_JUNK_SUFFIXES = (
    ".log",
    ".out",
    ".toc",
    ".fls",
    ".fdb_latexmk",
    ".synctex",
    ".synctex.gz",
    ".blg",
)

PDF_REQUIRED = {
    "paper2": [
        r"Corollary C\.1",
        r"CCS Fig\. C16",
        r"CCS Fig\. C17",
        r"S6\s*-\s*S7\s*-\s*S9\s+hub complex",
        r"Lemma 4\.1",
    ],
    "paper3": [
        r"Lemma 2\.3",
        r"Lemma 4\.1",
        r"S6\s*-\s*S7\s*-\s*S9\s+hub complex",
    ],
}

PDF_FORBIDDEN = {
    "paper1": [
        r"Lemma \?\?",
    ],
    "paper2": [
        r"Lemma \?\?",
        r"Corollary Appendix C\.1",
        r"S6\s*-\s*S7\s+hub complex",
    ],
    "paper3": [
        r"Lemma \?\?",
        r"Lemma 4\.2\s*\(Lie-Generated Support Invariance\)",
        r"S6\s*-\s*S7\s+hub complex",
    ],
}


def _run(cmd: list[str], cwd: Path = BASE) -> None:
    print("\n$ " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _is_junk(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in BUILD_JUNK_SUFFIXES)


def _package_dir(name: str) -> Path:
    return ARXIV_DIR / name


def _required_root_entries(name: str) -> set[str]:
    target = TARGETS[name]
    aux = {f"{tex_name}.aux" for tex_name in TARGETS.values()}
    return {
        f"{target}.tex",
        f"{target}.bbl",
        "figures",
        "xr_sources",
        *aux,
    }


def check_package_dirs() -> dict[str, dict[str, int | bool]]:
    print("\n== Package directory check ==")
    summaries: dict[str, dict[str, int | bool]] = {}
    ok = True

    for name in PACKAGES:
        package_dir = _package_dir(name)
        if not package_dir.is_dir():
            print(f"ERROR {name}: missing {package_dir}")
            ok = False
            continue

        root_entries = {path.name for path in package_dir.iterdir()}
        missing = sorted(_required_root_entries(name) - root_entries)
        junk = [path for path in package_dir.rglob("*") if path.is_file() and _is_junk(path)]
        figures = list((package_dir / "figures").glob("*"))
        xr_sources = list((package_dir / "xr_sources").glob("*_arxiv.tex"))
        root_tex = list(package_dir.glob("*_arxiv.tex"))
        bbl = list(package_dir.glob("*.bbl"))
        aux = list(package_dir.glob("*_arxiv.aux"))

        summary = {
            "root_tex": len(root_tex),
            "bbl": len(bbl),
            "aux": len(aux),
            "figures": len(figures),
            "xr_sources": len(xr_sources),
            "build_junk": len(junk),
            "ok": (
                not missing
                and len(root_tex) == 1
                and len(bbl) == 1
                and len(aux) == 4
                and len(figures) == EXPECTED_FIGURES[name]
                and len(xr_sources) == 3
                and not junk
            ),
        }
        summaries[name] = summary

        print(
            f"{name}: tex={summary['root_tex']} bbl={summary['bbl']} "
            f"aux={summary['aux']} figures={summary['figures']} "
            f"xr_sources={summary['xr_sources']} junk={summary['build_junk']}"
        )
        if missing:
            print(f"  ERROR missing: {', '.join(missing)}")
        for path in junk[:8]:
            print(f"  ERROR build junk: {path}")
        ok = bool(summary["ok"]) and ok

    if not ok:
        raise SystemExit(1)
    return summaries


def check_zips() -> dict[str, dict[str, int | bool]]:
    print("\n== ZIP check ==")
    summaries: dict[str, dict[str, int | bool]] = {}
    ok = True

    for name in PACKAGES:
        zip_path = ARXIV_DIR / f"{name}.zip"
        if not zip_path.exists():
            print(f"ERROR {name}: missing {zip_path}")
            ok = False
            continue

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            root_entries = {item.split("/", 1)[0] for item in names}
            nested = [item for item in names if item.startswith(f"{name}/")]
            junk = [item for item in names if _is_junk(Path(item))]
            missing = sorted(_required_root_entries(name) - root_entries)

        summary = {
            "entries": len(names),
            "bytes": zip_path.stat().st_size,
            "nested_prefix": bool(nested),
            "build_junk": len(junk),
            "ok": not missing and not nested and not junk,
        }
        summaries[name] = summary
        print(
            f"{name}.zip: entries={summary['entries']} "
            f"size={summary['bytes']} nested={summary['nested_prefix']} "
            f"junk={summary['build_junk']}"
        )
        if missing:
            print(f"  ERROR missing root entries: {', '.join(missing)}")
        ok = bool(summary["ok"]) and ok

    if not ok:
        raise SystemExit(1)
    return summaries


def _read_log(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def compile_check(*, check_text: bool = True) -> dict[str, dict[str, int | bool]]:
    print("\n== Package compile check ==")
    xelatex = shutil.which("xelatex")
    if not xelatex:
        print("ERROR: xelatex not found")
        raise SystemExit(1)

    summaries: dict[str, dict[str, int | bool]] = {}
    ok = True

    with tempfile.TemporaryDirectory(
        prefix="rime_arxiv_compile_", ignore_cleanup_errors=True
    ) as temp:
        temp_dir = Path(temp)
        for name in PACKAGES:
            package_dir = _package_dir(name)
            out_dir = temp_dir / name
            out_dir.mkdir(parents=True, exist_ok=True)
            tex_path = package_dir / f"{TARGETS[name]}.tex"
            passes = []

            for idx in (1, 2):
                console = out_dir / f"console-pass{idx}.log"
                cmd = [
                    xelatex,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-output-directory",
                    str(out_dir),
                    tex_path.name,
                ]
                result = subprocess.run(
                    cmd,
                    cwd=package_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                console.write_text(result.stdout, encoding="utf-8", errors="replace")
                passes.append(result.returncode)

            log = _read_log(out_dir / f"{TARGETS[name]}.log")
            pdf_path = out_dir / f"{TARGETS[name]}.pdf"
            pdf_exists = pdf_path.exists()
            text_guard_ok = (
                _pdf_text_matches(name, pdf_path)
                if check_text and pdf_exists and name in {"paper1", "paper2", "paper3"}
                else True
            )
            bad_patterns = {
                "output_written": "Output written on" in log,
                "undefined_refs": bool(
                    re.search(r"undefined references|Reference .* undefined", log)
                ),
                "label_changed": "Label(s) may have changed" in log,
                "missing_graphics": bool(
                    re.search(r"File .* not found|Unable to load picture", log)
                ),
                "fatal": bool(re.search(r"Fatal error|Emergency stop|^!", log, re.M)),
            }
            summary = {
                "exit1": passes[0],
                "exit2": passes[1],
                "pdf_exists": pdf_exists,
                "text_guard": text_guard_ok,
                **bad_patterns,
            }
            summaries[name] = summary
            package_ok = (
                passes == [0, 0]
                and pdf_exists
                and bad_patterns["output_written"]
                and text_guard_ok
                and not bad_patterns["undefined_refs"]
                and not bad_patterns["label_changed"]
                and not bad_patterns["missing_graphics"]
                and not bad_patterns["fatal"]
            )
            ok = package_ok and ok
            print(
                f"{name}: exit={passes} pdf={pdf_exists} "
                f"undefined={bad_patterns['undefined_refs']} "
                f"label_changed={bad_patterns['label_changed']} "
                f"missing_graphics={bad_patterns['missing_graphics']} "
                f"fatal={bad_patterns['fatal']} text_guard={text_guard_ok}"
            )

    if not ok:
        raise SystemExit(1)
    return summaries


def _extract_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        pdftotext = shutil.which("pdftotext")
        if not pdftotext:
            raise RuntimeError("Neither pypdf nor pdftotext is available")
        result = subprocess.run(
            [pdftotext, "-layout", str(pdf_path), "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"pdftotext failed: {pdf_path}")
        return result.stdout


def _normalize_pdf_text(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2212", "-")
    return re.sub(r"\s+", " ", text)


def _pdf_text_matches(name: str, pdf_path: Path) -> bool:
    """Check the PDF compiled from the exact package being validated."""
    try:
        text = _normalize_pdf_text(_extract_pdf_text(pdf_path))
    except Exception as exc:
        print(f"ERROR {name}: cannot extract PDF text: {exc}")
        return False
    ok = True
    for pattern in PDF_REQUIRED.get(name, []):
        if not re.search(pattern, text):
            print(f"ERROR {name}: required text not found: {pattern}")
            ok = False
    for pattern in PDF_FORBIDDEN.get(name, []):
        if re.search(pattern, text):
            print(f"ERROR {name}: forbidden text found: {pattern}")
            ok = False
    return ok


def pdf_text_guard() -> None:
    print("\n== PDF text guard ==")
    ok = True

    for name in ("paper1", "paper2", "paper3"):
        pdf_path = BUILD_DIR / f"{TARGETS[name]}.pdf"
        if not pdf_path.exists():
            print(f"ERROR {name}: missing {pdf_path}")
            ok = False
            continue
        try:
            text = _normalize_pdf_text(_extract_pdf_text(pdf_path))
        except Exception as exc:
            print(f"ERROR {name}: cannot extract PDF text: {exc}")
            ok = False
            continue

        for pattern in PDF_REQUIRED.get(name, []):
            if not re.search(pattern, text):
                print(f"ERROR {name}: required text not found: {pattern}")
                ok = False
        for pattern in PDF_FORBIDDEN.get(name, []):
            if re.search(pattern, text):
                print(f"ERROR {name}: forbidden text found: {pattern}")
                ok = False
        print(f"{name}: text guard checked")

    if not ok:
        raise SystemExit(1)


def write_manifest(version: str | None, summaries: dict[str, object]) -> None:
    manifest = {
        "created_unix": int(time.time()),
        "version": version,
        "packages": {},
        "summaries": summaries,
    }
    for name in PACKAGES:
        zip_path = ARXIV_DIR / f"{name}.zip"
        if zip_path.exists():
            manifest["packages"][name] = {
                "zip": str(zip_path.relative_to(ARXIV_DIR)),
                "bytes": zip_path.stat().st_size,
            }

    destinations = [ARXIV_DIR / "MANIFEST.json"]
    if version:
        destinations.append(ARXIV_DIR / "releases" / version / "MANIFEST.json")

    for path in destinations:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"manifest: {path}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build, package, zip, and verify arXiv release files.")
    parser.add_argument("--version", help="Optional release tag, e.g. v1 or v2.")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-prepare", action="store_true")
    parser.add_argument("--skip-zip", action="store_true")
    parser.add_argument("--skip-compile-check", action="store_true")
    parser.add_argument("--skip-text-check", action="store_true")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only verify existing package directories, ZIPs, and PDFs.",
    )
    args = parser.parse_args(argv[1:])

    if args.check_only:
        args.skip_build = True
        args.skip_prepare = True
        args.skip_zip = True

    if not args.skip_build:
        _run([sys.executable, "build.py", "all"])
    if not args.skip_prepare:
        _run([sys.executable, "prepare_arxiv.py"])
    if not args.skip_zip:
        zip_cmd = [sys.executable, "package_arxiv_zips.py"]
        if args.version:
            zip_cmd.extend(["--version", args.version])
        _run(zip_cmd)

    summaries: dict[str, object] = {}
    summaries["package_dirs"] = check_package_dirs()
    summaries["zips"] = check_zips()
    if not args.skip_compile_check:
        summaries["compile_check"] = compile_check(
            check_text=not args.skip_text_check
        )
    elif not args.skip_text_check:
        print(
            "ERROR: package text guards require package compilation; "
            "remove --skip-compile-check or add --skip-text-check"
        )
        return 2

    write_manifest(args.version, summaries)
    print("\nRelease check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
