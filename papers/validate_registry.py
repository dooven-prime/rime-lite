#!/usr/bin/env python3
"""
validate_registry.py - Validate public identities and embedded document rules.

The active checks are maintained directly in this module; retired registry
files under docs/archive are historical provenance, not runtime inputs.
- "positive" checks: the value string MUST appear in the file
- "negative" checks: the forbidden string must NOT appear

This catches label drift (e.g., 11→10, 6→7, 4→3).
"""

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIBLIOGRAPHY = ROOT / "papers" / "tex" / "trilogy.bib"


def _find_paper(paper_dir, prefix):
    """Find the latest dated manuscript in a paper directory.

    Matches ``prefix - *.md`` (e.g. ``Paper I - 260518.md``) and returns the
    newest by modification time.  The undated originals (``Paper I.md``) are
    never picked up — only explicitly dated files are considered editable.
    """
    pattern = f"{prefix} - *.md"
    candidates = sorted(
        (ROOT / "papers" / paper_dir).glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            f"No dated manuscript found: papers/{paper_dir}/{pattern}"
        )
    return candidates[0]


PAPERS = {
    "Paper I":   ROOT / "papers" / "paper1" / "Paper I.md",
    "Paper II":  ROOT / "papers" / "paper2" / "Paper II.md",
    "Paper III": ROOT / "papers" / "paper3" / "Paper III.md",
    "CCS":       ROOT / "ccs" / "canonical_specification.md",
}


def grep_file(filepath, pattern, use_regex=True):
    """Return True if pattern found anywhere in file.

    If use_regex=True (default), pattern is a regex.
    If use_regex=False, pattern is a plain substring (no escaping issues).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if use_regex:
        import re
        return bool(re.search(pattern, content))
    else:
        return pattern in content


def check(pattern, files, description, must_exist=True, use_regex=True):
    """
    If must_exist=True: pattern MUST be found in all files (positive check).
    If must_exist=False: pattern must NOT be found in any file (negative check).
    Returns list of error messages.
    """
    errors = []
    for fk in files:
        found = grep_file(PAPERS[fk], pattern, use_regex=use_regex)
        if must_exist and not found:
            errors.append(f"  {fk}: MISSING pattern")
        if not must_exist and found:
            errors.append(f"  {fk}: FORBIDDEN pattern FOUND")
    return errors


def _bib_entries():
    """Return raw BibTeX entries keyed by citation key.

    The scanner is brace-aware so nested title braces do not terminate an
    entry. BibTeX itself remains the syntax validator during document builds.
    """
    content = BIBLIOGRAPHY.read_text(encoding="utf-8")
    starts = list(re.finditer(r"(?m)^@\w+\s*\{\s*([^,\s]+)\s*,", content))
    entries = {}
    duplicates = []
    for match in starts:
        opening = content.find("{", match.start())
        depth = 0
        end = None
        for index in range(opening, len(content)):
            if content[index] == "{":
                depth += 1
            elif content[index] == "}":
                depth -= 1
                if depth == 0:
                    end = index + 1
                    break
        if end is None:
            continue
        key = match.group(1)
        if key in entries:
            duplicates.append(key)
        entries[key] = content[match.start():end]
    return entries, duplicates


def check_bibliography_identities():
    """Enforce immutable release identities and active DOI state."""
    entries, duplicates = _bib_entries()
    errors = [f"duplicate BibTeX key: {key}" for key in duplicates]

    historical = {
        "paper4v1": (
            "Collision Geometry of Joint Spectra: Affine Branch Arrangements, Visible Collisions, and Spectral Quotients",
            "10.5281/zenodo.21127271",
        ),
        "paper5v1": (
            "Accessibility Repair Calculus: Local R2 Repair and Exceptional Loci for Length-2 Witnesses",
            "10.5281/zenodo.21152972",
        ),
        "paper6v1": (
            "Phase Transition Geometry on the Generator-Set Moduli Space: Global Stratification, Local Commutativity Geometry, and Accessibility Walls",
            "10.5281/zenodo.21154656",
        ),
        "paper7v1": (
            "Generic Accessibility Completion: Incidence Varieties, Rank-Protected Bridges, and the Generic Completion Principle",
            "10.5281/zenodo.21193940",
        ),
    }
    active = {
        "paper1": (
            "I",
            "Spectral Sector Decomposition in the Rubik's Cube Representation: Block Spectral Structure and a Conditional Rationality Criterion",
        ),
        "paper2": (
            "II",
            "Noncommutative Transport Topology in the Rubik's Cube Representation: Sector Non-Invariance, Direct Support, and Transport Channels",
        ),
        "paper3": (
            "III",
            "Support-Graph Reachability and Matrix-Composition Obstructions: Image--Kernel Mismatch with a Rubik-Cube Case Study",
        ),
        "paper4": (
            "IV",
            "Collision Geometry of Joint Spectra: Affine Branch Arrangements, Exact Finite Censuses, and Conditional Spectral Quotients",
        ),
        "paper5": (
            "V",
            "Boolean Support Does Not Determine Commutator Accessibility: Direct Support, Exact Cancellation, and Low-Depth Hall Bridges",
        ),
        "paper6": (
            "VI",
            "Linearized Commutativity Geometry on the Generator-Set Moduli Space: Full-Matrix Jacobian Certificates, Normality Gates, and Typed Spectral Registrations",
        ),
        "paper7": (
            "VII",
            "Incidence Geometry of Projected Operator Composition: Rank Protection, Image--Kernel Alignment, and Promotion Limits",
        ),
        "paper8": (
            "VIII",
            "Sectorized Observable Framework: A Typed Static Object Language for Sectorized Observables",
        ),
    }
    published_active = {
        "paper1": (
            "10.5281/zenodo.21571403",
            "https://doi.org/10.5281/zenodo.21571403",
            "Paper I of the RIME program, version 2.0. DOI:",
        ),
        "paper2": (
            "10.5281/zenodo.21581072",
            "https://doi.org/10.5281/zenodo.21581072",
            "Paper II of the RIME program, version 2.0. DOI:",
        ),
        "paper3": (
            "10.5281/zenodo.21583070",
            "https://doi.org/10.5281/zenodo.21583070",
            "Paper III of the RIME program, version 2.0. DOI:",
        ),
        "paper4": (
            "10.5281/zenodo.21972335",
            "https://doi.org/10.5281/zenodo.21972335",
            "Paper IV of the RIME program, version 2.1. DOI:",
        ),
        "paper5": (
            "10.5281/zenodo.21634007",
            "https://doi.org/10.5281/zenodo.21634007",
            "Paper V of the RIME program, version 2.0. DOI:",
        ),
        "paper6": (
            "10.5281/zenodo.21973224",
            "https://doi.org/10.5281/zenodo.21973224",
            "Paper VI of the RIME program, version 2.1. DOI:",
        ),
        "paper7": (
            "10.5281/zenodo.21976516",
            "https://doi.org/10.5281/zenodo.21976516",
            "Paper VII of the RIME program, version 2.1. DOI:",
        ),
        "paper8": (
            "10.5281/zenodo.21977464",
            "https://doi.org/10.5281/zenodo.21977464",
            "Paper VIII of the RIME program, version 2.1. DOI:",
        ),
    }

    def displayed_title(entry):
        match = re.search(r"(?m)^\s*title\s*=\s*\{(.*)\},\s*$", entry)
        if match is None:
            return None
        # Ignore BibTeX case-protection braces when checking reader-facing titles.
        return match.group(1).replace("{", "").replace("}", "")

    for key, (title, doi) in historical.items():
        entry = entries.get(key)
        if entry is None:
            errors.append(f"missing historical BibTeX key: {key}")
            continue
        if displayed_title(entry) != title:
            errors.append(f"{key}: title does not match the immutable v1 object")
        if f"doi     = {{{doi}}}" not in entry:
            errors.append(f"{key}: missing or incorrect historical DOI {doi}")

    for key, (roman, title) in active.items():
        entry = entries.get(key)
        if entry is None:
            errors.append(f"missing active BibTeX key: {key}")
            continue
        if displayed_title(entry) != title:
            errors.append(f"{key}: title does not match the active v2 manuscript")
        if key in published_active:
            doi, url, note = published_active[key]
            if f"doi     = {{{doi}}}" not in entry:
                errors.append(f"{key}: missing or incorrect active DOI {doi}")
            if f"url     = {{{url}}}" not in entry:
                errors.append(f"{key}: missing or incorrect active DOI URL {url}")
            if note not in entry:
                errors.append(f"{key}: published version note is missing")
        elif re.search(r"(?m)^\s*(doi|url)\s*=", entry):
            errors.append(f"{key}: active entry must remain DOI/URL-free until deposited")
        if key in {"paper4", "paper5", "paper6", "paper7"} and key not in published_active and (
            "Version 2 manuscript" not in entry
        ):
            errors.append(f"{key}: version-2 manuscript note is missing")

    companion = entries.get("ccs")
    companion_title = (
        "RIME Computational Companion Archive: Versioned Reproducibility "
        "Data, Computational Observations, Open Problems, and Historical Records"
    )
    if companion is None:
        errors.append("missing active BibTeX key: ccs")
    else:
        if displayed_title(companion) != companion_title:
            errors.append("ccs: title does not match the published v2 archive")
        if "doi     = {10.5281/zenodo.21616956}" not in companion:
            errors.append("ccs: missing or incorrect v2 archive DOI")
        if "Optional non-paper archive, version 2.0." not in companion:
            errors.append("ccs: published version note is missing")

    combined = entries.get("rimecombinedv1")
    if combined is None:
        errors.append("missing historical BibTeX key: rimecombinedv1")
    elif "doi     = {10.5281/zenodo.21108197}" not in combined:
        errors.append("rimecombinedv1: historical DOI does not match")

    return errors


# ── Check table ─────────────────────────────────────────────────────────────
# (pattern, [files], description, must_exist)
# must_exist=True → positive check (value must appear)
# must_exist=False → negative check (drifted value must NOT appear)

LEGACY_CHECKS = [
    # ═══ Representation ═══
    (r"228.dim|228-dimensional|\\mathbb\{C\}\^\{?228|228\\\)|dimension 228|228 =|\b228\b", ["Paper I", "Paper II", "Paper III", "CCS"],
     "Total dim = 228", True),
    (r"64\s*\+\s*144\s*\+\s*8\s*\+\s*12|64\+144\+8\+12", ["Paper I", "Paper II", "Paper III", "CCS"],
     "Block sum 64+144+8+12", True),

    # ═══ Spectral ═══
    (r"6\s+(canonical\s+)?(spectral\s+)?layers|6\s+distinct\s+eigenvalues", ["Paper I", "Paper III", "CCS"],
     "6 spectral layers", True),
    (r"0,\s*1,\s*2,\s*3,\s*4,\s*6", ["Paper I", "CCS"],
     "k-set includes 0,1,2,3,4,6", True),
    (r"k\s*=\s*5.*(?:vacan|absent|missing|gap|forbid)", ["Paper I", "CCS"],
     "k=5 vacancy", True),
    (r"1\s*-\s*k\s*/\s*9|1-k/9|1 - k/9", ["Paper I", "Paper III", "CCS"],
     "Eigenvalue form λ=1-k/9", True),

    # ═══ 9 QT/HT joint-spectral sectors (legacy: primitive sectors) ═══
    (r"9\s+(?:QT/HT\s+joint-spectral|primitive)\s+sectors|9\s+sectors", ["Paper I", "Paper II", "Paper III", "CCS"],
     "9 QT/HT joint-spectral sectors", True),

    # ═══ Sector dimensions ═══
    (r"S2.*\b2\b.*eo|S2.*2-dim|\b2\b.*dim.*S2", ["Paper II", "CCS"],
     "S2 has dim 2", True),
    (r"S4.*26.*ep.*co|S4.*26-dim|26.*ep.*co.*S4", ["Paper II", "CCS"],
     "S4 dim=26, ep+co", True),
    (r"S5.*\b1\b.*eo|S5.*1-dim.*eo|eo.*1.*S5", ["Paper II", "CCS"],
     "S5 dim=1, pure eo", True),
    (r"S7.*66.*cp.*ep.*co.*eo|S7.*66-dim", ["Paper II", "CCS"],
     "S7 dim=66, all blocks", True),
    (r"S8.*\b8\b.*cp|S8.*8-dim|pure.*CP.*\b8\b", ["Paper II", "CCS"],
     "S8 dim=8, pure CP", True),
    (r"S9.*27.*cp.*co|S9.*27-dim|CP\+CO.*27", ["Paper II", "CCS"],
     "S9 dim=27, cp+co", True),

    # ═══ Transport ═══
    (r"10\s+direct\s+(transport\s+)?edges", ["Paper II", "CCS"],
     "10 direct edges", True),
    (r"10\s+(direct|undirected)\s+(edges|pairs)", ["Paper III"],
     "10 edges/pairs in Paper III", True),
    (r"Type\s+I.*(?:9|nine)|(?:9|nine).*Type\s+I|9.*Type I.*edge", ["Paper II", "CCS"],
     "9 Type I edges", True),
    (r"S8.*S9.*2\.83|S8↔S9.*2\.83|Type\s+II.*CP|CP.*permutation.*channel", ["Paper II", "CCS"],
     "Type II CP channel S8↔S9", True),

    # ═══ T7 ═══
    (r"5\s+T7\s+pairs|T7.*\b5\b.*cross-block|\b5\b.*cross-block.*T7", ["Paper II", "Paper III", "CCS"],
     "5 T7 pairs", True),
    (r"T7.*cross.block|cross.block.*T7|all\s+cross-block.*T7|T7.*all\s+cross-block", ["Paper II", "Paper III", "CCS"],
     "All T7 cross-block", True),

    # ═══ Hub degrees ═══
    (r"S6.*(?:primary\s+)?hub.*(?:degree|deg)\s*5|S6.*degree 5|degree 5.*S6|deg.*5.*S6", ["Paper II", "Paper III", "CCS"],
     "S6 hub degree = 5", True),
    (r"S7.*(?:secondary\s+)?hub.*(?:degree|deg)\s*3|S7.*degree 3|degree 3.*S7|deg.*3.*S7", ["Paper II", "Paper III", "CCS"],
     "S7 hub degree = 3", True),

    # ═══ Curvature ═══
    (r"7\s+(?:pure\s+)?curvature\s+channels", ["Paper III", "CCS"],
     "7 pure curvature channels", True),
    (r"curvature.*within.block|within.block.*curvature|all.*within-block.*curvature", ["Paper III", "CCS"],
     "All curvature within-block", True),

    # ═══ Commutant ═══
    (r"Comm.*610|610.*commutant|\\mathrm\{Comm\}.*610|610.*dim", ["Paper I", "Paper II", "CCS"],
     "Comm(ρ)=610", True),
    (r"Comm.*804|804.*commutant|\\mathrm\{Comm\}.*804|804.*dim", ["CCS"],
     "Comm(A)=804", True),
    (r"\\Delta.*194|194.*commutant|Δ.*194", ["CCS"],
     "Δ_comm=194", True),

    # ═══ Isotypic ═══
    (r"51\s+isotypic\s+components", ["Paper I", "CCS"],
     "51 isotypic components", True),
    (r"multiplicity\s+reservoir|V_\{5/9\}\^\{\\?\(3,11\)\\?\}|3\\text\{D\}\\times11.*V_\{5/9\}", ["Paper I", "CCS"],
     "Multiplicity reservoir V_{5/9}^{(3,11)}", True),

    # ═══ EP Algebra ═══
    (r"M_2.*\\mathbb\{C\}.*\)\^4|M_2\(C\)\^4|M_2\^4", ["Paper II", "CCS"],
     "M₂(C)⁴", True),
    (r"3\s+active\s+M.*2|3.*M.*2.*active|active.*3.*M", ["Paper II", "CCS"],
     "3 active M₂", True),

    # ═══ Noncommutativity ═══
    (r"93\.9\s*\\?%|93\.9%.*noncommut|noncommut.*93\.9", ["Paper II", "Paper III", "CCS"],
     "93.9% EP noncommutativity", True),
    (r"2\.74.*ep|ep.*2\.74|QT.*2\.74", ["Paper II", "CCS"],
     "EP QT commutator = 2.74", True),

    # ═══ S₃ Prototypes ═══
    (r"S.*3.*nat.*reg.*9.dim|9-dim.*nat.*reg|nat.*oplus.*reg.*9", ["Paper III", "CCS"],
     "S₃ nat⊕reg 9-dim", True),
    (r"S.?(3|₃).*reg.*reg.*12.dim|12-dim.*reg.*reg|reg.*oplus.*reg.*12", ["Paper III", "CCS"],
     "S₃ reg⊕reg 12-dim", True),
    (r"nat.*reg.*0\s+T7|0\s+T7.*nat", ["Paper III", "CCS"],
     "S₃ nat⊕reg: 0 T7 pairs (negative control)", True),
    (r"reg.*reg.*0\s+T7|0\s+T7.*reg.*reg", ["Paper III", "CCS"],
     "S₃ reg⊕reg: 0 T7 pairs (negative control)", True),

    # ═══ N=2 Negative Control ═══
    (r"N=2.*(?:0|zero)\s+T7|0\s+T7.*N=2|pocket.*cube.*(?:0|zero).*T7", ["CCS"],
     "N=2: 0 T7 pairs", True),
    (r"N=2.*(?:0|zero)\s+hybrid|0\s+hybrid.*N=2", ["CCS"],
     "N=2: 0 hybrid sectors", True),

    # ═══════════════════════════════════════════════════════════════
    # NEGATIVE CHECKS — forbidden drifted values
    # ═══════════════════════════════════════════════════════════════

    # S7 degree 4
    (r"S7.*(?:secondary\s+)?hub.*(?:degree|deg)\s*4|S7.*degree 4",
     ["Paper I", "Paper II", "Paper III", "CCS"],
     "S7 degree 4 (should be 3) MUST NOT appear", False),

    # 11 direct edges
    (r"11\s+direct\s+(?:transport\s+)?edges",
     ["Paper I", "Paper II", "Paper III", "CCS"],
     "'11 direct edges' must NOT appear (should be 10)", False),

    # 6 pure curvature channels at 9-sector
    (r"6\s+pure\s+curvature\s+channels",
     ["Paper III"],
     "'6 pure curvature channels' (should be 7 at 9-sector) MUST NOT appear", False),

    # paper_data.md in Paper II/III running text
    (r"\[paper_data\.md\]|paper_data\.md",
     ["Paper II", "Paper III"],
     "paper_data.md references in Paper II/III must NOT appear", False),

    # T7 count = 4
    (r"4\s+T7\s+pairs.*Rubik|Rubik.*4\s+T7\s+pairs",
     ["Paper I", "Paper II", "Paper III", "CCS"],
     "'4 T7 pairs' for Rubik must NOT appear (should be 5)", False),

    # Stale S3 T7 counts (fixed 2026-05-26 — now 0 T7, negative controls)
    (r"nat.*reg.*3\s+T7|3\s+T7.*nat",
     ["Paper I", "Paper II", "Paper III", "CCS"],
     "'3 T7' in S₃ nat⊕reg must NOT appear (should be 0, negative control)", False),
    (r"reg.*reg.*9\s+T7|9\s+T7.*reg.*reg",
     ["Paper I", "Paper II", "Paper III", "CCS"],
     "'9 T7' in S₃ reg⊕reg must NOT appear (should be 0, negative control)", False),

    # 10 pure curvature channels
    (r"10\s+(?:pure\s+)?curvature\s+channels",
     ["Paper I", "Paper II", "Paper III", "CCS"],
     "'10 curvature channels' must NOT appear (should be 7)", False),

    # ═══════════════════════════════════════════════════════════════
    # NOTATION CHECKS - legacy forbidden forms retained as inline rules.
    # Use plain substring matching (use_regex=False) to avoid escaping hell.
    # ═══════════════════════════════════════════════════════════════

    # --- Multi-letter operators: \operatorname vs \text / \mathrm ---
    (r"\text{Comm}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{Comm} must NOT appear (use \operatorname{Comm})", False, False),
    (r"\mathrm{Comm}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\mathrm{Comm} must NOT appear (use \operatorname{Comm})", False, False),
    (r"\text{End}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{End} must NOT appear (use \operatorname{End})", False, False),
    (r"\mathrm{End}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\mathrm{End} must NOT appear (use \operatorname{End})", False, False),
    (r"\text{Center}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{Center} must NOT appear (use \operatorname{Center})", False, False),
    (r"\mathrm{Center}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\mathrm{Center} must NOT appear (use \operatorname{Center})", False, False),
    (r"\text{Supp}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{Supp} must NOT appear (use \operatorname{Supp})", False, False),
    (r"\mathrm{Supp}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\mathrm{Supp} must NOT appear (use \operatorname{Supp})", False, False),
    (r"\text{Tr}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{Tr} must NOT appear (use \operatorname{Tr})", False, False),
    (r"\mathrm{Tr}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\mathrm{Tr} must NOT appear (use \operatorname{Tr})", False, False),
    (r"\text{Spec}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{Spec} must NOT appear (use \operatorname{Spec})", False, False),
    (r"\mathrm{Spec}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\mathrm{Spec} must NOT appear (use \operatorname{Spec})", False, False),
    (r"\text{Lie}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{Lie} must NOT appear (use \operatorname{Lie})", False, False),
    (r"\mathrm{Lie}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\mathrm{Lie} must NOT appear (use \operatorname{Lie})", False, False),

    # --- Block labels: \mathrm{cp/ep/co/eo} ---
    (r"\text{cp}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{cp} must NOT appear (use \mathrm{cp})", False, False),
    (r"\text{ep}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{ep} must NOT appear (use \mathrm{ep})", False, False),
    (r"\text{co}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{co} must NOT appear (use \mathrm{co})", False, False),
    (r"\text{eo}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{eo} must NOT appear (use \mathrm{eo})", False, False),

    # --- Operator labels: \mathrm{QT/HT} ---
    (r"\text{QT}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{QT} must NOT appear (use \mathrm{QT})", False, False),
    (r"\text{HT}", ["Paper I", "Paper II", "Paper III", "CCS"],
     r"\text{HT} must NOT appear (use \mathrm{HT})", False, False),

    # --- lam18 / lam_{18} ---
    ("lam_{18}", ["Paper I", "Paper II", "Paper III", "CCS"],
     "lam_{18} must NOT appear (use \\lambda)", False, False),
    ("lam18", ["Paper I", "Paper II", "Paper III", "CCS"],
     "lam18 must NOT appear (use \\lambda)", False, False),

    # --- Block name variants (plain text) ---
    ("E_P", ["Paper I", "Paper II", "Paper III", "CCS"],
     "E_P must NOT appear (use EP)", False, False),
    ("E_O", ["Paper I", "Paper II", "Paper III", "CCS"],
     "E_O must NOT appear (use EO)", False, False),
    ("C_P", ["Paper I", "Paper II", "Paper III", "CCS"],
     "C_P must NOT appear (use CP)", False, False),
    ("C_O", ["Paper I", "Paper II", "Paper III", "CCS"],
     "C_O must NOT appear (use CO)", False, False),
    ("even permutation block", ["Paper I", "Paper II", "Paper III", "CCS"],
     "'even permutation block' must NOT appear (use EP block)", False, False),
]


# Current manuscript and archive checks. The first-version table above is
# retained only as provenance for the claim-diff and is deliberately not
# executed. CCS v2 is an archive, not a second assertion surface for every
# numerical claim owned by Papers I--III.
CHECKS = [
    (r"228.dim|228-dimensional|\b228\b",
     ["Paper I", "Paper II", "Paper III"],
     "ambient representation dimension 228", True),
    (r"64\s*\+\s*144\s*\+\s*8\s*\+\s*12|64\+144\+8\+12",
     ["Paper I", "Paper II", "Paper III"],
     "physical block dimensions 64+144+8+12", True),
    (r"6\s+(canonical\s+)?(spectral\s+)?layers|six-layer",
     ["Paper I"],
     "six canonical A-spectral layers", True),
    (r"9\s+(?:QT/HT\s+joint-spectral|QH\s+joint|registered QH|primitive)\s+sectors|nine\s+QH\s+joint",
     ["Paper II"],
     "nine QH joint-spectral sectors", True),
    (r"(?:10|ten)\s+(?:direct|undirected)\s+(?:transport\s+)?(?:edges|pairs)",
     ["Paper II"],
     "ten direct support edges", True),
    (r"(?:15|fifteen)\s+(?:overlap\s+)?(?:candidate|pair)|(?:candidate|pair)[^\n]{0,40}(?:15|fifteen)",
     ["Paper II"],
     "15 block-level Supp_nc overlap candidates", True),
    (r"(?:6|six)\s+(?:false-positive\s+)?(?:candidate|nonedge)|(?:false-positive|nonedge)[^\n]{0,40}(?:6|six)",
     ["Paper II"],
     "six Supp_nc overlap nonedges", True),
    (r"(?i)transport.{0,20}non-invariance|non-invariance.{0,20}transport",
     ["Paper II"],
     "transport-non-invariance identity", True),
    (r"graph.only|graph/operator|support.graph.*projected|projected.*composition",
     ["Paper II", "Paper III"],
     "support graph and projected composition are separated", True),
    (r"five\s+(?:canonical\s+)?(?:graph-only|two-step|support)|5\s+graph-only",
     ["Paper III"],
     "five graph-only obstruction witnesses", True),
    (r"machine-zero|products?\s+vanish|projected products vanish",
     ["Paper II", "Paper III"],
     "canonical projected products vanish", True),
    (r"optional human-readable companion material|not a paper, theorem source",
     ["CCS"],
     "CCS archive boundary", True),
    (r"10\.5281/zenodo\.21571403|10\.5281/zenodo\.21581072|10\.5281/zenodo\.21583070",
     ["CCS"],
     "CCS navigation to independent Paper I--III DOI records", True),
    (r"historical combined package|immutable provenance record",
     ["CCS"],
     "historical combined release is provenance only", True),
    (r"not a sufficient transport criterion",
     ["CCS"],
     "CCS preserves the Paper II localizer boundary", True),
    (r"five declared two-step support-graph|five declared two-step",
     ["CCS"],
     "CCS identifies the finite Paper III composition audit", True),
    (r"composition path .*works",
     ["Paper I", "Paper II", "Paper III"],
     "support path must not be called a working composition", False),
    (r"5\s+T7\s+morphisms|five\s+T7\s+morphisms",
     ["Paper I", "Paper II", "Paper III"],
     "five T7 morphisms must not be promoted in current papers", False),
    (r"compositional accessibility.*strict|strict separation.*Lie",
     ["Paper I", "Paper II", "Paper III"],
     "old strict-containment theorem must not appear in current papers", False),
    (r"unique\s+G-invariant\s+proper\s+subrepresentation",
     ["Paper I", "Paper II", "Paper III"],
     "S1 must not be called the unique proper G-subrepresentation", False),
    (r"CCS-r2",
     ["Paper I", "Paper II", "Paper III"],
     "current papers must not cite CCS-r2", False),
]


def main():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("RIME Registry Validator")
    print(
        f"Checking {len(PAPERS)} documents against {len(CHECKS)} checks "
        "plus versioned bibliography identities\n"
    )

    errors_by_file = {fk: [] for fk in PAPERS}

    for entry in CHECKS:
        pattern, files, description, must_exist = entry[:4]
        use_regex = entry[4] if len(entry) > 4 else True
        errs = check(pattern, files, description, must_exist, use_regex=use_regex)
        if errs:
            tag = "MISSING" if must_exist else "FORBIDDEN"
            print(f"FAIL [{tag}]: {description}")
            for fk in files:
                ferrs = [e for e in errs if e.startswith(f"  {fk}:")]
                for e in ferrs:
                    print(e)
                    errors_by_file[fk].append((description, e))
            print()

    bibliography_errors = check_bibliography_identities()
    if bibliography_errors:
        print("FAIL [BIBLIOGRAPHY]: versioned publication identities")
        for error in bibliography_errors:
            print(f"  Bibliography: {error}")
        print()

    total_errs = sum(len(v) for v in errors_by_file.values()) + len(
        bibliography_errors
    )
    print(f"{'='*60}")
    if total_errs == 0:
        print("ALL CHECKS PASSED - registry matches all documents.")
        return 0
    else:
        failing_sources = sum(1 for v in errors_by_file.values() if v)
        if bibliography_errors:
            failing_sources += 1
        print(f"FAILURES: {total_errs} total across {failing_sources} sources")
        for fk, errs in errors_by_file.items():
            if errs:
                print(f"  {fk}: {len(errs)} failures")
        return 1


if __name__ == "__main__":
    sys.exit(main())
